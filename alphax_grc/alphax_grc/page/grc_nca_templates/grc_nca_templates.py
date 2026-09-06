import frappe


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive", "Compliance Officer",
    "GRC Assessor", "GRC Auditor", "Risk Owner", "Privacy Officer",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_template_library():
    """Return all NCA library entries (Policy, Standard, Procedure, Form),
    grouped by kind, suitable for the catalogue browser.

    v1.4.1: self-heals an empty library by calling the seeders inline.
    Triggers only for admin roles, only when ALL four libraries are empty,
    and only if the doctypes themselves exist."""
    _check_auth()

    # Self-heal: seed if empty and user is admin
    is_admin = bool(set(frappe.get_roles(frappe.session.user)) &
                    {"System Manager", "GRC Admin"})
    if is_admin:
        _self_heal_libraries()

    out = {"Policy": [], "Standard": [], "Procedure": [], "Form": []}
    for kind, doctype in (
        ("Policy",    "GRC NCA Policy Library"),
        ("Standard",  "GRC NCA Standard Library"),
        ("Procedure", "GRC NCA Procedure Library"),
        ("Form",      "GRC NCA Form Library"),
    ):
        if not frappe.db.exists("DocType", doctype):
            continue
        rows = frappe.get_all(
            doctype,
            filters={"is_active": 1},
            fields=["name", "template_code", "template_name",
                    "template_name_ar", "category", "ecc_controls",
                    "description", "official_word_url", "official_pdf_url",
                    "version"],
            order_by="category asc, template_name asc",
        )
        out[kind] = rows
    return out


@frappe.whitelist()
def adopt_template_for_client(client, kind, template_code):
    """One-click: create a draft Policy / etc for the given client based on
    a library template. Returns the new doc name."""
    _check_auth()
    if not frappe.db.exists("GRC Client Profile", client):
        frappe.throw(f"Client {client} not found.")

    library_doctype = {
        "Policy":    "GRC NCA Policy Library",
        "Standard":  "GRC NCA Standard Library",
        "Procedure": "GRC NCA Procedure Library",
        "Form":      "GRC NCA Form Library",
    }.get(kind)
    if not library_doctype:
        frappe.throw(f"Unknown library kind: {kind}")

    if not frappe.db.exists(library_doctype, template_code):
        frappe.throw(f"Template {template_code} not found in {library_doctype}.")

    template = frappe.get_doc(library_doctype, template_code)

    # Map to target doctype
    if kind == "Policy" and frappe.db.exists("DocType", "GRC Policy"):
        new_doc = frappe.get_doc({
            "doctype": "GRC Policy",
            "client": client,
            "policy_name": template.template_name,
            "category": template.category,
            "status": "Draft",
            "description": template.description or "",
        })
    elif kind in ("Standard", "Procedure", "Form") and frappe.db.exists("DocType", "GRC ISMS Document Register"):
        new_doc = frappe.get_doc({
            "doctype": "GRC ISMS Document Register",
            "client": client,
            "document_name": template.template_name,
            "document_type": kind,
            "status": "Draft",
            "description": template.description or "",
        })
    else:
        frappe.throw("No target doctype available for this kind.")

    new_doc.insert(ignore_permissions=True)
    return {"name": new_doc.name, "doctype": new_doc.doctype}


def _self_heal_libraries():
    """If any of the four NCA libraries is empty AND the doctype exists,
    call the seeder inline. Idempotent (each seeder guards on count > 0)."""
    pairs = [
        ("GRC NCA Policy Library",    "seed_nca_policy_library"),
        ("GRC NCA Standard Library",  "seed_nca_standard_library"),
        ("GRC NCA Procedure Library", "seed_nca_procedure_library"),
        ("GRC NCA Form Library",      "seed_nca_form_library"),
    ]
    triggered = False
    try:
        from alphax_grc import install
    except Exception:
        return
    for doctype, fn_name in pairs:
        if not frappe.db.exists("DocType", doctype):
            continue
        try:
            count = frappe.db.count(doctype) or 0
        except Exception:
            continue
        if count == 0:
            fn = getattr(install, fn_name, None)
            if callable(fn):
                try:
                    fn()
                    triggered = True
                except Exception:
                    try:
                        frappe.log_error(frappe.get_traceback(),
                                         f"NCA library self-heal failed: {fn_name}")
                    except Exception:
                        pass
    # Also seed Threat Catalogue (referenced by Vulnerability) if empty
    try:
        if (frappe.db.exists("DocType", "GRC Threat Catalogue")
                and frappe.db.count("GRC Threat Catalogue") == 0):
            fn = getattr(install, "seed_threat_catalogue", None)
            if callable(fn):
                fn()
                triggered = True
    except Exception:
        pass
    if triggered:
        try:
            frappe.db.commit()
        except Exception:
            pass


