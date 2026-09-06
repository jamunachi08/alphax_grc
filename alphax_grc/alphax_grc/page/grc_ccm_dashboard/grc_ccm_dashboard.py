import frappe
from frappe.utils import add_days, today


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive",
    "Compliance Officer", "GRC Assessor", "GRC Auditor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_ccm_dashboard(client=None):
    """Return continuous-control-monitoring summary."""
    _check_auth()

    # Active rules
    rule_filters = {"is_active": 1}
    if client:
        rule_filters["client"] = ["in", [client, ""]]

    rules = []
    if frappe.db.exists("DocType", "GRC Evidence Rule"):
        rules = frappe.get_all(
            "GRC Evidence Rule",
            filters=rule_filters,
            fields=["name", "rule_name", "framework", "control_reference",
                    "rule_priority", "source_doctype", "evaluation_type",
                    "last_evaluated", "last_pass_count", "last_fail_count",
                    "last_pass_rate", "client"],
            order_by="last_pass_rate asc, modified desc",
            limit_page_length=200,
        )

    # Compute aggregates
    total_rules = len(rules)
    failing_rules = sum(1 for r in rules if (r.last_fail_count or 0) > 0)
    never_evaluated = sum(1 for r in rules if not r.last_evaluated)
    perfect_rules = sum(1 for r in rules
                        if r.last_evaluated and (r.last_fail_count or 0) == 0)
    avg_pass_rate = (sum(float(r.last_pass_rate or 0) for r in rules) / total_rules
                     if total_rules else 0)

    # Framework breakdown
    framework_breakdown = {}
    for r in rules:
        fw = r.framework or "Custom"
        if fw not in framework_breakdown:
            framework_breakdown[fw] = {"total": 0, "failing": 0,
                                        "passing": 0, "untested": 0}
        framework_breakdown[fw]["total"] += 1
        if not r.last_evaluated:
            framework_breakdown[fw]["untested"] += 1
        elif (r.last_fail_count or 0) > 0:
            framework_breakdown[fw]["failing"] += 1
        else:
            framework_breakdown[fw]["passing"] += 1

    # Recent evaluations (last 14 days, latest 50)
    recent = []
    if frappe.db.exists("DocType", "GRC Evidence Rule Evaluation"):
        eval_filters = {"evaluated_at": [">=", add_days(today(), -14)]}
        if client:
            eval_filters["client"] = client
        recent = frappe.get_all(
            "GRC Evidence Rule Evaluation",
            filters=eval_filters,
            fields=["name", "rule", "evaluated_at", "framework",
                    "control_reference", "trigger_type",
                    "pass_count", "fail_count", "pass_rate",
                    "evaluation_status", "finding_created", "client"],
            order_by="evaluated_at desc",
            limit_page_length=50,
        )

    # Recent failures only — for the alert section
    recent_failures = [r for r in recent if r.evaluation_status == "Failed"][:10]

    return {
        "summary": {
            "total_rules": total_rules,
            "failing_rules": failing_rules,
            "perfect_rules": perfect_rules,
            "never_evaluated": never_evaluated,
            "avg_pass_rate": round(avg_pass_rate, 1),
        },
        "framework_breakdown": framework_breakdown,
        "rules": rules,
        "recent_evaluations": recent,
        "recent_failures": recent_failures,
        "client": client,
    }


@frappe.whitelist()
def evaluate_now(rule_name):
    """Trigger a manual evaluation of a single rule."""
    _check_auth()
    if not frappe.db.exists("GRC Evidence Rule", rule_name):
        frappe.throw(f"Rule {rule_name} not found")
    rule = frappe.get_doc("GRC Evidence Rule", rule_name)
    eval_doc = rule.evaluate(trigger_type="Manual")
    if not eval_doc:
        return {"ok": False, "message": "Rule is inactive"}
    return {
        "ok": True,
        "evaluation": eval_doc.name,
        "status": eval_doc.evaluation_status,
        "pass_count": eval_doc.pass_count,
        "fail_count": eval_doc.fail_count,
        "pass_rate": eval_doc.pass_rate,
    }
