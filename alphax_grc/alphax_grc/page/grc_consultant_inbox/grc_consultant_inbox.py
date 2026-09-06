"""GRC Consultant Inbox — unified work queue.

Aggregates across engagements, tasks, findings, and evidence-rule failures
to give the logged-in consultant a single screen showing what needs their
attention right now, sorted by urgency.
"""

import frappe
from frappe.utils import today, add_days, getdate, date_diff


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
def get_inbox(scope="mine"):
    """Return the unified work queue for the current user.

    scope: 'mine' = only items I own/lead, 'all' = everything visible.
    """
    _check_auth()
    user = frappe.session.user

    # ---- Engagements I lead (or all if scope=all) ----
    eng_filters = {"engagement_status": ["in", ["Active", "Draft"]]}
    if scope == "mine":
        eng_filters["lead_consultant"] = user

    engagements = []
    if frappe.db.exists("DocType", "GRC Engagement"):
        engagements = frappe.get_all(
            "GRC Engagement",
            filters=eng_filters,
            fields=["name", "engagement_title", "client", "engagement_type",
                    "engagement_status", "current_phase_number",
                    "current_phase_label", "is_overdue",
                    "days_in_current_phase", "open_findings_count",
                    "high_risks_count", "tasks_pending_count",
                    "tasks_overdue_count", "evidence_rule_failures",
                    "target_completion_date"],
            order_by="is_overdue desc, modified desc",
            limit_page_length=50,
        )

    # ---- Tasks assigned to me ----
    my_tasks = []
    if frappe.db.exists("DocType", "GRC Implementation Task"):
        task_filters = {"status": ["in", ["Pending", "In Progress"]]}
        if scope == "mine":
            task_filters["responsible_owner"] = user
        my_tasks = frappe.get_all(
            "GRC Implementation Task",
            filters=task_filters,
            fields=["name", "task_title", "engagement", "client",
                    "control_reference", "framework", "category",
                    "responsible_team", "priority", "status",
                    "due_date", "responsible_owner"],
            order_by="due_date asc, priority asc",
            limit_page_length=50,
        )

    today_d = getdate(today())
    overdue_tasks, due_soon_tasks, future_tasks = [], [], []
    for t in my_tasks:
        if t.due_date and getdate(t.due_date) < today_d:
            overdue_tasks.append(t)
        elif t.due_date and date_diff(t.due_date, today()) <= 7:
            due_soon_tasks.append(t)
        else:
            future_tasks.append(t)

    # ---- Findings assigned to me ----
    my_findings = []
    if frappe.db.exists("DocType", "GRC Audit Finding"):
        finding_filters = {"status": ["in", ["Open", "In Progress"]]}
        if scope == "mine":
            # Try by responsible_owner if the field exists
            meta = frappe.get_meta("GRC Audit Finding")
            owner_fields = [f.fieldname for f in meta.fields
                            if f.fieldname in ("responsible_owner", "owner_user", "assigned_to")]
            if owner_fields:
                finding_filters[owner_fields[0]] = user
        try:
            my_findings = frappe.get_all(
                "GRC Audit Finding",
                filters=finding_filters,
                fields=["name", "title", "client", "framework",
                        "control_reference", "severity", "status",
                        "target_date"],
                order_by="severity asc, target_date asc",
                limit_page_length=20,
            )
        except Exception:
            my_findings = []

    # ---- Recent Evidence Rule failures ----
    recent_failures = []
    if frappe.db.exists("DocType", "GRC Evidence Rule Evaluation"):
        try:
            recent_failures = frappe.get_all(
                "GRC Evidence Rule Evaluation",
                filters={
                    "evaluation_status": "Failed",
                    "evaluated_at": [">=", add_days(today(), -7)],
                },
                fields=["name", "rule", "client", "framework",
                        "control_reference", "trigger_type",
                        "fail_count", "evaluated_at", "finding_created"],
                order_by="evaluated_at desc",
                limit_page_length=15,
            )
        except Exception:
            recent_failures = []

    # v1.9.3 — total client count for orientation-rail step 1 routing
    total_clients = 0
    if frappe.db.exists("DocType", "GRC Client Profile"):
        try:
            total_clients = frappe.db.count("GRC Client Profile")
        except Exception:
            total_clients = 0

    # ---- Engagement summary numbers ----
    summary = {
        "total_clients": total_clients,
        "total_engagements": len(engagements),
        "overdue_engagements": sum(1 for e in engagements if e.is_overdue),
        "tasks_overdue": len(overdue_tasks),
        "tasks_due_soon": len(due_soon_tasks),
        "open_findings": len(my_findings),
        "rule_failures_7d": len(recent_failures),
    }

    return {
        "user": user,
        "scope": scope,
        "summary": summary,
        "engagements": engagements,
        "tasks_overdue": overdue_tasks,
        "tasks_due_soon": due_soon_tasks,
        "tasks_future_count": len(future_tasks),
        "findings": my_findings,
        "rule_failures": recent_failures,
    }


@frappe.whitelist()
def quick_advance_engagement(engagement_name):
    """Inbox shortcut to advance an engagement's phase."""
    _check_auth()
    if not frappe.db.exists("GRC Engagement", engagement_name):
        frappe.throw("Engagement not found")
    eng = frappe.get_doc("GRC Engagement", engagement_name)
    return eng.advance_phase()
