# Copyright (c) 2026, Neotec Integrated Solutions
"""
Schedule engine for GRC Project Plan.

Turns a task list plus a start date into dated tasks, skipping non-working
days. Three ways a task can be positioned, checked in this order:

    start_offset_days   pinned N working days from the plan start
    depends_on          starts the working day after that WBS finishes
    (neither)           starts the working day after the previous task

`duration_days = 0` marks a milestone: it lands on a single day and consumes
none of the calendar.

Rescheduling preserves work already done: a task with `locked = 1` keeps its
dates, and anything chained behind it picks up from where it actually ends,
not from where the template said it would. That is what makes the plan
editable without the next regeneration throwing the edits away.
"""

from __future__ import annotations

import datetime

import frappe
from frappe.utils import add_days, getdate

# Which weekday numbers are days off. Python: Monday=0 ... Sunday=6.
WEEKEND_PATTERNS = {
	"Sun-Thu (KSA)": {4, 5},        # Friday, Saturday off
	"Mon-Fri": {5, 6},              # Saturday, Sunday off
	"Sat-Thu (6 day)": {4},         # Friday off
	"All days": set(),
}


def _holidays(holiday_list: str | None) -> set:
	if not holiday_list:
		return set()
	try:
		rows = frappe.get_all(
			"Holiday", filters={"parent": holiday_list}, fields=["holiday_date"], limit=500
		)
	except Exception:
		return set()
	return {getdate(r["holiday_date"]) for r in rows if r.get("holiday_date")}


class Calendar:
	def __init__(self, working_days: str = "Sun-Thu (KSA)", holiday_list: str | None = None):
		self.off = WEEKEND_PATTERNS.get(working_days, WEEKEND_PATTERNS["Sun-Thu (KSA)"])
		self.holidays = _holidays(holiday_list)

	def is_working(self, day) -> bool:
		day = getdate(day)
		return day.weekday() not in self.off and day not in self.holidays

	def next_working(self, day):
		"""The given day if it works, otherwise the next one that does."""
		day = getdate(day)
		for _ in range(400):
			if self.is_working(day):
				return day
			day = add_days(day, 1)
		return day

	def add_working_days(self, start, days: int):
		"""End date of a task starting on `start` and lasting `days` working days."""
		day = self.next_working(start)
		remaining = max(int(days or 0), 1) - 1
		while remaining > 0:
			day = self.next_working(add_days(day, 1))
			remaining -= 1
		return day

	def count_working_days(self, start, end) -> int:
		start, end = getdate(start), getdate(end)
		if end < start:
			return 0
		total, day = 0, start
		while day <= end:
			if self.is_working(day):
				total += 1
			day = add_days(day, 1)
		return total


def schedule(tasks: list[dict], start_date, working_days: str = "Sun-Thu (KSA)",
			 holiday_list: str | None = None, respect_locked: bool = True) -> list[dict]:
	"""Date every task in order. Returns the same dicts, dated.

	`tasks` need: wbs, duration_days, and optionally depends_on,
	start_offset_days, is_milestone, locked, start_date, end_date.
	"""
	cal = Calendar(working_days, holiday_list)
	plan_start = cal.next_working(getdate(start_date))

	ends: dict[str, datetime.date] = {}
	previous_end = None

	for task in tasks:
		duration = int(task.get("duration_days") or 0)
		milestone = bool(task.get("is_milestone")) or duration == 0

		if respect_locked and task.get("locked") and task.get("start_date"):
			# Honour the dates a human set, and let the chain continue from them.
			task_start = getdate(task["start_date"])
			task_end = getdate(task.get("end_date") or task_start)
		else:
			offset = task.get("start_offset_days")
			depends = (task.get("depends_on") or "").strip()

			if offset not in (None, ""):
				task_start = plan_start if int(offset) <= 0 else cal.add_working_days(
					plan_start, int(offset) + 1
				)
			elif depends and depends in ends:
				# A milestone marks the completion of what it follows, so it
				# lands on that day rather than the day after — otherwise a
				# closing milestone pushes the plan end date out by a day.
				task_start = (
					cal.next_working(ends[depends]) if milestone
					else cal.next_working(add_days(ends[depends], 1))
				)
			elif previous_end:
				task_start = (
					cal.next_working(previous_end) if milestone
					else cal.next_working(add_days(previous_end, 1))
				)
			else:
				task_start = plan_start

			task_end = task_start if milestone else cal.add_working_days(task_start, duration)

		task["start_date"] = task_start
		task["end_date"] = task_end
		task["duration_days"] = 0 if milestone else cal.count_working_days(task_start, task_end)
		if task.get("wbs"):
			ends[task["wbs"]] = task_end

		# A milestone (and a summary row like "1.0") marks a point rather than
		# occupying the calendar, so it must not advance the chain: the task
		# after it starts where the last real piece of work finished.
		if not milestone:
			previous_end = task_end

	return tasks


def rollup(tasks: list[dict]) -> dict:
	"""Plan-level end date, working-day total, and weighted completion."""
	dated = [t for t in tasks if t.get("start_date") and t.get("end_date")]
	if not dated:
		return {"end_date": None, "total_working_days": 0, "pct_complete": 0}

	end = max(getdate(t["end_date"]) for t in dated)
	start = min(getdate(t["start_date"]) for t in dated)

	weighted = [t for t in dated if int(t.get("duration_days") or 0) > 0]
	total_days = sum(int(t["duration_days"]) for t in weighted)
	if total_days:
		done = sum(int(t["duration_days"]) * float(t.get("pct_complete") or 0) for t in weighted)
		pct = round(done / total_days, 1)
	else:
		pct = round(sum(float(t.get("pct_complete") or 0) for t in dated) / len(dated), 1)

	return {
		"start_date": start,
		"end_date": end,
		"total_working_days": total_days,
		"pct_complete": pct,
	}
