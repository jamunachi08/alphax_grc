"""GRC Engagement — the consultant's cockpit.

This controller implements the state machine that drives a consulting
engagement through 7 phases (or 8 for Aramco). On every interaction it:

  - Validates phase entry/completion criteria
  - Logs every decision into GRC Engagement Decision Log
  - Auto-creates downstream artifacts (per-client controls, tasks, findings)
  - Computes engagement health (overdue tasks, blocking issues, etc.)
  - Refuses to advance to the next phase if blockers are open

The phases are defined in data via GRC Engagement Phase Template, so adding
a new engagement type or modifying an existing one does not require code
changes — just new template records.
"""

import frappe
import json
from frappe.model.document import Document
from frappe.utils import (
    today, now_datetime, getdate, add_days, date_diff, cint, flt,
)


class GRCEngagement(Document):

    # ----------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------

    def validate(self):
        # Bootstrap phase log on first save if missing
        if not self.phase_log and self.engagement_type:
            self._bootstrap_phase_log()

        # If status moved to Active and we haven't started phase 1 yet, start it
        if (self.engagement_status == "Active"
                and (not self.current_phase_number or self.current_phase_number < 1)
                and self.phase_log):
            self._start_phase(1)

        # Compute days_in_current_phase + overdue
        if self.current_phase_started:
            self.days_in_current_phase = date_diff(today(), self.current_phase_started)
            tmpl = self._current_phase_template()
            expected = (tmpl.get("expected_duration_days") if tmpl else 14) or 14
            self.is_overdue = 1 if self.days_in_current_phase > expected else 0

    def on_update(self):
        # Refresh engagement health metrics on every save
        self._refresh_health_metrics()
        # v2.0.0 — auto-create per-client controls when frameworks_in_scope
        # changes. Idempotent: skips frameworks already populated for this
        # client. Only triggers when frameworks_in_scope actually changed
        # (avoids re-running on every save).
        if self.has_value_changed("frameworks_in_scope") and self.frameworks_in_scope:
            try:
                from alphax_grc.engagement_automation import (
                    auto_create_per_client_controls,
                )
                results = auto_create_per_client_controls(self)
                if results:
                    # Surface a non-blocking message
                    summaries = [f"{fw}: {r}" for fw, r in results.items()]
                    try:
                        frappe.msgprint(
                            "Per-client controls auto-created — "
                            + "; ".join(summaries),
                            title="Frameworks Adopted",
                            indicator="green",
                            alert=True,
                        )
                    except Exception:
                        pass
            except Exception:
                try:
                    frappe.log_error(frappe.get_traceback(),
                                     f"Engagement {self.name}: framework "
                                     f"auto-creation hook failed")
                except Exception:
                    pass

    # ----------------------------------------------------------------
    # Phase log bootstrap
    # ----------------------------------------------------------------

    def _bootstrap_phase_log(self):
        """Populate phase_log child table from the templates for this
        engagement_type. Idempotent — only runs if phase_log is empty."""
        if self.phase_log:
            return
        templates = self._all_phase_templates()
        if not templates:
            return
        for t in templates:
            self.append("phase_log", {
                "phase_number": t.get("phase_number"),
                "phase_code": t.get("phase_code"),
                "phase_label": t.get("phase_label"),
                "status": "Locked" if t.get("phase_number") > 1 else "Ready",
                "completion_pct": 0,
                "blocker_count": 0,
            })

    def _all_phase_templates(self):
        """Return ordered list of phase template dicts for this engagement_type."""
        if not self.engagement_type:
            return []
        rows = frappe.get_all(
            "GRC Engagement Phase Template",
            filters={"engagement_type": self.engagement_type, "is_active": 1},
            fields=["name", "phase_number", "phase_code", "phase_label",
                    "purpose_summary", "expected_duration_days",
                    "entry_criteria", "completion_criteria",
                    "auto_advance_when_complete",
                    "on_phase_start_method", "on_phase_complete_method",
                    "icon"],
            order_by="phase_number asc",
        )
        return rows

    def _phase_template(self, phase_number):
        """Return the phase template dict for a given phase number."""
        if not phase_number:
            return None
        rows = frappe.get_all(
            "GRC Engagement Phase Template",
            filters={"engagement_type": self.engagement_type,
                     "phase_number": phase_number, "is_active": 1},
            fields=["name", "phase_number", "phase_code", "phase_label",
                    "purpose_summary", "expected_duration_days",
                    "entry_criteria", "completion_criteria",
                    "auto_advance_when_complete",
                    "on_phase_start_method", "on_phase_complete_method"],
            limit=1,
        )
        return rows[0] if rows else None

    def _current_phase_template(self):
        return self._phase_template(self.current_phase_number)

    # ----------------------------------------------------------------
    # State machine operations
    # ----------------------------------------------------------------

    def _start_phase(self, phase_number):
        """Move into the given phase. Updates current_phase_* fields and
        marks the corresponding phase_log row as In Progress."""
        tmpl = self._phase_template(phase_number)
        if not tmpl:
            frappe.throw(f"No phase template found for phase {phase_number} "
                         f"in engagement type {self.engagement_type}")
        self.current_phase_number = phase_number
        self.current_phase_label = tmpl["phase_label"]
        self.current_phase_started = now_datetime()
        self.days_in_current_phase = 0
        self.is_overdue = 0

        for row in (self.phase_log or []):
            if row.phase_number == phase_number:
                row.status = "In Progress"
                row.started_at = now_datetime()
                row.completion_pct = 0
            elif row.phase_number < phase_number:
                if row.status not in ("Completed", "Skipped"):
                    row.status = "Completed"
                    row.completed_at = row.completed_at or now_datetime()
                    row.completion_pct = 100
            else:
                if row.status not in ("Completed", "Skipped"):
                    row.status = "Locked"

        # Log the decision
        self._log_decision(
            decision_type="Phase Transition",
            summary=f"Started phase {phase_number} — {tmpl['phase_label']}",
            rationale=tmpl.get("purpose_summary") or "",
        )

        # Optional automation hook
        method = tmpl.get("on_phase_start_method")
        if method:
            try:
                frappe.get_attr(method)(self)
            except Exception:
                frappe.log_error(frappe.get_traceback(),
                                 f"Phase start automation failed: {method}")

    @frappe.whitelist()
    def advance_phase(self, force=False):
        """Move to the next phase. Refuses if blocking criteria are unmet
        unless force=True (System Manager override)."""
        if self.engagement_status != "Active":
            frappe.throw("Engagement must be Active to advance phases. "
                         "Set status to Active and save first.")

        current = self.current_phase_number or 0
        if not current:
            self._start_phase(1)
            self.save(ignore_permissions=True)
            return {"ok": True, "new_phase": 1,
                    "message": "Started phase 1"}

        # Check completion criteria of current phase
        blockers = self.get_blockers() if not force else []
        if blockers:
            return {"ok": False, "blockers": blockers,
                    "message": "Cannot advance — blockers open. "
                               "Resolve them or use force=true (admin)."}

        # Advance
        next_phase = current + 1
        all_phases = self._all_phase_templates()
        if next_phase > len(all_phases):
            # End of lifecycle
            self.engagement_status = "Completed"
            self.actual_completion_date = today()
            for row in (self.phase_log or []):
                if row.phase_number == current and row.status != "Completed":
                    row.status = "Completed"
                    row.completed_at = now_datetime()
                    row.completion_pct = 100
            self._log_decision(
                decision_type="Closure",
                summary=f"Engagement completed (all {current} phases done)",
                rationale="All phases complete; engagement marked Completed.",
            )
            self.save(ignore_permissions=True)
            return {"ok": True, "completed": True,
                    "message": f"Engagement completed."}

        # Mark current done, start next
        for row in (self.phase_log or []):
            if row.phase_number == current and row.status != "Completed":
                row.status = "Completed"
                row.completed_at = now_datetime()
                row.completion_pct = 100

        # Optional completion hook on the OLD phase
        old_tmpl = self._phase_template(current)
        method = (old_tmpl or {}).get("on_phase_complete_method")
        if method:
            try:
                frappe.get_attr(method)(self)
            except Exception:
                frappe.log_error(frappe.get_traceback(),
                                 f"Phase complete automation failed: {method}")

        self._start_phase(next_phase)
        self.save(ignore_permissions=True)
        return {"ok": True, "new_phase": next_phase,
                "message": f"Advanced to phase {next_phase}"}

    @frappe.whitelist()
    def get_blockers(self):
        """Return list of human-readable blockers preventing phase advance."""
        blockers = []
        # Phase 1 (Discovery) blockers
        if self.current_phase_number == 1:
            if not self.executive_sponsor:
                blockers.append("Executive sponsor not set")
            if not self.scope_summary:
                blockers.append("Scope summary not written")

        # Phase 2 (Scoping) blockers
        if self.current_phase_number == 2:
            if not self.frameworks_in_scope:
                blockers.append("No frameworks selected for scope")

        # Phase 3 (Assessment) blockers — at least 50% of controls assessed
        if self.current_phase_number == 3:
            if not self._assessment_threshold_met(0.5):
                blockers.append(
                    "Less than 50% of in-scope controls have been assessed")

        # Phase 4 (Risk Analysis) — every Not Implemented finding has a risk
        if self.current_phase_number == 4:
            unmapped = self._findings_without_risk()
            if unmapped:
                blockers.append(
                    f"{len(unmapped)} finding(s) without an associated "
                    f"Risk Register entry")

        # Phase 5 (Treatment Planning) — every High/Critical risk has a treatment
        if self.current_phase_number == 5:
            untreated = self._high_risks_without_treatment()
            if untreated:
                blockers.append(
                    f"{untreated} High/Critical risk(s) without treatment plan")

        # Generic blocker: any phase_log checklist item flagged is_blocker that's not done
        # (currently checklist items live in JSON field; future enhancement)

        return blockers

    def _assessment_threshold_met(self, fraction):
        """Returns True if at least `fraction` of in-scope controls have a
        compliance_status set to anything other than 'Not Started' / blank."""
        if not self.client:
            return False
        # We can't know exactly which doctype to count without the framework,
        # so check each adopted framework's per-client tracking doctype.
        total, assessed = 0, 0
        if frappe.db.exists("DocType", "GRC NCA ECC Control"):
            total += frappe.db.count("GRC NCA ECC Control", {"client": self.client})
            assessed += frappe.db.count("GRC NCA ECC Control", {
                "client": self.client,
                "compliance_status": ["not in",
                                      ["Not Started", "", None]],
            })
        if frappe.db.exists("DocType", "GRC ISO42001 Control"):
            total += frappe.db.count("GRC ISO42001 Control", {"client": self.client})
            assessed += frappe.db.count("GRC ISO42001 Control", {
                "client": self.client,
                "compliance_status": ["not in",
                                      ["Not Started", "", None]],
            })
        if total == 0:
            return False
        return (assessed / total) >= fraction

    def _findings_without_risk(self):
        """Return list of finding names that don't have a corresponding risk."""
        if not frappe.db.exists("DocType", "GRC Audit Finding"):
            return []
        if not frappe.db.exists("DocType", "GRC Risk Register"):
            return []
        findings = frappe.get_all(
            "GRC Audit Finding",
            filters={"client": self.client, "status": ["in",
                ["Open", "In Progress"]]},
            fields=["name", "control_reference"],
            limit_page_length=500,
        )
        unmapped = []
        for f in findings:
            if not f.control_reference:
                continue
            # Look for a risk with matching control_reference
            try:
                exists = frappe.db.exists("GRC Risk Register", {
                    "client": self.client,
                    "linked_controls": ["like", f"%{f.control_reference}%"],
                })
            except Exception:
                exists = None
            if not exists:
                unmapped.append(f.name)
        return unmapped

    def _high_risks_without_treatment(self):
        """Return count of High/Critical risks that don't have any treatment."""
        if not frappe.db.exists("DocType", "GRC Risk Register"):
            return 0
        try:
            rows = frappe.get_all(
                "GRC Risk Register",
                filters={
                    "client": self.client,
                    "risk_rating": ["in", ["High", "Critical"]],
                },
                fields=["name", "treatment_strategy"],
                limit_page_length=500,
            )
        except Exception:
            return 0
        return sum(1 for r in rows
                   if not (r.treatment_strategy and r.treatment_strategy.strip()))

    # ----------------------------------------------------------------
    # Decision log helper
    # ----------------------------------------------------------------

    def _log_decision(self, decision_type, summary, rationale=""):
        try:
            doc = frappe.get_doc({
                "doctype": "GRC Engagement Decision Log",
                "engagement": self.name,
                "client": self.client,
                "logged_at": now_datetime(),
                "logged_by": frappe.session.user,
                "decision_type": decision_type,
                "phase_at_decision": self.current_phase_label or "",
                "decision_summary": summary,
                "rationale": rationale,
            })
            doc.insert(ignore_permissions=True)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Decision log insert failed: {self.name}")
            except Exception:
                pass

    # ----------------------------------------------------------------
    # Health metrics — auto-populated read-only fields
    # ----------------------------------------------------------------

    def _refresh_health_metrics(self):
        if not self.client:
            return
        # Open findings
        if frappe.db.exists("DocType", "GRC Audit Finding"):
            try:
                self.db_set("open_findings_count", frappe.db.count(
                    "GRC Audit Finding",
                    {"client": self.client,
                     "status": ["in", ["Open", "In Progress"]]}),
                    update_modified=False)
            except Exception:
                pass

        # High/Critical risks
        if frappe.db.exists("DocType", "GRC Risk Register"):
            try:
                self.db_set("high_risks_count", frappe.db.count(
                    "GRC Risk Register",
                    {"client": self.client,
                     "risk_rating": ["in", ["High", "Critical"]]}),
                    update_modified=False)
            except Exception:
                pass

        # Tasks
        if frappe.db.exists("DocType", "GRC Implementation Task"):
            try:
                self.db_set("tasks_pending_count", frappe.db.count(
                    "GRC Implementation Task",
                    {"engagement": self.name,
                     "status": ["in", ["Pending", "In Progress"]]}),
                    update_modified=False)
                self.db_set("tasks_overdue_count", frappe.db.count(
                    "GRC Implementation Task",
                    {"engagement": self.name,
                     "status": ["in", ["Pending", "In Progress"]],
                     "due_date": ["<", today()]}),
                    update_modified=False)
            except Exception:
                pass

        # Evidence rule failures (last 30 days for this client)
        if frappe.db.exists("DocType", "GRC Evidence Rule Evaluation"):
            try:
                self.db_set("evidence_rule_failures", frappe.db.count(
                    "GRC Evidence Rule Evaluation",
                    {"client": self.client,
                     "evaluation_status": "Failed",
                     "evaluated_at": [">=", add_days(today(), -30)]}),
                    update_modified=False)
            except Exception:
                pass


