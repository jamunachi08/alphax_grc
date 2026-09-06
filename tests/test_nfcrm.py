"""
Asserts the risk engine matches the NCA National Framework for Cybersecurity
Risk Management (NFCRM-1:2025) exactly — all 25 matrix cells, the five bands
from Figure 3, CIA-derived impact from Figure 4, and the NFCRM 5.5 reporting
flag.
"""

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

stub = runpy.run_path(os.path.join(ROOT, "tests", "test_offline.py"), run_name="stub")
Doc = stub["Doc"]

from alphax_grc.alphax_grc.doctype.grc_risk_register.grc_risk_register import (  # noqa: E402
    GRCRiskRegister,
    _derived_impact,
    _score_to_rating,
    evaluate_appetite,
    APPETITE_FIELD,
)

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


# Figure 2 of NFCRM-1:2025, transcribed cell by cell.
# rows = impact 1..5, cols = likelihood 1..5
MATRIX = {
    1: ["Very Low", "Very Low", "Low", "Low", "Low"],
    2: ["Very Low", "Low", "Low", "Medium", "Medium"],
    3: ["Low", "Low", "Medium", "Medium", "High"],
    4: ["Low", "Medium", "Medium", "High", "Critical"],
    5: ["Low", "Medium", "High", "Critical", "Critical"],
}


def test_every_matrix_cell():
    wrong = []
    for impact, expected_row in MATRIX.items():
        for idx, expected in enumerate(expected_row):
            likelihood = idx + 1
            got = _score_to_rating(impact * likelihood)
            if got != expected:
                wrong.append(f"I{impact}xL{likelihood}={impact * likelihood}: got {got}, NFCRM says {expected}")
    check("all 25 cells of the NFCRM matrix are rated correctly", not wrong, wrong[:5])


def test_band_boundaries():
    bands = [(1, "Very Low"), (2, "Very Low"), (3, "Low"), (7, "Low"), (8, "Medium"),
             (14, "Medium"), (15, "High"), (19, "High"), (20, "Critical"), (25, "Critical")]
    wrong = [f"{s}->{_score_to_rating(s)} (want {want})" for s, want in bands
             if _score_to_rating(s) != want]
    check("Figure 3 band boundaries hold exactly", not wrong, wrong)
    check("an unscored risk is N/A, not Very Low", _score_to_rating(0) == "N/A")


def test_very_low_is_reachable():
    """The old bands never produced Very Low even though the field offered it."""
    check("Very Low is actually produced", _score_to_rating(2) == "Very Low")


def test_impact_derives_from_cia():
    doc = Doc("GRC Risk Register", impact_confidentiality="2", impact_integrity="5",
              impact_availability="1")
    check("impact is the highest of the three CIA elements", _derived_impact(doc) == 5,
          _derived_impact(doc))
    blank = Doc("GRC Risk Register")
    check("impact is left alone when no CIA values are given", _derived_impact(blank) is None)


import json as _json

_SCHEMA = _json.load(open(os.path.join(
    ROOT, "alphax_grc/alphax_grc/doctype/grc_risk_register/grc_risk_register.json")))

# Frappe hands the controller a doc carrying every declared field, so build the
# default from the shipped schema rather than guessing which ones it touches.
DEFAULTS = {f["fieldname"]: None for f in _SCHEMA["fields"] if f.get("fieldname")}
DEFAULTS.update(residual_score=0, inherent_score=0, nca_reportable=0,
                escalation_status="Normal")


def _score(**kw):
    """Real Frappe hands the controller a doc with every declared field present."""
    fields = dict(DEFAULTS)
    fields.update(kw)
    doc = Doc("GRC Risk Register", **fields)
    GRCRiskRegister.validate(doc)
    return doc


def test_validate_scores_and_flags():
    doc = _score(impact="4", likelihood="4", residual_impact=2, residual_likelihood=2,
                 escalation_status="Normal", manual_rating_override=None)
    check("inherent score is impact x likelihood", doc.inherent_score == 16, doc.inherent_score)
    check("16 is High under NFCRM, not Critical", doc.risk_rating == "High", doc.risk_rating)
    check("residual is banded too", doc.residual_rating == "Low", doc.residual_rating)
    check("a High risk is flagged reportable to the NCA", doc.nca_reportable == 1)

    low = _score(impact="2", likelihood="3", escalation_status="Normal",
                 manual_rating_override=None)
    check("a Low risk is not flagged reportable", low.nca_reportable == 0, low.risk_rating)

    override = _score(impact="2", likelihood="2", escalation_status="Normal",
                      manual_rating_override="Critical")
    check("a manual override to Critical makes it reportable", override.nca_reportable == 1)


