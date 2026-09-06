"""
Runs the shipped alphax_grc/diagnostics.py against simulated site states and
asserts it names the right stopper. Uses the same frappe stub as
test_offline.py.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runpy  # noqa: E402

stub = runpy.run_path(os.path.join(ROOT, "tests", "test_offline.py"), run_name="stub")
frappe = stub["frappe"]
Doc = stub["Doc"]
STORE = stub["STORE"]
META = stub["META"]
MODULE_APP = stub["MODULE_APP"]

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


# --- extra stub surface the diagnostics module needs ----------------------
INSTALLED = ["frappe", "erpnext"]
frappe.get_installed_apps = lambda **kw: list(INSTALLED)
frappe.get_roles = lambda *a: ["System Manager"]
frappe.get_app_path = lambda app, *parts: os.path.join(ROOT, app, *parts)
frappe.local.site = "testneo.frappe.cloud"
frappe.utils.cint = lambda v: int(v or 0)
frappe.db.get_single_value = lambda dt, f: 1
frappe.get_attr = lambda dotted: "2.3.3"

import alphax_grc.diagnostics as diag  # noqa: E402


def _levels(results, check_name):
    return [r["level"] for r in results if r["check"] == check_name]


def _stopper(results):
    blockers = [r for r in results if r["level"] == "BLOCKER"]
    return blockers[0] if blockers else None


def test_names_the_module_conflict():
    MODULE_APP.clear()
    MODULE_APP["alphax_grc"] = "alphax_grc"
    MODULE_APP["grc_evidence_automation"] = "alphax_grc_evidence_automation"
    results = diag.check_module_ownership()
    check("module conflict is reported as a blocker", "BLOCKER" in _levels(results, "module ownership"))
    blocker = [r for r in results if r["level"] == "BLOCKER"][0]
    check("it names the offending app", "alphax_grc_evidence_automation" in blocker["detail"],
          blocker["detail"])
    check("it says to remove it from the bench group", "bench group" in blocker["fix"])


def test_clean_module_ownership():
    MODULE_APP.clear()
    MODULE_APP["alphax_grc"] = "alphax_grc"
    MODULE_APP["grc_evidence_automation"] = "alphax_grc"
    results = diag.check_module_ownership()
    check("no blocker when both modules resolve to this app",
          set(_levels(results, "module ownership")) == {"OK"})


def test_detects_synced_but_unregistered():
    STORE.clear()
    META["DocType"] = {"module": None}
    for i, dt in enumerate(["GRC Risk Register", "GRC Policy", "GRC Evidence"]):
        d = Doc("DocType", module="AlphaX GRC")
        d.name = dt
        d.insert()
    INSTALLED[:] = ["frappe", "erpnext"]
    results = diag.check_installed()
    blocker = [r for r in results if r["level"] == "BLOCKER"][0]
    check("half-installed state is a blocker", blocker is not None)
    check("it counts the stranded doctypes", "3 of its DocTypes" in blocker["detail"],
          blocker["detail"])
    check("it explains add_to_installed_apps ordering", "add_to_installed_apps" in blocker["fix"])
    check("it warns against hand-editing installed_apps", "hand-edit" in blocker["fix"])


def test_registered_app_passes():
    INSTALLED[:] = ["frappe", "erpnext", "alphax_grc"]
    check("registered app reports OK", _levels(diag.check_installed(), "app registration") == ["OK"])


def test_controllers_are_checked_against_real_files():
    """Imports every shipped controller for real - no stubbing."""
    results = diag.check_controllers()
    levels = _levels(results, "doctype controllers")
    check("all shipped controllers import and expose the right class",
          levels == ["OK"], [r["detail"] for r in results])
    check("the check covered the whole app",
          "controllers import cleanly" in results[0]["detail"], results[0]["detail"])


def test_orphan_doctypes_flagged():
    STORE.clear()
    ghost = Doc("DocType", module="GRC Evidence Automation")
    ghost.name = "GRC Deleted Thing"
    ghost.insert()
    results = diag.check_orphan_doctypes()
    check("a DocType row with no file is flagged", results[0]["level"] == "WARNING")
    check("the orphan is named", "GRC Deleted Thing" in results[0]["detail"], results[0]["detail"])


def test_preflight_surfaces_the_first_blocker():
    MODULE_APP.clear()
    MODULE_APP["alphax_grc"] = "alphax_grc"
    MODULE_APP["grc_evidence_automation"] = "alphax_grc_evidence_automation"
    INSTALLED[:] = ["frappe", "erpnext"]
    results = diag.collect()
    stopper = _stopper(results)
    check("collect() runs every check without raising", len(results) >= 8, len(results))
    check("the first blocker is the earliest-biting one",
          stopper and stopper["check"] == "module ownership", stopper and stopper["check"])
    check("every blocker carries a fix",
          all(r["fix"] for r in results if r["level"] == "BLOCKER"))


def main():
    for fn in [
        test_names_the_module_conflict,
        test_clean_module_ownership,
        test_detects_synced_but_unregistered,
        test_registered_app_passes,
        test_controllers_are_checked_against_real_files,
        test_orphan_doctypes_flagged,
        test_preflight_surfaces_the_first_blocker,
    ]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")

    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} diagnostics checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