# ===================================================================
# Whitelisted module-level helpers (callable from JS)
# ===================================================================

@frappe.whitelist()
def advance_engagement_phase(engagement_name, force=0):
    eng = frappe.get_doc("GRC Engagement", engagement_name)
    return eng.advance_phase(force=cint(force))


@frappe.whitelist()
def get_engagement_blockers(engagement_name):
    eng = frappe.get_doc("GRC Engagement", engagement_name)
    return eng.get_blockers()


@frappe.whitelist()
def get_engagement_overview(engagement_name):
    """Comprehensive overview for the engagement form's status tab."""
    if not frappe.db.exists("GRC Engagement", engagement_name):
        frappe.throw(f"Engagement {engagement_name} not found")
    eng = frappe.get_doc("GRC Engagement", engagement_name)
    eng._refresh_health_metrics()
    eng.reload()

    blockers = eng.get_blockers()
    current_tmpl = eng._current_phase_template()
    return {
        "engagement": engagement_name,
        "client": eng.client,
        "title": eng.engagement_title,
        "type": eng.engagement_type,
        "status": eng.engagement_status,
        "current_phase_number": eng.current_phase_number,
        "current_phase_label": eng.current_phase_label,
        "current_phase_started": str(eng.current_phase_started or ""),
        "days_in_phase": eng.days_in_current_phase or 0,
        "is_overdue": eng.is_overdue,
        "all_phases": eng._all_phase_templates(),
        "phase_log": [
            {
                "phase_number": r.phase_number,
                "phase_code": r.phase_code,
                "phase_label": r.phase_label,
                "status": r.status,
                "started_at": str(r.started_at or ""),
                "completed_at": str(r.completed_at or ""),
                "completion_pct": r.completion_pct or 0,
            }
            for r in (eng.phase_log or [])
        ],
        "current_phase_purpose": (current_tmpl or {}).get("purpose_summary") or "",
        "current_phase_entry": (current_tmpl or {}).get("entry_criteria") or "",
        "current_phase_completion": (current_tmpl or {}).get("completion_criteria") or "",
        "blockers": blockers,
        "health": {
            "open_findings": eng.open_findings_count or 0,
            "high_risks": eng.high_risks_count or 0,
            "tasks_pending": eng.tasks_pending_count or 0,
            "tasks_overdue": eng.tasks_overdue_count or 0,
            "evidence_rule_failures": eng.evidence_rule_failures or 0,
        },
    }


@frappe.whitelist()
def kickoff_engagement(engagement_name):
    """One-click 'start the engagement': flips Draft → Active and starts phase 1."""
    eng = frappe.get_doc("GRC Engagement", engagement_name)
    if eng.engagement_status == "Draft":
        eng.engagement_status = "Active"
        if not eng.kickoff_date:
            eng.kickoff_date = today()
        eng.save(ignore_permissions=True)
        return {"ok": True, "started": True,
                "message": "Engagement kicked off; now in phase 1."}
    return {"ok": False,
            "message": f"Engagement is {eng.engagement_status}, not Draft. "
                       f"Already started."}
