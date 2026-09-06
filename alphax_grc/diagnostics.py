# Copyright (c) 2026, Neotec Integrated Solutions
"""
Live self-diagnosis for AlphaX GRC.

Answers one question: what exactly is stopping this app from working on this
site right now? Every check reports BLOCKER (install/runtime will fail),
WARNING (works, but wrong), or OK, and every failure carries the fix.

Run it from the bench:

    bench --site <site> execute alphax_grc.diagnostics.preflight

or from the desk (System Manager only):

    /api/method/alphax_grc.diagnostics.run_diagnostics

The checks are ordered by how early they bite, so the first BLOCKER is the
one to fix.
"""

from __future__ import annotations

import importlib
import json
import os

import frappe

APP = "alphax_grc"
OUR_MODULES = ("AlphaX GRC", "GRC Evidence Automation")
RETIRED_APPS = ("alphax_grc_evidence_automation",)

BLOCKER = "BLOCKER"
WARNING = "WARNING"
OK = "OK"


def _r(level, check, detail, fix=""):
	return {"level": level, "check": check, "detail": detail, "fix": fix}


# --------------------------------------------------------------------------
# 1. Is another app on the bench claiming our modules?
# --------------------------------------------------------------------------


def check_module_ownership():
	results = []
	for module in OUR_MODULES:
		try:
			owner = frappe.get_module_app(frappe.scrub(module))
		except Exception:
			owner = None

		if owner == APP:
			results.append(_r(OK, "module ownership", f"'{module}' resolves to {APP}"))
		elif owner:
			results.append(_r(
				BLOCKER, "module ownership",
				f"'{module}' resolves to app '{owner}', not {APP}",
				f"Another app on this bench declares the same module in its modules.txt. "
				f"Frappe builds the map from sites/apps.txt and last app wins, so doctype "
				f"sync imports controllers from '{owner}'. Remove '{owner}' from the bench "
				f"group and deploy again.",
			))
		else:
			results.append(_r(
				BLOCKER, "module ownership",
				f"'{module}' resolves to no app at all",
				"During a web request Frappe builds this map from the site's installed_apps. "
				f"If {APP} is not installed on this site, every document in it returns "
				"'Module not found'. Finish installing the app.",
			))
	return results


# --------------------------------------------------------------------------
# 2. Is the app actually registered as installed?
# --------------------------------------------------------------------------


def check_installed():
	installed = frappe.get_installed_apps()
	if APP in installed:
		return [_r(OK, "app registration", f"{APP} is in installed_apps")]

	doctype_rows = frappe.db.count("DocType", {"module": ["in", list(OUR_MODULES)]})
	if doctype_rows:
		return [_r(
			BLOCKER, "app registration",
			f"{APP} is NOT in installed_apps, but {doctype_rows} of its DocTypes are in the "
			"database",
			"A previous install died inside sync_for. install_app() calls "
			"add_to_installed_apps() only after sync completes, so the doctypes landed and "
			"the app was never registered. Re-run the install and let it finish; do not "
			"hand-edit installed_apps, or after_install and the patch log will be skipped.",
		)]
	return [_r(
		BLOCKER, "app registration",
		f"{APP} is not installed on this site",
		f"bench --site {frappe.local.site} install-app {APP}",
	)]


# --------------------------------------------------------------------------
# 3. Module Def rows left behind by a retired app
# --------------------------------------------------------------------------


def check_module_defs():
	results = []
	stale = frappe.get_all(
		"Module Def", filters={"app_name": ["in", list(RETIRED_APPS)]},
		fields=["name", "app_name"],
	)
	if stale:
		results.append(_r(
			WARNING, "module def records",
			", ".join(f"'{r.name}' still owned by '{r.app_name}'" for r in stale),
			"Cosmetic for module resolution (that comes from modules.txt), but it skews desk "
			"metadata. before_install repairs this automatically on the next install.",
		))

	for module in OUR_MODULES:
		if not frappe.db.exists("Module Def", module):
			results.append(_r(
				WARNING, "module def records", f"no Module Def row for '{module}'",
				"add_module_defs() creates these during install; a missing row means the "
				"install did not reach that step.",
			))

	if not results:
		results.append(_r(OK, "module def records", "all module defs point at this app"))
	return results


# --------------------------------------------------------------------------
# 4. Can every shipped DocType's controller actually be imported?
# --------------------------------------------------------------------------


