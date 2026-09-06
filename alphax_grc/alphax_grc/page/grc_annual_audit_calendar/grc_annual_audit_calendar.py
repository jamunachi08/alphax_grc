"""GRC Annual Audit Calendar — year-at-a-glance view + auto-roll-forward.

Aggregates GRC Audit Plan records by their planned_start_date month
and provides controls to:

 - Filter by year and client
 - Roll all recurring templates forward to the next year (creating
   new GRC Audit Plan records dated 12 months ahead)
"""

import frappe
from frappe.utils import (
    today, getdate, add_months, get_first_day, get_last_day,
)
from datetime import date


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive",
    "Compliance Officer", "GRC Auditor", "GRC Assessor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_calendar(year=None, client=None):
    """Return audit plans organized by month for a given year + client."""
    _check_auth()

    if not year:
        year = date.today().year
    year = int(year)

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    filters = {
        "planned_start_date": ["between", [year_start, year_end]],
    }
    if client:
        filters["client"] = client

    plans = []
    if frappe.db.exists("DocType", "GRC Audit Plan"):
        plans = frappe.get_all(
            "GRC Audit Plan",
            filters=filters,
            fields=["name", "audit_title", "client", "audit_type",
                    "audit_owner", "lead_auditor", "team_responsible",
                    "planned_start_date", "planned_end_date",
                    "status", "linked_framework", "frequency",
                    "is_recurring_template", "parent_audit_plan"],
            order_by="planned_start_date asc",
            limit_page_length=500,
        )

    # Bucket by month
    months = {m: [] for m in range(1, 13)}
    for p in plans:
        if not p.planned_start_date:
            continue
        m = getdate(p.planned_start_date).month
        months[m].append(p)

    # Compute summary stats
    today_d = getdate(today())
    summary = {
        "year": year,
        "total_audits": len(plans),
        "completed": sum(1 for p in plans if (p.status or "") == "Completed"),
        "in_progress": sum(1 for p in plans if (p.status or "") == "In Progress"),
        "planned": sum(1 for p in plans if (p.status or "") in ("", "Planned", "Scheduled")),
        "overdue": sum(1 for p in plans if p.planned_end_date
                       and getdate(p.planned_end_date) < today_d
                       and (p.status or "") != "Completed"),
        "recurring_templates": sum(1 for p in plans if p.is_recurring_template),
    }

    # Convert dates to strings for JSON
    for p in plans:
        if p.planned_start_date:
            p.planned_start_date = str(p.planned_start_date)
        if p.planned_end_date:
            p.planned_end_date = str(p.planned_end_date)
    for m, lst in months.items():
        for p in lst:
            if p.planned_start_date:
                p.planned_start_date = str(p.planned_start_date)
            if p.planned_end_date:
                p.planned_end_date = str(p.planned_end_date)

    return {
        "summary": summary,
        "year": year,
        "client": client,
        "months": months,
        "plans": plans,
    }


@frappe.whitelist()
def roll_forward_recurring(target_year=None, source_year=None, client=None):
    """Auto-roll-forward function: for every Audit Plan in source_year that
    is marked as a recurring template, create a copy dated target_year.

    Idempotent — skips audits that already have a child plan in target_year.
    """
    _check_auth()
    if "GRC Admin" not in frappe.get_roles(frappe.session.user) and \
       "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw("GRC Admin or System Manager role required to roll forward.")

    if not source_year:
        source_year = date.today().year
    source_year = int(source_year)
    if not target_year:
        target_year = source_year + 1
    target_year = int(target_year)

    if target_year <= source_year:
        frappe.throw("target_year must be greater than source_year")

    src_start = date(source_year, 1, 1)
    src_end = date(source_year, 12, 31)

    filters = {
        "is_recurring_template": 1,
        "planned_start_date": ["between", [src_start, src_end]],
    }
    if client:
        filters["client"] = client

    if not frappe.db.exists("DocType", "GRC Audit Plan"):
        return {"ok": False, "error": "GRC Audit Plan doctype not found"}

    templates = frappe.get_all(
        "GRC Audit Plan", filters=filters,
        fields=["name", "audit_title", "client", "audit_type", "audit_owner",
                "lead_auditor", "team_responsible", "planned_start_date",
                "planned_end_date", "linked_framework", "frequency",
                "audit_id", "audit_or_review", "scope_summary",
                "audit_methodology", "audit_methods", "criteria",
                "sampling", "evidence_needed", "duration_estimate",
                "schedule_notes", "cost"],
    )

    rolled = 0
    skipped = 0
    failed = 0

    for t in templates:
        # Compute new dates: same month/day, but target_year
        try:
            old_start = getdate(t.planned_start_date)
            old_end = getdate(t.planned_end_date) if t.planned_end_date else None
            new_start = old_start.replace(year=target_year)
            new_end = old_end.replace(year=target_year) if old_end else None
        except Exception:
            failed += 1
            continue

        # Idempotent: skip if a child of this template already exists in target_year
        try:
            existing = frappe.db.exists("GRC Audit Plan", {
                "parent_audit_plan": t.name,
                "planned_start_date": ["between",
                                       [date(target_year, 1, 1),
                                        date(target_year, 12, 31)]],
            })
        except Exception:
            existing = False
        if existing:
            skipped += 1
            continue

        # Create the new plan
        try:
            new_plan = frappe.get_doc({
                "doctype": "GRC Audit Plan",
                "audit_title": t.audit_title,
                "client": t.client,
                "audit_type": t.audit_type,
                "audit_owner": t.audit_owner,
                "lead_auditor": t.lead_auditor,
                "team_responsible": t.team_responsible,
                "planned_start_date": new_start,
                "planned_end_date": new_end,
                "linked_framework": t.linked_framework,
                "frequency": t.frequency,
                "is_recurring_template": 0,  # children are not templates themselves
                "parent_audit_plan": t.name,
                "status": "Planned",
                "audit_id": t.audit_id,
                "audit_or_review": t.audit_or_review,
                "scope_summary": t.scope_summary,
                "audit_methodology": t.audit_methodology,
                "audit_methods": t.audit_methods,
                "criteria": t.criteria,
                "sampling": t.sampling,
                "evidence_needed": t.evidence_needed,
                "duration_estimate": t.duration_estimate,
                "schedule_notes": t.schedule_notes,
                "cost": t.cost,
            })
            new_plan.insert(ignore_permissions=True)
            rolled += 1
        except Exception:
            failed += 1
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Roll-forward failed for {t.name}")
            except Exception:
                pass

    try:
        frappe.db.commit()
    except Exception:
        pass

    return {
        "ok": True,
        "source_year": source_year,
        "target_year": target_year,
        "templates_found": len(templates),
        "rolled_forward": rolled,
        "skipped_already_exists": skipped,
        "failed": failed,
    }
