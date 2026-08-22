#!/usr/bin/env python3
"""
verify_tree.py — offline structural guard for alphax_grc_evidence_automation.

Run before every build/push. Catches the failure classes that only surface
as a red X on Frappe Cloud twenty minutes later:

  1. flit cannot build without __version__ / README.md
  2. hooks.py / __init__.py version drift
  3. fixtures re-introduced (this app is code-seeded on purpose)
  4. missing patches.txt or frappe-dependencies in pyproject.toml
  5. module folder vs modules.txt mismatch
  6. doctype folder name vs JSON name/module mismatch
  7. workspace content blocks referencing shortcuts/cards that
     aren't in the workspace child tables (renders blank)
  8. hook targets that don't resolve to a real module path
  9. frappe.log_error() called with a positional title, or a title
     literal over 140 chars
 10. reserved Document attribute shadowing on controllers

Usage:  python3 verify_tree.py
Exit 0 = clean, 1 = at least one failure.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = "alphax_grc"
APP_DIR = os.path.join(ROOT, APP)

RESERVED_DOC_ATTRS = {
	"name", "doctype", "owner", "creation", "modified", "modified_by", "docstatus",
	"parent", "parentfield", "parenttype", "idx", "save", "insert", "delete",
	"submit", "cancel", "load_from_db", "db_insert", "db_update", "get", "set",
	"update", "reload", "run_method", "meta", "flags",
}

PAGES: set = set()
NEW_MODULE = "GRC Evidence Automation"
failures: list[str] = []
warnings: list[str] = []


def fail(msg: str):
	failures.append(msg)


def fail_for(module: str, msg: str):
	"""Hard failure inside the new module, warning in pre-existing code."""
	(fail if module == NEW_MODULE else warn)(msg)


def warn(msg: str):
	warnings.append(msg)


def read(path: str) -> str:
	with open(path, encoding="utf-8") as f:
		return f.read()


# --- 1 & 2: packaging + version ------------------------------------------


def check_packaging():
	init_path = os.path.join(APP_DIR, "__init__.py")
	init_src = read(init_path)
	m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_src, re.M)
	if not m:
		fail(f"{APP}/__init__.py has no __version__ — flit build will fail on Frappe Cloud")
		version = None
	else:
		version = m.group(1)

	pyproject = read(os.path.join(ROOT, "pyproject.toml"))

	readme_m = re.search(r'^readme\s*=\s*"([^"]+)"', pyproject, re.M)
	if readme_m and not os.path.exists(os.path.join(ROOT, readme_m.group(1))):
		fail(f"pyproject.toml points at {readme_m.group(1)} but that file is missing — flit will fail")

	if "[tool.bench.frappe-dependencies]" not in pyproject:
		fail("pyproject.toml is missing [tool.bench.frappe-dependencies] — Frappe Cloud requires it")

	if not os.path.exists(os.path.join(APP_DIR, "patches.txt")):
		fail(f"{APP}/patches.txt is missing — bench migrate expects it")

	hooks = read(os.path.join(APP_DIR, "hooks.py"))
	hv = re.search(r'^app_version\s*=\s*["\']([^"\']+)["\']', hooks, re.M)
	if hv and version and hv.group(1) != version:
		fail(f"version drift: __init__.py={version} but hooks.py app_version={hv.group(1)}")

	return version


# --- 3: no fixtures -------------------------------------------------------


def check_no_fixtures():
	"""Seeding is code-driven. An empty fixtures list is fine — this app ships
	an intentionally empty grc_pages.json to overwrite stale files on disk."""
	hooks = read(os.path.join(APP_DIR, "hooks.py"))
	m = re.search(r"^fixtures\s*=\s*(.+)$", hooks, re.M)
	if m and m.group(1).strip() not in ("[]", "[]  # noqa"):
		if not m.group(1).lstrip().startswith("[]"):
			fail("hooks.py declares fixtures — this app seeds in code (see pathway/setup.py)")

	fixtures_dir = os.path.join(APP_DIR, "fixtures")
	if not os.path.isdir(fixtures_dir):
		return
	for fn in sorted(os.listdir(fixtures_dir)):
		if not fn.endswith(".json"):
			continue
		path = os.path.join(fixtures_dir, fn)
		try:
			data = json.loads(read(path))
		except Exception:
			fail(f"fixtures/{fn} is not valid JSON")
			continue
		if not data:
			continue
		missing = [i for i, row in enumerate(data) if isinstance(row, dict) and "name" not in row]
		if missing:
			fail(f"fixtures/{fn}: {len(missing)} record(s) have no 'name' key — migrate raises KeyError")
		else:
			warn(f"fixtures/{fn} ships {len(data)} record(s) — prefer a code seeder")


# --- 5 & 6: modules and doctypes -----------------------------------------


def module_folder(module_name: str) -> str:
	return module_name.lower().replace(" ", "_").replace("-", "_")


def check_modules():
	modules = [m.strip() for m in read(os.path.join(APP_DIR, "modules.txt")).splitlines() if m.strip()]
	if not modules:
		fail("modules.txt is empty")
	for module in modules:
		folder = os.path.join(APP_DIR, module_folder(module))
		if not os.path.isdir(folder):
			fail(f"modules.txt lists '{module}' but folder {module_folder(module)}/ does not exist")
	return modules


def check_doctypes(modules: list[str]):
	all_doctypes: dict = {}
	for module in modules:
		dt_root = os.path.join(APP_DIR, module_folder(module), "doctype")
		if not os.path.isdir(dt_root):
			continue
		for folder in sorted(os.listdir(dt_root)):
			folder_path = os.path.join(dt_root, folder)
			if not os.path.isdir(folder_path) or folder.startswith("__"):
				continue

			json_path = os.path.join(folder_path, f"{folder}.json")
			if not os.path.exists(json_path):
				fail(f"doctype folder {folder}/ has no {folder}.json")
				continue
			if not os.path.exists(os.path.join(folder_path, "__init__.py")):
				fail(f"doctype folder {folder}/ has no __init__.py")

			d = json.loads(read(json_path))
			expected_folder = d["name"].lower().replace(" ", "_").replace("-", "_")
			if expected_folder != folder:
				fail(f"doctype '{d['name']}' lives in folder {folder}/ (expected {expected_folder}/)")
			if d.get("module") != module:
				fail(f"doctype '{d['name']}' declares module '{d.get('module')}', folder says '{module}'")
			if not d.get("istable") and not d.get("issingle") and not d.get("autoname"):
				warn(f"doctype '{d['name']}' has no autoname — Frappe will fall back to hash names")

			# Child tables inherit permissions from their parent; they must not
			# declare their own. Everything else needs System Manager.
			if d.get("istable"):
				if d.get("permissions"):
					fail_for(module, f"child doctype '{d['name']}' declares its own permissions block")
			elif not d.get("permissions"):
				fail(f"doctype '{d['name']}' has no permissions block")
			elif not any(p.get("role") == "System Manager" for p in d["permissions"]):
				warn(f"doctype '{d['name']}' has no System Manager permission")

			# A DocField named like a framework column shares that column: the
			# field's value overwrites the record's real owner/creation/etc.
			FRAMEWORK_COLUMNS = {"owner", "modified_by", "creation", "modified", "docstatus", "idx",
								 "parent", "parentfield", "parenttype", "name"}
			for f in d.get("fields", []):
				fn = f.get("fieldname")
				if fn in FRAMEWORK_COLUMNS and f.get("fieldtype") not in ("Section Break", "Column Break"):
					fail_for(
						module,
						f"doctype '{d['name']}': field '{fn}' collides with the framework column "
						f"of the same name — writing it overwrites the record's real {fn}"
					)

			# A Column Break with a label renders that label as stray text on
			# the form ("Cb Head"). Section Breaks may be labelled; column
			# breaks may not.
			for f in d.get("fields", []):
				if f.get("fieldtype") == "Column Break" and f.get("label"):
					fail_for(
						module,
						f"doctype '{d['name']}': column break '{f.get('fieldname')}' has a label "
						f"('{f.get('label')}') — it will render as stray text on the form"
					)
				if f.get("fieldtype") == "Section Break" and (f.get("label") or "").lower().replace(" ", "").startswith("sec"):
					warn(
						f"doctype '{d['name']}': section break '{f.get('fieldname')}' looks like an "
						f"auto-derived label ('{f.get('label')}')"
					)

			field_order = d.get("field_order")
			if field_order:
				declared = [f["fieldname"] for f in d.get("fields", []) if f.get("fieldname")]
				if set(field_order) != set(declared):
					warn(
						f"doctype '{d['name']}': field_order lists {len(field_order)} of "
						f"{len(declared)} fields — the rest are appended in file order"
					)

			for perm in d.get("permissions", []):
				if perm.get("role") not in ("System Manager", "All"):
					fail_for(module,
						f"doctype '{d['name']}' ships a DocPerm for role '{perm.get('role')}' — "
						"a role that doesn't exist yet fails DocType sync; grant it in seed_role_permissions() instead"
					)

			all_doctypes[d["name"]] = d

			py_path = os.path.join(folder_path, f"{folder}.py")
			check_controller_module(folder_path, folder, d)
			if os.path.exists(py_path):
				check_controller(py_path, d)

	check_table_targets(all_doctypes)


def check_table_targets(all_doctypes: dict):
	"""A Table field pointing at a child doctype we don't ship is a sync failure."""
	for name, d in all_doctypes.items():
		for f in d.get("fields", []):
			if f.get("fieldtype") not in ("Table", "Table MultiSelect"):
				continue
			target = f.get("options")
			if not target:
				fail(f"doctype '{name}': Table field '{f.get('fieldname')}' has no options")
			elif target in all_doctypes and not all_doctypes[target].get("istable"):
				fail(f"doctype '{name}': Table field '{f.get('fieldname')}' points at '{target}', which is not a child table")


