"""
Offline smoke test. Stubs enough of `frappe` to exercise the seeders and the
evidence runner without a bench, then asserts on the resulting state.

Run:  python3 tests/test_offline.py
"""

import json
import os
import sys
import types
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# --------------------------------------------------------------------------
# Stub frappe
# --------------------------------------------------------------------------

STORE = {}          # (doctype, name) -> doc
META = {}           # doctype -> set(fieldnames)
LOGS = []
COMMITS = {"commit": 0, "rollback": 0}
CUSTOM_FIELDS = []


class DoesNotExistError(Exception):
	pass


class PermissionError_(Exception):
	pass


class Doc(dict):
	def __init__(self, doctype, **kw):
		super().__init__(**kw)
		self.doctype = doctype
		self.flags = types.SimpleNamespace(name_set=False, ignore_permissions=False, ignore_mandatory=False)
		self.name = None
		self.creation = None

	def __getattr__(self, k):
		try:
			return self[k]
		except KeyError:
			# Real Frappe returns None for any declared-but-unset field.
			if k in META.get(object.__getattribute__(self, "doctype"), {}):
				return None
			raise AttributeError(k)

	def __setattr__(self, k, v):
		if k in ("doctype", "flags", "name", "creation", "idx"):
			object.__setattr__(self, k, v)
		else:
			self[k] = v

	def set(self, k, v):
		setattr(self, k, v)

	def get(self, k, default=None):
		if k in ("doctype", "name", "creation"):
			return object.__getattribute__(self, k)
		return dict.get(self, k, default)

	def append(self, table, row):
		# Real Frappe returns child Documents, not dicts — controllers rely on
		# attribute access (row.framework), so mirror that here.
		if isinstance(row, dict):
			child = Doc(row.get("doctype", "Child"))
			child.update(row)
			row = child
		self.setdefault(table, []).append(row)
		return row

	@property
	def meta(self):
		return Meta(self.doctype)

	def is_new(self):
		return self.creation is None

	def insert(self, ignore_permissions=False):
		if not self.name:
			# Honour the autoname rule declared in the shipped DocType JSON,
			# so the seeders' frappe.db.exists(code) lookups are exercised
			# against the naming this app actually ships.
			rule = AUTONAME.get(self.doctype, "")
			if rule.startswith("field:"):
				self.name = self.get(rule.split(":", 1)[1])
			if not self.name:
				self.name = f"{self.doctype}-{len(STORE) + 1:05d}"
		self.creation = "2026-08-14 00:00:00"
		STORE[(self.doctype, self.name)] = self
		return self

	def save(self, ignore_permissions=False):
		if self.is_new():
			return self.insert()
		STORE[(self.doctype, self.name)] = self
		return self

	def db_set(self, field, value, update_modified=True):
		setattr(self, field, value)


class Field:
	def __init__(self, fieldname, options=None):
		self.fieldname = fieldname
		self.options = options


class Meta:
	def __init__(self, doctype):
		self.doctype = doctype

	def get_field(self, fieldname):
		spec = META.get(self.doctype, {})
		if fieldname not in spec:
			return None
		return Field(fieldname, spec[fieldname])


def _matches(doc, filters):
	for key, cond in (filters or {}).items():
		value = doc.get(key)
		if isinstance(cond, list) and len(cond) == 2:
			op, target = cond
			if op == "in" and value not in target:
				return False
			if op == "not in" and value in target:
				return False
		elif value != cond:
			return False
	return True


class DB:
	def exists(self, doctype, name=None):
		if isinstance(doctype, str) and name is not None:
			if doctype == "DocType":
				return name if name in META else None
			if doctype == "Report":
				return name if name in REPORTS else None
			if isinstance(name, dict):
				return self.get_value(doctype, name)
			return name if (doctype, name) in STORE else None
		return None

	def get_value(self, doctype, filters, fieldname=None, order_by=None, **kw):
		matches = []
		for (dt, nm), doc in STORE.items():
			if dt != doctype:
				continue
			if isinstance(filters, dict) and all(doc.get(k) == v for k, v in filters.items()):
				matches.append((nm, doc))
			elif isinstance(filters, str) and nm == filters:
				matches.append((nm, doc))
		if not matches:
			return None
		# honour "creation desc" by insertion order (STORE is insertion-ordered)
		nm, doc = matches[-1] if (order_by or "").endswith("desc") else matches[0]
		return doc.get(fieldname) if fieldname else nm

	def count(self, doctype, filters=None):
		n = 0
		for (dt, nm), doc in STORE.items():
			if dt != doctype:
				continue
			if filters and not _matches(doc, filters):
				continue
			n += 1
		return n

	def set_value(self, doctype, name, field, value, update_modified=True):
		doc = STORE.get((doctype, name))
		if doc is not None:
			doc.set(field, value)

	def commit(self):
		COMMITS["commit"] += 1

	def rollback(self):
		COMMITS["rollback"] += 1


frappe = types.ModuleType("frappe")
frappe.db = DB()
frappe.DoesNotExistError = DoesNotExistError
frappe.PermissionError = PermissionError_
frappe.get_meta = lambda dt: Meta(dt)
frappe.new_doc = lambda dt: Doc(dt)
frappe.get_traceback = lambda: traceback.format_exc()


def _get_doc(doctype, name=None):
	if isinstance(doctype, dict):
		d = Doc(doctype["doctype"])
		d.update({k: v for k, v in doctype.items() if k != "doctype"})
		return d
	doc = STORE.get((doctype, name))
	if not doc:
		raise DoesNotExistError(f"{doctype} {name} not found")
	return doc


def _get_all(doctype, filters=None, pluck=None, fields=None, order_by=None, **kw):
	if isinstance(filters, dict):
		filters = {k: (tuple(v) if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str)
					   and v[0] in ("in", "not in") else v) for k, v in filters.items()}
		filters = {k: (list(v) if isinstance(v, tuple) else v) for k, v in filters.items()}
	out = []
	for (dt, nm), doc in STORE.items():
		if dt != doctype:
			continue
		if filters and not _matches(doc, filters):
			continue
		if pluck:
			out.append(nm if pluck == "name" else doc.get(pluck))
		elif fields:
			row = frappe._dict() if hasattr(frappe, "_dict") else dict()
			row.update({f: (nm if f == "name" else doc.get(f)) for f in fields})
			out.append(row)
		else:
			out.append(doc)
	if (order_by or "").endswith("desc"):
		out.reverse()
	return out


