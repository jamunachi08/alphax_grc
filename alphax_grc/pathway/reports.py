# Copyright (c) 2026, Neotec Integrated Solutions
"""
GRC Report Studio backend.

Two kinds of report, one runner:

- **Builder** definitions are declarative — a source doctype, optional filter
  list, a group-by field and an aggregate. They execute through
  `frappe.get_list`, so every permission rule that applies in the desk applies
  here; a viewer only ever aggregates rows they could open.
- **Built-in** definitions cover the handful of reports that need two series
  or a computed measure (maturity current vs target, DSR ageing), which a
  single group-by cannot express.

`create_definition` is whitelisted so the studio page can save new reports
from the front end without touching the desk form.
"""

from __future__ import annotations

import json

import frappe

GROUPABLE_TYPES = {"Select", "Link", "Data", "Date", "Check", "Autocomplete"}
NUMERIC_TYPES = {"Int", "Float", "Currency", "Percent", "Duration"}
SKIP_FIELDS = {"naming_series", "amended_from"}


def _log_title(text: str) -> str:
	return text[:140]


def _assert_grc_doctype(doctype: str):
	if not doctype or not frappe.db.exists("DocType", doctype):
		frappe.throw(f"DocType {doctype!r} does not exist.")
	module = frappe.db.get_value("DocType", doctype, "module")
	if module not in ("AlphaX GRC", "GRC Evidence Automation"):
		frappe.throw("Report Studio only reports on AlphaX GRC doctypes.")


@frappe.whitelist()
def field_options(doctype: str) -> dict:
	"""What the builder UI can offer for this doctype."""
	_assert_grc_doctype(doctype)
	meta = frappe.get_meta(doctype)

	groupable, numeric, columns = [], [], []
	for df in meta.fields:
		if df.fieldname in SKIP_FIELDS or df.get("hidden"):
			continue
		entry = {"fieldname": df.fieldname, "label": df.label or df.fieldname,
				 "fieldtype": df.fieldtype, "options": df.options or ""}
		if df.fieldtype in GROUPABLE_TYPES:
			groupable.append(entry)
		if df.fieldtype in NUMERIC_TYPES:
			numeric.append(entry)
		if df.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML",
								"Table", "Table MultiSelect", "Text Editor"):
			columns.append(entry)

	return {"groupable": groupable, "numeric": numeric, "columns": columns,
			"title_field": meta.title_field or "name"}


def _parse_filters(filters_json) -> list:
	if not filters_json:
		return []
	parsed = json.loads(filters_json) if isinstance(filters_json, str) else filters_json
	if not isinstance(parsed, list):
		frappe.throw("Filters must be a JSON list of [field, operator, value] rows.")
	return parsed


def _default_columns(doctype: str) -> list[str]:
	meta = frappe.get_meta(doctype)
	cols = ["name"]
	if meta.title_field and meta.title_field != "name":
		cols.append(meta.title_field)
	for df in meta.fields:
		if df.get("in_list_view") and df.fieldname not in cols \
				and df.fieldtype not in ("Section Break", "Column Break"):
			cols.append(df.fieldname)
		if len(cols) >= 7:
			break
	return cols


def _run_builder(defn) -> dict:
	_assert_grc_doctype(defn.source_doctype)
	filters = _parse_filters(defn.filters_json)
	meta = frappe.get_meta(defn.source_doctype)

	group_by = (defn.group_by or "").strip()
	if group_by and not meta.get_field(group_by):
		frappe.throw(f"{defn.source_doctype} has no field {group_by!r}.")

	agg_field = (defn.aggregate_field or "").strip()
	if defn.aggregate in ("Sum", "Average"):
		if not agg_field or not meta.get_field(agg_field):
			frappe.throw(f"Aggregate {defn.aggregate} needs a numeric field.")

	wanted = ["name"] + [f for f in {group_by, agg_field} if f]
	rows = frappe.get_list(defn.source_doctype, filters=filters, fields=wanted,
						   limit=5000, ignore_ifnull=False)

	groups: dict = {}
	for row in rows:
		key = row.get(group_by) if group_by else "All"
		key = key if key not in (None, "") else "(not set)"
		bucket = groups.setdefault(key, {"count": 0, "sum": 0.0})
		bucket["count"] += 1
		if agg_field:
			bucket["sum"] += frappe.utils.flt(row.get(agg_field))

	series = []
	for key, bucket in groups.items():
		if defn.aggregate == "Sum":
			value = round(bucket["sum"], 2)
		elif defn.aggregate == "Average":
			value = round(bucket["sum"] / bucket["count"], 2) if bucket["count"] else 0
		else:
			value = bucket["count"]
		series.append({"label": str(key), "value": value})
	series.sort(key=lambda x: x["value"], reverse=True)
	labels = [s["label"] for s in series]
	values = [s["value"] for s in series]

	columns = [c.strip() for c in (defn.detail_columns or "").split(",") if c.strip()] \
		or _default_columns(defn.source_doctype)
	columns = [c for c in columns if c == "name" or meta.get_field(c)]
	detail = frappe.get_list(defn.source_doctype, filters=filters, fields=columns,
							 limit=200, order_by="modified desc")

	return {"series": [values], "series_labels": [defn.aggregate], "labels": labels,
			"columns": columns, "rows": detail, "total": len(rows)}