def check_controllers():
	"""The failure mode that broke two installs, checked directly."""
	broken, missing_class = [], []
	checked = 0

	app_path = frappe.get_app_path(APP)
	for module in OUR_MODULES:
		folder = os.path.join(app_path, frappe.scrub(module), "doctype")
		if not os.path.isdir(folder):
			continue
		for name in sorted(os.listdir(folder)):
			json_path = os.path.join(folder, name, f"{name}.json")
			if not os.path.exists(json_path):
				continue
			with open(json_path) as f:
				doctype = json.load(f).get("name")
			if not doctype:
				continue
			checked += 1

			dotted = f"{APP}.{frappe.scrub(module)}.doctype.{name}.{name}"
			try:
				mod = importlib.import_module(dotted)
			except Exception as e:
				broken.append(f"{doctype}: {e}")
				continue

			expected = doctype.replace(" ", "").replace("-", "")
			if not hasattr(mod, expected):
				missing_class.append(f"{doctype}: {name}.py has no class {expected}")

	results = []
	if broken:
		results.append(_r(
			BLOCKER, "doctype controllers",
			f"{len(broken)} controller module(s) will not import: " + "; ".join(broken[:5]),
			"DocType sync imports this module on every install and migrate, so it aborts "
			"part-way. Usually a missing <name>.py in the doctype folder.",
		))
	if missing_class:
		results.append(_r(
			BLOCKER, "doctype controllers",
			f"{len(missing_class)} controller(s) lack the expected class: "
			+ "; ".join(missing_class[:5]),
			"get_controller() derives the class name as "
			"doctype.replace(' ', '').replace('-', ''), so 'GRC Evidence Run' needs "
			"GRCEvidenceRun, not GrcEvidenceRun. Records of these types raise ImportError "
			"when opened.",
		))
	if not results:
		results.append(_r(OK, "doctype controllers", f"all {checked} controllers import cleanly"))
	return results


# --------------------------------------------------------------------------
# 5. DocType rows with no file behind them
# --------------------------------------------------------------------------


def check_orphan_doctypes():
	app_path = frappe.get_app_path(APP)
	on_disk = set()
	for module in OUR_MODULES:
		folder = os.path.join(app_path, frappe.scrub(module), "doctype")
		if not os.path.isdir(folder):
			continue
		for name in os.listdir(folder):
			json_path = os.path.join(folder, name, f"{name}.json")
			if os.path.exists(json_path):
				with open(json_path) as f:
					on_disk.add(json.load(f).get("name"))

	in_db = set(frappe.get_all("DocType", filters={"module": ["in", list(OUR_MODULES)]}, pluck="name"))
	orphans = sorted(in_db - on_disk)

	if orphans:
		return [_r(
			WARNING, "orphan doctypes",
			f"{len(orphans)} DocType(s) in the database have no file in this app: "
			+ ", ".join(orphans[:8]),
			"Left over from an older version or a partial install. They still render in the "
			"desk and will error on open. Delete them once you have confirmed they hold no "
			"data you need.",
		)]
	return [_r(OK, "orphan doctypes", "every DocType row has a file behind it")]


# --------------------------------------------------------------------------
# 6. Roles that permissions depend on
# --------------------------------------------------------------------------


def check_roles():
	needed = set(frappe.get_all(
		"DocPerm",
		filters={"parent": ["in", frappe.get_all(
			"DocType", filters={"module": ["in", list(OUR_MODULES)]}, pluck="name")]},
		pluck="role",
	))
	missing = sorted(r for r in needed if r and not frappe.db.exists("Role", r))
	if missing:
		return [_r(
			BLOCKER, "roles", "permissions reference roles that do not exist: " + ", ".join(missing),
			"before_install -> create_roles() should create these. A missing role makes "
			"DocType sync fail on link validation.",
		)]
	return [_r(OK, "roles", f"all {len(needed)} referenced roles exist")]


# --------------------------------------------------------------------------
# 7. Did the seeders actually run?
# --------------------------------------------------------------------------