def _log_error(title=None, message=None, **kw):
	assert title is not None, "log_error must be called with a keyword title"
	assert len(title) <= 140, f"log_error title too long: {len(title)}"
	LOGS.append((title, message))


def _throw(msg, exc=None, title=None):
	THROWN.append(msg)
	raise (exc or Exception)(msg)


def _get_cached_doc(doctype, name=None):
	if name is None:  # Single
		existing = STORE.get((doctype, doctype))
		if existing:
			return existing
		d = Doc(doctype)
		d.name = doctype
		return d
	return _get_doc(doctype, name)


CACHE_CLEARED = []
THROWN = []
MODULE_APP = {}


class _Cache:
	def delete_value(self, key):
		CACHE_CLEARED.append(key)


frappe.cache = _Cache()
frappe.clear_cache = lambda *a, **kw: CACHE_CLEARED.append("all")
class _Dict(dict):
	def __getattr__(self, k):
		try:
			return self[k]
		except KeyError:
			raise AttributeError(k)

	def __setattr__(self, k, v):
		self[k] = v


frappe._dict = _Dict
frappe.local = types.SimpleNamespace()
frappe.local.module_app = {"alphax_grc": "alphax_grc"}
frappe.local.app_modules = {"alphax_grc": ["alphax_grc"]}
frappe.get_cached_doc = _get_cached_doc
frappe.parse_json = lambda v: v
frappe.get_doc = _get_doc
frappe.get_all = _get_all
frappe.log_error = _log_error
frappe.throw = _throw
frappe.has_permission = lambda *a, **kw: True
frappe.scrub = lambda s: s.lower().replace(" ", "_").replace("-", "_")
frappe.get_module_list = lambda app: ["AlphaX GRC", "GRC Evidence Automation"]
frappe.get_module_app = lambda module: MODULE_APP.get(module)
frappe.get_app_path = lambda app, *parts: os.path.join(ROOT, app, *parts)
frappe.only_for = lambda *a, **kw: True
frappe.msgprint = lambda *a, **kw: None
frappe.publish_realtime = lambda *a, **kw: None
frappe.sendmail = lambda *a, **kw: None
frappe.whitelist = lambda *a, **kw: (lambda fn: fn)

utils = types.ModuleType("frappe.utils")
class _Now:
	def strftime(self, fmt):
		return "14 Aug 2026 09:00"

	def __str__(self):
		return "2026-08-14 09:00:00"


utils.now_datetime = lambda: _Now()
utils.nowdate = lambda: "2026-08-14"
utils.add_months = lambda d, m: f"2027-08-14"
utils.cint = lambda v: int(v or 0)
utils.today = lambda: "2026-08-15"
utils.getdate = lambda v=None: v
utils.add_days = lambda d, n: d
utils.add_years = lambda d, n: d
utils.flt = lambda v, p=None: float(v or 0)
utils.cstr = lambda v: "" if v is None else str(v)
utils.now = lambda: "2026-08-15 09:00:00"
utils.get_datetime = lambda v=None: v
utils.date_diff = lambda a, b: 0
utils.formatdate = lambda v=None, f=None: str(v)
utils.nowtime = lambda: "09:00:00"
utils.random_string = lambda n: "x" * n


class _UtilsModule(types.ModuleType):
	"""Any frappe.utils helper a controller imports resolves to a no-op.

	Keeps the stub from masking a real import failure as a missing helper.
	"""

	def __getattr__(self, name):
		if name.startswith("__"):
			raise AttributeError(name)
		return lambda *a, **kw: None


utils.__class__ = _UtilsModule
utils.nowdate = lambda: "2026-08-14"
frappe.utils = utils
frappe.utils.cint = utils.cint

perm_mod = types.ModuleType("frappe.permissions")
GRANTS = []
perm_mod.add_permission = lambda dt, role, level: GRANTS.append((dt, role))
perm_mod.update_permission_property = lambda dt, role, level, ptype, value: None

custom_mod = types.ModuleType("frappe.custom.doctype.custom_field.custom_field")


def _create_custom_fields(spec, ignore_validate=False, update=False):
	for dt, fields in spec.items():
		for f in fields:
			CUSTOM_FIELDS.append((dt, f["fieldname"], f.get("insert_after")))


custom_mod.create_custom_fields = _create_custom_fields

model_mod = types.ModuleType("frappe.model.document")
model_mod.Document = type("Document", (object,), {})

for name, mod in [
	("frappe", frappe),
	("frappe.utils", utils),
	("frappe.custom", types.ModuleType("frappe.custom")),
	("frappe.custom.doctype", types.ModuleType("frappe.custom.doctype")),
	("frappe.custom.doctype.custom_field", types.ModuleType("frappe.custom.doctype.custom_field")),
	("frappe.custom.doctype.custom_field.custom_field", custom_mod),
	("frappe.model", types.ModuleType("frappe.model")),
	("frappe.model.document", model_mod),
	("frappe.permissions", perm_mod),
]:
	sys.modules[name] = mod


# --------------------------------------------------------------------------
# Seed a fake AlphaX GRC schema
# --------------------------------------------------------------------------

def _f(*names):
	return {n: None for n in names}


# Mirrored from alphax_grc v2.2.0 (github.com/jamunachi08/alphax_grc @ a88373a).
# Select options are real, so an illegal write fails here instead of on site.
EVIDENCE_STATUS = "Draft\nCollected\nVerified\nArchived"
EVIDENCE_TYPES = "Document\nScreenshot\nLog\nConfiguration\nApproval\nOther"