@frappe.whitelist()
def force_seed_libraries():
    """Admin-only: re-run all v1.4.0 seeders. Hookable from a UI button."""
    _check_auth()
    if not (set(frappe.get_roles(frappe.session.user)) &
            {"System Manager", "GRC Admin"}):
        frappe.throw("Only System Manager / GRC Admin can re-seed.",
                     frappe.PermissionError)
    try:
        from alphax_grc import install
    except Exception as e:
        frappe.throw(f"Could not import install module: {e}")

    results = {}
    for fn_name in ("seed_threat_catalogue",
                     "seed_nca_policy_library",
                     "seed_nca_standard_library",
                     "seed_nca_procedure_library",
                     "seed_nca_form_library",
                     "seed_sample_vulnerabilities",
                     "seed_sample_kpis"):
        fn = getattr(install, fn_name, None)
        if not callable(fn):
            results[fn_name] = "skipped (function not found)"
            continue
        try:
            fn()
            results[fn_name] = "ok"
        except Exception as e:
            results[fn_name] = f"failed: {e}"
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"force_seed_libraries: {fn_name} failed")
            except Exception:
                pass
    try:
        frappe.db.commit()
    except Exception:
        pass
    return results


@frappe.whitelist()
def bulk_adopt_for_client(client, kind, template_codes):
    """Adopt multiple templates for one client in one server call.
    template_codes is a JSON-encoded list of codes (Frappe whitelist
    serializes lists this way from JS)."""
    _check_auth()
    if not frappe.db.exists("GRC Client Profile", client):
        frappe.throw(f"Client {client} not found.")

    if isinstance(template_codes, str):
        import json
        try:
            template_codes = json.loads(template_codes)
        except Exception:
            template_codes = [c.strip() for c in template_codes.split(",") if c.strip()]

    if not template_codes:
        return {"created": [], "errors": []}

    created = []
    errors = []
    for code in template_codes:
        try:
            r = adopt_template_for_client(client, kind, code)
            created.append(r.get("name"))
        except Exception as e:
            errors.append({"code": code, "error": str(e)})

    return {"created": created, "errors": errors,
            "summary": f"{len(created)} adopted, {len(errors)} failed"}


@frappe.whitelist()
def get_client_policy_coverage(client):
    """Per-client gap analysis: which NCA-mapped ECC controls are covered
    by an adopted Policy and which aren't."""
    _check_auth()
    if not frappe.db.exists("GRC Client Profile", client):
        return {"covered": [], "gaps": [], "summary": {}}

    # All ECC controls referenced by any policy template in the library
    template_controls = set()
    if frappe.db.exists("DocType", "GRC NCA Policy Library"):
        for r in frappe.get_all("GRC NCA Policy Library",
                                 fields=["template_code", "ecc_controls"]):
            for c in (r.ecc_controls or "").split(","):
                c = c.strip()
                if c:
                    template_controls.add(c)

    # Adopted policies for this client
    adopted = []
    if frappe.db.exists("DocType", "GRC Policy"):
        adopted = frappe.get_all(
            "GRC Policy",
            filters={"client": client},
            fields=["name", "policy_title", "status"],
        )

    # Build "covered controls" by matching adopted policy titles back to
    # library entries (best-effort name match)
    covered_controls = set()
    if adopted and frappe.db.exists("DocType", "GRC NCA Policy Library"):
        for p in adopted:
            t = (p.policy_title or "").strip().lower()
            if not t:
                continue
            # Exact name match against library
            for libr in frappe.get_all("GRC NCA Policy Library",
                                        fields=["template_name", "ecc_controls"]):
                if libr.template_name and libr.template_name.strip().lower() == t:
                    for c in (libr.ecc_controls or "").split(","):
                        c = c.strip()
                        if c:
                            covered_controls.add(c)

    gaps = sorted(template_controls - covered_controls)
    covered = sorted(covered_controls)

    return {
        "covered": covered,
        "gaps": gaps,
        "summary": {
            "adopted_policies": len(adopted),
            "controls_covered": len(covered),
            "controls_missing": len(gaps),
            "total_template_controls": len(template_controls),
            "coverage_pct": round(
                (len(covered) / len(template_controls) * 100), 1
            ) if template_controls else 0,
        },
        "policies": adopted,
    }


@frappe.whitelist()
def get_client_adoption_status(client):
    """For the given client, return the set of NCA template_codes that
    have already been adopted (i.e. a Policy/ISMS doc exists with the
    same template_name). Used by the UI to show ✓ badges on cards."""
    _check_auth()
    if not client or not frappe.db.exists("GRC Client Profile", client):
        return {"adopted_codes": []}

    # Build a name → code lookup across all four libraries
    name_to_code = {}
    for lib in ("GRC NCA Policy Library", "GRC NCA Standard Library",
                "GRC NCA Procedure Library", "GRC NCA Form Library"):
        if not frappe.db.exists("DocType", lib):
            continue
        for r in frappe.get_all(lib, fields=["template_code", "template_name"]):
            if r.template_name:
                name_to_code[r.template_name.strip().lower()] = r.template_code

    adopted_names = set()
    if frappe.db.exists("DocType", "GRC Policy"):
        for p in frappe.get_all("GRC Policy",
                                 filters={"client": client},
                                 fields=["policy_title"]):
            if p.policy_title:
                adopted_names.add(p.policy_title.strip().lower())
    if frappe.db.exists("DocType", "GRC ISMS Document Register"):
        for d in frappe.get_all("GRC ISMS Document Register",
                                 filters={"client": client},
                                 fields=["document_name"]):
            if d.document_name:
                adopted_names.add(d.document_name.strip().lower())

    adopted_codes = [
        code for nm, code in name_to_code.items() if nm in adopted_names
    ]
    return {"adopted_codes": adopted_codes,
            "adopted_count": len(adopted_codes),
            "total_count": len(name_to_code)}
