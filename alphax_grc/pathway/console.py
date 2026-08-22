# Copyright (c) 2026, Neotec Integrated Solutions
"""
State engine behind the Pathway Console.

The console is a working tool, not a dashboard: every stage reports what has
been done, what is blocking it, and the concrete transactions available right
now. Gating is computed here rather than in the browser so the same rules
apply to any client of the API.

A stage is:
  blocked   — a prerequisite stage is not yet done
  ready     — unlocked, nothing created yet
  progress  — records exist, completion criteria not met
  done      — completion criteria met

Every stage whose DocType is missing (or which the user can't read) is dropped
entirely rather than rendered as a broken tile, so the console degrades
cleanly on a partial AlphaX GRC install.
"""

from __future__ import annotations

import frappe

# key, label, doctype, client-scoped?, prerequisites, blurb
STAGE_SPECS = [
	{
		"key": "client", "label": "Client profile", "doctype": "GRC Client Profile",
		"client_field": None, "requires": [],
		"blurb": "Everything in the app is scoped to a client. Start here.",
		"done_when": None,
		"actions": [
			{"label": "New client", "type": "new", "target": "GRC Client Profile"},
			{"label": "All clients", "type": "list", "target": "GRC Client Profile"},
		],
	},
	{
		"key": "engagement", "label": "Engagement", "doctype": "GRC Engagement",
		"client_field": "client", "requires": ["client"],
		"blurb": "Open the engagement that findings, risks, and phases roll up to.",
		"done_when": {"engagement_status": "Active"},
		"done_label": "active engagement",
		"actions": [
			{"label": "Open engagement", "type": "new", "target": "GRC Engagement"},
			{"label": "All engagements", "type": "list", "target": "GRC Engagement"},
		],
	},
	{
		"key": "framework", "label": "Frameworks", "doctype": "GRC Framework",
		"client_field": None, "requires": ["engagement"],
		"blurb": "Confirm the frameworks in scope — ECC, ISO 27001, PDPL, and so on.",
		"done_when": None,
		"actions": [
			{"label": "Add framework", "type": "new", "target": "GRC Framework"},
			{"label": "All frameworks", "type": "list", "target": "GRC Framework"},
		],
	},
	{
		"key": "control", "label": "Controls", "doctype": "GRC Control",
		"client_field": "client", "requires": ["framework"],
		"blurb": "Load and assess the control set for each framework in scope.",
		"done_when": None,
		"actions": [
			{"label": "Add control", "type": "new", "target": "GRC Control"},
			{"label": "Assess controls", "type": "list", "target": "GRC Control"},
		],
	},
	{
		"key": "risk", "label": "Risk register", "doctype": "GRC Risk Register",
		"client_field": "client", "requires": ["control"],
		"blurb": "Score likelihood and impact, assign owners, break treatment into actions.",
		"done_when": None,
		"attention": {"within_appetite": 0, "status": ["in", ["Open", "Monitoring"]]},
		"attention_label": "above appetite",
		"actions": [
			{"label": "Log risk", "type": "new", "target": "GRC Risk Register"},
			{"label": "Risk register", "type": "list", "target": "GRC Risk Register"},
			{"label": "Risk summary", "type": "report", "target": "GRC Risk Summary"},
		],
	},
	{
		# v2.10.0 — resilience had no stage of its own; a business impact
		# analysis was invisible to the console even once fully approved.
		"key": "resilience", "label": "Business continuity", "doctype": "GRC Business Impact Analysis",
		"client_field": "client", "requires": ["risk"],
		"blurb": "Assess RTO/RPO per critical activity, then approve a DR plan against it.",
		"done_when": {"approver": ["is", "set"], "approval_date": ["is", "set"]},
		"done_label": "approved BIA",
		"attention": {"approver": ["is", "not set"]},
		"attention_label": "awaiting approval",
		"actions": [
			{"label": "New BIA", "type": "new", "target": "GRC Business Impact Analysis"},
			{"label": "All BIAs", "type": "list", "target": "GRC Business Impact Analysis"},
			{"label": "DR plans", "type": "list", "target": "GRC DR Plan"},
		],
	},
	{
		"key": "evidence", "label": "Evidence", "doctype": "GRC Evidence",
		"client_field": "client", "requires": ["control"],
		"blurb": "Attach evidence per control, or let a fetcher collect it on a schedule.",
		"done_when": {"status": "Verified"}, "done_label": "verified evidence",
		"attention": {"status": ["in", ["Draft", "Collected"]]}, "attention_label": "unverified",
		"actions": [
			{"label": "Add evidence", "type": "new", "target": "GRC Evidence"},
			{"label": "Automate collection", "type": "new", "target": "GRC Evidence Fetcher"},
			{"label": "All evidence", "type": "list", "target": "GRC Evidence"},
		],
	},
	{
		"key": "finding", "label": "Findings", "doctype": "GRC Audit Finding",
		"client_field": "client", "requires": ["control"],
		"blurb": "Log every gap the assessment surfaces, with severity and owner.",
		"done_when": None,
		"attention": {"status": ["not in", ["Resolved", "Closed"]]},
		"attention_label": "unresolved",
		"actions": [
			{"label": "Raise finding", "type": "new", "target": "GRC Audit Finding"},
			{"label": "All findings", "type": "list", "target": "GRC Audit Finding"},
			{"label": "Findings report", "type": "report", "target": "GRC Audit Findings Report"},
		],
	},
	{
		"key": "policy", "label": "Policies", "doctype": "GRC Policy",
		"client_field": "client", "requires": ["engagement"],
		"blurb": "Adopt the policy set from the global library, then review and publish.",
		"done_when": {"publication_status": "Published"}, "done_label": "published",
		"actions": [
			{"label": "Adopt from library", "type": "adopt", "target": "GRC Global Policy"},
			{"label": "Client policies", "type": "list", "target": "GRC Policy"},
			{"label": "Policy library", "type": "list", "target": "GRC Global Policy"},
		],
	},
	{
		"key": "vendor", "label": "Third parties", "doctype": "GRC Vendor",
		"client_field": None, "requires": ["engagement"],
		"blurb": "Register vendors in scope and assess them.",
		"done_when": None,
		"attention": {"status": "Blocked"}, "attention_label": "blocked",
		"actions": [
			{"label": "Add vendor", "type": "new", "target": "GRC Vendor"},
			{"label": "All vendors", "type": "list", "target": "GRC Vendor"},
		],
	},
	{
		"key": "report", "label": "Report and sign off", "doctype": "GRC Control",
		"client_field": "client", "requires": ["control", "evidence"],
		"blurb": "Close the engagement with an audit-ready compliance pack.",
		"done_when": None, "is_terminal": True,
		"actions": [
			{"label": "Compliance status", "type": "report", "target": "GRC Compliance Status"},
			{"label": "ITGC progress", "type": "report", "target": "GRC ITGC Progress"},
		],
	},
]

