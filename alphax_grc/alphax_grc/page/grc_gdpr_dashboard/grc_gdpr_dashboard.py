import frappe


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive",
    "Compliance Officer", "Privacy Officer", "GRC Assessor", "GRC Auditor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_gdpr_dashboard(client=None):
    """Return GDPR catalog summary + per-client status."""
    _check_auth()

    catalog = []
    if frappe.db.exists("DocType", "GRC GDPR Catalog"):
        catalog = frappe.get_all(
            "GRC GDPR Catalog",
            filters={"is_active": 1},
            fields=["name", "article_code", "chapter_code", "chapter_label",
                    "article_title", "summary", "implementation_guidance",
                    "evidence_artifacts", "applicability"],
            order_by="article_code asc",
            limit_page_length=200,
        )

    chapters_rollup = {}
    for c in catalog:
        ch = c.chapter_code or "unknown"
        if ch not in chapters_rollup:
            chapters_rollup[ch] = {
                "code": ch,
                "label": c.chapter_label,
                "count": 0,
            }
        chapters_rollup[ch]["count"] += 1

    client_status = {}
    if client and frappe.db.exists("DocType", "GRC GDPR Control"):
        rows = frappe.get_all(
            "GRC GDPR Control",
            filters={"client": client},
            fields=["name", "catalog_ref", "article_code",
                    "compliance_status", "compliance_score",
                    "responsible_owner", "target_date",
                    "data_processing_scope"],
            limit_page_length=200,
        )
        for r in rows:
            client_status[r.catalog_ref] = r

    chapter_implementation = {}
    if client:
        for c in catalog:
            ch = c.chapter_code
            if ch not in chapter_implementation:
                chapter_implementation[ch] = {
                    "Implemented": 0, "Partially Implemented": 0,
                    "In Progress": 0, "Not Started": 0,
                    "Not Applicable": 0, "Untracked": 0, "total": 0,
                }
            cs = client_status.get(c.name)
            chapter_implementation[ch]["total"] += 1
            if not cs:
                chapter_implementation[ch]["Untracked"] += 1
                continue
            status = (cs.compliance_status or "").strip()
            if status in chapter_implementation[ch]:
                chapter_implementation[ch][status] += 1
            else:
                chapter_implementation[ch]["Untracked"] += 1

    return {
        "summary": {
            "total_articles": len(catalog),
            "chapters": len(chapters_rollup),
            "tracked_for_client": len(client_status) if client else 0,
        },
        "chapters_rollup": list(chapters_rollup.values()),
        "chapter_implementation": chapter_implementation,
        "client": client,
    }


@frappe.whitelist()
def get_chapter_articles(chapter_code, client=None):
    """Return articles in a specific chapter with per-client status."""
    _check_auth()
    if not chapter_code:
        return {"articles": []}

    catalog = []
    if frappe.db.exists("DocType", "GRC GDPR Catalog"):
        catalog = frappe.get_all(
            "GRC GDPR Catalog",
            filters={"chapter_code": chapter_code, "is_active": 1},
            fields=["name", "article_code", "article_title",
                    "summary", "implementation_guidance",
                    "evidence_artifacts", "iso27701_xref", "applicability"],
            order_by="article_code asc",
        )

    client_status = {}
    if client and frappe.db.exists("DocType", "GRC GDPR Control"):
        rows = frappe.get_all(
            "GRC GDPR Control",
            filters={"client": client, "catalog_ref": ["in", [c.name for c in catalog]]},
            fields=["name", "catalog_ref", "compliance_status",
                    "compliance_score", "responsible_owner"],
        )
        for r in rows:
            client_status[r.catalog_ref] = r

    return {
        "chapter_code": chapter_code,
        "articles": [{**c, "client_status": client_status.get(c.name)} for c in catalog],
    }
