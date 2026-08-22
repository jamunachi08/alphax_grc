"""
Report Studio tests: builder grouping/aggregation through the permission
layer, filter validation, built-ins with the two-series maturity report,
seeded definitions all runnable, and field discovery.
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
frappe.utils.flt = lambda v, p=None: float(v or 0)
frappe.utils.cint = lambda v: int(str(v or 0)) if str(v or "0").isdigit() else 0

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


# --- stub surface ---------------------------------------------------------

DOCTYPE_MODULES = {
    "GRC Incident": "AlphaX GRC", "GRC Risk Register": "AlphaX GRC",
    "GRC SAMA Assessment Line": "GRC Evidence Automation",
    "GRC SAMA Deliverable": "GRC Evidence Automation",
    "GRC Report Definition": "GRC Evidence Automation",
    "GRC Policy": "AlphaX GRC", "GRC Data Subject Request": "AlphaX GRC",
    "GRC Asset Inventory": "AlphaX GRC", "GRC Project Plan": "GRC Evidence Automation",
    "GRC SAMA Assessment": "GRC Evidence Automation",
}
_orig_db_exists = frappe.db.exists if hasattr(frappe.db, "exists") else None


class _MetaField:
    def __init__(self, fieldname, fieldtype="Data", label=None, options="", **kw):
        self.fieldname, self.fieldtype = fieldname, fieldtype
        self.label, self.options = label or fieldname, options
        self._extra = kw

    def get(self, k, default=None):
        return self._extra.get(k, getattr(self, k, default))


class _Meta:
    def __init__(self, fields, title_field=None):
        self.fields = fields
        self.title_field = title_field

    def get_field(self, name):
        return next((f for f in self.fields if f.fieldname == name), None)


METAS = {
    "GRC Incident": _Meta([
        _MetaField("incident_title", "Data", in_list_view=1),
        _MetaField("severity", "Select", options="Low\nMedium\nHigh\nCritical", in_list_view=1),
        _MetaField("status", "Select", in_list_view=1),
        _MetaField("reported_on", "Date"),
    ], title_field="incident_title"),
    "GRC Risk Register": _Meta([
        _MetaField("risk_title", "Data"),
        _MetaField("risk_category", "Select"),
        _MetaField("inherent_score", "Int"),
        _MetaField("status", "Select"),
    ], title_field="risk_title"),
    "GRC Asset Inventory": _Meta([
        _MetaField("asset_name", "Data"), _MetaField("asset_type", "Select"),
        _MetaField("department", "Data"), _MetaField("data_classification", "Select"),
    ]),
}
frappe.get_meta = lambda dt: METAS[dt]

_real_exists = frappe.db.exists


def _exists(dt, name=None, *a, **kw):
    if dt == "DocType":
        return name in DOCTYPE_MODULES
    return _real_exists(dt, name) if callable(_real_exists) else None


frappe.db.exists = _exists
frappe.db.get_value = (lambda _orig: lambda dt, flt, field=None, **kw:
    DOCTYPE_MODULES.get(flt) if dt == "DocType" and field == "module"
    else _orig(dt, flt, field, **kw))(frappe.db.get_value)

PERMITTED = {"denied-doc"}


def _get_list(doctype, filters=None, fields=None, limit=None, **kw):
    out = []
    for (dt, nm), doc in STORE.items():
        if dt != doctype or nm in PERMITTED:
            continue
        ok = True
        for f in (filters or []) if isinstance(filters, list) else []:
            fname, op, val = f[0], f[1], f[2]
            v = doc.get(fname)
            if op == "in":
                ok = ok and v in val
            elif op == "=":
                ok = ok and v == val
            elif op == "!=":
                ok = ok and v != val
        if isinstance(filters, dict):
            for k, v in filters.items():
                dv = doc.get(k)
                if isinstance(v, list) and len(v) == 2 and v[0] == "in":
                    ok = ok and dv in v[1]
                elif isinstance(v, list) and len(v) == 2 and v[0] == "!=":
                    ok = ok and dv != v[1]
                else:
                    ok = ok and dv == v
        if not ok:
            continue
        row = frappe._dict({f: (nm if f == "name" else doc.get(f)) for f in (fields or ["name"])})
        out.append(row)
    return out


frappe.get_list = _get_list
frappe.only_for = lambda roles: None

import alphax_grc.pathway.reports as rep  # noqa: E402


def _seed(dt, rows):
    for i, kw in enumerate(rows):
        d = Doc(dt, **kw)
        d.name = kw.get("name", f"{dt[:3].upper()}-{i}")
        STORE[(dt, d.name)] = d


# --- tests ----------------------------------------------------------------

def test_field_options_shape():
    opts = rep.field_options("GRC Incident")
    names = [f["fieldname"] for f in opts["groupable"]]
    check("select and data fields are groupable", "severity" in names and "incident_title" in names)
    check("dates are groupable", "reported_on" in names)
    check("title field reported", opts["title_field"] == "incident_title")
    try:
        rep.field_options("User")
        outside = False
    except Exception:
        outside = True
    check("non-GRC doctypes are refused", outside)


def test_builder_count_and_filters():
    STORE.clear()
    _seed("GRC Incident", [
        {"incident_title": "a", "severity": "High", "status": "Open"},
        {"incident_title": "b", "severity": "High", "status": "Closed"},
        {"incident_title": "c", "severity": "Low", "status": "Open"},
    ])
    defn = Doc("GRC Report Definition", definition_type="Builder",
               source_doctype="GRC Incident", filters_json='[["status","=","Open"]]',
               group_by="severity", aggregate="Count", aggregate_field="",
               detail_columns="")
    out = rep._run_builder(defn)
    got = dict(zip(out["labels"], out["series"][0]))
    check("filters narrow the rows before grouping", got == {"High": 1, "Low": 1}, got)
    check("total reflects filtered rows", out["total"] == 2, out["total"])


def test_builder_average():
    STORE.clear()
    _seed("GRC Risk Register", [
        {"risk_category": "Cybersecurity", "inherent_score": 20, "status": "Open"},
        {"risk_category": "Cybersecurity", "inherent_score": 10, "status": "Open"},
        {"risk_category": "Privacy", "inherent_score": 9, "status": "Open"},
    ])
    defn = Doc("GRC Report Definition", definition_type="Builder",
               source_doctype="GRC Risk Register", filters_json="",
               group_by="risk_category", aggregate="Average",
               aggregate_field="inherent_score", detail_columns="risk_title,risk_category")
    out = rep._run_builder(defn)
    got = dict(zip(out["labels"], out["series"][0]))
    check("average aggregates per group", got == {"Cybersecurity": 15.0, "Privacy": 9.0}, got)


def test_builder_rejects_bad_definitions():
    def throws(**kw):
        base = dict(definition_type="Builder", filters_json="", group_by="",
                    aggregate="Count", aggregate_field="", detail_columns="")
        base.update(kw)
        defn = Doc("GRC Report Definition", **base)
        try:
            rep._run_builder(defn)
            return False
        except Exception:
            return True
    check("unknown group_by field is refused",
          throws(source_doctype="GRC Incident", group_by="nonexistent"))
    check("Sum without a numeric field is refused",
          throws(source_doctype="GRC Incident", aggregate="Sum"))
    check("bad filter JSON is refused",
          throws(source_doctype="GRC Incident", filters_json='{"not":"a list"}'))


def test_permission_layer_is_used():
    """Rows the viewer cannot read never reach the aggregate."""
    STORE.clear()
    _seed("GRC Incident", [
        {"name": "ok-doc", "incident_title": "seen", "severity": "High", "status": "Open"},
        {"name": "denied-doc", "incident_title": "hidden", "severity": "High", "status": "Open"},
    ])
    defn = Doc("GRC Report Definition", definition_type="Builder",
               source_doctype="GRC Incident", filters_json="", group_by="severity",
               aggregate="Count", aggregate_field="", detail_columns="")
    out = rep._run_builder(defn)
    check("a row excluded by permissions is excluded from the report",
          out["series"][0] == [1], out["series"])


def test_builtin_maturity_two_series():
    STORE.clear()
    _seed("GRC SAMA Assessment Line", [
        {"domain": "3.1", "current_level": "2 - x", "target_level": "3 - x", "applicable": 1},
        {"domain": "3.1", "current_level": "4 - x", "target_level": "3 - x", "applicable": 1},
        {"domain": "3.3", "current_level": "1 - x", "target_level": "3 - x", "applicable": 1},
        {"domain": "3.3", "current_level": "5 - x", "target_level": "3 - x", "applicable": 0},
    ])
    out = rep._bi_sama_maturity_by_domain()
    check("two series: current and target", out["series_labels"] == ["Current", "Target"])
    got = dict(zip(out["labels"], out["series"][0]))
    check("current averages per domain over applicable lines only",
          got == {"3.1": 3.0, "3.3": 1.0}, got)
    gap = {r["domain"]: r["gap"] for r in out["rows"]}
    check("gap per domain in the drill-down", gap == {"3.1": 0.0, "3.3": 2.0}, gap)


def test_builtin_policy_pct():
    STORE.clear()
    _seed("GRC Policy", [
        {"policy_title": "A", "publication_status": "Published"},
        {"policy_title": "B", "publication_status": "Published"},
        {"policy_title": "C", "publication_status": "Draft"},
    ])
    frappe.db.count = lambda dt, flt=None: (
        2 if flt else 3
    ) if dt == "GRC Policy" else 0
    out = rep._bi_policy_publication_pct()
    check("publication percentage computed", out["number"] == 66.7, out["number"])
    check("unpublished policies listed for drill-down", len(out["rows"]) == 1)


def test_seeded_definitions_are_valid():
    keys = {s.get("builtin_key") for s in rep.SEED_DEFINITIONS if s["definition_type"] == "Built-in"}
    check("every seeded built-in has an implementation", keys <= set(rep.BUILTINS), keys - set(rep.BUILTINS))
    titles = [s["report_title"] for s in rep.SEED_DEFINITIONS]
    check("seeded titles are unique", len(titles) == len(set(titles)))
    check("ten reports seed out of the box", len(rep.SEED_DEFINITIONS) == 10, len(titles))
    for s in rep.SEED_DEFINITIONS:
        if s["definition_type"] == "Builder":
            check(f"seeded builder targets a GRC doctype: {s['report_title']}",
                  s["source_doctype"] in DOCTYPE_MODULES, s["source_doctype"])


def main():
    for fn in [test_field_options_shape, test_builder_count_and_filters, test_builder_average,
               test_builder_rejects_bad_definitions, test_permission_layer_is_used,
               test_builtin_maturity_two_series, test_builtin_policy_pct,
               test_seeded_definitions_are_valid]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")
    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} report checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