# Layered domain map — the shape of a GRC programme, not a list of doctypes.
DOMAIN_MAP = [
	{
		"pillar": "Governance", "tone": "blue", "caption": "Directs and oversees",
		"items": [
			{"label": "Client profiles", "doctype": "GRC Client Profile"},
			{"label": "Engagements", "doctype": "GRC Engagement"},
			{"label": "Policies", "doctype": "GRC Policy"},
			{"label": "Policy library", "doctype": "GRC Global Policy"},
		],
	},
	{
		"pillar": "Risk", "tone": "green", "caption": "Identifies and manages",
		"items": [
			{"label": "Risk register", "doctype": "GRC Risk Register"},
			{"label": "Risk acceptance", "doctype": "GRC Risk Acceptance"},
			{"label": "Third parties", "doctype": "GRC Vendor"},
			{"label": "Vendor assessments", "doctype": "GRC Vendor Assessment"},
			# v2.10.0 — KRI/KPI tracking existed as doctypes but had no home
			# in the visual domain map, so it was easy for a new user to miss.
			{"label": "Key risk indicators", "doctype": "GRC KRI"},
			{"label": "Key performance indicators", "doctype": "GRC KPI"},
		],
	},
	{
		# v2.10.0 — new pillar. Resilience (business continuity / disaster
		# recovery) is a full GRC domain that previously had no visual
		# presence anywhere in the app, despite the doctypes existing.
		"pillar": "Resilience", "tone": "teal", "caption": "Prepares and recovers",
		"items": [
			{"label": "Business impact analyses", "doctype": "GRC Business Impact Analysis"},
			{"label": "DR plans", "doctype": "GRC DR Plan"},
		],
	},
	{
		"pillar": "Compliance", "tone": "amber", "caption": "Ensures conformance",
		"items": [
			{"label": "Frameworks", "doctype": "GRC Framework"},
			{"label": "Controls", "doctype": "GRC Control"},
			{"label": "Evidence", "doctype": "GRC Evidence"},
			{"label": "Findings", "doctype": "GRC Audit Finding"},
		],
	},
	{
		"pillar": "Automation", "tone": "purple", "caption": "Collects and proves",
		"items": [
			{"label": "Connectors", "doctype": "GRC Evidence Connector"},
			{"label": "Fetchers", "doctype": "GRC Evidence Fetcher"},
			{"label": "Run log", "doctype": "GRC Evidence Run"},
		],
	},
]


