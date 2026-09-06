"""v2.14.0 governance patch.

1. Installs the three new approval workflows (Risk Acceptance, SAMA Waiver,
   DPIA) on existing sites — install_workflows() skips ones that exist.
2. Migrates legacy GRC Data Subject Request records into GRC DSAR Request,
   idempotently (a migrated legacy name is recorded in the DSAR notes and
   checked before copying again).
"""

import frappe


def execute():
    install_new_workflows()
    migrate_legacy_dsr()


def install_new_workflows():
    try:
        from alphax_grc.install import install_workflows
        install_workflows()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "v2_14_0: workflow install")


def migrate_legacy_dsr():
    if not frappe.db.exists("DocType", "GRC Data Subject Request"):
        return
    if not frappe.db.exists("DocType", "GRC DSAR Request"):
        return
    dsar_meta = frappe.get_meta("GRC DSAR Request")

    def dsar_has(field):
        return dsar_meta.has_field(field)

    legacy_rows = frappe.get_all("GRC Data Subject Request", fields=["name"])
    migrated = 0
    for row in legacy_rows:
        marker = f"migrated-from:{row.name}"
        if frappe.db.exists("GRC DSAR Request", {"legacy_reference": row.name}) if dsar_has("legacy_reference") else _marker_exists(marker):
            continue
        old = frappe.get_doc("GRC Data Subject Request", row.name)
        new = frappe.new_doc("GRC DSAR Request")
        mapping = {
            "client": "client",
            "request_type": "request_type",
            "requester_name": "data_subject_name",
            "received_on": "received_date",
            "due_date": "due_date",
            "request_summary": "request_details",
            "owner_user": "assigned_to",
            "request_reference": "legacy_reference",
        }
        for src, dst in mapping.items():
            if old.get(src) is not None and dsar_has(dst):
                new.set(dst, old.get(src))
        # always keep a traceable marker
        for notes_field in ("request_details", "notes", "remarks"):
            if dsar_has(notes_field):
                existing = new.get(notes_field) or ""
                new.set(notes_field, (existing + "\n" if existing else "") + marker)
                break
        new.flags.ignore_permissions = True
        new.flags.ignore_mandatory = True
        try:
            new.insert(ignore_permissions=True)
            migrated += 1
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                f"v2_14_0: DSR migration failed for {row.name}")
    if migrated:
        frappe.db.commit()


def _marker_exists(marker):
    for notes_field in ("request_details", "notes", "remarks"):
        try:
            if frappe.db.exists("GRC DSAR Request", {notes_field: ("like", f"%{marker}%")}):
                return True
        except Exception:
            continue
    return False
