import frappe


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
def get_iso42001_dashboard(client=None):
    """Return ISO 42001 catalog summary + per-client status."""
    _check_auth()

    catalog = []
    if frappe.db.exists("DocType", "GRC ISO42001 Catalog"):
        catalog = frappe.get_all(
            "GRC ISO42001 Catalog",
            filters={"is_active": 1},
            fields=["name", "control_code", "domain_code", "domain_label",
                    "control_title", "implementation_guidance",
                    "document_to_prepare_code", "document_to_prepare_title"],
            order_by="control_code asc",
            limit_page_length=200,
        )

    # Per-domain rollup
    domains_rollup = {}
    for c in catalog:
        d = c.domain_code or "unknown"
        if d not in domains_rollup:
            domains_rollup[d] = {
                "code": d,
                "label": c.domain_label,
                "count": 0,
            }
        domains_rollup[d]["count"] += 1

    # Per-client implementation
    client_status = {}
    if client and frappe.db.exists("DocType", "GRC ISO42001 Control"):
        rows = frappe.get_all(
            "GRC ISO42001 Control",
            filters={"client": client},
            fields=["name", "catalog_ref", "control_code",
                    "compliance_status", "compliance_score",
                    "responsible_owner", "target_date", "ai_system_scope"],
            limit_page_length=200,
        )
        for r in rows:
            client_status[r.catalog_ref] = r

    # Domain implementation rollup if client selected
    domain_implementation = {}
    if client:
        for c in catalog:
            d = c.domain_code
            if d not in domain_implementation:
                domain_implementation[d] = {
                    "Implemented": 0, "Partially Implemented": 0,
                    "In Progress": 0, "Not Started": 0,
                    "Not Applicable": 0, "Untracked": 0, "total": 0,
                }
            cs = client_status.get(c.name)
            domain_implementation[d]["total"] += 1
            if not cs:
                domain_implementation[d]["Untracked"] += 1
                continue
            status = (cs.compliance_status or "").strip()
            if status in domain_implementation[d]:
                domain_implementation[d][status] += 1
            else:
                domain_implementation[d]["Untracked"] += 1

    return {
        "summary": {
            "total_controls": len(catalog),
            "domains": len(domains_rollup),
            "tracked_for_client": len(client_status) if client else 0,
        },
        "domains_rollup": list(domains_rollup.values()),
        "domain_implementation": domain_implementation,
        "client": client,
    }


@frappe.whitelist()
def get_domain_controls(domain_code, client=None):
    """Return controls in a specific domain with per-client status."""
    _check_auth()
    if not domain_code:
        return {"controls": []}

    catalog = []
    if frappe.db.exists("DocType", "GRC ISO42001 Catalog"):
        catalog = frappe.get_all(
            "GRC ISO42001 Catalog",
            filters={"domain_code": domain_code, "is_active": 1},
            fields=["name", "control_code", "control_title",
                    "implementation_guidance", "document_to_prepare_code",
                    "document_to_prepare_title", "iso_xrefs"],
            order_by="control_code asc",
        )

    client_status = {}
    if client and frappe.db.exists("DocType", "GRC ISO42001 Control"):
        rows = frappe.get_all(
            "GRC ISO42001 Control",
            filters={"client": client, "catalog_ref": ["in", [c.name for c in catalog]]},
            fields=["name", "catalog_ref", "compliance_status",
                    "compliance_score", "responsible_owner"],
        )
        for r in rows:
            client_status[r.catalog_ref] = r

    return {
        "domain_code": domain_code,
        "controls": [{**c, "client_status": client_status.get(c.name)} for c in catalog],
    }