def test_cia_drives_the_score():
    doc = _score(impact_confidentiality="5", impact_integrity="1", impact_availability="1",
                 likelihood="4", escalation_status="Normal", manual_rating_override=None)
    check("CIA impact feeds the inherent score", doc.inherent_score == 20, doc.inherent_score)
    check("that lands as Critical", doc.risk_rating == "Critical", doc.risk_rating)


# --------------------------------------------------------------------------
# Question 5: is the residual risk acceptable to the business?
# --------------------------------------------------------------------------

STORE = stub["STORE"]
META = stub["META"]


def _client(**appetite):
    META["GRC Client Profile"] = {**META.get("GRC Client Profile", {}),
                                  **{k: None for k in APPETITE_FIELD.values()}}
    c = Doc("GRC Client Profile", client_name="Wadi", **appetite)
    c.name = "CL-APP"
    STORE[("GRC Client Profile", "CL-APP")] = c
    return c.name


def test_appetite_categories_cover_the_risk_register():
    import json as _json
    schema = _json.load(open(os.path.join(
        ROOT, "alphax_grc/alphax_grc/doctype/grc_risk_register/grc_risk_register.json")))
    cats = {o for o in next(f for f in schema["fields"] if f["fieldname"] == "risk_category")
            ["options"].split("\n") if o}
    check("every risk category maps to an appetite field", not (cats - set(APPETITE_FIELD)),
          sorted(cats - set(APPETITE_FIELD)))
    client_schema = _json.load(open(os.path.join(
        ROOT, "alphax_grc/alphax_grc/doctype/grc_client_profile/grc_client_profile.json")))
    client_fields = {f["fieldname"] for f in client_schema["fields"]}
    check("every mapped appetite field exists on the client profile",
          set(APPETITE_FIELD.values()) <= client_fields,
          sorted(set(APPETITE_FIELD.values()) - client_fields))


def test_within_appetite():
    client = _client(appetite_cybersecurity="Moderate")
    v = evaluate_appetite(client, "Cybersecurity", "Low", "Mitigate", None)
    check("a Low residual is within a Moderate appetite", v["within_appetite"] == 1, v)
    check("the ceiling is reported", v["ceiling"] == "Medium", v)
    v = evaluate_appetite(client, "Cybersecurity", "Medium", "Mitigate", None)
    check("a residual equal to the ceiling is within appetite", v["within_appetite"] == 1, v)


def test_above_appetite_needs_a_decision():
    client = _client(appetite_cybersecurity="Low")
    v = evaluate_appetite(client, "Cybersecurity", "High", "Mitigate", None)
    check("a High residual breaches a Low appetite", v["within_appetite"] == 0, v)
    check("and says it needs treatment or acceptance", "needs" in v["status"], v["status"])


def test_formal_acceptance_is_recognised():
    client = _client(appetite_privacy="None")
    v = evaluate_appetite(client, "Privacy", "Medium", "Accept", "RA-0007")
    check("an accepted risk above appetite is flagged but recognised as accepted",
          v["within_appetite"] == 0 and "accepted" in v["status"], v)
    v = evaluate_appetite(client, "Privacy", "Medium", "Accept", None)
    check("'Accept' without an acceptance record still needs a decision",
          "needs" in v["status"], v["status"])


def test_undefined_appetite_is_not_a_breach():
    client = _client()
    v = evaluate_appetite(client, "Cybersecurity", "Critical", "Mitigate", None)
    check("no appetite set -> no verdict, not a false breach", v["within_appetite"] is None, v)
    v = evaluate_appetite(client, "Cybersecurity", "N/A", "Mitigate", None)
    check("an unscored residual gives no verdict", v["within_appetite"] is None, v)


def test_appetite_flows_through_validate():
    # validate() checks meta.get_field("within_appetite") before stamping,
    # so the stub meta must carry the new fields as the shipped schema does.
    META["GRC Risk Register"] = {**META.get("GRC Risk Register", {}),
                                 "within_appetite": None, "appetite_ceiling": None,
                                 "appetite_status": None}
    client = _client(appetite_operational="Low")
    doc = _score(client=client, risk_category="Operational", impact="4", likelihood="4",
                 residual_impact=3, residual_likelihood=3, risk_response="Mitigate",
                 acceptance_reference=None, escalation_status="Normal",
                 manual_rating_override=None)
    check("validate stamps the appetite verdict on the risk",
          doc.within_appetite == 0 and doc.appetite_ceiling == "Low", 
          (doc.within_appetite, doc.appetite_ceiling, doc.appetite_status))


def main():
    for fn in [test_every_matrix_cell, test_band_boundaries, test_very_low_is_reachable,
               test_impact_derives_from_cia, test_validate_scores_and_flags,
               test_cia_drives_the_score, test_appetite_categories_cover_the_risk_register,
               test_within_appetite, test_above_appetite_needs_a_decision,
               test_formal_acceptance_is_recognised, test_undefined_appetite_is_not_a_breach,
               test_appetite_flows_through_validate]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")

    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} NFCRM checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
