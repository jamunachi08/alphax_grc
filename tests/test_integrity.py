"""
Tests the v2.10.0 features after porting them onto the 2.9 base:
hash-chained evidence evaluations and policy versions, immutability,
the policy snapshot hook, and earned value computed on working days.
"""

import datetime
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

stub = runpy.run_path(os.path.join(ROOT, "tests", "test_offline.py"), run_name="stub")
frappe = stub["frappe"]
Doc = stub["Doc"]
STORE = stub["STORE"]
META = stub["META"]

frappe.utils.getdate = lambda v=None: (
    datetime.date(2026, 9, 20) if v is None
    else v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v)[:10])
)
frappe.utils.add_days = lambda d, n: frappe.utils.getdate(d) + datetime.timedelta(days=n)
frappe.utils.flt = lambda v, p=None: float(v or 0)
frappe.utils.now_datetime = lambda: datetime.datetime(2026, 9, 20, 9, 0, 0)
frappe.session = type("S", (), {"user": "auditor@x.com"})()

import alphax_grc.integrity as integ  # noqa: E402
import alphax_grc.policy_versioning as pv  # noqa: E402
from alphax_grc.alphax_grc.doctype.grc_evidence_rule_evaluation.grc_evidence_rule_evaluation import (  # noqa: E402
    GRCEvidenceRuleEvaluation,
)
from alphax_grc.alphax_grc.doctype.grc_policy_version.grc_policy_version import GRCPolicyVersion  # noqa: E402
import alphax_grc.pathway.scheduler as sch  # noqa: E402
from alphax_grc.grc_evidence_automation.doctype.grc_project_plan.grc_project_plan import (  # noqa: E402
    GRCProjectPlan,
)

# bind the real controller methods to the stub so compute_evm can call its helpers
Doc._planned_pct_complete = GRCProjectPlan._planned_pct_complete
Doc._actual_cost_from_timesheets = GRCProjectPlan._actual_cost_from_timesheets
Doc.compute_evm = GRCProjectPlan.compute_evm

sch.getdate = frappe.utils.getdate
sch.add_days = frappe.utils.add_days

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


META.update({
    "GRC Evidence Rule Evaluation": {k: None for k in
        ["rule", "evaluated_at", "pass_count", "fail_count", "evaluation_status", "prev_hash", "snapshot_hash"]},
    "GRC Policy Version": {k: None for k in
        ["policy", "version_label", "published_on", "published_by", "snapshot_json", "prev_hash", "snapshot_hash"]},
    "GRC Policy": {k: None for k in
        ["policy_title", "policy_category", "version_no", "status", "publication_status", "summary", "client"]},
})


# --- integrity primitives -------------------------------------------------

def test_hash_is_deterministic_and_sensitive():
    h1 = integ.compute_chain_hash("genesis", "R1", "2026-09-01", 10, 2, "Pass")
    h2 = integ.compute_chain_hash("genesis", "R1", "2026-09-01", 10, 2, "Pass")
    h3 = integ.compute_chain_hash("genesis", "R1", "2026-09-01", 10, 3, "Pass")
    check("same inputs give the same hash", h1 == h2)
    check("one changed part gives a different hash", h1 != h3)
    check("hash is a 64-char hex sha256", len(h1) == 64 and all(c in "0123456789abcdef" for c in h1), h1[:16])


def _eval(rule, n, prev, passes, fails, status="Pass"):
    d = Doc("GRC Evidence Rule Evaluation", rule=rule, evaluated_at=f"2026-09-0{n}",
            pass_count=passes, fail_count=fails, evaluation_status=status, prev_hash=prev)
    d.snapshot_hash = integ.compute_chain_hash(prev, rule, d.evaluated_at, passes, fails, status)
    d.name = f"EV-{n}"
    d.insert()
    return d