def _count(doctype: str, filters: dict | None = None) -> int:
	try:
		return frappe.db.count(doctype, filters or None)
	except Exception:
		return 0


def _readable(doctype: str) -> bool:
	if not frappe.db.exists("DocType", doctype):
		return False
	try:
		return bool(frappe.has_permission(doctype, ptype="read"))
	except Exception:
		return False


def _stage_state(spec: dict, client: str | None) -> dict | None:
	doctype = spec["doctype"]
	if not _readable(doctype):
		return None

	base: dict = {}
	if client and spec.get("client_field"):
		base[spec["client_field"]] = client

	total = _count(doctype, dict(base))

	done_count = total
	if spec.get("done_when"):
		done_filters = dict(base)
		done_filters.update(spec["done_when"])
		done_count = _count(doctype, done_filters)

	attention = 0
	if spec.get("attention"):
		attention_filters = dict(base)
		attention_filters.update(spec["attention"])
		attention = _count(doctype, attention_filters)

	metrics = []
	if spec.get("done_when") and total:
		metrics.append({"label": spec.get("done_label", "complete"), "value": done_count})
	if attention:
		metrics.append({"label": spec["attention_label"], "value": attention, "warn": 1})

	return {
		"key": spec["key"],
		"label": spec["label"],
		"blurb": spec["blurb"],
		"doctype": doctype,
		"client_field": spec.get("client_field"),
		"count": total,
		"done_count": done_count,
		"attention": attention,
		"metrics": metrics,
		"actions": [a for a in spec["actions"] if _action_available(a)],
		"requires": spec["requires"],
		"is_terminal": int(bool(spec.get("is_terminal"))),
	}


def _action_available(action: dict) -> bool:
	if action["type"] == "report":
		return bool(frappe.db.exists("Report", action["target"]))
	if action["type"] == "adopt":
		return bool(frappe.db.exists("DocType", "GRC Global Policy"))
	return _readable(action["target"])


@frappe.whitelist()
def get_console_state(client: str | None = None) -> dict:
	"""Stage-by-stage state for the Pathway Console."""
	from alphax_grc.pathway.api import _settings

	settings = _settings()
	client = client or settings.get("default_client") or None

	stages: list[dict] = []
	done_keys: set[str] = set()

	for spec in STAGE_SPECS:
		stage = _stage_state(spec, client)
		if not stage:
			continue

		blockers = [
			k for k in stage["requires"]
			if k not in done_keys and any(s["key"] == k for s in stages)
		]

		if stage["is_terminal"]:
			is_done = not blockers and stage["done_count"] > 0
		else:
			is_done = stage["done_count"] > 0

		if blockers:
			stage["state"] = "blocked"
		elif is_done:
			stage["state"] = "done"
		elif stage["count"] > 0:
			stage["state"] = "progress"
		else:
			stage["state"] = "ready"

		stage["blockers"] = [
			next(s["label"] for s in stages if s["key"] == k) for k in blockers
		]
		if is_done and not blockers:
			done_keys.add(stage["key"])

		stages.append(stage)

	clients = []
	if _readable("GRC Client Profile"):
		for row in frappe.get_all(
			"GRC Client Profile", fields=["name", "client_name"], limit=200, order_by="name asc"
		):
			clients.append({"value": row.name, "label": row.get("client_name") or row.name})

	pillars = []
	for group in DOMAIN_MAP:
		items = []
		for item in group["items"]:
			if not _readable(item["doctype"]):
				continue
			filters = {}
			if client and frappe.get_meta(item["doctype"]).get_field("client"):
				filters["client"] = client
			items.append({
				"label": item["label"],
				"doctype": item["doctype"],
				"count": _count(item["doctype"], filters),
				"scoped": int(bool(filters)),
			})
		if items:
			pillars.append({
				"pillar": group["pillar"], "tone": group["tone"],
				"caption": group["caption"], "items": items,
			})

	total = len(stages)
	complete = len([s for s in stages if s["state"] == "done"])

	return {
		"client": client or "",
		"clients": clients,
		"stages": stages,
		"pillars": pillars,
		"progress": {
			"done": complete,
			"total": total,
			"pct": round((complete / total) * 100) if total else 0,
			"next": next((s["label"] for s in stages if s["state"] in ("ready", "progress")), ""),
		},
		"theme": settings["color_theme"],
		"allow_user_override": int(settings["allow_user_override"] or 0),
	}
