# Copyright (c) 2026, Neotec Integrated Solutions
"""Whitelisted endpoints. Every mutating call is permission-checked."""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from alphax_grc.grc_evidence_automation.engine.evidence_runner import run_fetcher

# --------------------------------------------------------------------------
# Evidence automation
# --------------------------------------------------------------------------


@frappe.whitelist()
def run_fetcher_now(fetcher: str) -> dict:
	"""Manual 'Run Now' from the GRC Evidence Fetcher form."""
	if not frappe.has_permission("GRC Evidence Fetcher", ptype="write", doc=fetcher):
		frappe.throw(
			"You are not permitted to run this evidence fetcher.", frappe.PermissionError
		)

	run_name = run_fetcher(fetcher)
	return {
		"run": run_name,
		"result": frappe.db.get_value("GRC Evidence Run", run_name, "result"),
	}


# --------------------------------------------------------------------------
# Pathway board
#
# Each stage declares the doctype it counts, an optional "needs attention"
# filter, and how to route on click. Stages whose doctype is missing are
# dropped rather than rendered as a broken tile.
# --------------------------------------------------------------------------

STAGES = [
	{"label": "Clients", "doctype": "GRC Client Profile", "client_field": None,
	 "hint": "Client profiles in scope"},
	{"label": "Engagements", "doctype": "GRC Engagement", "client_field": "client",
	 "attention": {"engagement_status": "Active"}, "attention_label": "active",
	 "hint": "Consulting engagements"},
	{"label": "Frameworks", "doctype": "GRC Framework", "client_field": None,
	 "hint": "Frameworks with control sets loaded"},
	{"label": "Controls", "doctype": "GRC Control", "client_field": "client",
	 "hint": "Controls available for assessment"},
	{"label": "Risks", "doctype": "GRC Risk Register", "client_field": "client",
	 "attention": {"status": ["in", ["Open", "Monitoring"]]}, "attention_label": "open",
	 "hint": "Risk register entries"},
	{"label": "Evidence", "doctype": "GRC Evidence", "client_field": "client",
	 "attention": {"status": ["in", ["Draft", "Collected"]]}, "attention_label": "unverified",
	 "hint": "Evidence collected against controls"},
	{"label": "Findings", "doctype": "GRC Audit Finding", "client_field": "client",
	 "attention": {"status": ["not in", ["Resolved", "Closed"]]}, "attention_label": "unresolved",
	 "hint": "Gaps raised by assessment"},
	{"label": "Policies", "doctype": "GRC Policy", "client_field": "client",
	 "attention": {"publication_status": "Published"}, "attention_label": "published",
	 "hint": "Client policy set"},
	{"label": "Vendors", "doctype": "GRC Vendor", "client_field": None,
	 "attention": {"status": "Blocked"}, "attention_label": "blocked",
	 "hint": "Third parties in scope"},
	{"label": "Reporting", "report": "GRC Compliance Status", "doctype": "GRC Control",
	 "client_field": "client", "hint": "Compliance status report"},
]

THEME_DEFAULT = "Ocean"


def _settings() -> dict:
	defaults = {
		"color_theme": THEME_DEFAULT,
		"allow_user_override": 1,
		"show_counts": 1,
		"show_progress_rail": 1,
		"compact_mode": 0,
		"default_client": None,
	}
	if not frappe.db.exists("DocType", "GRC Pathway Settings"):
		return defaults
	try:
		doc = frappe.get_cached_doc("GRC Pathway Settings")
	except Exception:
		return defaults
	for key in defaults:
		value = doc.get(key)
		if value not in (None, ""):
			defaults[key] = value
	return defaults


def _count(doctype: str, filters: dict) -> int:
	try:
		return frappe.db.count(doctype, filters or None)
	except Exception:
		return 0


