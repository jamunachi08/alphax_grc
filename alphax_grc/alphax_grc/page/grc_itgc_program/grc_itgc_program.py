import frappe

# Roles allowed to view GRC dashboards (kept in sync with api.py).
_GRC_DASHBOARD_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive", "Compliance Officer",
    "GRC Assessor", "GRC Auditor", "Risk Owner", "Privacy Officer",
    "Aramco Compliance Owner",
}

def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_DASHBOARD_ROLES):
        frappe.throw("You are not permitted to access this GRC resource.", frappe.PermissionError)


@frappe.whitelist()
def get_itgc_summary():
    """Return ITGC audit programme summary stats for the dashboard."""
    _check_auth()
    if not frappe.db.exists("DocType", "GRC ITGC Audit Item"):
        return {}

    total = frappe.db.count("GRC ITGC Audit Item")
    delivered = frappe.db.count("GRC ITGC Audit Item", {"delivery_status": "Delivered"})
    partial = frappe.db.count("GRC ITGC Audit Item", {"delivery_status": "Partially Delivered"})
    pending = frappe.db.count("GRC ITGC Audit Item", {"delivery_status": "Pending"})
    na = frappe.db.count("GRC ITGC Audit Item", {"delivery_status": "Not Applicable"})
    satisfactory = frappe.db.count("GRC ITGC Audit Item", {"review_status": "Satisfactory"})
    requires_improvement = frappe.db.count("GRC ITGC Audit Item", {"review_status": "Requires Improvement"})
    unsatisfactory = frappe.db.count("GRC ITGC Audit Item", {"review_status": "Unsatisfactory"})

    # By domain
    domains = frappe.db.sql("""
        SELECT control_domain,
               COUNT(*) as total,
               SUM(CASE WHEN delivery_status='Delivered' THEN 1 ELSE 0 END) as delivered,
               SUM(CASE WHEN delivery_status='Pending' THEN 1 ELSE 0 END) as pending,
               SUM(CASE WHEN review_status='Satisfactory' THEN 1 ELSE 0 END) as satisfactory,
               SUM(CASE WHEN review_status='Unsatisfactory' THEN 1 ELSE 0 END) as unsatisfactory
        FROM `tabGRC ITGC Audit Item`
        GROUP BY control_domain
        ORDER BY total DESC
    """, as_dict=True)

    # By control type
    ctrl_types = frappe.db.sql("""
        SELECT
            SUM(ctrl_administrative) as administrative,
            SUM(ctrl_technical) as technical,
            SUM(ctrl_physical) as physical
        FROM `tabGRC ITGC Audit Item`
    """, as_dict=True)

    # Framework coverage
    fw_coverage = frappe.db.sql("""
        SELECT
            SUM(map_glba) as glba, SUM(map_nist) as nist,
            SUM(map_iso) as iso, SUM(map_pci_dss) as pci_dss,
            SUM(map_cobit) as cobit, SUM(map_cis) as cis,
            SUM(map_ffiec) as ffiec, SUM(map_ncua) as ncua,
            SUM(map_nca_ecc) as nca_ecc, SUM(map_sama) as sama
        FROM `tabGRC ITGC Audit Item`
    """, as_dict=True)

    completion_pct = round((delivered / total * 100), 1) if total else 0

    return {
        "total": total,
        "delivered": delivered,
        "partial": partial,
        "pending": pending,
        "not_applicable": na,
        "satisfactory": satisfactory,
        "requires_improvement": requires_improvement,
        "unsatisfactory": unsatisfactory,
        "completion_pct": completion_pct,
        "domains": domains,
        "ctrl_types": ctrl_types[0] if ctrl_types else {},
        "fw_coverage": fw_coverage[0] if fw_coverage else {},
    }
