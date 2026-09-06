"""GRC Evidence Rule — continuous control monitoring engine.

A rule is a one-time-defined pattern that says: "this control is satisfied
when these records in this doctype meet these conditions." The engine
evaluates the rule whenever the source data changes (real-time) or on a
daily schedule, and creates Audit Findings automatically when rules fail.
"""

import json
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_days, getdate, today, flt


class GRCEvidenceRule(Document):
    def validate(self):
        # Validate JSON in source_filters
        if self.source_filters:
            try:
                json.loads(self.source_filters)
            except (TypeError, ValueError) as e:
                frappe.throw(f"source_filters is not valid JSON: {e}")

        # Evaluation-type-specific validation
        if self.evaluation_type in ("Field Must Be Set", "Field Must Equal Value",
                                     "Field Must Be Within Days") and not self.field_to_check:
            frappe.throw(f"field_to_check is required for evaluation type "
                         f"{self.evaluation_type}")
        if self.evaluation_type == "Field Must Equal Value" and not self.expected_value:
            frappe.throw("expected_value is required for 'Field Must Equal Value' rules")

    def evaluate(self, trigger_type="Manual", record_name=None):
        """Run the evaluation. Returns the evaluation log document.

        record_name: if set, evaluate only that single source record (real-time mode).
        Otherwise evaluate all matching records (scheduled / manual mode).
        """
        if not self.is_active:
            return None

        try:
            if record_name:
                pass_count, fail_count, failed_records, log = self._evaluate_single(record_name)
            else:
                pass_count, fail_count, failed_records, log = self._evaluate_all()
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"Evidence Rule evaluation error: {self.name}")
            pass_count, fail_count, failed_records = 0, 0, []
            log = f"Evaluation error: {frappe.get_traceback()[:1000]}"
            status = "Error"
        else:
            total = pass_count + fail_count
            if fail_count == 0 and total > 0:
                status = "Passed"
            elif fail_count > 0:
                status = "Failed"
            elif total == 0 and self.evaluation_type == "Minimum Record Count":
                status = "Failed"
                fail_count = 1
            elif total == 0:
                status = "Warning"
            else:
                status = "Passed"

        total = pass_count + fail_count
        pass_rate = (pass_count / total * 100.0) if total > 0 else 100.0

        # Persist evaluation log
        eval_doc = frappe.get_doc({
            "doctype": "GRC Evidence Rule Evaluation",
            "rule": self.name,
            "evaluated_at": now_datetime(),
            "client": self.client,
            "framework": self.framework,
            "control_reference": self.control_reference,
            "trigger_type": trigger_type,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "evaluation_status": status,
            "failed_records": json.dumps(failed_records[:100]) if failed_records else "[]",
            "evaluation_log": log,
        })

        # v2.10.0 — chain this evaluation to the previous one for this rule,
        # so a stored Pass/Fail result can't be edited after the fact
        # without the chain breaking (see alphax_grc.integrity.verify_chain).
        from alphax_grc.integrity import compute_chain_hash, get_last_hash
        prev_hash = get_last_hash("GRC Evidence Rule Evaluation", {"rule": self.name})
        eval_doc.prev_hash = prev_hash
        eval_doc.snapshot_hash = compute_chain_hash(
            prev_hash, self.name, eval_doc.evaluated_at, pass_count, fail_count, status,
        )

        eval_doc.insert(ignore_permissions=True)

        # Update rule's last-evaluated cache
        self.last_evaluated = now_datetime()
        self.last_pass_count = pass_count
        self.last_fail_count = fail_count
        self.last_pass_rate = pass_rate
        self.db_update()

        # Auto-create Finding if configured and rule failed
        if status == "Failed" and self.auto_create_finding:
            try:
                finding = self._create_finding(eval_doc, failed_records)
                if finding:
                    eval_doc.finding_created = finding
                    eval_doc.db_update()
            except Exception:
                frappe.log_error(frappe.get_traceback(),
                                 f"Failed to auto-create finding for rule {self.name}")

        frappe.db.commit()
        return eval_doc

    def _evaluate_all(self):
        """Evaluate the rule against all source records matching filters."""
        if not frappe.db.exists("DocType", self.source_doctype):
            return 0, 0, [], f"Source doctype '{self.source_doctype}' not found on this site."

        filters = json.loads(self.source_filters) if self.source_filters else {}
        records = frappe.get_all(self.source_doctype, filters=filters,
                                 fields=["name"], limit_page_length=10000)

        if self.evaluation_type == "Minimum Record Count":
            count = len(records)
            min_required = int(self.min_required_count or 1)
            if count >= min_required:
                return count, 0, [], f"Found {count} records (min required: {min_required}) — PASS"
            return 0, 1, [], f"Found {count} records (min required: {min_required}) — FAIL"

        if self.evaluation_type == "No Records Allowed":
            count = len(records)
            if count == 0:
                return 1, 0, [], "No matching records found — PASS"
            return 0, count, [r.name for r in records], (
                f"{count} records found that should not exist")

        # Per-record evaluation
        pass_count, fail_count, failed = 0, 0, []
        log_lines = []
        for r in records:
            ok, reason = self._evaluate_record(r.name)
            if ok:
                pass_count += 1
            else:
                fail_count += 1
                failed.append(r.name)
                if len(log_lines) < 30:
                    log_lines.append(f"  {r.name}: {reason}")

        log = (f"Evaluated {len(records)} records of {self.source_doctype}. "
               f"Pass: {pass_count}, Fail: {fail_count}.\n" +
               ("\n".join(log_lines) if log_lines else ""))
        return pass_count, fail_count, failed, log

    def _evaluate_single(self, record_name):
        """Real-time mode: evaluate just one record (after_save hook)."""
        if not frappe.db.exists(self.source_doctype, record_name):
            return 0, 0, [], f"Record {record_name} no longer exists"
        ok, reason = self._evaluate_record(record_name)
        if ok:
            return 1, 0, [], f"{record_name}: PASS"
        return 0, 1, [record_name], f"{record_name}: FAIL — {reason}"

    def _evaluate_record(self, record_name):
        """Apply the rule to a single record. Return (passed, reason)."""
        try:
            doc = frappe.get_doc(self.source_doctype, record_name)
        except Exception as e:
            return False, f"Cannot load record: {e}"

        if self.evaluation_type == "Field Must Be Set":
            value = doc.get(self.field_to_check)
            if value is None or value == "":
                return False, f"Field '{self.field_to_check}' is empty"
            return True, ""

        if self.evaluation_type == "Field Must Equal Value":
            value = str(doc.get(self.field_to_check) or "")
            expected = str(self.expected_value or "")
            if value == expected:
                return True, ""
            return False, f"{self.field_to_check}={value!r}, expected {expected!r}"

        if self.evaluation_type == "Field Must Be Within Days":
            value = doc.get(self.field_to_check)
            if not value:
                return False, f"Field '{self.field_to_check}' is empty"
            try:
                target_date = getdate(value)
            except Exception:
                return False, f"Field '{self.field_to_check}' is not a date"
            tolerance = int(self.tolerance_days or 0)
            today_date = getdate(today())
            if (today_date - target_date).days <= tolerance:
                return True, ""
            return False, (f"{self.field_to_check}={value} is "
                           f"{(today_date - target_date).days} days old "
                           f"(tolerance {tolerance})")

        if self.evaluation_type == "Custom Python Method":
            return False, "Custom Python Method evaluation not yet wired (v1.8.x)"

        return False, f"Unknown evaluation type: {self.evaluation_type}"

    def _create_finding(self, eval_doc, failed_records):
        """Create a GRC Audit Finding for the failure."""
        if not frappe.db.exists("DocType", "GRC Audit Finding"):
            return None
        # Avoid duplicate findings — only one open finding per rule per client
        existing = frappe.get_all("GRC Audit Finding",
            filters={
                "client": self.client or "",
                "control_reference": self.control_reference,
                "source_evidence_rule": self.name,
                "status": ["in", ["Open", "In Progress"]],
            },
            limit=1,
        )
        if existing:
            return existing[0].name

        try:
            finding_data = {
                "doctype": "GRC Audit Finding",
                "client": self.client or None,
                "title": f"Evidence rule failed: {self.rule_name}",
                "description": (f"Continuous control monitoring detected "
                                f"{eval_doc.fail_count} record(s) failing rule "
                                f"'{self.rule_name}' for control "
                                f"{self.control_reference}.\n\n"
                                f"Failed records: "
                                f"{', '.join(failed_records[:20])}"
                                f"{'...' if len(failed_records) > 20 else ''}"),
                "severity": self.finding_severity,
                "status": "Open",
                "control_reference": self.control_reference,
                "framework": self.framework,
                "source_evidence_rule": self.name,
                "responsible_owner": self.auto_assign_to or None,
                "raised_date": today(),
                "target_date": add_days(today(), 30),
            }
            # Defensive: only include fields that exist on the doctype
            meta = frappe.get_meta("GRC Audit Finding")
            valid_fields = {f.fieldname for f in meta.fields}
            valid_fields.update(("doctype", "name"))
            cleaned = {k: v for k, v in finding_data.items()
                       if k in valid_fields and v is not None}
            cleaned["doctype"] = "GRC Audit Finding"
            finding = frappe.get_doc(cleaned).insert(ignore_permissions=True)
            return finding.name
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                             f"Auto-finding creation failed for rule {self.name}")
            return None


