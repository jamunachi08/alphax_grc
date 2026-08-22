import frappe

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
def get_asset_summary():
    """Return asset inventory summary for the dashboard."""
    _check_auth()
    if not frappe.db.exists("DocType", "GRC Asset Inventory"):
        return _empty()

    total = frappe.db.count("GRC Asset Inventory")
    if not total:
        return _empty()

    # By type
    by_type = frappe.db.sql("""
        SELECT asset_type, COUNT(*) as count
        FROM `tabGRC Asset Inventory`
        GROUP BY asset_type ORDER BY count DESC
    """, as_dict=True)

    # By criticality
    by_criticality = frappe.db.sql("""
        SELECT asset_criticality, COUNT(*) as count
        FROM `tabGRC Asset Inventory`
        GROUP BY asset_criticality ORDER BY FIELD(asset_criticality,'Critical','High','Medium','Low','Very Low')
    """, as_dict=True)

    # By status
    by_status = frappe.db.sql("""
        SELECT asset_status, COUNT(*) as count
        FROM `tabGRC Asset Inventory`
        GROUP BY asset_status ORDER BY count DESC
    """, as_dict=True)

    # By NCA domain
    by_nca = frappe.db.sql("""
        SELECT nca_ecc_domain, COUNT(*) as count
        FROM `tabGRC Asset Inventory`
        WHERE nca_ecc_domain IS NOT NULL AND nca_ecc_domain != ''
        GROUP BY nca_ecc_domain ORDER BY count DESC
    """, as_dict=True)

    # CIA stats
    critical = frappe.db.count("GRC Asset Inventory", {"asset_criticality": "Critical"})
    high = frappe.db.count("GRC Asset Inventory", {"asset_criticality": "High"})
    personal_data = frappe.db.count("GRC Asset Inventory", {"contains_personal_data": 1})
    end_of_life = frappe.db.count("GRC Asset Inventory", {"maintenance_status": "End of Life"})
    overdue_review = frappe.db.sql("""
        SELECT COUNT(*) as cnt FROM `tabGRC Asset Inventory`
        WHERE next_review_date < CURDATE() AND asset_status = 'Active'
    """, as_dict=True)
    overdue = overdue_review[0].cnt if overdue_review else 0

    # Recent assets
    recent = frappe.db.sql("""
        SELECT name, asset_name, asset_type, asset_criticality, asset_status,
               confidentiality, integrity, availability, nca_ecc_domain, ip_address
        FROM `tabGRC Asset Inventory`
        ORDER BY creation DESC LIMIT 10
    """, as_dict=True)

    return {
        "total": total, "critical": critical, "high": high,
        "personal_data": personal_data, "end_of_life": end_of_life, "overdue": overdue,
        "by_type": by_type, "by_criticality": by_criticality,
        "by_status": by_status, "by_nca": by_nca, "recent": recent,
    }

def _empty():
    return {"total":0,"critical":0,"high":0,"personal_data":0,"end_of_life":0,"overdue":0,
            "by_type":[],"by_criticality":[],"by_status":[],"by_nca":[],"recent":[]}


@frappe.whitelist()
def get_nca_ecc_summary():
    """Return NCA ECC-2:2024 compliance summary."""
    if not frappe.db.exists("DocType", "GRC NCA ECC Control"):
        return {}
    total = frappe.db.count("GRC NCA ECC Control")
    if not total:
        return {}
    compliant = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Compliant"})
    partial = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Partially Compliant"})
    non_compliant = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Non-Compliant"})
    not_assessed = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Not Assessed"})
    by_domain = frappe.db.sql("""
        SELECT main_domain, COUNT(*) as total,
               SUM(CASE WHEN compliance_status='Compliant' THEN 1 ELSE 0 END) as compliant,
               SUM(CASE WHEN compliance_status='Partially Compliant' THEN 1 ELSE 0 END) as partial,
               SUM(CASE WHEN compliance_status='Non-Compliant' THEN 1 ELSE 0 END) as non_compliant
        FROM `tabGRC NCA ECC Control` GROUP BY main_domain
    """, as_dict=True)
    by_pillar = frappe.db.sql("""
        SELECT
            SUM(pillar_zero_trust) as zero_trust,
            SUM(pillar_cyber_resilience) as cyber_resilience,
            SUM(pillar_data_sovereignty) as data_sovereignty,
            SUM(pillar_ai_automation) as ai_automation
        FROM `tabGRC NCA ECC Control`
    """, as_dict=True)
    avg_score = frappe.db.sql("SELECT AVG(compliance_score) as avg FROM `tabGRC NCA ECC Control`", as_dict=True)
    score = round(avg_score[0].avg or 0, 1) if avg_score else 0.0
    return {
        "total": total, "compliant": compliant, "partial": partial,
        "non_compliant": non_compliant, "not_assessed": not_assessed,
        "score": score, "by_domain": by_domain,
        "by_pillar": by_pillar[0] if by_pillar else {}
    }