@frappe.whitelist()
def get_pathway_stats(client: str | None = None) -> dict:
	"""Live counts per pathway stage, scoped to a client when one is given."""
	settings = _settings()
	client = client or settings.get("default_client") or None

	stages = []
	for spec in STAGES:
		doctype = spec["doctype"]
		if not frappe.db.exists("DocType", doctype):
			continue
		if not frappe.has_permission(doctype, ptype="read"):
			continue

		base: dict = {}
		if client and spec.get("client_field"):
			base[spec["client_field"]] = client

		total = _count(doctype, dict(base))

		meta = ""
		flag = ""
		if spec.get("attention") and total:
			attention_filters = dict(base)
			attention_filters.update(spec["attention"])
			hits = _count(doctype, attention_filters)
			if hits:
				meta = f"{hits} {spec['attention_label']}"
			flag = "needs attention" if hits and spec["attention_label"] in (
				"open", "unresolved", "unverified", "blocked"
			) else ""

		stages.append({
			"label": spec["label"],
			"count": total,
			"meta": meta,
			"flag": flag,
			"hint": spec.get("hint", ""),
			"route_type": "report" if spec.get("report") else "list",
			"route_to": spec.get("report") or doctype,
		})

	clients = []
	if frappe.db.exists("DocType", "GRC Client Profile") and frappe.has_permission(
		"GRC Client Profile", ptype="read"
	):
		for row in frappe.get_all(
			"GRC Client Profile", fields=["name", "client_name"], limit=200, order_by="name asc"
		):
			clients.append({"value": row.name, "label": row.get("client_name") or row.name})

	return {
		"stages": stages,
		"clients": clients,
		"default_client": client or "",
		"theme": settings["color_theme"],
		"settings": {
			"allow_user_override": int(settings["allow_user_override"] or 0),
			"show_counts": int(settings["show_counts"] or 0),
			"show_progress_rail": int(settings["show_progress_rail"] or 0),
			"compact_mode": int(settings["compact_mode"] or 0),
		},
		"as_of": now_datetime().strftime("%d %b %Y %H:%M"),
	}


# --------------------------------------------------------------------------
# Global policy library
# --------------------------------------------------------------------------


@frappe.whitelist()
def adopt_policies(client: str, policies=None, only_mandatory: int = 0) -> dict:
	"""Instantiate global policy library entries as client-scoped GRC Policies."""
	if not frappe.has_permission("GRC Policy", ptype="create"):
		frappe.throw("You are not permitted to create policies.", frappe.PermissionError)
	if not frappe.db.exists("GRC Client Profile", client):
		frappe.throw(f"Client {client} not found.")

	if isinstance(policies, str):
		policies = frappe.parse_json(policies)

	if not policies:
		filters = {"is_active": 1}
		if frappe.utils.cint(only_mandatory):
			filters["is_mandatory"] = 1
		policies = frappe.get_all(
			"GRC Global Policy", filters=filters, pluck="name", order_by="display_order asc"
		)

	created, skipped, failed = [], [], []
	for name in policies:
		try:
			doc = frappe.get_doc("GRC Global Policy", name)
			policy, is_new = doc.adopt_for_client(client)
			(created if is_new else skipped).append(policy.name)
		except Exception:
			failed.append(name)
			frappe.log_error(
				title=f"Policy adoption failed: {name}"[:140],
				message=frappe.get_traceback(),
			)

	frappe.db.commit()
	return {
		"created": created,
		"skipped": skipped,
		"failed": failed,
		"message": f"{len(created)} created, {len(skipped)} already existed, {len(failed)} failed",
	}


# --------------------------------------------------------------------------
# Project plans / Gantt
# --------------------------------------------------------------------------


@frappe.whitelist()
def get_gantt(plan: str) -> dict:
	"""Everything the Gantt page needs, already dated by the plan controller."""
	if not frappe.has_permission("GRC Project Plan", ptype="read", doc=plan):
		frappe.throw("You are not permitted to view this plan.", frappe.PermissionError)

	doc = frappe.get_doc("GRC Project Plan", plan)
	tasks = []
	for row in doc.get("tasks") or []:
		tasks.append({
			"idx": row.idx,
			"wbs": row.wbs or "",
			"depth": (row.wbs or "").count(".") if row.wbs else 0,
			"title": row.task_title,
			"phase": row.phase or "",
			"start": str(row.start_date) if row.start_date else None,
			"end": str(row.end_date) if row.end_date else None,
			"days": int(row.duration_days or 0),
			"pct": float(row.pct_complete or 0),
			"status": row.status or "Not Started",
			"milestone": int(row.is_milestone or 0),
			"locked": int(row.locked or 0),
			"role": row.responsible_role or "",
			"assigned_to": row.assigned_to or "",
			"depends_on": row.depends_on or "",
		})

	return {
		"plan": doc.name,
		"title": doc.plan_title,
		"client": doc.client,
		"start": str(doc.start_date) if doc.start_date else None,
		"end": str(doc.end_date) if doc.end_date else None,
		"working_days": doc.working_days,
		"total_working_days": int(doc.total_working_days or 0),
		"pct_complete": float(doc.pct_complete or 0),
		"tasks": tasks,
		"theme": _settings()["color_theme"],
	}


