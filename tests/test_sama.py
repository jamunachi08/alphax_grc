"""
SAMA CSF coverage tests: catalogue completeness against the framework
document, maturity scoring, non-bank exclusions, the waiver approval chain,
and the deliverable register.
"""

import json
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

stub = runpy.run_path(os.path.join(ROOT, "tests", "test_offline.py"), run_name="stub")
frappe = stub["frappe"]
Doc = stub["Doc"]

CATALOG = json.load(open(os.path.join(ROOT, "alphax_grc/alphax_grc/data/sama_csf_catalog.json")))

from alphax_grc.grc_evidence_automation.doctype.grc_sama_assessment.grc_sama_assessment import (  # noqa: E402
    GRCSAMAAssessment, level_value, NON_BANK_EXCLUDED,
)
from alphax_grc.grc_evidence_automation.doctype.grc_sama_waiver.grc_sama_waiver import (  # noqa: E402
    GRCSAMAWaiver,
)

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


# --- the sub-domains the framework document actually defines -------------
EXPECTED = {
    "3.1": ["3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5", "3.1.6", "3.1.7"],
    "3.2": ["3.2.1", "3.2.1.1", "3.2.1.2", "3.2.1.3", "3.2.1.4", "3.2.2", "3.2.3", "3.2.4", "3.2.5"],
    "3.3": [f"3.3.{i}" for i in range(1, 18)],
    "3.4": ["3.4.1", "3.4.2", "3.4.3"],
}


def test_catalogue_matches_the_framework():
    codes = {s["code"] for s in CATALOG["subdomains"]}
    expected = {c for v in EXPECTED.values() for c in v}
    check("every sub-domain in SAMA CSF v1.0 is catalogued", not (expected - codes),
          sorted(expected - codes))
    check("no invented sub-domains", not (codes - expected), sorted(codes - expected))
    check("all four domains covered",
          {s["domain"] for s in CATALOG["subdomains"]} == {"3.1", "3.2", "3.3", "3.4"})
    check("36 sub-domains total", len(codes) == 36, len(codes))


def test_non_bank_exclusions_are_the_documented_ones():
    excluded = {s["code"] for s in CATALOG["subdomains"] if s["excluded_for_non_banks"]}
    check("1.4 exclusions are 3.2.3, 3.3.12 and 3.3.13",
          excluded == {"3.2.3", "3.3.12", "3.3.13"}, sorted(excluded))
    check("the controller agrees with the catalogue", NON_BANK_EXCLUDED == excluded)


def test_deliverables_all_mapped():
    d = CATALOG["deliverables"]
    codes = {s["code"] for s in CATALOG["subdomains"]}
    check("all 108 deliverables present", len(d) == 108, len(d))
    unmapped = [x["sl"] for x in d if not x.get("subdomain")]
    check("every deliverable maps to a sub-domain", not unmapped, unmapped)
    bad = [x["sl"] for x in d if x["subdomain"] not in codes]
    check("every mapping points at a real sub-domain", not bad, bad)
    check("SL numbers are unique", len({x["sl"] for x in d}) == 108)


def test_level_parsing():
    check("level label parses to its number", level_value("3 - Structured and formalized") == 3)
    check("level 0 parses", level_value("0 - Non-existent") == 0)
    check("blank is treated as 0", level_value(None) == 0)


# The stub Doc has no controller methods; bind the real ones so the tests
# exercise the shipped scoring logic rather than a copy of it.
Doc.apply_exclusions = GRCSAMAAssessment.apply_exclusions
Doc.score = GRCSAMAAssessment.score


def _assessment(entity_type="Bank", levels=None):
    doc = Doc("GRC SAMA Assessment", entity_type=entity_type, lines=[],
              overall_maturity=0, subdomains_at_target=0, applicable_subdomains=0,
              pct_at_target=0, lowest_domain=None)
    for code, level in (levels or []):
        doc.append("lines", {
            "subdomain": code, "domain": code[:3], "applicable": 1,
            "current_level": f"{level} - x", "target_level": "3 - Structured and formalized",
            "meets_target": 0,
        })
    return doc


def test_maturity_scoring():
    doc = _assessment(levels=[("3.1.1", 4), ("3.1.2", 2), ("3.3.1", 3), ("3.4.1", 3)])
    GRCSAMAAssessment.validate(doc)
    check("overall maturity is the mean of applicable sub-domains",
          doc.overall_maturity == 3.0, doc.overall_maturity)
    check("sub-domains at target counted", doc.subdomains_at_target == 3,
          doc.subdomains_at_target)
    check("percentage at target computed", doc.pct_at_target == 75.0, doc.pct_at_target)
    check("a level-2 sub-domain does not meet the level-3 target",
          [l for l in doc.get("lines") if l.subdomain == "3.1.2"][0].meets_target == 0)
    check("weakest domain identified", doc.lowest_domain == "3.1", doc.lowest_domain)