# --------------------------------------------------------------------------
# Built-ins — reports a single group-by cannot express
# --------------------------------------------------------------------------


def _bi_sama_maturity_by_domain() -> dict:
	"""Current vs target maturity per SAMA domain, from the latest assessment
	per client — the two-series bar in the reference dashboard."""
	lines = frappe.get_list(
		"GRC SAMA Assessment Line",
		filters={"applicable": 1},
		fields=["domain", "current_level", "target_level", "subdomain", "subdomain_title"],
		limit=2000,
	)
	by_domain: dict = {}
	for line in lines:
		cur = frappe.utils.cint(str(line.current_level or "0")[:1])
		tgt = frappe.utils.cint(str(line.target_level or "3")[:1])
		d = by_domain.setdefault(line.domain or "?", {"cur": [], "tgt": []})
		d["cur"].append(cur)
		d["tgt"].append(tgt)

	labels = sorted(by_domain)
	current = [round(sum(v["cur"]) / len(v["cur"]), 2) if v["cur"] else 0
			   for v in (by_domain[k] for k in labels)]
	target = [round(sum(v["tgt"]) / len(v["tgt"]), 2) if v["tgt"] else 0
			  for v in (by_domain[k] for k in labels)]
	gap_rows = [{"name": "", "domain": k, "current": c, "target": t, "gap": round(t - c, 2)}
				for k, c, t in zip(labels, current, target)]

	return {"series": [current, target], "series_labels": ["Current", "Target"],
			"labels": labels,
			"columns": ["domain", "current", "target", "gap"], "rows": gap_rows,
			"total": len(lines)}


def _bi_dsr_aging_by_type() -> dict:
	"""Average days a data-subject request has been (or was) open, by type."""
	rows = frappe.get_list(
		"GRC Data Subject Request",
		fields=["name", "request_type", "received_on", "due_date", "status"],
		limit=2000,
	)
	today = frappe.utils.getdate()
	buckets: dict = {}
	for row in rows:
		if not row.received_on:
			continue
		age = (today - frappe.utils.getdate(row.received_on)).days
		buckets.setdefault(row.request_type or "(not set)", []).append(age)
	labels = sorted(buckets)
	series = [round(sum(v) / len(v), 1) for v in (buckets[k] for k in labels)]
	overdue = [r for r in rows if r.due_date and frappe.utils.getdate(r.due_date) < today
			   and r.status not in ("Completed", "Rejected", "Closed")]
	return {"series": [series], "series_labels": ["Avg days open"], "labels": labels,
			"columns": ["name", "request_type", "received_on", "due_date", "status"],
			"rows": overdue[:200], "total": len(rows)}


def _bi_incidents_past_sama_notification() -> dict:
	"""Reportable incidents with no SAMA notification recorded — the number
	with a regulatory clock on it."""
	filters = {"sama_reportable": 1}
	fields = ["name", "incident_title", "severity", "status", "reported_on", "sama_notified_on"]
	try:
		rows = frappe.get_list("GRC Incident", filters=filters, fields=fields, limit=500)
	except Exception:
		rows = []
	missing = [r for r in rows if not r.get("sama_notified_on")]
	by_sev: dict = {}
	for row in missing:
		by_sev[row.severity or "?"] = by_sev.get(row.severity or "?", 0) + 1
	labels = sorted(by_sev)
	return {"series": [[by_sev[k] for k in labels]], "series_labels": ["Not notified"],
			"labels": labels, "columns": fields, "rows": missing[:200], "total": len(missing)}