META.update({
	"GRC Risk Register": {**_f("treatment_plan", "client", "within_appetite", "appetite_status",
							   "appetite_ceiling"),
						  "status": "Open\nMonitoring\nMitigated\nClosed"},
	"GRC Engagement": {**_f("client"),
					   "engagement_status": "Draft\nActive\nOn Hold\nCompleted\nCancelled"},
	"GRC Audit Finding": {"severity": "Critical\nHigh\nMedium\nLow",
						  "status": "Open\nAssigned\nIn Progress\nResolved\nVerified\nClosed"},
	"GRC Policy": {"status": "Draft\nUnder Review\nApproved\nRetired",
				   "publication_status": "Draft\nReview\nApproved\nPublished\nRetired"},
	"GRC Vendor": {**_f("vendor_name"), "status": "Active\nInactive\nBlocked\nUnder Review"},
	"GRC Client Profile": _f("client_code", "client_name"),
	"GRC Framework": _f("framework_name"),
	"GRC Control": _f("control_name", "client"),
	"GRC Evidence": {**_f("client", "related_doctype", "related_document", "evidence_title",
						  "notes", "collected_on"),
					 "status": EVIDENCE_STATUS, "evidence_type": EVIDENCE_TYPES},
	"Number Card": _f("label", "document_type", "function", "filters_json", "is_public",
					  "show_percentage_stats", "color", "type", "module", "is_standard"),
	"Onboarding Step": _f("title", "action", "reference_document", "description",
						  "validate_action", "is_single", "is_complete"),
	"Module Onboarding": _f("module", "title", "subtitle", "success_message",
							"documentation_url", "is_complete", "steps"),
	"Module Def": _f("module_name"),
	"GRC Evidence Fetcher": _f("client", "fetcher_name", "connector", "control", "check_key",
							   "schedule", "enabled", "last_run", "last_result"),
	"GRC Evidence Connector": _f("client", "connector_name", "status"),
	"GRC Evidence Run": _f("fetcher", "started_at", "finished_at", "result", "detail",
						   "evidence_record"),
	"GRC Global Policy": _f("policy_code", "policy_title", "policy_title_ar", "category",
							"source", "is_mandatory", "is_active", "purpose", "scope", "summary",
							"review_cycle_months", "default_owner_role", "acknowledgement_required",
							"display_order", "framework_mappings"),
	"GRC Pathway Settings": _f("color_theme", "allow_user_override", "show_counts",
							   "show_progress_rail", "compact_mode", "default_client"),
	"GRC Policy": {**_f("client", "policy_title", "policy_owner", "version_no",
						"effective_date", "review_due_date", "summary", "acknowledgement_required",
						"acknowledgment_required", "published_on"),
				   "policy_category": "Information Security\nPrivacy\nRisk\nCompliance\nHR\nOperations",
				   "status": "Draft\nUnder Review\nApproved\nRetired",
				   "publication_status": "Draft\nReview\nApproved\nPublished\nRetired"},
	"GRC NCA Policy Library": _f("template_code", "template_name", "template_name_ar",
								 "category", "ecc_controls", "is_active"),
	"GRC Risk Acceptance": _f("client", "risk"),
	"GRC Vendor Assessment": _f("vendor", "status"),
	"Custom HTML Block": _f("html", "style", "script", "public"),
	"GRC SAMA Subdomain": _f("code", "subdomain_title", "domain", "domain_title",
							 "control_considerations", "excluded_for_non_banks", "is_active"),
	"GRC SAMA Deliverable": {**_f("sl_no", "deliverable_title", "subdomain", "client", "is_master"),
							 "status": "Not Started\nIn Progress\nDrafted\nApproved\n"
									   "Evidence Filed\nNot Applicable"},
	"GRC SAMA Waiver": {**_f("subject", "client", "subdomain", "request_type"),
						"status": "Draft\nCISO Approval\nCommittee Approval\n"
								  "Submitted to SAMA\nApproved\nRejected\nWithdrawn"},
	"GRC SAMA Assessment": _f("client", "assessment_title", "overall_maturity", "pct_at_target"),
	"GRC Project Plan": _f("client", "plan_title", "start_date", "end_date", "pct_complete"),
	"GRC Plan Template": _f("template_name", "framework", "is_active"),
	"GRC Report Definition": _f("report_title", "definition_type", "category", "source_doctype",
								"builtin_key", "chart_type", "is_active"),
	"Workspace": _f("content", "module", "label"),
})
REPORTS = {"GRC Compliance Status", "GRC Risk Summary", "GRC Audit Findings Report",
		   "GRC ITGC Progress"}
STORE[("Module Def", "GRC Evidence Automation")] = Doc("Module Def", module_name="GRC Evidence Automation")

# Autoname rules read straight from the shipped DocType JSON.
AUTONAME = {}
for _dirpath, _dirs, _files in os.walk(
	os.path.join(ROOT, "alphax_grc", "grc_evidence_automation", "doctype")
):
	for _fn in _files:
		if _fn.endswith(".json"):
			try:
				_d = json.load(open(os.path.join(_dirpath, _fn)))
				if _d.get("name") and _d.get("autoname"):
					AUTONAME[_d["name"]] = _d["autoname"]
			except Exception:
				pass

RESULTS = []


def check(label, cond, detail=""):
	RESULTS.append((label, bool(cond), detail))


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

from alphax_grc.pathway import setup as install  # noqa: E402
from alphax_grc.grc_evidence_automation.engine import evidence_runner as er  # noqa: E402


def test_seeders_full_schema():
	LOGS.clear()
	install.seed_all()
	risk = json.load(open(os.path.join(
		ROOT, "alphax_grc/alphax_grc/doctype/grc_risk_register/grc_risk_register.json")))
	fieldnames = [f["fieldname"] for f in risk["fields"]]
	check("treatment_actions is a native DocField, not a Custom Field",
		  "treatment_actions" in fieldnames)
	check("treatment_actions sits right after treatment_plan",
		  fieldnames.index("treatment_actions") == fieldnames.index("treatment_plan") + 1)
	risk_customs = [c for c in CUSTOM_FIELDS if c[0] == "GRC Risk Register"]
	check("no Custom Field is applied to GRC Risk Register any more", not risk_customs,
		  risk_customs)
	# SAMA extends base-app doctypes, so those stay Custom Fields by design.
	sama_targets = {c[0] for c in CUSTOM_FIELDS}
	check("SAMA fields are applied to the base doctypes they extend",
		  sama_targets <= {"GRC Incident", "GRC Client Profile"}, sorted(sama_targets))
	cards = [nm for (dt, nm) in STORE if dt == "Number Card"]
	check("every number card seeds with its forced name",
		  len(cards) == len(install.NUMBER_CARDS) and "grc-card-open-risks" in cards, cards)
	check("SAMA cards are among them", "grc-card-sama-waivers" in cards, cards)
	steps = [nm for (dt, nm) in STORE if dt == "Onboarding Step"]
	check("all 10 pathway onboarding steps seeded", len(steps) == 10, steps)
	ob = STORE.get(("Module Onboarding", "GRC Pathway"))
	check("module onboarding links every seeded step", ob and len(ob.get("steps")) == len(steps))
	check("onboarding bound to own module", ob and ob.get("module") == "GRC Evidence Automation")
	# The module reclaim writes an informational entry when it repairs a row;
	# that is a success notice, not a seeding failure.
	failures = [t for t, _m in LOGS if "reclaimed" not in t]
	check("no errors logged on a complete schema", not failures, failures)


