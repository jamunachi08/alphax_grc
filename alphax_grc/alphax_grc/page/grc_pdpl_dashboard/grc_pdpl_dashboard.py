"""GRC PDPL Dashboard — KSA Privacy posture by article section.

Shows 4 PDPL section cards (PDPL Law / Implementing Regulation /
Cross-Border Transfer / NDMO Guidance) + DSAR backlog + DPIA risk mix.
"""

import frappe
from frappe.utils import today, add_days


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
def get_dashboard(client=None):
    """Return PDPL posture for a client (or app-wide if client not set)."""
    _check_auth()

    if not frappe.db.exists("DocType", "GRC PDPL Catalog"):
        return {
            "sections": [], "summary": {}, "client": client,
            "dsar": {}, "dpia": {}, "doctype_missing": True,
        }

    # PDPL catalog sections
    catalog_rows = frappe.get_all(
        "GRC PDPL Catalog",
        filters={"is_active": 1},
        fields=["name", "article_section", "article_code"],
        limit_page_length=200,
    )

    section_totals = {}
    for r in catalog_rows:
        s = r.article_section or "—"
        if s not in section_totals:
            section_totals[s] = {"code": s, "total": 0}
        section_totals[s]["total"] += 1

    # Per-client tracking
    status_counts = {s: {} for s in section_totals}
    score_sum = {s: 0.0 for s in section_totals}
    score_count = {s: 0 for s in section_totals}

    if frappe.db.exists("DocType", "GRC PDPL Control"):
        filters = {}
        if client:
            filters["client"] = client
        controls = frappe.get_all(
            "GRC PDPL Control",
            filters=filters,
            fields=["article_section", "compliance_status",
                    "compliance_score"],
            limit_page_length=2000,
        )
        for c in controls:
            s = c.article_section or "—"
            if s not in status_counts:
                continue
            status = c.compliance_status or "Not Started"
            status_counts[s][status] = status_counts[s].get(status, 0) + 1
            try:
                score_sum[s] += float(c.compliance_score or 0)
                score_count[s] += 1
            except Exception:
                pass

    desired_order = ["PDPL Law", "Implementing Regulation",
                     "Cross-Border Transfer Regulation", "NDMO Guidance"]
    sections = []
    for sn in desired_order:
        if sn not in section_totals:
            continue
        st = section_totals[sn]
        avg = (score_sum[sn] / score_count[sn]) if score_count[sn] else 0
        sections.append({
            "code": sn,
            "total_articles": st["total"],
            "status_breakdown": status_counts.get(sn, {}),
            "avg_score": round(avg, 1),
            "tracked_count": score_count[sn],
        })

    # DSAR backlog
    dsar = {"total": 0, "open": 0, "overdue": 0, "by_status": {}}
    if frappe.db.exists("DocType", "GRC DSAR Request"):
        dsar_filters = {}
        if client:
            dsar_filters["client"] = client
        dsar_rows = frappe.get_all(
            "GRC DSAR Request", filters=dsar_filters,
            fields=["status", "is_overdue"],
            limit_page_length=2000)
        dsar["total"] = len(dsar_rows)
        terminal = {"Responded", "Closed", "Declined", "Withdrawn"}
        for d in dsar_rows:
            dsar["by_status"][d.status or "Unknown"] = (
                dsar["by_status"].get(d.status or "Unknown", 0) + 1)
            if d.status not in terminal:
                dsar["open"] += 1
            if d.is_overdue:
                dsar["overdue"] += 1

    # DPIA risk mix
    dpia = {"total": 0, "high_risk": 0, "by_decision": {},
            "by_inherent_risk": {}}
    if frappe.db.exists("DocType", "GRC DPIA Record"):
        dpia_filters = {}
        if client:
            dpia_filters["client"] = client
        dpia_rows = frappe.get_all(
            "GRC DPIA Record", filters=dpia_filters,
            fields=["decision", "is_high_risk", "inherent_risk_level"],
            limit_page_length=2000)
        dpia["total"] = len(dpia_rows)
        for d in dpia_rows:
            if d.is_high_risk:
                dpia["high_risk"] += 1
            dec = d.decision or "Pending"
            dpia["by_decision"][dec] = dpia["by_decision"].get(dec, 0) + 1
            ir = d.inherent_risk_level or "Not Assessed"
            dpia["by_inherent_risk"][ir] = (
                dpia["by_inherent_risk"].get(ir, 0) + 1)

    summary = {
        "total_articles": len(catalog_rows),
        "total_sections": len(section_totals),
        "tracked_overall": sum(score_count.values()),
        "client": client,
    }

    return {
        "sections": sections, "summary": summary,
        "dsar": dsar, "dpia": dpia, "client": client,
    }
