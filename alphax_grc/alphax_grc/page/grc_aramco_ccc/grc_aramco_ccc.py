import frappe
from frappe.utils import today, date_diff


_GRC_ROLES = {
    "System Manager", "GRC Admin", "Aramco Compliance Owner",
    "GRC Executive", "Compliance Officer", "GRC Auditor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_aramco_ccc_dashboard(client=None):
    """Return summary + engagement list + certificate list, scoped to a
    client or firm-wide if client is None."""
    _check_auth()

    eng_filters = {"client": client} if client else {}
    cert_filters = {"client": client} if client else {}

    engagements = []
    if frappe.db.exists("DocType", "GRC Aramco CCC Engagement"):
        engagements = frappe.get_all(
            "GRC Aramco CCC Engagement",
            filters=eng_filters,
            fields=["name", "engagement_title", "client", "third_party_profile",
                    "engagement_status", "service_class_tier",
                    "compliance_percentage", "audit_findings_open",
                    "self_assessment_due_date", "audit_scheduled_date",
                    "lead_consultant"],
            order_by="modified desc",
            limit_page_length=100,
        )

    certificates = []
    if frappe.db.exists("DocType", "GRC Aramco Certificate"):
        certificates = frappe.get_all(
            "GRC Aramco Certificate",
            filters=cert_filters,
            fields=["name", "certificate_number", "client", "third_party_profile",
                    "status", "issue_date", "expiry_date", "days_to_expiry",
                    "service_class_tier", "audit_firm"],
            order_by="expiry_date asc",
            limit_page_length=200,
        )

    # Summary buckets
    by_status = {}
    for e in engagements:
        by_status[e.engagement_status] = by_status.get(e.engagement_status, 0) + 1

    cert_by_status = {}
    for c in certificates:
        cert_by_status[c.status or "Unknown"] = cert_by_status.get(c.status or "Unknown", 0) + 1

    expiring_30 = sum(1 for c in certificates
                      if c.days_to_expiry is not None and 0 <= (c.days_to_expiry or 0) <= 30)
    expiring_90 = sum(1 for c in certificates
                      if c.days_to_expiry is not None and 30 < (c.days_to_expiry or 0) <= 90)
    expired = sum(1 for c in certificates
                  if c.days_to_expiry is not None and (c.days_to_expiry or 0) < 0)

    return {
        "summary": {
            "total_engagements": len(engagements),
            "total_certificates": len(certificates),
            "active_certificates": cert_by_status.get("Active", 0),
            "expiring_30": expiring_30,
            "expiring_90": expiring_90,
            "expired": expired,
            "by_status": by_status,
            "cert_by_status": cert_by_status,
        },
        "engagements": engagements,
        "certificates": certificates,
    }