def test_chain_verifies_and_detects_tampering():
    STORE.clear()
    e1 = _eval("R1", 1, integ.GENESIS, 10, 0)
    e2 = _eval("R1", 2, e1.snapshot_hash, 9, 1)
    e3 = _eval("R1", 3, e2.snapshot_hash, 10, 0)
    parts = ["rule", "evaluated_at", "pass_count", "fail_count", "evaluation_status"]

    r = integ.verify_chain("GRC Evidence Rule Evaluation", {"rule": "R1"}, parts)
    check("an intact chain verifies", r["valid"] and r["chain_length"] == 3, r)

    e2.fail_count = 0  # someone "fixes" the history
    r = integ.verify_chain("GRC Evidence Rule Evaluation", {"rule": "R1"}, parts)
    check("altering one record breaks the chain", not r["valid"])
    check("the broken link is named", r.get("broken_at") == "EV-2", r)
    e2.fail_count = 1

    e3.prev_hash = "deadbeef"
    r = integ.verify_chain("GRC Evidence Rule Evaluation", {"rule": "R1"}, parts)
    check("a re-linked record is caught as a prev_hash mismatch",
          not r["valid"] and "prev_hash" in r["reason"], r)


def test_evaluations_are_immutable():
    d = Doc("GRC Evidence Rule Evaluation", rule="R9"); d.name = "EV-9"; d.insert()
    def throws(fn):
        try: fn(); return False
        except Exception: return True
    check("editing an existing evaluation raises", throws(lambda: GRCEvidenceRuleEvaluation.validate(d)))
    check("deleting an evaluation raises", throws(lambda: GRCEvidenceRuleEvaluation.on_trash(d)))
    fresh = Doc("GRC Evidence Rule Evaluation", rule="R9")
    check("a new evaluation validates", not throws(lambda: GRCEvidenceRuleEvaluation.validate(fresh)))


# --- policy versioning ----------------------------------------------------

def _policy(**kw):
    base = dict(policy_title="Access Control Policy", policy_category="Information Security",
                version_no="1.0", status="Approved", publication_status="Draft", summary="s",
                client="CL-1")
    base.update(kw)
    p = Doc("GRC Policy", **base); p.name = "POL-0001"; p.insert()
    return p


def test_snapshot_only_when_published():
    STORE.clear()
    p = _policy()
    pv.snapshot_if_published(p)
    check("a Draft policy takes no snapshot",
          not [1 for (dt, _n) in STORE if dt == "GRC Policy Version"])

    p.publication_status = "Published"
    pv.snapshot_if_published(p)
    versions = [d for (dt, _n), d in STORE.items() if dt == "GRC Policy Version"]
    check("publishing takes exactly one snapshot", len(versions) == 1, len(versions))
    check("snapshot carries the policy and version label",
          versions[0].get("policy") == "POL-0001" and versions[0].get("version_label") == "1.0")
    check("first version chains from genesis", versions[0].get("prev_hash") == integ.GENESIS)
    check("snapshot records who published", versions[0].get("published_by") == "auditor@x.com")


def test_resave_does_not_duplicate_and_new_version_chains():
    p = STORE[("GRC Policy", "POL-0001")]
    p.summary = "unrelated edit"
    pv.snapshot_if_published(p)
    versions = [d for (dt, _n), d in STORE.items() if dt == "GRC Policy Version"]
    check("re-saving the same published version does not duplicate", len(versions) == 1, len(versions))

    p.version_no = "1.1"
    pv.snapshot_if_published(p)
    versions = sorted([d for (dt, _n), d in STORE.items() if dt == "GRC Policy Version"],
                      key=lambda d: d.get("version_label"))
    check("a new version number takes a new snapshot", len(versions) == 2, len(versions))
    check("v1.1 chains from v1.0's hash",
          versions[1].get("prev_hash") == versions[0].get("snapshot_hash"))

    r = pv.verify_policy_chain("POL-0001")
    check("the policy's version chain verifies end to end", r["valid"] and r["chain_length"] == 2, r)