def test_seeders_are_idempotent():
	before = len(STORE)
	install.seed_all()
	check("re-running seeders creates no duplicates", len(STORE) == before, f"{before} -> {len(STORE)}")


def test_seeders_survive_missing_base_app():
	STORE.clear()
	LOGS.clear()
	CUSTOM_FIELDS.clear()
	saved = dict(META)
	for dt in list(META):
		if dt.startswith("GRC ") and dt not in ("GRC Evidence Fetcher", "GRC Evidence Connector", "GRC Evidence Run"):
			del META[dt]
	STORE[("Module Def", "GRC Evidence Automation")] = Doc("Module Def", module_name="GRC Evidence Automation")
	try:
		install.seed_all()
		check("seeders do not raise when alphax_grc is absent", True)
		check("missing base app is logged, not raised", any("not found" in t or "skipped" in t for t, _ in LOGS), [t for t, _ in LOGS])
		check("no custom field applied on a bare site", not CUSTOM_FIELDS)
	except Exception as e:
		check("seeders do not raise when alphax_grc is absent", False, repr(e))
	META.clear()
	META.update(saved)


def test_every_outcome_maps_to_a_legal_status():
	legal = set(EVIDENCE_STATUS.split("\n"))
	bad = {k: v for k, v in er.STATUS_MAP.items() if v not in legal}
	check("all 5 fetcher outcomes map to legal GRC Evidence statuses", not bad, bad)
	check("configured evidence_type is legal", er.EVIDENCE_TYPE in EVIDENCE_TYPES.split("\n"), er.EVIDENCE_TYPE)


def test_illegal_option_falls_back():
	got = er._legal_option("GRC Evidence", "status", "Requested")
	check("an illegal status falls back to a legal one", got == "Draft", got)
	kept = er._legal_option("GRC Evidence", "status", "Verified")
	check("a legal status is passed through untouched", kept == "Verified", kept)


def test_number_card_filter_sanitising():
	out = install._sanitise_filters(
		"GRC Policy",
		'[["GRC Policy","publication_status","=","Published"],["GRC Policy","policy_status","=","x"]]',
	)
	check("filters on non-existent fields are dropped",
		  out.count("publication_status") == 1 and "policy_status" not in out.replace("publication_status", ""), out)


def test_seeded_card_filters_use_real_fields():
	bad = []
	for spec in install.NUMBER_CARDS:
		kept = json.loads(install._sanitise_filters(spec["document_type"], spec["filters_json"]))
		if not kept:
			bad.append(spec["name"])
	check("every number card filter targets a real AlphaX GRC field", not bad, bad)


def test_runner_happy_path():
	STORE.clear()
	LOGS.clear()
	conn = Doc("GRC Evidence Connector", client="C1", connector_name="Azure", status="Active")
	conn.name = "CONN-00001"
	conn.insert()
	f = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="MFA on admins", connector="CONN-00001",
			control="CTRL-1", check_key="mfa_all_admins", schedule="Hourly", enabled=1)
	f.name = "FETCH-00001"
	f.insert()

	@er.register_handler("mfa_all_admins")
	def _h(connector, fetcher):
		return {"result": "Pass", "detail": {"admins": 12}}

	runs = er.run_due_fetchers("Hourly")
	check("one run logged", len(runs) == 1, runs)
	run = STORE[("GRC Evidence Run", runs[0])]
	check("run result is Pass", run.get("result") == "Pass")
	check("evidence record linked to run", bool(run.get("evidence_record")))
	ev = [d for (dt, nm), d in STORE.items() if dt == "GRC Evidence"]
	check("evidence written back to GRC Evidence", len(ev) == 1 and ev[0].get("status") == "Verified")
	legal_status = EVIDENCE_STATUS.split("\n")
	legal_types = EVIDENCE_TYPES.split("\n")
	check("evidence status is a legal AlphaX GRC option", ev[0].get("status") in legal_status, ev[0].get("status"))
	check("evidence_type is a legal AlphaX GRC option", ev[0].get("evidence_type") in legal_types, ev[0].get("evidence_type"))
	check("collected_on written as a datetime, not a date", " " in str(ev[0].get("collected_on")), ev[0].get("collected_on"))
	check("fetcher stamped with last_result", f.get("last_result") == "Pass")


def test_runner_no_handler_is_inconclusive():
	f = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="Unmapped check", connector="CONN-00001",
			control="CTRL-2", check_key="nothing_registered", schedule="Daily", enabled=1)
	f.name = "FETCH-00002"
	f.insert()
	runs = er.run_due_fetchers("Daily")
	run = STORE[("GRC Evidence Run", runs[0])]
	check("unmapped check_key returns Inconclusive, not skipped", run.get("result") == "Inconclusive")


def test_runner_isolates_failures():
	LOGS.clear()
	COMMITS["commit"] = 0

	@er.register_handler("explodes")
	def _bad(connector, fetcher):
		raise RuntimeError("upstream 500")

	bad = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="Breaks", connector="CONN-00001",
			  control="CTRL-3", check_key="explodes", schedule="Weekly", enabled=1)
	bad.name = "FETCH-00003"
	bad.insert()
	good = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="Fine", connector="CONN-00001",
			   control="CTRL-4", check_key="mfa_all_admins", schedule="Weekly", enabled=1)
	good.name = "FETCH-00004"
	good.insert()

	runs = er.run_due_fetchers("Weekly")
	check("a failing fetcher does not abort the batch", len(runs) == 2, runs)
	results = sorted(STORE[("GRC Evidence Run", r)].get("result") for r in runs)
	check("failure recorded as Fail alongside the good run", results == ["Fail", "Pass"], results)
	check("each fetcher committed independently", COMMITS["commit"] >= 2, COMMITS)
	check("traceback logged for the failure", any("fetcher failed" in t.lower() for t, _ in LOGS), [t for t, _ in LOGS])