def check_controller_module(folder_path: str, folder: str, d: dict):
	"""Every DocType needs a controller module with an exactly-named class.

	Frappe imports `<app>.<module>.doctype.<folder>.<folder>` on every
	DocType sync, and `get_controller` then looks for a class named
	doctype.replace(" ", "").replace("-", "") — so "GRC Evidence Run" must be
	`GRCEvidenceRun`, not `GrcEvidenceRun`. Both failures are install-time
	ImportErrors, and child tables are not exempt.
	"""
	py_path = os.path.join(folder_path, f"{folder}.py")
	if not os.path.exists(py_path):
		fail(
			f"doctype '{d['name']}' has no controller {folder}/{folder}.py — "
			"bench install-app aborts with 'Module import failed'"
		)
		return

	expected = d["name"].replace(" ", "").replace("-", "")
	classes = [
		node.name for node in ast.walk(ast.parse(read(py_path)))
		if isinstance(node, ast.ClassDef)
	]
	if expected not in classes:
		fail(
			f"doctype '{d['name']}': {folder}.py must define `class {expected}` "
			f"(found: {', '.join(classes) or 'none'}) — get_controller derives the "
			"class name from the doctype and raises ImportError otherwise"
		)


def check_controller(py_path: str, d: dict):
	tree = ast.parse(read(py_path))
	for node in ast.walk(tree):
		if isinstance(node, ast.ClassDef):
			for item in node.body:
				if isinstance(item, ast.FunctionDef) and item.name in RESERVED_DOC_ATTRS:
					fail(f"{os.path.basename(py_path)}: method '{item.name}' shadows a Document attribute")