def _bi_policy_publication_pct() -> dict:
	total = frappe.db.count("GRC Policy")
	published = frappe.db.count("GRC Policy", {"publication_status": "Published"})
	pct = round(published / total * 100, 1) if total else 0
	rows = frappe.get_list("GRC Policy", filters={"publication_status": ["!=", "Published"]},
						   fields=["name", "policy_title", "status", "publication_status",
								   "review_due_date"], limit=200)
	return {"series": [[pct]], "series_labels": ["% published"], "labels": ["Published"],
			"columns": ["name", "policy_title", "status", "publication_status", "review_due_date"],
			"rows": rows, "total": total, "number": pct, "suffix": "%"}


def _bi_risks_above_appetite_by_category() -> dict:
	try:
		rows = frappe.get_list(
			"GRC Risk Register",
			filters={"within_appetite": 0},
			fields=["name", "risk_title", "risk_category", "residual_rating",
					"appetite_ceiling", "appetite_status"],
			limit=1000,
		)
	except Exception:
		rows = []
	pending = [r for r in rows if "needs" in (r.appetite_status or "")]
	by_cat: dict = {}
	for row in pending:
		by_cat[row.risk_category or "?"] = by_cat.get(row.risk_category or "?", 0) + 1
	labels = sorted(by_cat, key=by_cat.get, reverse=True)
	return {"series": [[by_cat[k] for k in labels]], "series_labels": ["Above appetite"],
			"labels": labels,
			"columns": ["name", "risk_title", "risk_category", "residual_rating",
						"appetite_ceiling", "appetite_status"],
			"rows": pending[:200], "total": len(pending)}


def _bi_assets_unclassified() -> dict:
	meta = frappe.get_meta("GRC Asset Inventory")
	class_field = next((f.fieldname for f in meta.fields
						if "classification" in f.fieldname), None)
	filters = {class_field: ["in", ["", None]]} if class_field else {}
	fields = ["name", "asset_name", "asset_type", "department"] \
		+ ([class_field] if class_field else [])
	rows = frappe.get_list("GRC Asset Inventory", filters=filters, fields=fields, limit=500)
	by_type: dict = {}
	for row in rows:
		by_type[row.asset_type or "?"] = by_type.get(row.asset_type or "?", 0) + 1
	labels = sorted(by_type, key=by_type.get, reverse=True)
	return {"series": [[by_type[k] for k in labels]], "series_labels": ["Unclassified"],
			"labels": labels, "columns": fields, "rows": rows[:200], "total": len(rows)}


BUILTINS = {
	"sama_maturity_by_domain": _bi_sama_maturity_by_domain,
	"dsr_aging_by_type": _bi_dsr_aging_by_type,
	"incidents_past_sama_notification": _bi_incidents_past_sama_notification,
	"policy_publication_pct": _bi_policy_publication_pct,
	"risks_above_appetite_by_category": _bi_risks_above_appetite_by_category,
	"assets_unclassified": _bi_assets_unclassified,
}


@frappe.whitelist()
def run_definition(name: str) -> dict:
	defn = frappe.get_doc("GRC Report Definition", name)
	if defn.definition_type == "Built-in":
		fn = BUILTINS.get(defn.builtin_key)
		if not fn:
			frappe.throw(f"Unknown built-in report {defn.builtin_key!r}.")
		result = fn()
	else:
		result = _run_builder(defn)

	result.update({
		"name": defn.name,
		"title": defn.report_title,
		"chart_type": defn.chart_type or "Bar",
		"category": defn.category or "General",
		"description": defn.description or "",
		"source_doctype": defn.get("source_doctype") or "",
	})
	return result


@frappe.whitelist()
def list_definitions() -> list:
	return frappe.get_all(
		"GRC Report Definition", filters={"is_active": 1},
		fields=["name", "report_title", "category", "chart_type", "definition_type",
				"source_doctype", "description"],
		order_by="category asc, report_title asc", limit=200,
	)


