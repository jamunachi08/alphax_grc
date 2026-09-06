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
def get_ecc2_dashboard(client=None):
    """Return ECC-2:2024 catalog summary + per-client implementation status
    if a client is selected. Used by the /app/grc-ecc2-dashboard page."""
    _check_auth()

    catalog = []
    if frappe.db.exists("DocType", "GRC NCA ECC2 Catalog"):
        catalog = frappe.get_all(
            "GRC NCA ECC2 Catalog",
            filters={"is_active": 1},
            fields=["name", "control_code", "domain", "subdomain_code",
                    "subdomain_label_en", "subdomain_label_ar",
                    "is_subcontrol", "parent_control_code",
                    "control_text_en", "control_text_ar"],
            order_by="control_code asc",
            limit_page_length=500,
        )

    # Per-domain rollup
    domains_rollup = {}
    subdomains_rollup = {}
    for c in catalog:
        d = c.domain or "(unknown)"
        domains_rollup[d] = domains_rollup.get(d, 0) + 1
        sd = c.subdomain_code or ""
        if sd not in subdomains_rollup:
            subdomains_rollup[sd] = {
                "subdomain_code": sd,
                "subdomain_label_en": c.subdomain_label_en or "",
                "subdomain_label_ar": c.subdomain_label_ar or "",
                "domain": c.domain,
                "total_controls": 0,
                "main_controls": 0,
                "sub_controls": 0,
            }
        subdomains_rollup[sd]["total_controls"] += 1
        if c.is_subcontrol:
            subdomains_rollup[sd]["sub_controls"] += 1
        else:
            subdomains_rollup[sd]["main_controls"] += 1

    # If a client is selected, layer in per-client implementation status
    client_status = {}
    if client and frappe.db.exists("DocType", "GRC NCA ECC Control"):
        rows = frappe.get_all(
            "GRC NCA ECC Control",
            filters={"client": client},
            fields=["name", "ecc2_catalog_ref", "control_number",
                    "compliance_status", "compliance_score",
                    "sub_compliance_status", "compliance_classification",
                    "responsible_owner", "target_date",
                    "last_assessed", "review_date"],
            limit_page_length=500,
        )
        for r in rows:
            key = r.ecc2_catalog_ref or r.control_number
            if key:
                client_status[key] = r

    # Build per-subdomain implementation summary if client selected
    subdomain_implementation = {}
    if client:
        for c in catalog:
            sd = c.subdomain_code
            if sd not in subdomain_implementation:
                subdomain_implementation[sd] = {
                    "Implemented": 0, "Partially Implemented": 0,
                    "Not Implemented": 0, "Not Applicable": 0,
                    "Untracked": 0, "total": 0,
                }
            cs = client_status.get(c.name) or client_status.get(c.control_code)
            subdomain_implementation[sd]["total"] += 1
            if not cs:
                subdomain_implementation[sd]["Untracked"] += 1
                continue
            status = (cs.compliance_status or "").strip()
            if status in subdomain_implementation[sd]:
                subdomain_implementation[sd][status] += 1
            elif "Implement" in status and "Partial" in status:
                subdomain_implementation[sd]["Partially Implemented"] += 1
            elif "Implement" in status:
                subdomain_implementation[sd]["Implemented"] += 1
            elif "Not Applicable" in status or "N/A" in status:
                subdomain_implementation[sd]["Not Applicable"] += 1
            elif status:
                subdomain_implementation[sd]["Not Implemented"] += 1
            else:
                subdomain_implementation[sd]["Untracked"] += 1

    return {
        "summary": {
            "total_controls": len(catalog),
            "main_controls": sum(1 for c in catalog if not c.is_subcontrol),
            "sub_controls": sum(1 for c in catalog if c.is_subcontrol),
            "domains_rollup": domains_rollup,
            "tracked_for_client": len(client_status) if client else 0,
        },
        "subdomains": list(subdomains_rollup.values()),
        "subdomain_implementation": subdomain_implementation,
        "client": client,
    }


@frappe.whitelist()
def get_subdomain_controls(subdomain_code, client=None):
    """Return all controls in a subdomain, with per-client status if applicable."""
    _check_auth()
    if not subdomain_code:
        return {"controls": []}

    catalog = []
    if frappe.db.exists("DocType", "GRC NCA ECC2 Catalog"):
        catalog = frappe.get_all(
            "GRC NCA ECC2 Catalog",
            filters={"subdomain_code": subdomain_code, "is_active": 1},
            fields=["name", "control_code", "is_subcontrol", "parent_control_code",
                    "control_text_en", "control_text_ar",
                    "implementation_method_ar", "expected_output_ar",
                    "related_tools_ar"],
            order_by="control_code asc",
        )

    client_status = {}
    if client and frappe.db.exists("DocType", "GRC NCA ECC Control"):
        rows = frappe.get_all(
            "GRC NCA ECC Control",
            filters={"client": client, "ecc2_catalog_ref": ["in", [c.name for c in catalog]]},
            fields=["name", "ecc2_catalog_ref",
                    "compliance_status", "compliance_score",
                    "responsible_owner", "target_date"],
        )
        for r in rows:
            client_status[r.ecc2_catalog_ref] = r

    return {
        "subdomain_code": subdomain_code,
        "controls": [{**c, "client_status": client_status.get(c.name)} for c in catalog],
    }