def test_runner_handles_missing_connector():
	f = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="Orphan", connector="CONN-99999",
			control="CTRL-5", check_key="mfa_all_admins", schedule="Monthly", enabled=1)
	f.name = "FETCH-00005"
	f.insert()
	runs = er.run_due_fetchers("Monthly")
	run = STORE[("GRC Evidence Run", runs[0])]
	check("missing connector degrades to Auth Error", run.get("result") == "Auth Error")


def test_disabled_connector():
	conn = STORE[("GRC Evidence Connector", "CONN-00001")]
	conn.status = "Disabled"
	f = Doc("GRC Evidence Fetcher", client="C1", fetcher_name="Disabled conn", connector="CONN-00001",
			control="CTRL-6", check_key="mfa_all_admins", schedule="Hourly", enabled=1)
	f.name = "FETCH-00006"
	f.insert()
	runs = er.run_due_fetchers("Hourly")
	results = {STORE[("GRC Evidence Run", r)].get("result") for r in runs}
	check("disabled connector reported as Auth Error", "Auth Error" in results, results)
	conn.status = "Active"


# --------------------------------------------------------------------------
# v0.3.0 — policy library, pathway board, theming
# --------------------------------------------------------------------------

from alphax_grc.pathway import policies as pol  # noqa: E402
from alphax_grc.grc_evidence_automation.doctype.grc_global_policy.grc_global_policy import (  # noqa: E402
	GRCGlobalPolicy,
)

# Exercise the real controller logic, not a reimplementation of it.
Doc.adopt_for_client = GRCGlobalPolicy.adopt_for_client
Doc._dedupe_mappings = GRCGlobalPolicy._dedupe_mappings
from alphax_grc.pathway import board  # noqa: E402
from alphax_grc.pathway import api  # noqa: E402


def test_policy_catalogue_shape():
	codes = [r[0] for r in pol.CATALOGUE]
	check("catalogue has no duplicate policy codes", len(codes) == len(set(codes)),
		  [c for c in codes if codes.count(c) > 1])
	legal_categories = set(META["GRC Policy"]["policy_category"].split("\n"))
	bad = sorted({r[3] for r in pol.CATALOGUE} - legal_categories)
	check("every catalogue category is legal on GRC Policy", not bad, bad)
	check("catalogue covers all six categories",
		  len({r[3] for r in pol.CATALOGUE}) == len(legal_categories))
	no_map = [r[0] for r in pol.CATALOGUE if not r[9]]
	check("every policy carries at least one framework mapping", not no_map, no_map)
	check("catalogue is a meaningful baseline", len(pol.CATALOGUE) >= 40, len(pol.CATALOGUE))
	mandatory = [r for r in pol.CATALOGUE if r[5]]
	check("a mandatory baseline subset exists", 15 <= len(mandatory) <= 40, len(mandatory))


def test_policy_seeding_and_idempotency():
	STORE.clear()
	LOGS.clear()
	STORE[("Module Def", "GRC Evidence Automation")] = Doc("Module Def", module_name="GRC Evidence Automation")
	pol.seed_global_policies()
	first = len([1 for (dt, _n) in STORE if dt == "GRC Global Policy"])
	check("all catalogue policies seeded", first == len(pol.CATALOGUE), first)
	pol.seed_global_policies()
	second = len([1 for (dt, _n) in STORE if dt == "GRC Global Policy"])
	check("re-seeding creates no duplicates", first == second, f"{first} -> {second}")
	check("no errors logged while seeding policies", not LOGS, [t for t, _ in LOGS])

	sample = STORE[("GRC Global Policy", "NEO-POL-PRV-01")]
	check("seeded policy keeps its Arabic title", bool(sample.get("policy_title_ar")))
	check("seeded policy carries framework mappings", len(sample.get("framework_mappings")) >= 2)


def test_local_edits_survive_reseed():
	doc = STORE[("GRC Global Policy", "NEO-POL-ISMS-01")]
	doc.purpose = "Locally reworded purpose"
	pol.seed_global_policies()
	check("a locally edited purpose is not overwritten on re-seed",
		  STORE[("GRC Global Policy", "NEO-POL-ISMS-01")].get("purpose") == "Locally reworded purpose")


def test_nca_library_import_dedupes():
	nca = Doc("GRC NCA Policy Library", template_code="NCA-POL-MALWARE",
			  template_name="Malware Protection Policy", category="Application",
			  ecc_controls="2-3-1", is_active=1)
	nca.name = "NCA-POL-MALWARE"
	nca.insert()
	other = Doc("GRC NCA Policy Library", template_code="NCA-POL-UNIQUE",
				template_name="Some NCA-Only Template", category="Governance",
				ecc_controls="1-1-1", is_active=1)
	other.name = "NCA-POL-UNIQUE"
	other.insert()

	imported = pol.import_from_nca_library()
	check("NCA entry already in the catalogue is not duplicated", imported == 1, imported)
	check("NCA-only entry is imported", bool(STORE.get(("GRC Global Policy", "NCA-NCA-POL-UNIQUE"))))
	again = pol.import_from_nca_library()
	check("NCA import is idempotent", again == 0, again)


def test_adopt_for_client():
	client = Doc("GRC Client Profile", client_name="Wadi Marine")
	client.name = "CL-0001"
	client.insert()

	res = api.adopt_policies("CL-0001", only_mandatory=1)
	created = len(res["created"])
	mandatory = len([r for r in pol.CATALOGUE if r[5]])
	check("baseline adoption creates one GRC Policy per mandatory entry",
		  created == mandatory, f"{created} vs {mandatory}")
	check("nothing failed during adoption", not res["failed"], res["failed"])

	policy = STORE[("GRC Policy", res["created"][0])]
	legal_cat = META["GRC Policy"]["policy_category"].split("\n")
	check("adopted policy category is legal", policy.get("policy_category") in legal_cat,
		  policy.get("policy_category"))
	check("adopted policy is scoped to the client", policy.get("client") == "CL-0001")
	check("adopted policy starts as Draft", policy.get("status") == "Draft")
	check("adopted policy gets a review due date", bool(policy.get("review_due_date")))

	res2 = api.adopt_policies("CL-0001", only_mandatory=1)
	check("re-adopting skips existing policies rather than duplicating",
		  len(res2["created"]) == 0 and len(res2["skipped"]) == mandatory,
		  f"created={len(res2['created'])} skipped={len(res2['skipped'])}")