# --- 7: workspace integrity ----------------------------------------------


def check_workspaces(modules: list[str]):
	for module in modules:
		ws_root = os.path.join(APP_DIR, module_folder(module), "workspace")
		if not os.path.isdir(ws_root):
			continue
		for folder in sorted(os.listdir(ws_root)):
			path = os.path.join(ws_root, folder, f"{folder}.json")
			if not os.path.exists(path):
				continue
			w = json.loads(read(path))
			if w.get("module") != module:
				fail(f"workspace '{w.get('name')}' declares module '{w.get('module')}', folder says '{module}'")

			for shortcut in w.get("shortcuts", []):
				if shortcut.get("type") == "Page" and shortcut.get("link_to") not in PAGES:
					fail(
						f"workspace '{w.get('name')}': shortcut points at page "
						f"'{shortcut.get('link_to')}', which this app does not ship"
					)

			content = json.loads(w.get("content") or "[]")
			declared_shortcuts = {s.get("label") for s in w.get("shortcuts", [])}
			declared_cards = {c.get("label") for c in w.get("number_cards", [])}

			for block in content:
				data = block.get("data", {})
				if block.get("type") == "shortcut":
					label = data.get("shortcut_name")
					if label not in declared_shortcuts:
						fail(
							f"workspace '{w.get('name')}': shortcut block '{label}' "
							"is not in the shortcuts table — it renders blank"
						)
				elif block.get("type") == "number_card":
					label = data.get("number_card_name")
					if label not in declared_cards:
						fail(
							f"workspace '{w.get('name')}': number_card block '{label}' "
							"is not in the number_cards table — it renders blank"
						)