@frappe.whitelist()
def list_plans(client: str | None = None) -> list:
	filters = {"client": client} if client else None
	return frappe.get_all(
		"GRC Project Plan", filters=filters,
		fields=["name", "plan_title", "client", "start_date", "end_date", "pct_complete", "status"],
		order_by="start_date desc", limit=100,
	)


@frappe.whitelist()
def update_task_dates(plan: str, idx: int, start_date=None, duration_days=None,
					  pct_complete=None, lock: int = 1) -> dict:
	"""Edit one bar from the Gantt and let the rest of the chain follow.

	Editing from the chart locks the row by default, so the next reschedule
	keeps the change instead of overwriting it.
	"""
	if not frappe.has_permission("GRC Project Plan", ptype="write", doc=plan):
		frappe.throw("You are not permitted to edit this plan.", frappe.PermissionError)

	doc = frappe.get_doc("GRC Project Plan", plan)
	row = next((t for t in doc.get("tasks") or [] if int(t.idx) == int(idx)), None)
	if not row:
		frappe.throw(f"Task {idx} not found on {plan}.")

	if start_date:
		row.start_date = frappe.utils.getdate(start_date)
		row.locked = frappe.utils.cint(lock)
	if duration_days not in (None, ""):
		row.duration_days = frappe.utils.cint(duration_days)
		row.locked = frappe.utils.cint(lock)
	if pct_complete not in (None, ""):
		row.pct_complete = frappe.utils.flt(pct_complete)

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return get_gantt(plan)


# --------------------------------------------------------------------------
# SAMA CSF dashboard
# --------------------------------------------------------------------------

SAMA_DOMAINS = {
	"3.1": "Leadership & Governance",
	"3.2": "Risk Management & Compliance",
	"3.3": "Operations & Technology",
	"3.4": "Third Party",
}

SAMA_TARGET = 3


