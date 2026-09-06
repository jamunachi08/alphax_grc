# Copyright (c) 2026, Neotec Integrated Solutions
"""
Idempotent setup for the GRC Pathway add-on.

Replaces the previous `fixtures` block in hooks.py. Fixture JSON was
importing a Custom Field payload with no `name` key, which crashes
`bench migrate` with KeyError: 'name' inside frappe.modules.import_file,
and it hard-fails whenever a referenced AlphaX GRC DocType is absent.

Everything here is safe to re-run: each record is created if missing and
patched in place if present, and every seeder that depends on an AlphaX GRC
DocType checks for that DocType first and logs a warning instead of raising.
"""

from __future__ import annotations

import json

import frappe
from alphax_grc.pathway.board import seed_pathway_board
from alphax_grc.pathway.plans import seed_plan_templates
from alphax_grc.pathway.reports import seed_report_definitions
from alphax_grc.pathway.sama import seed_sama
from alphax_grc.pathway.policies import import_from_nca_library, seed_global_policies

MODULE = "GRC Evidence Automation"

# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------


def after_install():
	seed_all()


def after_migrate():
	seed_all()


def seed_all():
	_run(seed_number_cards)
	_run(seed_onboarding)
	_run(seed_global_policies)
	_run(import_from_nca_library)
	_run(seed_role_permissions)
	_run(seed_plan_templates)
	_run(seed_sama)
	_run(seed_report_definitions)
	_run(seed_pathway_board)
	frappe.db.commit()


def _run(fn):
	try:
		fn()
	except Exception:
		frappe.db.rollback()
		frappe.log_error(
			title=_title(f"GRC Pathway setup failed: {fn.__name__}"),
			message=frappe.get_traceback(),
		)


def _title(text: str) -> str:
	"""frappe.log_error rejects titles over 140 chars."""
	return text[:140]


def _doctype_exists(doctype: str) -> bool:
	return bool(frappe.db.exists("DocType", doctype))


def _has_field(doctype: str, fieldname: str) -> bool:
	try:
		return bool(frappe.get_meta(doctype).get_field(fieldname))
	except Exception:
		return False


def _set_if_field(doc, fieldname: str, value):
	"""Only set fields that exist on this Frappe version's DocType."""
	if _has_field(doc.doctype, fieldname):
		doc.set(fieldname, value)


def _resolve_module(preferred: str = MODULE) -> str:
	"""Own module first; fall back to the base app's module if ours is missing."""
	for candidate in (preferred, "AlphaX GRC"):
		if frappe.db.exists("Module Def", candidate):
			return candidate
	return preferred


# --------------------------------------------------------------------------
# 1. (removed in v2.3.0)
#
# `GRC Risk Register.treatment_actions` used to be applied as a Custom Field
# from a separate app. Now that both live in alphax_grc it is a native
# DocField on the doctype, so there is nothing to seed.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# 2. Number Cards
# --------------------------------------------------------------------------

NUMBER_CARDS = [
	{
		"name": "grc-card-active-engagements",
		"label": "Active engagements",
		"document_type": "GRC Engagement",
		"filters_json": '[["GRC Engagement","engagement_status","=","Active"]]',
		"color": "#378ADD",
	},
	{
		"name": "grc-card-open-risks",
		"label": "Open risks",
		"document_type": "GRC Risk Register",
		"filters_json": '[["GRC Risk Register","status","in",["Open","Monitoring"]]]',
		"color": "#F5A623",
	},
	{
		"name": "grc-card-above-appetite",
		"label": "Risks above appetite",
		"document_type": "GRC Risk Register",
		"filters_json": '[["GRC Risk Register","within_appetite","=",0],["GRC Risk Register","appetite_status","like","%needs%"]]',
		"color": "#E24C4C",
	},
	{
		"name": "grc-card-critical-findings",
		"label": "Critical findings",
		"document_type": "GRC Audit Finding",
		"filters_json": '[["GRC Audit Finding","severity","=","Critical"]]',
		"color": "#E24C4C",
	},
	{
		"name": "grc-card-open-findings",
		"label": "Open findings",
		"document_type": "GRC Audit Finding",
		"filters_json": '[["GRC Audit Finding","status","not in",["Resolved","Closed"]]]',
		"color": "#E24C4C",
	},
	{
		"name": "grc-card-published-policies",
		"label": "Published policies",
		"document_type": "GRC Policy",
		"filters_json": '[["GRC Policy","publication_status","=","Published"]]',
		"color": "#29CD42",
	},
	{
		"name": "grc-card-sama-deliverables",
		"label": "SAMA deliverables outstanding",
		"document_type": "GRC SAMA Deliverable",
		"filters_json": '[["GRC SAMA Deliverable","status","not in",["Approved","Evidence Filed","Not Applicable"]]]',
		"color": "#0891b2",
	},
	{
		"name": "grc-card-sama-waivers",
		"label": "Open SAMA waivers",
		"document_type": "GRC SAMA Waiver",
		"filters_json": '[["GRC SAMA Waiver","status","not in",["Approved","Rejected","Withdrawn"]]]',
		"color": "#f59e0b",
	},
	{
		"name": "grc-card-blocked-vendors",
		"label": "Blocked vendors",
		"document_type": "GRC Vendor",
		"filters_json": '[["GRC Vendor","status","=","Blocked"]]',
		"color": "#8D99A6",
	},
]