# --- 8: hook targets resolve ---------------------------------------------


def check_pages(modules: list[str]) -> set:
	"""Page folder/name/module must line up, and the JS controller must exist."""
	page_names = set()
	for module in modules:  # noqa: B007
		root = os.path.join(APP_DIR, module_folder(module), "page")
		if not os.path.isdir(root):
			continue
		for folder in sorted(os.listdir(root)):
			folder_path = os.path.join(root, folder)
			if not os.path.isdir(folder_path) or folder.startswith("__"):
				continue

			json_path = os.path.join(folder_path, f"{folder}.json")
			if not os.path.exists(json_path):
				fail(f"page folder {folder}/ has no {folder}.json")
				continue
			if not os.path.exists(os.path.join(folder_path, "__init__.py")):
				fail(f"page folder {folder}/ has no __init__.py")
			if not os.path.exists(os.path.join(folder_path, f"{folder}.js")):
				fail(f"page '{folder}' has no {folder}.js — the page renders blank")

			d = json.loads(read(json_path))
			page_names.add(d["name"])
			if d["name"].replace("-", "_") != folder:
				fail(f"page '{d['name']}' lives in folder {folder}/ (expected {d['name'].replace('-', '_')}/)")
			if d.get("module") != module:
				fail(f"page '{d['name']}' declares module '{d.get('module')}', folder says '{module}'")
			if d.get("standard") != "Yes":
				# standard="No" pages are treated as user-created: bench migrate
				# will not sync them from disk, which is why this app has to
				# recreate them in code on every install.
				fail_for(module, f"page '{d['name']}' is standard=No — it will not sync from disk")

			js = read(os.path.join(folder_path, f"{folder}.js"))
			if f'frappe.pages["{d["name"]}"]' not in js and f"frappe.pages['{d['name']}']" not in js:
				fail(f"page '{d['name']}': {folder}.js does not register frappe.pages[\"{d['name']}\"]")

	return page_names


def check_hook_targets_importable():
	"""Hook and doc_event targets must resolve by Python import path, not just
	by a file existing somewhere in the tree.

	v2.10.0 put policy_versioning.py under alphax_grc/alphax_grc/ but
	registered it as alphax_grc.policy_versioning — the file existed, the
	import did not, and every GRC Policy save raised ModuleNotFoundError.
	"""
	import importlib.util
	hooks_src = read(os.path.join(APP_DIR, "hooks.py"))
	dotted = sorted(set(re.findall(rf"['\"]({APP}\.[a-z0-9_.]+)['\"]", hooks_src)))
	saved = list(sys.path)
	sys.path.insert(0, ROOT)
	try:
		for target in dotted:
			module_path = target.rsplit(".", 1)[0]
			try:
				spec = importlib.util.find_spec(module_path)
			except (ModuleNotFoundError, ValueError):
				spec = None
			if spec is None:
				fail(
					f"hooks.py target '{target}': module '{module_path}' is not importable — "
					"is the file at the right package level?"
				)
	finally:
		sys.path[:] = saved