@frappe.whitelist()
def evaluate_rule(rule_name):
    """Manually trigger evaluation of one rule. Returns the eval doc name."""
    rule = frappe.get_doc("GRC Evidence Rule", rule_name)
    eval_doc = rule.evaluate(trigger_type="Manual")
    return eval_doc.name if eval_doc else None


@frappe.whitelist()
def evaluate_all_active_rules():
    """Scheduler entry point — evaluates all active rules with evaluate_daily=1."""
    rules = frappe.get_all("GRC Evidence Rule",
        filters={"is_active": 1, "evaluate_daily": 1}, pluck="name")
    succeeded, failed = 0, 0
    for r in rules:
        try:
            rule = frappe.get_doc("GRC Evidence Rule", r)
            rule.evaluate(trigger_type="Daily Scheduler")
            succeeded += 1
        except Exception:
            failed += 1
            frappe.log_error(frappe.get_traceback(),
                             f"Daily evaluation failed for rule {r}")
    frappe.logger().info(
        f"Evidence Rule daily evaluation: {succeeded} ok, {failed} failed.")
    return {"succeeded": succeeded, "failed": failed}


def trigger_realtime_evaluation(doc, method=None):
    """doc_events hook: when any record is saved, find active rules whose
    source_doctype matches, and evaluate just this record."""
    try:
        if not frappe.db.exists("DocType", "GRC Evidence Rule"):
            return
        rules = frappe.get_all("GRC Evidence Rule",
            filters={
                "is_active": 1,
                "evaluate_on_save": 1,
                "source_doctype": doc.doctype,
            }, pluck="name")
        for rule_name in rules:
            try:
                rule = frappe.get_doc("GRC Evidence Rule", rule_name)
                rule.evaluate(trigger_type="Real-time Save",
                              record_name=doc.name)
            except Exception:
                frappe.log_error(frappe.get_traceback(),
                                 f"Real-time eval failed: rule {rule_name} "
                                 f"on {doc.doctype} {doc.name}")
    except Exception:
        # Hook must NEVER raise — would block legitimate saves
        pass