def test_pathway_stats():
	data = api.get_pathway_stats()
	labels = [s["label"] for s in data["stages"]]
	check("pathway board returns stages for the doctypes present",
		  "Policies" in labels and "Clients" in labels, labels)
	check("every stage declares a route target", all(s["route_to"] for s in data["stages"]))
	check("the reporting stage routes to a report",
		  any(s["route_type"] == "report" for s in data["stages"]))
	check("client list is offered for filtering", data["clients"][0]["label"] == "Wadi Marine")
	policies_stage = [s for s in data["stages"] if s["label"] == "Policies"][0]
	check("policy stage counts the adopted policies", policies_stage["count"] > 0,
		  policies_stage["count"])
	check("theme defaults to Ocean when unset", data["theme"] == "Ocean", data["theme"])
	check("settings are returned for the frontend",
		  set(data["settings"]) == {"allow_user_override", "show_counts", "show_progress_rail",
									"compact_mode"}, data["settings"])


def test_theme_setting_is_respected():
	settings = Doc("GRC Pathway Settings", color_theme="Monochrome (No Colour)",
				   allow_user_override=0, show_counts=1, show_progress_rail=0, compact_mode=0)
	settings.name = "GRC Pathway Settings"
	settings.insert()
	data = api.get_pathway_stats()
	check("configured theme is served to the board",
		  data["theme"] == "Monochrome (No Colour)", data["theme"])
	check("user override can be switched off", data["settings"]["allow_user_override"] == 0)
	check("progress rail can be hidden", data["settings"]["show_progress_rail"] == 0)


def test_board_themes_match_settings_options():
	import re
	css_themes = set(re.findall(r'\[data-theme="(\w+)"\]', board.BOARD_STYLE))
	js_themes = set(re.findall(r'"(\w+)": "(\w+)"', board.BOARD_SCRIPT))
	mapped = {v for _k, v in js_themes}
	check("every theme offered in the picker has CSS", mapped <= css_themes,
		  sorted(mapped - css_themes))
	check("a no-colour theme exists", "mono" in css_themes)
	check("a high-contrast theme exists", "contrast" in css_themes)

	import json as _json
	settings_json = _json.load(open(os.path.join(
		ROOT, "alphax_grc/grc_evidence_automation/doctype/"
		"grc_pathway_settings/grc_pathway_settings.json")))
	opts = [f for f in settings_json["fields"] if f["fieldname"] == "color_theme"][0]["options"].split("\n")
	from alphax_grc.pathway.board import BOARD_SCRIPT
	missing = [o for o in opts if o not in BOARD_SCRIPT]
	check("every theme in GRC Pathway Settings is handled by the board script", not missing, missing)


def test_board_seeding_and_workspace_wiring():
	ws = Doc("Workspace", label="GRC Pathway", module="GRC Evidence Automation",
			 content=json.dumps([{"type": "header", "data": {"text": "GRC Pathway"}},
								 {"type": "paragraph", "data": {"text": "..."}}]))
	ws.name = "GRC Pathway"
	ws.insert()

	board.seed_pathway_board()
	check("custom html block created", bool(STORE.get(("Custom HTML Block", "GRC Pathway Board"))))
	content = json.loads(STORE[("Workspace", "GRC Pathway")].get("content"))
	blocks = [b for b in content if b.get("type") == "custom_block"]
	check("board injected into the workspace exactly once", len(blocks) == 1, len(blocks))
	check("board sits directly under the page header", content[1]["type"] == "custom_block",
		  [b["type"] for b in content[:3]])

	board.seed_pathway_board()
	content = json.loads(STORE[("Workspace", "GRC Pathway")].get("content"))
	check("re-seeding does not stack duplicate boards",
		  len([b for b in content if b.get("type") == "custom_block"]) == 1)


def test_board_degrades_without_custom_html_block():
	saved = META.pop("Custom HTML Block")
	del STORE[("Custom HTML Block", "GRC Pathway Board")]
	board.seed_pathway_board()
	content = json.loads(STORE[("Workspace", "GRC Pathway")].get("content"))
	check("board block is removed when Custom HTML Block is unavailable",
		  not [b for b in content if b.get("type") == "custom_block"],
		  [b["type"] for b in content])
	META["Custom HTML Block"] = saved


def test_role_grants_are_guarded():
	GRANTS.clear()
	install.seed_role_permissions()
	check("no permissions granted for roles that don't exist", not GRANTS, GRANTS)
	STORE[("Role", "GRC Admin")] = Doc("Role", role_name="GRC Admin")
	META["Role"] = {}
	install.seed_role_permissions()
	check("existing roles do get granted", any(r == "GRC Admin" for _dt, r in GRANTS), GRANTS)


# --------------------------------------------------------------------------
# v0.4.0 — pathway console
# --------------------------------------------------------------------------

from alphax_grc.pathway import console  # noqa: E402


def _fresh_site():
	STORE.clear()
	LOGS.clear()
	STORE[("Module Def", "GRC Evidence Automation")] = Doc("Module Def", module_name="GRC Evidence Automation")
	c = Doc("GRC Client Profile", client_name="Wadi Marine")
	c.name = "CL-0001"
	c.insert()
	return "CL-0001"


def _add(doctype, **kw):
	d = Doc(doctype, **kw)
	d.insert()
	return d


def test_console_gates_on_prerequisites():
	client = _fresh_site()
	state = console.get_console_state(client)
	by_key = {s["key"]: s for s in state["stages"]}

	check("client stage is done once a client exists", by_key["client"]["state"] == "done",
		  by_key["client"]["state"])
	check("engagement is ready, not blocked, once client is done",
		  by_key["engagement"]["state"] == "ready", by_key["engagement"]["state"])
	check("controls are blocked before frameworks exist",
		  by_key["control"]["state"] == "blocked", by_key["control"]["state"])
	check("blocked stage names what it is waiting on",
		  by_key["control"]["blockers"] == ["Frameworks"], by_key["control"]["blockers"])
	check("risk is blocked transitively through controls",
		  by_key["risk"]["state"] == "blocked", by_key["risk"]["state"])


