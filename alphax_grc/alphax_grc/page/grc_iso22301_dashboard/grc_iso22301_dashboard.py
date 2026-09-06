"""GRC ISO 22301 BCMS Dashboard — section-by-section view per client.

Shows 7 ISO 22301 sections (4 Context through 10 Improvement) as cards
with compliance breakdown and progress.
"""

import frappe


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
    """Return ISO 22301 BCMS posture for a client (or app-wide)."""
    _check_auth()

    if not frappe.db.exists("DocType", "GRC ISO22301 Catalog"):
        return {"sections": [], "summary": {}, "client": client}

    catalog_rows = frappe.get_all(
        "GRC ISO22301 Catalog",
        filters={"is_active": 1},
        fields=["name", "section_number", "section_label", "clause_code"],
        limit_page_length=200,
    )

    section_totals = {}
    for r in catalog_rows:
        sn = r.section_number or "—"
        if sn not in section_totals:
            section_totals[sn] = {
                "code": sn,
                "label": r.section_label or sn,
                "total": 0,
            }
        section_totals[sn]["total"] += 1

    status_counts = {sn: {} for sn in section_totals}
    score_sum = {sn: 0.0 for sn in section_totals}
    score_count = {sn: 0 for sn in section_totals}

    if frappe.db.exists("DocType", "GRC ISO22301 Control"):
        filters = {}
        if client:
            filters["client"] = client
        controls = frappe.get_all(
            "GRC ISO22301 Control",
            filters=filters,
            fields=["section_number", "compliance_status", "compliance_score"],
            limit_page_length=2000,
        )
        for c in controls:
            sn = c.section_number or "—"
            if sn not in status_counts:
                continue
            status = c.compliance_status or "Not Started"
            status_counts[sn][status] = status_counts[sn].get(status, 0) + 1
            try:
                score_sum[sn] += float(c.compliance_score or 0)
                score_count[sn] += 1
            except Exception:
                pass

    desired_order = ["4 Context", "5 Leadership", "6 Planning",
                     "7 Support", "8 Operation",
                     "9 Performance Evaluation", "10 Improvement"]
    sections = []
    for sn in desired_order:
        if sn not in section_totals:
            continue
        st = section_totals[sn]
        avg_score = (score_sum[sn] / score_count[sn]) if score_count[sn] else 0
        sections.append({
            "code": sn,
            "label": st["label"],
            "total_clauses": st["total"],
            "status_breakdown": status_counts.get(sn, {}),
            "avg_score": round(avg_score, 1),
            "tracked_count": score_count[sn],
        })

    summary = {
        "total_clauses": len(catalog_rows),
        "total_sections": len(section_totals),
        "tracked_overall": sum(score_count.values()),
        "client": client,
    }

    return {"sections": sections, "summary": summary, "client": client}
