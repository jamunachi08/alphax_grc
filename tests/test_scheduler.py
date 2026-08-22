"""
Tests the working-day scheduler against the behaviour a consultant expects:
KSA weekends skipped, chains that follow, milestones that consume no calendar,
locked rows that survive a reschedule, and holidays honoured.
"""

import datetime
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

stub = runpy.run_path(os.path.join(ROOT, "tests", "test_offline.py"), run_name="stub")
frappe = stub["frappe"]

# real date helpers, not the no-op stubs
frappe.utils.getdate = lambda v=None: (
    v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v)[:10])
)
frappe.utils.add_days = lambda d, n: frappe.utils.getdate(d) + datetime.timedelta(days=n)
HOLIDAYS = []
frappe.get_all = lambda dt, **kw: HOLIDAYS if dt == "Holiday" else []

import alphax_grc.pathway.scheduler as sch  # noqa: E402

sch.getdate = frappe.utils.getdate
sch.add_days = frappe.utils.add_days

RESULTS = []


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


def T(wbs, days, **kw):
    d = {"wbs": wbs, "task_title": wbs, "duration_days": days}
    d.update(kw)
    return d


def iso(d):
    return str(d)


# 2026-08-16 is a Sunday — a working day in the KSA week.
START = "2026-08-16"


def test_ksa_week_skips_fri_sat():
    cal = sch.Calendar("Sun-Thu (KSA)")
    check("Sunday is a working day", cal.is_working("2026-08-16"))
    check("Thursday is a working day", cal.is_working("2026-08-20"))
    check("Friday is off", not cal.is_working("2026-08-21"))
    check("Saturday is off", not cal.is_working("2026-08-22"))
    check("next_working rolls Friday to Sunday",
          iso(cal.next_working("2026-08-21")) == "2026-08-23",
          iso(cal.next_working("2026-08-21")))


def test_mon_fri_week():
    cal = sch.Calendar("Mon-Fri")
    check("Mon-Fri: Saturday is off", not cal.is_working("2026-08-22"))
    check("Mon-Fri: Sunday is off", not cal.is_working("2026-08-23"))
    check("Mon-Fri: Friday works", cal.is_working("2026-08-21"))