def test_console_unblocks_as_work_lands():
	client = _fresh_site()
	_add("GRC Engagement", client=client, engagement_status="Active")
	_add("GRC Framework", framework_name="NCA ECC-2:2024")
	_add("GRC Control", client=client, control_name="2-2-1")

	by_key = {s["key"]: s for s in console.get_console_state(client)["stages"]}
	check("engagement completes only on an Active engagement",
		  by_key["engagement"]["state"] == "done", by_key["engagement"]["state"])
	check("risk unblocks once controls exist", by_key["risk"]["state"] == "ready",
		  by_key["risk"]["state"])
	check("evidence unblocks once controls exist", by_key["evidence"]["state"] == "ready")
	check("reporting still blocked with no evidence", by_key["report"]["state"] == "blocked",
		  by_key["report"]["blockers"])


def test_console_completion_criteria_are_not_just_counts():
	client = _fresh_site()
	engagement = _add("GRC Engagement", client=client, engagement_status="Draft")
	by_key = {s["key"]: s for s in console.get_console_state(client)["stages"]}
	check("a Draft engagement is in progress, not done",
		  by_key["engagement"]["state"] == "progress", by_key["engagement"]["state"])
	check("downstream stages stay blocked behind an incomplete engagement",
		  by_key["framework"]["state"] == "blocked", by_key["framework"]["state"])

	engagement.engagement_status = "Active"
	_add("GRC Framework", framework_name="ISO 27001:2022")
	_add("GRC Control", client=client, control_name="A.5.1")
	_add("GRC Evidence", client=client, status="Collected", evidence_title="E1")
	by_key = {s["key"]: s for s in console.get_console_state(client)["stages"]}
	check("collected-but-unverified evidence is in progress, not done",
		  by_key["evidence"]["state"] == "progress", by_key["evidence"]["state"])
	check("unverified count surfaces as an attention metric",
		  any(m.get("warn") for m in by_key["evidence"]["metrics"]), by_key["evidence"]["metrics"])

	_add("GRC Evidence", client=client, status="Verified", evidence_title="E2")
	by_key = {s["key"]: s for s in console.get_console_state(client)["stages"]}
	check("evidence completes on a Verified record", by_key["evidence"]["state"] == "done",
		  by_key["evidence"]["state"])


def test_console_scopes_counts_to_the_client():
	client = _fresh_site()
	other = _add("GRC Client Profile", client_name="Other Co")
	other.name = "CL-0002"
	STORE[("GRC Client Profile", "CL-0002")] = other
	_add("GRC Risk Register", client=client, status="Open")
	_add("GRC Risk Register", client="CL-0002", status="Open")
	_add("GRC Risk Register", client="CL-0002", status="Open")

	scoped = {s["key"]: s for s in console.get_console_state(client)["stages"]}
	unscoped = {s["key"]: s for s in console.get_console_state(None)["stages"]}
	check("client filter scopes stage counts", scoped["risk"]["count"] == 1,
		  scoped["risk"]["count"])
	check("no client shows the whole site", unscoped["risk"]["count"] == 3,
		  unscoped["risk"]["count"])


def test_console_progress_and_next_step():
	client = _fresh_site()
	state = console.get_console_state(client)
	check("progress counts completed stages", state["progress"]["done"] >= 1, state["progress"])
	check("progress reports a percentage", 0 <= state["progress"]["pct"] <= 100,
		  state["progress"]["pct"])
	check("console names the next actionable stage",
		  state["progress"]["next"] == "Engagement", state["progress"]["next"])


def test_console_actions_are_real_and_reachable():
	client = _fresh_site()
	stages = console.get_console_state(client)["stages"]
	bad_targets = []
	for stage in stages:
		for action in stage["actions"]:
			if action["type"] == "report":
				if action["target"] not in REPORTS:
					bad_targets.append(action["target"])
			elif action["type"] in ("new", "list"):
				if action["target"] not in META:
					bad_targets.append(action["target"])
	check("every offered action points at something that exists", not bad_targets, bad_targets)
	check("every stage offers at least one action", all(s["actions"] for s in stages),
		  [s["key"] for s in stages if not s["actions"]])

	policy_stage = [s for s in stages if s["key"] == "policy"][0]
	check("policy stage offers library adoption as its first action",
		  policy_stage["actions"][0]["type"] == "adopt", policy_stage["actions"][0])


def test_console_drops_missing_doctypes():
	client = _fresh_site()
	saved = META.pop("GRC Vendor")
	stages = console.get_console_state(client)["stages"]
	check("a missing doctype drops its stage rather than breaking the console",
		  not [s for s in stages if s["key"] == "vendor"], [s["key"] for s in stages])
	check("remaining stages still gate correctly",
		  {s["key"] for s in stages} >= {"client", "engagement", "control"})
	META["GRC Vendor"] = saved


def test_domain_map_shape():
	client = _fresh_site()
	_add("GRC Risk Register", client=client, status="Open")
	pillars = console.get_console_state(client)["pillars"]
	names = [p["pillar"] for p in pillars]
	check("domain map exposes the GRC pillars",
		  names == ["Governance", "Risk", "Compliance", "Automation"], names)
	check("every pillar has at least one reachable item", all(p["items"] for p in pillars))
	risk_items = {i["label"]: i for i in [p for p in pillars if p["pillar"] == "Risk"][0]["items"]}
	check("map items carry live counts", risk_items["Risk register"]["count"] == 1,
		  risk_items["Risk register"])
	check("client-scoped map items are flagged as scoped",
		  risk_items["Risk register"]["scoped"] == 1)


def test_controller_class_names_match_frappe_convention():
	import re as _re
	roots = [
		os.path.join(ROOT, "alphax_grc/grc_evidence_automation/doctype"),
		os.path.join(ROOT, "alphax_grc/alphax_grc/doctype"),
	]
	bad = []
	folders = [(r, f) for r in roots for f in sorted(os.listdir(r))
			   if os.path.isdir(os.path.join(r, f))
			   and os.path.exists(os.path.join(r, f, f + ".json"))]
	for root, folder in folders:
		folder_path = os.path.join(root, folder)
		if not os.path.isdir(folder_path):
			continue
		d = json.load(open(os.path.join(folder_path, f"{folder}.json")))
		py = os.path.join(folder_path, f"{folder}.py")
		if not os.path.exists(py):
			bad.append(f"{d['name']}: no controller module")
			continue
		expected = d["name"].replace(" ", "").replace("-", "")
		classes = _re.findall(r"^class (\w+)", open(py).read(), _re.M)
		if expected not in classes:
			bad.append(f"{d['name']}: expected {expected}, found {classes}")
	check(f"all {len(folders)} doctypes across both modules have correctly-named controllers",
		  not bad, bad[:6])


