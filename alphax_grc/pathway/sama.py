# Copyright (c) 2026, Neotec Integrated Solutions
"""
SAMA CSF setup: sub-domain catalogue, deliverable master register, and the
incident fields the framework requires but the base app never had.

Everything is idempotent and guarded on the target DocType existing.
"""

from __future__ import annotations

import json
import os

import frappe

CATALOG = "sama_csf_catalog.json"


def _log_title(text: str) -> str:
	return text[:140]


def _catalog() -> dict:
	path = os.path.join(frappe.get_app_path("alphax_grc"), "alphax_grc", "data", CATALOG)
	if not os.path.exists(path):
		return {}
	with open(path, encoding="utf-8") as f:
		return json.load(f)


# --------------------------------------------------------------------------
# 1. Sub-domain catalogue (36 rows across the 4 SAMA domains)
# --------------------------------------------------------------------------


def seed_sama_subdomains():
	if not frappe.db.exists("DocType", "GRC SAMA Subdomain"):
		return 0

	data = _catalog()
	created = 0
	for row in data.get("subdomains", []):
		try:
			if frappe.db.exists("GRC SAMA Subdomain", row["code"]):
				doc = frappe.get_doc("GRC SAMA Subdomain", row["code"])
			else:
				doc = frappe.new_doc("GRC SAMA Subdomain")
				doc.code = row["code"]
				doc.flags.name_set = True
				created += 1

			doc.subdomain_title = row["title"]
			doc.domain = row["domain"]
			doc.domain_title = row["domain_title"]
			doc.control_considerations = row.get("control_considerations") or 0
			doc.excluded_for_non_banks = 1 if row.get("excluded_for_non_banks") else 0
			doc.is_active = 1
			doc.flags.ignore_permissions = True
			doc.flags.ignore_mandatory = True
			doc.insert(ignore_permissions=True) if doc.is_new() else doc.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(
				title=_log_title(f"SAMA sub-domain seed failed: {row.get('code')}"),
				message=frappe.get_traceback(),
			)
	return created


# --------------------------------------------------------------------------
# 2. Deliverable master register (the 108-item evidence set)
# --------------------------------------------------------------------------


def seed_sama_deliverables():
	if not frappe.db.exists("DocType", "GRC SAMA Deliverable"):
		return 0

	data = _catalog()
	created = 0
	for row in data.get("deliverables", []):
		name = f"SAMA-DEL-{row['sl']:03d}"
		try:
			if frappe.db.exists("GRC SAMA Deliverable", name):
				continue
			doc = frappe.new_doc("GRC SAMA Deliverable")
			doc.name = name
			doc.flags.name_set = True
			doc.sl_no = row["sl"]
			doc.deliverable_title = row["title"]
			doc.description = row.get("description") or ""
			doc.is_master = 1
			doc.status = "Not Started"
			if row.get("subdomain") and frappe.db.exists("GRC SAMA Subdomain", row["subdomain"]):
				doc.subdomain = row["subdomain"]
			doc.flags.ignore_permissions = True
			doc.flags.ignore_mandatory = True
			doc.insert(ignore_permissions=True)
			created += 1
		except Exception:
			frappe.log_error(
				title=_log_title(f"SAMA deliverable seed failed: {row.get('sl')}"),
				message=frappe.get_traceback(),
			)
	return created


# --------------------------------------------------------------------------
# 3. Incident fields required by SAMA CSF 3.3.15.5 - 3.3.15.7
# --------------------------------------------------------------------------