@frappe.whitelist()
def get_sama_dashboard(client: str | None = None) -> dict:
	"""Everything a SAMA engagement is judged on, in one call."""
	from alphax_grc.pathway.api import _settings

	settings = _settings()
	client = client or settings.get("default_client") or None

	if not frappe.db.exists("DocType", "GRC SAMA Subdomain"):
		return {"available": 0, "reason": "SAMA catalogue not installed — run bench migrate."}

	catalogue = frappe.get_all(
		"GRC SAMA Subdomain", filters={"is_active": 1},
		fields=["name", "domain", "domain_title", "subdomain_title",
				"control_considerations", "excluded_for_non_banks"],
		order_by="name asc",
	)

	# --- latest assessment for this client
	assessment = None
	domains = {code: {"code": code, "title": title, "total": 0, "assessed": 0,
					  "at_target": 0, "level": 0.0} for code, title in SAMA_DOMAINS.items()}
	for row in catalogue:
		d = domains.get(row.domain)
		if d:
			d["total"] += 1

	filters = {"client": client} if client else {}
	latest = frappe.get_all(
		"GRC SAMA Assessment", filters=filters,
		fields=["name", "assessment_title", "overall_maturity", "pct_at_target",
				"applicable_subdomains", "subdomains_at_target", "status",
				"assessment_date", "entity_type", "lowest_domain"],
		order_by="assessment_date desc, modified desc", limit=1,
	)
	weakest = []
	if latest:
		assessment = latest[0]
		lines = frappe.get_all(
			"GRC SAMA Assessment Line",
			filters={"parent": assessment["name"], "applicable": 1},
			fields=["subdomain", "subdomain_title", "domain", "current_level",
					"target_level", "meets_target", "gap_description"],
			limit=100,
		)
		levels = {}
		for line in lines:
			try:
				level = int(str(line.current_level or "0").strip()[0])
			except (ValueError, IndexError):
				level = 0
			levels.setdefault(line.domain, []).append(level)
			d = domains.get(line.domain)
			if d:
				d["assessed"] += 1
				d["at_target"] += 1 if line.meets_target else 0
			if level < SAMA_TARGET:
				weakest.append({
					"code": line.subdomain,
					"title": line.subdomain_title,
					"level": level,
					"gap": (line.gap_description or "")[:120],
				})
		for code, values in levels.items():
			if code in domains and values:
				domains[code]["level"] = round(sum(values) / len(values), 2)
		weakest.sort(key=lambda x: (x["level"], x["code"]))

	# --- deliverables
	del_filters = {"client": client} if client else {"is_master": 1}
	deliverables = frappe.get_all(
		"GRC SAMA Deliverable", filters=del_filters, fields=["status"], limit=500
	) if frappe.db.exists("DocType", "GRC SAMA Deliverable") else []
	done_states = ("Approved", "Evidence Filed")
	deliverable_stats = {
		"total": len(deliverables),
		"complete": len([d for d in deliverables if d.status in done_states]),
		"in_progress": len([d for d in deliverables if d.status in ("In Progress", "Drafted")]),
		"not_started": len([d for d in deliverables if d.status == "Not Started"]),
		"scoped_to_client": bool(client and del_filters.get("client")),
	}

	# --- waivers
	waivers = frappe.get_all(
		"GRC SAMA Waiver", filters=filters, fields=["name", "subject", "status", "request_type"],
		limit=100,
	) if frappe.db.exists("DocType", "GRC SAMA Waiver") else []
	open_waivers = [w for w in waivers if w.status not in ("Approved", "Rejected", "Withdrawn")]

	# --- reportable incidents
	incidents = []
	if frappe.db.exists("DocType", "GRC Incident"):
		try:
			incidents = frappe.get_all(
				"GRC Incident",
				filters={**filters, "sama_reportable": 1},
				fields=["name", "incident_title", "severity", "status", "sama_notified_on"],
				limit=50,
			)
		except Exception:
			incidents = []
	unreported = [i for i in incidents if not i.get("sama_notified_on")]

	return {
		"available": 1,
		"client": client or "",
		"target_level": SAMA_TARGET,
		"assessment": assessment,
		"domains": list(domains.values()),
		"weakest": weakest[:8],
		"deliverables": deliverable_stats,
		"waivers": {
			"total": len(waivers),
			"open": len(open_waivers),
			"awaiting_sama": len([w for w in waivers if w.status == "Submitted to SAMA"]),
		},
		"incidents": {
			"reportable": len(incidents),
			"not_yet_notified": len(unreported),
			"rows": unreported[:5],
		},
		"catalogue_size": len(catalogue),
		"theme": settings["color_theme"],
	}


@frappe.whitelist()
def suggest_templates(engagement: str | None = None, client: str | None = None) -> dict:
	"""Which plan templates fit this engagement.

	Matches on the engagement type first, then falls back to the frameworks
	the client has in scope, so the picker is never empty.
	"""
	if not frappe.db.exists("DocType", "GRC Plan Template"):
		return {"matches": [], "reason": "no templates installed"}

	engagement_type = None
	if engagement and frappe.db.exists("GRC Engagement", engagement):
		engagement_type = frappe.db.get_value("GRC Engagement", engagement, "engagement_type")

	fields = ["name", "template_name", "framework", "engagement_type",
			  "task_count", "indicative_duration_days", "default_working_days"]

	matches = []
	if engagement_type:
		matches = frappe.get_all(
			"GRC Plan Template",
			filters={"is_active": 1, "engagement_type": engagement_type},
			fields=fields, order_by="template_name asc",
		)

	if not matches and client and frappe.db.exists("DocType", "GRC Framework"):
		frameworks = frappe.get_all(
			"GRC Control", filters={"client": client}, pluck="framework", limit=50
		)
		if frameworks:
			matches = frappe.get_all(
				"GRC Plan Template",
				filters={"is_active": 1, "framework": ["in", list({f for f in frameworks if f})]},
				fields=fields, order_by="template_name asc",
			)

	return {
		"engagement_type": engagement_type,
		"matches": matches,
		"total_active": frappe.db.count("GRC Plan Template", {"is_active": 1}),
	}