def test_policy_versions_are_immutable():
    v = [d for (dt, _n), d in STORE.items() if dt == "GRC Policy Version"][0]
    def throws(fn):
        try: fn(); return False
        except Exception: return True
    check("editing a policy version raises", throws(lambda: GRCPolicyVersion.validate(v)))
    check("deleting a policy version raises", throws(lambda: GRCPolicyVersion.on_trash(v)))


def test_policy_version_grants_no_create():
    import json
    d = json.load(open(os.path.join(
        ROOT, "alphax_grc/alphax_grc/doctype/grc_policy_version/grc_policy_version.json")))
    check("no role can create a policy version directly",
          not any(p.get("create") for p in d["permissions"]),
          [(p["role"], p.get("create")) for p in d["permissions"]])


# --- earned value on working days ----------------------------------------

def test_planned_pct_uses_working_days():
    from alphax_grc.grc_evidence_automation.doctype.grc_project_plan.grc_project_plan import GRCProjectPlan

    # Plan: Sun 6 Sep -> Thu 1 Oct 2026 on a Sun-Thu week = 20 working days.
    # "Today" is Sun 20 Sep: 10 working days elapsed (two full weeks) but
    # 14 calendar days of a 25-day span.
    plan = Doc("GRC Project Plan", start_date="2026-09-06", end_date="2026-10-01",
               total_working_days=20, working_days="Sun-Thu (KSA)", holiday_list=None)
    got = GRCProjectPlan._planned_pct_complete(plan)
    cal = sch.Calendar("Sun-Thu (KSA)")
    expected = round(cal.count_working_days("2026-09-06", "2026-09-20") / 20 * 100, 2)
    calendar_based = round(14 / 25 * 100, 2)
    check("planned % counts working days", got == expected, f"{got} vs {expected}")
    check("and differs from the calendar-day answer that was shipped in 2.10",
          got != calendar_based, f"{got} vs calendar {calendar_based}")


def test_evm_formulas():
    from alphax_grc.grc_evidence_automation.doctype.grc_project_plan.grc_project_plan import GRCProjectPlan

    frappe.db.get_value = lambda dt, f=None, field=None, **kw: 40000 if dt == "GRC Consultant Timesheet" else None
    plan = Doc("GRC Project Plan", start_date="2026-09-06", end_date="2026-10-01",
               total_working_days=20, working_days="Sun-Thu (KSA)", holiday_list=None,
               budget_at_completion=100000, pct_complete=30, planned_pct_complete=0,
               actual_cost=0, cost_performance_index=0, schedule_performance_index=0,
               estimate_at_completion=0)
    plan.name = "PLAN-1"
    GRCProjectPlan.compute_evm(plan)
    # EV = 30k, AC = 40k -> CPI 0.75, EAC = 133,333
    check("CPI = EV / AC", plan.cost_performance_index == 0.75, plan.cost_performance_index)
    check("EAC = BAC / CPI", round(plan.estimate_at_completion) == 133333, plan.estimate_at_completion)
    check("SPI compares against working-day planned value", 0 < plan.schedule_performance_index < 1,
          plan.schedule_performance_index)
    check("actual cost comes from timesheets", plan.actual_cost == 40000)

    nobudget = Doc("GRC Project Plan", budget_at_completion=0, planned_pct_complete=5, actual_cost=5,
                   cost_performance_index=5, schedule_performance_index=5, estimate_at_completion=5)
    GRCProjectPlan.compute_evm(nobudget)
    check("no budget -> EVM stays zero and does not raise", nobudget.cost_performance_index == 0)


def main():
    for fn in [test_hash_is_deterministic_and_sensitive, test_chain_verifies_and_detects_tampering,
               test_evaluations_are_immutable, test_snapshot_only_when_published,
               test_resave_does_not_duplicate_and_new_version_chains,
               test_policy_versions_are_immutable, test_policy_version_grants_no_create,
               test_planned_pct_uses_working_days, test_evm_formulas]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")
    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} integrity checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