INCIDENT_FIELDS = [
	{"fieldname": "sec_sama_reporting", "fieldtype": "Section Break",
	 "label": "SAMA Reporting (CSF 3.3.15)", "insert_after": "sla_due_date"},
	{"fieldname": "sama_classification", "fieldtype": "Select", "label": "SAMA Classification",
	 "options": "\nLow\nMedium\nHigh", "insert_after": "sec_sama_reporting",
	 "description": "Medium and High must be reported to SAMA IT Risk Supervision immediately"},
	{"fieldname": "sama_reportable", "fieldtype": "Check", "label": "Reportable to SAMA",
	 "read_only": 1, "insert_after": "sama_classification"},
	{"fieldname": "sama_notified_on", "fieldtype": "Datetime", "label": "SAMA Notified On",
	 "insert_after": "sama_reportable"},
	{"fieldname": "sama_no_objection_obtained", "fieldtype": "Check",
	 "label": "SAMA 'No Objection' Obtained Before Media Contact",
	 "insert_after": "sama_notified_on",
	 "description": "CSF 3.3.15.6 — required before any media interaction"},
	{"fieldname": "cb_sama_reporting", "fieldtype": "Column Break",
	 "insert_after": "sama_no_objection_obtained"},
	{"fieldname": "occurred_on", "fieldtype": "Datetime", "label": "Date and Time Occurred",
	 "insert_after": "cb_sama_reporting"},
	{"fieldname": "detected_on", "fieldtype": "Datetime", "label": "Date and Time Detected",
	 "insert_after": "occurred_on"},
	{"fieldname": "assets_involved", "fieldtype": "Small Text", "label": "Information Assets Involved",
	 "insert_after": "detected_on"},
	{"fieldname": "sama_report_submitted_on", "fieldtype": "Date",
	 "label": "Formal Report Submitted On", "insert_after": "assets_involved"},
	{"fieldname": "sec_sama_report", "fieldtype": "Section Break",
	 "label": "Formal Incident Report (CSF 3.3.15.7)", "insert_after": "sama_report_submitted_on",
	 "collapsible": 1},
	{"fieldname": "technical_details", "fieldtype": "Text", "label": "Technical Details",
	 "insert_after": "sec_sama_report"},
	{"fieldname": "root_cause", "fieldtype": "Text", "label": "Root-Cause Analysis",
	 "insert_after": "technical_details"},
	{"fieldname": "corrective_actions", "fieldtype": "Text",
	 "label": "Corrective Activities Performed and Planned", "insert_after": "root_cause"},
	{"fieldname": "impact_description", "fieldtype": "Text",
	 "label": "Description of Impact", "insert_after": "corrective_actions",
	 "description": "Data loss, service disruption, unauthorised modification, customers impacted"},
	{"fieldname": "cb_sama_report", "fieldtype": "Column Break", "insert_after": "impact_description"},
	{"fieldname": "customers_impacted", "fieldtype": "Int", "label": "Customers Impacted",
	 "insert_after": "cb_sama_report"},
	{"fieldname": "estimated_incident_cost", "fieldtype": "Currency",
	 "label": "Total Estimated Cost of Incident", "insert_after": "customers_impacted"},
	{"fieldname": "estimated_corrective_cost", "fieldtype": "Currency",
	 "label": "Estimated Cost of Corrective Actions", "insert_after": "estimated_incident_cost"},
]

# CISO appointment evidence — CSF 3.1.1.9
CLIENT_FIELDS = [
	{"fieldname": "sec_sama_governance", "fieldtype": "Section Break",
	 "label": "SAMA Governance (CSF 3.1.1)", "insert_after": "contact_email", "collapsible": 1},
	{"fieldname": "ciso_user", "fieldtype": "Link", "options": "User", "label": "CISO",
	 "insert_after": "sec_sama_governance"},
	{"fieldname": "ciso_is_saudi_national", "fieldtype": "Check",
	 "label": "CISO is a Saudi National", "insert_after": "ciso_user",
	 "description": "CSF 3.1.1.9.a"},
	{"fieldname": "ciso_appointment_date", "fieldtype": "Date", "label": "CISO Appointment Date",
	 "insert_after": "ciso_is_saudi_national"},
	{"fieldname": "cb_sama_governance", "fieldtype": "Column Break",
	 "insert_after": "ciso_appointment_date"},
	{"fieldname": "sama_nol_obtained", "fieldtype": "Check",
	 "label": "SAMA No-Objection Letter Obtained", "insert_after": "cb_sama_governance",
	 "description": "CSF 3.1.1.9.c — required before assigning the CISO"},
	{"fieldname": "sama_nol_reference", "fieldtype": "Data", "label": "SAMA NOL Reference",
	 "insert_after": "sama_nol_obtained"},
	{"fieldname": "committee_charter_approved_on", "fieldtype": "Date",
	 "label": "Committee Charter Approved On", "insert_after": "sama_nol_reference",
	 "description": "CSF 3.1.1.4 — board-mandated charter, quarterly meetings minimum"},
]


def seed_sama_custom_fields():
	"""Applied as Custom Fields because they extend base-app doctypes."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	spec = {}
	if frappe.db.exists("DocType", "GRC Incident"):
		spec["GRC Incident"] = INCIDENT_FIELDS
	if frappe.db.exists("DocType", "GRC Client Profile"):
		spec["GRC Client Profile"] = CLIENT_FIELDS
	if not spec:
		return

	create_custom_fields(spec, ignore_validate=True, update=True)


def seed_sama():
	seed_sama_subdomains()
	seed_sama_deliverables()
	seed_sama_custom_fields()
