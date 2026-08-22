# Copyright (c) 2026, Neotec Integrated Solutions
"""
Dispatches enabled GRC Evidence Fetchers, logs a GRC Evidence Run, and
upserts the result into AlphaX GRC's own `GRC Evidence` doctype (client +
control scoped, matching its data model) rather than a separate evidence
table. Handlers register per check_key; a fetcher with no handler still
runs safely and returns "Inconclusive" instead of silently skipping.

Run rows are the audit trail, so the run is always written even when the
evidence upsert fails, and one bad fetcher never aborts the scheduled batch.
"""

from __future__ import annotations

import json

import frappe
from frappe.utils import now_datetime

HANDLER_REGISTRY: dict = {}

# AlphaX GRC v2.2.0 ships GRC Evidence.status as
# Draft / Collected / Verified / Archived and evidence_type as
# Document / Screenshot / Log / Configuration / Approval / Other.
# Anything outside those lists fails Select validation on save, so both
# are resolved against live meta at write time (see _legal_option).
STATUS_MAP = {
	"Pass": "Verified",
	"Fail": "Collected",
	"Not Applicable": "Archived",
	"Inconclusive": "Draft",
	"Auth Error": "Draft",
}

EVIDENCE_TYPE = "Configuration"


def register_handler(check_key: str):
	def decorator(fn):
		HANDLER_REGISTRY[check_key] = fn
		return fn

	return decorator


def _log_title(text: str) -> str:
	"""frappe.log_error rejects titles over 140 chars."""
	return text[:140]


def run_fetcher(fetcher_name: str) -> str:
	fetcher = frappe.get_doc("GRC Evidence Fetcher", fetcher_name)
	if not fetcher.enabled:
		frappe.throw(f"Fetcher {fetcher_name} is disabled.")

	run = frappe.new_doc("GRC Evidence Run")
	run.fetcher = fetcher.name
	run.started_at = now_datetime()

	result, detail = _execute(fetcher)

	run.finished_at = now_datetime()
	run.result = result
	run.detail = json.dumps(detail, default=str)

	# Write the run first: the audit trail must survive an evidence
	# write-back failure (missing field, permission, renamed doctype).
	run.insert(ignore_permissions=True)

	try:
		evidence = _upsert_evidence(fetcher, result, detail)
		run.db_set("evidence_record", evidence.name, update_modified=False)
	except Exception:
		frappe.log_error(
			title=_log_title(f"Evidence write-back failed: {fetcher.name}"),
			message=frappe.get_traceback(),
		)

	fetcher.db_set("last_run", run.started_at, update_modified=False)
	fetcher.db_set("last_result", result, update_modified=False)
	return run.name


def _execute(fetcher) -> tuple[str, dict]:
	try:
		connector = frappe.get_doc("GRC Evidence Connector", fetcher.connector)
	except frappe.DoesNotExistError:
		return "Auth Error", {"reason": f"connector {fetcher.connector} not found"}

	handler = HANDLER_REGISTRY.get(fetcher.check_key)

	if connector.status != "Active":
		return "Auth Error", {"reason": f"connector status is {connector.status}"}

	if handler is None:
		return "Inconclusive", {"reason": "no handler registered for this check_key"}

	try:
		outcome = handler(connector, fetcher) or {}
		return outcome.get("result", "Inconclusive"), outcome.get("detail", {})
	except Exception as e:
		frappe.log_error(
			title=_log_title(f"Evidence fetcher failed: {fetcher.name}"),
			message=frappe.get_traceback(),
		)
		return ("Auth Error" if "auth" in str(e).lower() else "Fail"), {"error": str(e)}


def _legal_option(doctype: str, fieldname: str, preferred: str) -> str:
	"""Return `preferred` if the Select still allows it, else the first option.

	Guards against AlphaX GRC renaming its status/type vocabularies under us:
	an illegal value would otherwise raise on every single evidence write.
	"""
	try:
		field = frappe.get_meta(doctype).get_field(fieldname)
		options = [o.strip() for o in (field.options or "").split("\n") if o.strip()]
	except Exception:
		return preferred

	if not options or preferred in options:
		return preferred
	return options[0]


def _upsert_evidence(fetcher, result: str, detail: dict):
	existing_name = frappe.db.get_value(
		"GRC Evidence",
		{
			"client": fetcher.client,
			"related_document": fetcher.control,
			"evidence_title": fetcher.fetcher_name,
		},
	)
	if existing_name:
		evidence = frappe.get_doc("GRC Evidence", existing_name)
	else:
		evidence = frappe.new_doc("GRC Evidence")
		evidence.client = fetcher.client
		evidence.evidence_title = fetcher.fetcher_name
		evidence.evidence_type = _legal_option("GRC Evidence", "evidence_type", EVIDENCE_TYPE)
		evidence.related_doctype = "GRC Control"
		evidence.related_document = fetcher.control

	evidence.status = _legal_option("GRC Evidence", "status", STATUS_MAP.get(result, "Draft"))
	evidence.collected_on = now_datetime()  # GRC Evidence.collected_on is a Datetime
	evidence.notes = json.dumps(detail, default=str)[:1000]
	evidence.flags.ignore_permissions = True
	evidence.save(ignore_permissions=True)
	return evidence


def run_due_fetchers(schedule: str = "Hourly") -> list[str]:
	"""Scheduled entry point. One failing fetcher must not kill the batch."""
	names = frappe.get_all(
		"GRC Evidence Fetcher", filters={"enabled": 1, "schedule": schedule}, pluck="name"
	)

	run_names: list[str] = []
	for name in names:
		try:
			run_names.append(run_fetcher(name))
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(
				title=_log_title(f"Evidence fetcher batch error: {name}"),
				message=frappe.get_traceback(),
			)

	return run_names