def check_seed_data():
	results = []
	expectations = [
		("GRC Global Policy", 40, "pathway policy library",
		 "alphax_grc.pathway.setup.seed_all"),
		("GRC NCA Policy Library", 30, "NCA policy templates",
		 "alphax_grc.install.bootstrap_grc"),
		("GRC Framework", 1, "default frameworks", "alphax_grc.install.bootstrap_grc"),
		("Role", 1, "GRC roles", "alphax_grc.install.create_roles"),
	]

	for doctype, minimum, label, seeder in expectations:
		if not frappe.db.exists("DocType", doctype):
			results.append(_r(WARNING, "seed data", f"{doctype} does not exist"))
			continue
		count = frappe.db.count(doctype)
		if count >= minimum:
			results.append(_r(OK, "seed data", f"{label}: {count} record(s)"))
		else:
			results.append(_r(
				WARNING, "seed data", f"{label}: only {count} record(s), expected {minimum}+",
				f"{seeder} either did not run or a step failed. bootstrap_grc() swallows "
				"failing steps, so check the Error Log for the seeder's own entry, then "
				"re-run: bench --site <site> migrate",
			))

	if frappe.db.exists("DocType", "Workspace"):
		if frappe.db.exists("Workspace", "GRC Pathway"):
			results.append(_r(OK, "seed data", "GRC Pathway workspace present"))
		else:
			results.append(_r(WARNING, "seed data", "GRC Pathway workspace missing",
							  "bench --site <site> migrate re-imports it from disk."))

	return results


# --------------------------------------------------------------------------
# 8. Background jobs
# --------------------------------------------------------------------------


def check_scheduler():
	results = []
	if frappe.utils.cint(frappe.db.get_single_value("System Settings", "enable_scheduler")):
		results.append(_r(OK, "scheduler", "enabled"))
	else:
		results.append(_r(
			WARNING, "scheduler", "disabled on this site",
			"Evidence fetchers and the GRC notification jobs will not run. Enable it in "
			"System Settings.",
		))

	if frappe.db.exists("DocType", "GRC Evidence Fetcher"):
		enabled = frappe.db.count("GRC Evidence Fetcher", {"enabled": 1})
		results.append(_r(OK, "scheduler", f"{enabled} evidence fetcher(s) enabled"))
	return results


CHECKS = [
	check_module_ownership,
	check_installed,
	check_module_defs,
	check_controllers,
	check_orphan_doctypes,
	check_roles,
	check_seed_data,
	check_scheduler,
]


def collect() -> list[dict]:
	results = []
	for check in CHECKS:
		try:
			results.extend(check())
		except Exception:
			results.append(_r(
				WARNING, check.__name__, "the check itself failed",
				frappe.get_traceback(),
			))
	return results


def preflight():
	"""Console entry point. Prints a readable report and returns the results."""
	results = collect()
	blockers = [r for r in results if r["level"] == BLOCKER]
	warnings = [r for r in results if r["level"] == WARNING]

	print("\n" + "=" * 72)
	print(f"AlphaX GRC preflight  —  site: {frappe.local.site}")
	print("=" * 72)

	for r in results:
		mark = {BLOCKER: "[X]", WARNING: "[!]", OK: "[.]"}[r["level"]]
		print(f"{mark} {r['check']}: {r['detail']}")
		if r["fix"] and r["level"] != OK:
			for line in _wrap(r["fix"]):
				print(f"      {line}")

	print("-" * 72)
	if blockers:
		print(f"{len(blockers)} blocker(s), {len(warnings)} warning(s).")
		print(f"\nSTOPPER: {blockers[0]['detail']}")
		print(f"FIX:     {blockers[0]['fix']}")
	else:
		print(f"No blockers. {len(warnings)} warning(s).")
	print("=" * 72 + "\n")

	return results


def _wrap(text: str, width: int = 66):
	words, line, out = text.split(), "", []
	for word in words:
		if len(line) + len(word) + 1 > width:
			out.append(line)
			line = word
		else:
			line = f"{line} {word}".strip()
	if line:
		out.append(line)
	return out


@frappe.whitelist()
def run_diagnostics() -> dict:
	"""Desk endpoint — for when bench console isn't available."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only a System Manager can run diagnostics.", frappe.PermissionError)

	results = collect()
	blockers = [r for r in results if r["level"] == BLOCKER]
	return {
		"site": frappe.local.site,
		"version": frappe.get_attr("alphax_grc.__version__"),
		"results": results,
		"blockers": len(blockers),
		"warnings": len([r for r in results if r["level"] == WARNING]),
		"stopper": blockers[0] if blockers else None,
	}
