"""GRC NIST CSF 2.0 Dashboard — function-by-function compliance view per client.

Shows the 6 NIST CSF functions (GV/ID/PR/DE/RS/RC) as cards with:
- Total subcategories per function
- Implementation tier breakdown
- Average implementation %
- Click-through to subcategory list
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
    """Return NIST CSF posture for a client (or app-wide if client not set)."""
    _check_auth()

    if not frappe.db.exists("DocType", "GRC NIST CSF Catalog"):
        return {"functions": [], "summary": {}, "client": client}

    # Catalog totals per function
    catalog_rows = frappe.get_all(
        "GRC NIST CSF Catalog",
        filters={"is_active": 1},
        fields=["name", "function_code", "function_label",
                "category_code", "subcategory_code"],
        limit_page_length=200,
    )

    function_totals = {}
    for r in catalog_rows:
        fc = r.function_code or "—"
        if fc not in function_totals:
            function_totals[fc] = {
                "code": fc,
                "label": r.function_label or fc,
                "total": 0,
                "categories": set(),
            }
        function_totals[fc]["total"] += 1
        function_totals[fc]["categories"].add(r.category_code)

    # Per-client tracking — count by tier
    tier_counts = {fc: {} for fc in function_totals}
    score_sum = {fc: 0.0 for fc in function_totals}
    score_count = {fc: 0 for fc in function_totals}

    if frappe.db.exists("DocType", "GRC NIST CSF Control"):
        filters = {}
        if client:
            filters["client"] = client
        controls = frappe.get_all(
            "GRC NIST CSF Control",
            filters=filters,
            fields=["function_code", "implementation_tier",
                    "compliance_score"],
            limit_page_length=2000,
        )
        for c in controls:
            fc = c.function_code or "—"
            if fc not in tier_counts:
                continue
            tier = c.implementation_tier or "Not Assessed"
            tier_counts[fc][tier] = tier_counts[fc].get(tier, 0) + 1
            try:
                score_sum[fc] += float(c.compliance_score or 0)
                score_count[fc] += 1
            except Exception:
                pass

    functions = []
    desired_order = ["GV", "ID", "PR", "DE", "RS", "RC"]
    for fc in desired_order:
        if fc not in function_totals:
            continue
        ft = function_totals[fc]
        avg_score = (score_sum[fc] / score_count[fc]) if score_count[fc] else 0
        functions.append({
            "code": fc,
            "label": ft["label"],
            "total_subcategories": ft["total"],
            "category_count": len(ft["categories"]),
            "tier_breakdown": tier_counts.get(fc, {}),
            "avg_score": round(avg_score, 1),
            "tracked_count": score_count[fc],
        })

    summary = {
        "total_subcategories": len(catalog_rows),
        "total_functions": len(function_totals),
        "client": client,
        "tracked_overall": sum(score_count.values()),
    }

    return {"functions": functions, "summary": summary, "client": client}