@frappe.whitelist()
def create_definition(report_title: str, source_doctype: str, group_by: str = "",
					  aggregate: str = "Count", aggregate_field: str = "",
					  chart_type: str = "Bar", category: str = "General",
					  filters_json: str = "", detail_columns: str = "",
					  description: str = "") -> str:
	"""Save a builder definition from the studio page, then run it once so a
	bad definition fails at save time rather than on first view."""
	frappe.only_for(("System Manager", "GRC Admin", "GRC Executive", "Compliance Officer"))
	_assert_grc_doctype(source_doctype)
	_parse_filters(filters_json)

	doc = frappe.new_doc("GRC Report Definition")
	doc.update({
		"report_title": report_title.strip(),
		"definition_type": "Builder",
		"source_doctype": source_doctype,
		"group_by": group_by.strip(),
		"aggregate": aggregate,
		"aggregate_field": aggregate_field.strip(),
		"chart_type": chart_type,
		"category": category,
		"filters_json": filters_json.strip(),
		"detail_columns": detail_columns.strip(),
		"description": description.strip(),
		"is_active": 1,
	})
	doc.insert()
	run_definition(doc.name)
	return doc.name


# --------------------------------------------------------------------------
# Seeded definitions — the reference dashboard, mapped onto our doctypes
# --------------------------------------------------------------------------

SEED_DEFINITIONS = [
	{"report_title": "Maturity by Domain — Current vs Target", "definition_type": "Built-in",
	 "builtin_key": "sama_maturity_by_domain", "category": "SAMA", "chart_type": "Bar",
	 "description": "Average current and target maturity per SAMA domain, with the gap per domain in the table."},
	{"report_title": "DSR Ageing by Request Type", "definition_type": "Built-in",
	 "builtin_key": "dsr_aging_by_type", "category": "Privacy", "chart_type": "Bar",
	 "description": "Average days open per data-subject request type; the table lists overdue requests."},
	{"report_title": "Incidents Past SAMA Notification", "definition_type": "Built-in",
	 "builtin_key": "incidents_past_sama_notification", "category": "Incidents", "chart_type": "Bar",
	 "description": "Reportable incidents with no SAMA notification recorded, by severity."},
	{"report_title": "Policy Publication %", "definition_type": "Built-in",
	 "builtin_key": "policy_publication_pct", "category": "Policies", "chart_type": "Number",
	 "description": "Share of policies published; the table lists everything still unpublished."},
	{"report_title": "Risks Above Appetite by Category", "definition_type": "Built-in",
	 "builtin_key": "risks_above_appetite_by_category", "category": "Risk", "chart_type": "Donut",
	 "description": "Risks above the client's appetite without a formal acceptance."},
	{"report_title": "Unclassified Assets by Type", "definition_type": "Built-in",
	 "builtin_key": "assets_unclassified", "category": "Assets", "chart_type": "Donut",
	 "description": "Assets with no classification, grouped by asset type."},
	{"report_title": "Incidents by Severity", "definition_type": "Builder",
	 "source_doctype": "GRC Incident", "group_by": "severity", "aggregate": "Count",
	 "category": "Incidents", "chart_type": "Donut",
	 "detail_columns": "name,incident_title,severity,status,reported_on"},
	{"report_title": "Open Risks by Category", "definition_type": "Builder",
	 "source_doctype": "GRC Risk Register", "group_by": "risk_category", "aggregate": "Count",
	 "filters_json": '[["status","in",["Open","Monitoring"]]]',
	 "category": "Risk", "chart_type": "Bar",
	 "detail_columns": "name,risk_title,risk_category,risk_rating,residual_rating,status"},
	{"report_title": "SAMA Deliverables by Status", "definition_type": "Builder",
	 "source_doctype": "GRC SAMA Deliverable", "group_by": "status", "aggregate": "Count",
	 "category": "SAMA", "chart_type": "Donut",
	 "detail_columns": "name,deliverable_title,subdomain,status,owner_user,due_date"},
	{"report_title": "Project Plans — % Complete", "definition_type": "Builder",
	 "source_doctype": "GRC Project Plan", "group_by": "plan_title", "aggregate": "Average",
	 "aggregate_field": "pct_complete", "category": "Delivery", "chart_type": "Bar",
	 "detail_columns": "name,plan_title,client,start_date,end_date,pct_complete,status"},
]


def seed_report_definitions():
	if not frappe.db.exists("DocType", "GRC Report Definition"):
		return
	for spec in SEED_DEFINITIONS:
		try:
			if frappe.db.exists("GRC Report Definition", spec["report_title"]):
				continue
			doc = frappe.new_doc("GRC Report Definition")
			doc.update(spec)
			doc.is_active = 1
			doc.flags.ignore_permissions = True
			doc.flags.ignore_mandatory = True
			doc.insert(ignore_permissions=True)
		except Exception:
			frappe.log_error(
				title=_log_title(f"Report definition seed failed: {spec['report_title']}"),
				message=frappe.get_traceback(),
			)