def test_duration_spans_the_weekend():
    tasks = [T("1.1", 5)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("a 5-day task starting Sunday ends Thursday",
          iso(tasks[0]["end_date"]) == "2026-08-20", iso(tasks[0]["end_date"]))

    tasks = [T("1.1", 7)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("a 7-day task jumps the Fri/Sat weekend",
          iso(tasks[0]["end_date"]) == "2026-08-24", iso(tasks[0]["end_date"]))


def test_chain_follows_previous():
    tasks = [T("1.1", 3), T("1.2", 2), T("1.3", 1)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("first task starts on the plan start", iso(tasks[0]["start_date"]) == START)
    check("second starts the working day after the first ends",
          iso(tasks[1]["start_date"]) == "2026-08-19", iso(tasks[1]["start_date"]))
    check("chain keeps running", iso(tasks[2]["start_date"]) == "2026-08-23",
          iso(tasks[2]["start_date"]))
    check("no task starts before it should",
          all(tasks[i]["end_date"] < tasks[i + 1]["start_date"] for i in range(2)))


def test_depends_on_overrides_the_chain():
    tasks = [T("1.1", 3), T("1.2", 10), T("1.3", 2, depends_on="1.1")]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("a dependent task follows its named predecessor, not the row above",
          tasks[2]["start_date"] <= tasks[1]["end_date"],
          f"{tasks[2]['start_date']} vs 1.2 ending {tasks[1]['end_date']}")
    check("it starts right after 1.1", iso(tasks[2]["start_date"]) == "2026-08-19",
          iso(tasks[2]["start_date"]))


def test_milestones_consume_no_calendar():
    tasks = [T("1.0", 0, is_milestone=1), T("1.1", 3), T("2.0", 0, is_milestone=1), T("2.1", 2)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("a milestone is a single day",
          tasks[0]["start_date"] == tasks[0]["end_date"])
    check("a milestone reports zero duration", tasks[0]["duration_days"] == 0)
    check("the task after a leading milestone still starts on day one",
          iso(tasks[1]["start_date"]) == START, iso(tasks[1]["start_date"]))
    check("a mid-plan milestone does not push the next task",
          iso(tasks[3]["start_date"]) == "2026-08-19", iso(tasks[3]["start_date"]))


def test_offset_pins_a_task():
    tasks = [T("1.1", 3), T("1.2", 2, start_offset_days=0)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("offset 0 pins a task to the plan start",
          iso(tasks[1]["start_date"]) == START, iso(tasks[1]["start_date"]))


def test_moving_the_start_date_moves_everything():
    tasks = [T("1.1", 3), T("1.2", 2)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    first = iso(tasks[1]["start_date"])
    sch.schedule(tasks, "2026-09-06", "Sun-Thu (KSA)")
    check("rescheduling shifts unlocked tasks", iso(tasks[1]["start_date"]) != first)
    check("and lands them on the new start",
          iso(tasks[0]["start_date"]) == "2026-09-06", iso(tasks[0]["start_date"]))


def test_locked_tasks_survive_a_reschedule():
    tasks = [T("1.1", 3), T("1.2", 2), T("1.3", 2)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    # consultant drags 1.2 out to a fixed date and locks it
    tasks[1]["start_date"] = frappe.utils.getdate("2026-09-01")
    tasks[1]["end_date"] = frappe.utils.getdate("2026-09-02")
    tasks[1]["locked"] = 1

    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    check("a locked task keeps its dates through a reschedule",
          iso(tasks[1]["start_date"]) == "2026-09-01", iso(tasks[1]["start_date"]))
    check("unlocked tasks around it still recompute",
          iso(tasks[0]["start_date"]) == START)
    check("the chain picks up from where the locked task actually ends",
          iso(tasks[2]["start_date"]) == "2026-09-03", iso(tasks[2]["start_date"]))


def test_holidays_are_skipped():
    global HOLIDAYS
    HOLIDAYS = [{"holiday_date": "2026-08-17"}]
    tasks = [T("1.1", 2)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)", holiday_list="KSA 2026")
    check("a holiday inside a task pushes its end date",
          iso(tasks[0]["end_date"]) == "2026-08-18", iso(tasks[0]["end_date"]))
    HOLIDAYS = []


def test_rollup():
    tasks = [T("1.1", 4), T("1.2", 6), T("2.0", 0, is_milestone=1)]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    tasks[0]["pct_complete"] = 100
    tasks[1]["pct_complete"] = 50
    totals = sch.rollup(tasks)
    check("total working days sums the real durations", totals["total_working_days"] == 10,
          totals["total_working_days"])
    check("completion is weighted by duration, not task count",
          totals["pct_complete"] == 70.0, totals["pct_complete"])
    check("plan end date is the latest task end",
          totals["end_date"] == max(t["end_date"] for t in tasks))


def test_real_template_schedules_cleanly():
    """The shipped SAMA template, dated end to end."""
    from alphax_grc.pathway.plans import TEMPLATES

    sama = next(t for t in TEMPLATES if t["framework"] == "SAMA CSF")
    tasks = [
        T(wbs, days, is_milestone=1 if days == 0 else 0, depends_on=dep or None)
        for wbs, _title, days, _role, _phase, dep in sama["tasks"]
    ]
    sch.schedule(tasks, START, "Sun-Thu (KSA)")
    totals = sch.rollup(tasks)

    check("every SAMA task got dates", all(t.get("start_date") for t in tasks))
    check("no task ends before it starts",
          all(t["end_date"] >= t["start_date"] for t in tasks))
    check("plan runs a realistic length", 150 <= totals["total_working_days"] <= 400,
          totals["total_working_days"])
    check("every dated day is a working day",
          all(sch.Calendar("Sun-Thu (KSA)").is_working(t["start_date"]) for t in tasks))

    wbs = [t["wbs"] for t in tasks]
    check("template WBS codes are unique", len(wbs) == len(set(wbs)),
          [w for w in wbs if wbs.count(w) > 1])
    deps = [d for d in (t.get("depends_on") for t in tasks) if d]
    check("every depends_on points at a real WBS", all(d in set(wbs) for d in deps), deps)


def test_all_templates_are_well_formed():
    from alphax_grc.pathway.plans import TEMPLATES

    check("the full template library ships", len(TEMPLATES) == 15, len(TEMPLATES))
    problems = []
    for tpl in TEMPLATES:
        wbs = [t[0] for t in tpl["tasks"]]
        if len(wbs) != len(set(wbs)):
            problems.append(f"{tpl['name']}: duplicate WBS")
        for row in tpl["tasks"]:
            if len(row) != 6:
                problems.append(f"{tpl['name']}: malformed row {row[0]}")
            if row[2] < 0:
                problems.append(f"{tpl['name']}: negative duration at {row[0]}")
            if row[5] and row[5] not in wbs:
                problems.append(f"{tpl['name']}: {row[0]} depends on missing {row[5]}")
    check("no structural problems in any template", not problems, problems)


LEGAL_ROLES = {"", "Project Manager", "GRC Consultant", "CISO", "IT Manager", "Internal Audit",
               "HR", "Legal", "Business Owner", "External Auditor", "Client"}


def test_every_template_schedules_and_is_consistent():
    """Date all 15 templates end to end and check the library conventions."""
    from alphax_grc.pathway.plans import TEMPLATES

    problems, summary = [], []
    for tpl in TEMPLATES:
        rows = tpl["tasks"]
        wbs = [r[0] for r in rows]

        if len(wbs) != len(set(wbs)):
            problems.append(f"{tpl['name']}: duplicate WBS")
        for r in rows:
            if r[5] and r[5] not in wbs:
                problems.append(f"{tpl['name']}: {r[0]} depends on missing {r[5]}")
            if r[5] == r[0]:
                problems.append(f"{tpl['name']}: {r[0]} depends on itself")
            if r[2] < 0:
                problems.append(f"{tpl['name']}: negative duration at {r[0]}")
            if r[3] not in LEGAL_ROLES:
                problems.append(f"{tpl['name']}: unknown role '{r[3]}' at {r[0]}")
            if not r[4]:
                problems.append(f"{tpl['name']}: {r[0]} has no phase")
        if len(rows) < 12:
            problems.append(f"{tpl['name']}: only {len(rows)} tasks")
        if not any(r[2] == 0 for r in rows):
            problems.append(f"{tpl['name']}: no milestone or phase header")
        if not tpl.get("source"):
            problems.append(f"{tpl['name']}: no source reference")

        tasks = [T(w, d, is_milestone=1 if d == 0 else 0, depends_on=dep or None)
                 for w, _t, d, _r, _p, dep in rows]
        sch.schedule(tasks, START, "Sun-Thu (KSA)")
        totals = sch.rollup(tasks)
        if not all(t.get("start_date") for t in tasks):
            problems.append(f"{tpl['name']}: some tasks did not get dates")
        if any(t["end_date"] < t["start_date"] for t in tasks):
            problems.append(f"{tpl['name']}: a task ends before it starts")
        summary.append((tpl["name"], len(rows), totals["total_working_days"]))

    check("every template in the library schedules cleanly", not problems, problems[:6])
    check("each plan has a sensible length",
          all(10 <= days <= 400 for _n, _c, days in summary),
          [(n, d) for n, _c, d in summary if not 10 <= d <= 400])


ENGAGEMENT_TYPES = {"Standard NCA Engagement", "Aramco CCC Pursuit", "ISO 27001 Certification",
                    "ISO 42001 AI Governance", "Managed Compliance (ongoing)",
                    "GDPR Compliance", "Custom"}


def test_engagement_types_match_the_base_app():
    """A template tagged with a type the Engagement doctype doesn't offer can
    never be matched to an engagement."""
    import json as _json
    from alphax_grc.pathway.plans import TEMPLATES

    schema = _json.load(open(os.path.join(
        ROOT, "alphax_grc/alphax_grc/doctype/grc_engagement/grc_engagement.json")))
    options = {o for o in next(
        f for f in schema["fields"] if f["fieldname"] == "engagement_type"
    )["options"].split("\n") if o}

    check("the expected engagement types are what the base app ships",
          options == ENGAGEMENT_TYPES, sorted(options ^ ENGAGEMENT_TYPES))

    used = {t["engagement_type"] for t in TEMPLATES}
    check("every template's engagement type is selectable on GRC Engagement",
          not (used - options), sorted(used - options))
    check("the common engagement types have a template",
          {"Standard NCA Engagement", "ISO 27001 Certification", "Aramco CCC Pursuit"} <= used,
          sorted(used))


def test_library_covers_the_frameworks_the_app_assesses():
    from alphax_grc.pathway.plans import TEMPLATES

    frameworks = {t["framework"] for t in TEMPLATES}
    expected = {"SAMA CSF", "NCA ECC-2:2024", "ISO 27001:2022", "ISO 22301", "ISO 42001",
                "SDAIA PDPL", "PCI DSS", "NIST CSF 2.0", "Aramco SACS-002", "General"}
    check("a plan exists for every framework the app assesses against",
          not (expected - frameworks), sorted(expected - frameworks))
    check("template names are unique",
          len({t["name"] for t in TEMPLATES}) == len(TEMPLATES))
    check("general-purpose engagement plans are included",
          len([t for t in TEMPLATES if t["framework"] == "General"]) >= 5)


def test_phase_headers_do_not_inflate_the_schedule():
    """A 1.0-style header must add no days to the plan."""
    from alphax_grc.pathway.plans import TEMPLATES

    tpl = next(t for t in TEMPLATES if t["name"].startswith("Cybersecurity Gap"))
    rows = tpl["tasks"]
    with_headers = [T(w, d, is_milestone=1 if d == 0 else 0) for w, _t, d, _r, _p, _dep in rows]
    without = [T(w, d) for w, _t, d, _r, _p, _dep in rows if d > 0]
    sch.schedule(with_headers, START, "Sun-Thu (KSA)")
    sch.schedule(without, START, "Sun-Thu (KSA)")
    check("headers add no working days to the plan",
          sch.rollup(with_headers)["total_working_days"] == sch.rollup(without)["total_working_days"])
    check("and no calendar time either",
          sch.rollup(with_headers)["end_date"] == sch.rollup(without)["end_date"],
          f"{sch.rollup(with_headers)['end_date']} vs {sch.rollup(without)['end_date']}")


def main():
    for fn in [test_ksa_week_skips_fri_sat, test_mon_fri_week, test_duration_spans_the_weekend,
               test_chain_follows_previous, test_depends_on_overrides_the_chain,
               test_milestones_consume_no_calendar, test_offset_pins_a_task,
               test_moving_the_start_date_moves_everything,
               test_locked_tasks_survive_a_reschedule, test_holidays_are_skipped,
               test_rollup, test_real_template_schedules_cleanly,
               test_all_templates_are_well_formed,
               test_every_template_schedules_and_is_consistent,
               test_engagement_types_match_the_base_app,
               test_library_covers_the_frameworks_the_app_assesses,
               test_phase_headers_do_not_inflate_the_schedule]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"raised {e!r}\n{traceback.format_exc()}")

    passed = sum(1 for _l, ok, _d in RESULTS if ok)
    for label, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"   [{detail}]" if not ok else ""))
    print(f"\n{passed}/{len(RESULTS)} scheduler checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