def seed_number_cards():
	if not _doctype_exists("Number Card"):
		return

	module = _resolve_module()
	missing = []

	for spec in NUMBER_CARDS:
		if not _doctype_exists(spec["document_type"]):
			missing.append(spec["document_type"])
			continue
		_upsert_number_card(spec, module)

	if missing:
		frappe.log_error(
			title=_title("GRC Pathway: number cards skipped"),
			message="These DocTypes were not found, so their cards were skipped: "
			+ ", ".join(sorted(set(missing))),
		)


def _upsert_number_card(spec: dict, module: str):
	filters_json = _sanitise_filters(spec["document_type"], spec["filters_json"])

	if frappe.db.exists("Number Card", spec["name"]):
		card = frappe.get_doc("Number Card", spec["name"])
	else:
		card = frappe.new_doc("Number Card")
		card.name = spec["name"]
		# Force the name past Number Card's own autoname rule so the
		# workspace content blocks keep resolving to these exact cards.
		card.flags.name_set = True

	card.label = spec["label"]
	card.document_type = spec["document_type"]
	card.function = "Count"
	card.filters_json = filters_json
	card.is_public = 1
	card.show_percentage_stats = 0
	card.color = spec["color"]
	_set_if_field(card, "type", "Document Type")
	_set_if_field(card, "module", module)
	_set_if_field(card, "is_standard", 0)

	card.flags.ignore_permissions = True
	card.flags.ignore_mandatory = True
	card.save(ignore_permissions=True) if not card.is_new() else card.insert(ignore_permissions=True)


def _sanitise_filters(doctype: str, filters_json: str) -> str:
	"""Drop filter rows whose fieldname doesn't exist on this build of AlphaX GRC."""
	try:
		filters = json.loads(filters_json)
	except Exception:
		return "[]"

	kept = [f for f in filters if isinstance(f, list) and len(f) >= 4 and _has_field(doctype, f[1])]
	return json.dumps(kept)


# --------------------------------------------------------------------------
# 3. Guided pathway — Module Onboarding + Onboarding Steps
# --------------------------------------------------------------------------

ONBOARDING_STEPS = [
	(
		"grc-step-01-client",
		"Add your first client",
		"GRC Client Profile",
		"<p>Every record in this app is scoped to a client. Start by creating a client profile: "
		"sector, country, applicable frameworks, and risk appetite.</p>",
	),
	(
		"grc-step-02-engagement",
		"Open an engagement",
		"GRC Engagement",
		"<p>Pick the engagement type to load the matching phase template, and assign a lead "
		"consultant. Findings, risks, and phase progress roll up here automatically.</p>",
	),
	(
		"grc-step-03-framework",
		"Confirm your frameworks",
		"GRC Framework",
		"<p>Check that the frameworks scoped for this client exist with their control sets "
		"loaded \u2014 NCA ECC, ISO 27001, SDAIA PDPL, GDPR, and so on.</p>",
	),
	(
		"grc-step-04-control",
		"Run the control assessment",
		"GRC Control",
		"<p>Work through the weighted questionnaire for each framework in scope. This is what "
		"produces the compliance percentage in the GRC Compliance Status report.</p>",
	),
	(
		"grc-step-05-risk",
		"Build the risk register",
		"GRC Risk Register",
		"<p>Score likelihood and impact, assign an owner, and break the treatment plan into "
		"the Treatment Actions table added by this add-on.</p>",
	),
	(
		"grc-step-06-evidence",
		"Collect evidence",
		"GRC Evidence",
		"<p>Attach evidence per control manually, or let a GRC Evidence Fetcher pull it from a "
		"connected system on a schedule.</p>",
	),
	(
		"grc-step-07-finding",
		"Raise findings",
		"GRC Audit Finding",
		"<p>Log every gap the assessment surfaces, with severity, owner, and remediation "
		"target date.</p>",
	),
	(
		"grc-step-08-policy",
		"Publish the supporting policies",
		"GRC Policy",
		"<p>Draft, review, and publish the policies that back the controls you just assessed.</p>",
	),
	(
		"grc-step-09-vendor",
		"Assess third parties",
		"GRC Vendor",
		"<p>Register vendors in scope and run a vendor assessment against them.</p>",
	),
	(
		"grc-step-10-report",
		"Report and sign off",
		"GRC Compliance Status",
		"<p>Run the compliance, risk, and findings reports to close out the engagement with an "
		"audit-ready pack.</p>",
	),
]