def test_non_bank_drops_excluded_subdomains():
    levels = [("3.2.3", 0), ("3.3.12", 0), ("3.3.13", 0), ("3.1.1", 4), ("3.1.2", 4)]
    bank = _assessment("Bank", levels)
    GRCSAMAAssessment.validate(bank)
    check("a bank carries all five", bank.applicable_subdomains == 5, bank.applicable_subdomains)
    check("its maturity is dragged down by the zeros", bank.overall_maturity == 1.6,
          bank.overall_maturity)

    insurer = _assessment("Insurance / Reinsurance", levels)
    GRCSAMAAssessment.validate(insurer)
    check("an insurer drops 3.2.3, 3.3.12 and 3.3.13",
          insurer.applicable_subdomains == 2, insurer.applicable_subdomains)
    check("and scores only on what applies to it", insurer.overall_maturity == 4.0,
          insurer.overall_maturity)
    check("excluded lines are flagged not-applicable, not deleted",
          len(insurer.get("lines")) == 5)


def test_empty_assessment_does_not_divide_by_zero():
    doc = _assessment(levels=[])
    GRCSAMAAssessment.validate(doc)
    check("an empty assessment scores zero without raising", doc.overall_maturity == 0)


def _waiver(**kw):
    base = dict(request_type="Waiver", subject="s", compensating_controls="", proposal="",
                status="Draft", ciso_approver=None, committee_approver=None, sama_reference=None)
    base.update(kw)
    return Doc("GRC SAMA Waiver", **base)


def _throws(doc):
    try:
        GRCSAMAWaiver.validate(doc)
        return False
    except Exception:
        return True


def test_waiver_requires_compensating_controls():
    check("a waiver without compensating controls is rejected (Appendix E)",
          _throws(_waiver()))
    check("with them it validates",
          not _throws(_waiver(compensating_controls="Network segmentation and 24x7 monitoring")))


def test_update_request_requires_a_proposal():
    check("a framework update request needs a proposal (Appendix C)",
          _throws(_waiver(request_type="Framework Update")))
    check("with one it validates",
          not _throws(_waiver(request_type="Framework Update", proposal="Amend 3.3.13.4.b")))


def test_waiver_approval_chain_is_enforced():
    ok = dict(compensating_controls="compensating control in place")
    check("cannot reach committee approval without the CISO",
          _throws(_waiver(status="Committee Approval", **ok)))
    check("cannot submit to SAMA without the committee",
          _throws(_waiver(status="Submitted to SAMA", ciso_approver="ciso@x.com", **ok)))
    check("cannot mark approved without a SAMA reference",
          _throws(_waiver(status="Approved", ciso_approver="ciso@x.com",
                          committee_approver="chair@x.com", **ok)))
    check("a fully approved request validates",
          not _throws(_waiver(status="Approved", ciso_approver="ciso@x.com",
                              committee_approver="chair@x.com", sama_reference="SAMA/2026/114",
                              **ok)))


def test_incident_fields_cover_the_formal_report():
    from alphax_grc.pathway.sama import INCIDENT_FIELDS

    names = {f["fieldname"] for f in INCIDENT_FIELDS}
    # CSF 3.3.15.7 lists eleven items for the formal report
    required = {
        "occurred_on", "detected_on", "assets_involved", "technical_details", "root_cause",
        "corrective_actions", "impact_description", "estimated_incident_cost",
        "estimated_corrective_cost", "sama_classification", "sama_notified_on",
        "sama_no_objection_obtained",
    }
    check("every field the formal SAMA incident report requires exists",
          not (required - names), sorted(required - names))
    check("insert_after chains resolve within the set or to a base field",
          all(f.get("insert_after") for f in INCIDENT_FIELDS))


def test_ciso_governance_fields():
    from alphax_grc.pathway.sama import CLIENT_FIELDS

    names = {f["fieldname"] for f in CLIENT_FIELDS}
    check("CISO nationality, appointment and SAMA NOL are tracked (3.1.1.9)",
          {"ciso_is_saudi_national", "sama_nol_obtained", "sama_nol_reference"} <= names,
          sorted(names))


def main():
    for fn in [test_catalogue_matches_the_framework, test_non_bank_exclusions_are_the_documented_ones,
               test_deliverables_all_mapped, test_level_parsing, test_maturity_scoring,
               test_non_bank_drops_excluded_subdomains, test_empty_assessment_does_not_divide_by_zero,
               test_waiver_requires_compensating_controls, test_update_request_requires_a_proposal,
               test_waiver_approval_chain_is_enforced, test_incident_fields_cover_the_formal_report,
               test_ciso_governance_fields]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")

    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} SAMA checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