def test_retires_stale_module_defs():
	"""The v2.3.1 install failure: a Module Def left pointing at the retired app."""
	STORE.clear()
	CACHE_CLEARED.clear()

	stale = Doc("Module Def", module_name="GRC Evidence Automation",
				app_name="alphax_grc_evidence_automation")
	stale.name = "GRC Evidence Automation"
	stale.insert()
	own = Doc("Module Def", module_name="AlphaX GRC", app_name="alphax_grc")
	own.name = "AlphaX GRC"
	own.insert()
	META["Module Def"] = _f("module_name", "app_name")

	inst = _load_reclaim()
	count = inst.retire_legacy_module_defs()

	check("stale module def is found and reclaimed", count == 1, count)
	check("module now resolves to alphax_grc",
		  STORE[("Module Def", "GRC Evidence Automation")].get("app_name") == "alphax_grc",
		  STORE[("Module Def", "GRC Evidence Automation")].get("app_name"))
	check("this app's own module def is left alone",
		  STORE[("Module Def", "AlphaX GRC")].get("app_name") == "alphax_grc")
	# Site caches get cleared, but frappe.local is left alone deliberately:
	# module -> app resolution comes from modules.txt on disk, not from the
	# Module Def rows this repairs, so there is nothing to invalidate in-process.
	check("site cache is cleared after the repair", "all" in CACHE_CLEARED, CACHE_CLEARED)

	check("reclaim is idempotent", inst.retire_legacy_module_defs() == 0)

	# v2.3.3: the reclaim used to delattr frappe.local.module_app, which is a
	# werkzeug Local — every later read then raised AttributeError and the
	# install died at add_module_defs -> frappe.new_doc("Module Def").
	check("frappe.local.module_app survives the reclaim",
		  getattr(frappe.local, "module_app", "GONE") != "GONE",
		  "module_app was deleted from frappe.local")
	check("frappe.local.app_modules survives the reclaim",
		  getattr(frappe.local, "app_modules", "GONE") != "GONE")
	src = open(os.path.join(ROOT, "alphax_grc/install.py")).read()
	check("install.py never delattrs frappe.local", "delattr(frappe.local" not in src)


def test_module_conflict_is_reported_legibly():
	"""The real v2.3.0/2.3.1 failure: the retired app still on the bench."""
	inst = _load_reclaim()
	THROWN.clear()

	# both apps on the bench declare 'GRC Evidence Automation'; last one wins
	MODULE_APP["grc_evidence_automation"] = "alphax_grc_evidence_automation"
	MODULE_APP["alphax_grc"] = "alphax_grc"

	try:
		inst.assert_module_ownership()
		raised = False
	except Exception:
		raised = True

	check("a conflicting bench app aborts the install", raised)
	msg = THROWN[0] if THROWN else ""
	check("the error names the conflicting module",
		  "GRC Evidence Automation" in msg, msg[:80])
	check("the error names the offending app",
		  "alphax_grc_evidence_automation" in msg, msg[:80])
	check("the error says what to actually do",
		  "bench group" in msg and "Remove" in msg, msg[:120])

	# once the retired app is off the bench, install proceeds
	THROWN.clear()
	MODULE_APP["grc_evidence_automation"] = "alphax_grc"
	try:
		inst.assert_module_ownership()
		clean = True
	except Exception:
		clean = False
	check("no conflict once the retired app is removed", clean and not THROWN)


def _load_reclaim():
	"""Exec just the reclaim function out of the real install.py.

	install.py pulls in the whole base app at import time; this keeps the test
	honest (it runs the shipped source) without stubbing all of it.
	"""
	import ast as _ast
	import types as _types
	src = open(os.path.join(ROOT, "alphax_grc/install.py")).read()
	tree = _ast.parse(src)
	wanted = [
		n for n in tree.body
		if (isinstance(n, _ast.FunctionDef)
			and n.name in ("retire_legacy_module_defs", "assert_module_ownership"))
		or (isinstance(n, _ast.Assign) and getattr(n.targets[0], "id", "") == "RETIRED_APPS")
	]
	mod = _types.ModuleType("reclaim")
	mod.frappe = frappe
	exec(compile(_ast.Module(body=wanted, type_ignores=[]), "install.py", "exec"), mod.__dict__)
	return mod


def main():
	for fn in [
		test_seeders_full_schema,
		test_seeders_are_idempotent,
		test_seeders_survive_missing_base_app,
		test_every_outcome_maps_to_a_legal_status,
		test_illegal_option_falls_back,
		test_number_card_filter_sanitising,
		test_seeded_card_filters_use_real_fields,
		test_runner_happy_path,
		test_runner_no_handler_is_inconclusive,
		test_runner_isolates_failures,
		test_runner_handles_missing_connector,
		test_disabled_connector,
		test_policy_catalogue_shape,
		test_policy_seeding_and_idempotency,
		test_local_edits_survive_reseed,
		test_nca_library_import_dedupes,
		test_adopt_for_client,
		test_pathway_stats,
		test_theme_setting_is_respected,
		test_board_themes_match_settings_options,
		test_board_seeding_and_workspace_wiring,
		test_board_degrades_without_custom_html_block,
		test_role_grants_are_guarded,
		test_controller_class_names_match_frappe_convention,
		test_console_gates_on_prerequisites,
		test_console_unblocks_as_work_lands,
		test_console_completion_criteria_are_not_just_counts,
		test_console_scopes_counts_to_the_client,
		test_console_progress_and_next_step,
		test_console_actions_are_real_and_reachable,
		test_console_drops_missing_doctypes,
		test_domain_map_shape,
		test_retires_stale_module_defs,
		test_module_conflict_is_reported_legibly,
	]:
		try:
			fn()
		except Exception as e:
			check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")

	passed = sum(1 for _, ok, _ in RESULTS if ok)
	for label, ok, detail in RESULTS:
		print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
	print(f"\n{passed}/{len(RESULTS)} checks passed")
	return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
	sys.exit(main())