def seed_onboarding():
	if not (_doctype_exists("Module Onboarding") and _doctype_exists("Onboarding Step")):
		return

	module = _resolve_module()
	created = []

	for name, title, reference_doctype, description in ONBOARDING_STEPS:
		if not (_doctype_exists(reference_doctype) or frappe.db.exists("Report", reference_doctype)):
			continue
		_upsert_onboarding_step(name, title, reference_doctype, description)
		created.append(name)

	if not created:
		frappe.log_error(
			title=_title("GRC Pathway: onboarding skipped"),
			message="No AlphaX GRC DocTypes were found, so the guided pathway was not seeded.",
		)
		return

	_upsert_module_onboarding(module, created)


def _upsert_onboarding_step(name: str, title: str, reference_doctype: str, description: str):
	is_report = not _doctype_exists(reference_doctype) and frappe.db.exists("Report", reference_doctype)

	if frappe.db.exists("Onboarding Step", name):
		step = frappe.get_doc("Onboarding Step", name)
	else:
		step = frappe.new_doc("Onboarding Step")
		step.name = name
		step.flags.name_set = True

	step.title = title
	step.action = "View Report" if is_report else "Create Entry"
	step.reference_document = reference_doctype
	step.description = description
	_set_if_field(step, "validate_action", 1)
	_set_if_field(step, "is_single", 0)
	_set_if_field(step, "is_skipped", 0)
	_set_if_field(step, "is_complete", 0)
	if is_report:
		_set_if_field(step, "reference_report", reference_doctype)
		_set_if_field(step, "report_reference_doctype", "GRC Control")
		_set_if_field(step, "report_type", "Script Report")

	step.flags.ignore_mandatory = True
	step.save(ignore_permissions=True) if not step.is_new() else step.insert(ignore_permissions=True)


def _upsert_module_onboarding(module: str, step_names: list[str]):
	name = "GRC Pathway"

	if frappe.db.exists("Module Onboarding", name):
		onboarding = frappe.get_doc("Module Onboarding", name)
	else:
		onboarding = frappe.new_doc("Module Onboarding")
		onboarding.name = name
		onboarding.flags.name_set = True

	onboarding.module = module
	onboarding.title = "Get started with GRC Pathway"
	onboarding.subtitle = "Walk through one full client engagement, end to end"
	onboarding.success_message = (
		"You've completed a full engagement cycle \u2014 client, framework, risk, evidence, "
		"findings, policy, vendor, and reporting all connected."
	)
	_set_if_field(onboarding, "documentation_url", "")
	_set_if_field(onboarding, "is_complete", 0)

	onboarding.set("steps", [])
	for step_name in step_names:
		onboarding.append("steps", {"step": step_name})

	onboarding.flags.ignore_mandatory = True
	onboarding.save(ignore_permissions=True) if not onboarding.is_new() else onboarding.insert(
		ignore_permissions=True
	)


# --------------------------------------------------------------------------
# 4. Role permissions
#
# The doctypes ship with System Manager only, because a DocPerm row naming a
# role that doesn't exist fails DocType sync outright. AlphaX GRC's own roles
# are granted here instead, once they're known to exist.
# --------------------------------------------------------------------------

ROLE_GRANTS = {
	"GRC Global Policy": [("GRC Admin", "write"), ("Compliance Officer", "write"),
						  ("GRC Executive", "read"), ("GRC Auditor", "read")],
	"GRC Pathway Settings": [("GRC Admin", "write")],
	"GRC Evidence Connector": [("GRC Admin", "write")],
	"GRC Evidence Fetcher": [("GRC Admin", "write"), ("Compliance Officer", "read")],
	"GRC Evidence Run": [("GRC Admin", "read"), ("Compliance Officer", "read"),
						 ("GRC Auditor", "read")],
}


def seed_role_permissions():
	from frappe.permissions import add_permission, update_permission_property

	for doctype, grants in ROLE_GRANTS.items():
		if not _doctype_exists(doctype):
			continue
		for role, level in grants:
			if not frappe.db.exists("Role", role):
				continue
			if frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
				continue
			try:
				add_permission(doctype, role, 0)
				update_permission_property(doctype, role, 0, "read", 1)
				if level == "write":
					for ptype in ("write", "create", "export", "report", "print"):
						update_permission_property(doctype, role, 0, ptype, 1)
			except Exception:
				frappe.log_error(
					title=_title(f"GRC Pathway: permission grant failed {doctype}/{role}"),
					message=frappe.get_traceback(),
				)