def check_hook_targets():
	hooks_src = read(os.path.join(APP_DIR, "hooks.py"))
	dotted = set(re.findall(rf"['\"]({APP}\.[a-z0-9_.]+)['\"]", hooks_src))
	for target in sorted(dotted):
		parts = target.split(".")[1:]
		# strip the trailing callable name, then check the module file exists
		for depth in (len(parts) - 1, len(parts)):
			candidate = os.path.join(APP_DIR, *parts[:depth])
			if os.path.exists(candidate + ".py") or os.path.isdir(candidate):
				break
		else:
			fail(f"hooks.py target '{target}' does not resolve to a file in the app")


def check_asset_paths():
	hooks_src = read(os.path.join(APP_DIR, "hooks.py"))
	for rel in re.findall(r"['\"](public/(?:js|css)/[^'\"]+)['\"]", hooks_src):
		if not os.path.exists(os.path.join(APP_DIR, rel)):
			fail(f"hooks.py references {rel} but the file is missing")


# --- 9: log_error discipline ---------------------------------------------


def check_frappe_local_mutation():
	"""frappe.local is a werkzeug Local — delattr does not reset, it breaks reads.

	`frappe.local.module_app` is populated once by setup_module_map() during
	frappe.init(). Deleting it makes every later frappe.new_doc() raise
	AttributeError: module_app, which aborts install at add_module_defs.
	"""
	for dirpath, _dirs, files in os.walk(APP_DIR):
		for fn in files:
			if not fn.endswith(".py"):
				continue
			path = os.path.join(dirpath, fn)
			rel = os.path.relpath(path, ROOT)
			tree = ast.parse(read(path))
			for node in ast.walk(tree):
				if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
					if node.func.id in ("delattr", "setattr") and node.args:
						target = node.args[0]
						if (isinstance(target, ast.Attribute) and target.attr == "local"
								and isinstance(target.value, ast.Name)
								and target.value.id == "frappe"):
							fail(
								f"{rel}:{node.lineno} {node.func.id}(frappe.local, ...) — "
								"frappe.local is a werkzeug Local; mutating it this way makes "
								"later reads raise AttributeError for the rest of the process"
							)


def check_log_error():
	for dirpath, _dirs, files in os.walk(APP_DIR):
		for fn in files:
			if not fn.endswith(".py"):
				continue
			path = os.path.join(dirpath, fn)
			tree = ast.parse(read(path))
			for node in ast.walk(tree):
				if not isinstance(node, ast.Call):
					continue
				func = node.func
				if not (isinstance(func, ast.Attribute) and func.attr == "log_error"):
					continue
				rel = os.path.relpath(path, ROOT)
				# New-module code must be clean; pre-existing calls are flagged
				# but don't block a push.
				new_code = "grc_evidence_automation" in rel or "/pathway/" in rel
				report = fail if new_code else warn
				if node.args:
					report(
						f"{rel}:{node.lineno} frappe.log_error() called positionally — "
						"title takes the first arg, so the traceback lands in the title field"
					)
				for kw in node.keywords:
					if kw.arg == "title" and isinstance(kw.value, ast.Constant):
						if isinstance(kw.value.value, str) and len(kw.value.value) > 140:
							report(f"{rel}:{node.lineno} log_error title exceeds 140 chars")


def main() -> int:
	version = check_packaging()
	check_no_fixtures()
	modules = check_modules()
	check_doctypes(modules)
	global PAGES
	PAGES = check_pages(modules)
	check_workspaces(modules)
	check_hook_targets()
	check_hook_targets_importable()
	check_asset_paths()
	check_frappe_local_mutation()
	check_log_error()

	for w in warnings:
		print(f"WARN  {w}")
	for f in failures:
		print(f"FAIL  {f}")

	if failures:
		print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s) — not safe to push.")
		return 1

	print(f"\nOK — {APP} v{version} passed all guards ({len(warnings)} warning(s)).")
	return 0


if __name__ == "__main__":
	sys.exit(main())
