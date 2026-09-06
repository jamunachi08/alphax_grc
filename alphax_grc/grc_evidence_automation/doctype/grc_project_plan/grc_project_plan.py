# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document

from alphax_grc.pathway.scheduler import Calendar, rollup, schedule


class GRCProjectPlan(Document):
	def validate(self):
		self.apply_defaults()
		self.recalculate()
		self.compute_evm()

	def apply_defaults(self):
		"""Fill what can be inferred so a plan is usable straight from a template."""
		if not self.start_date:
			self.start_date = frappe.utils.nowdate()

		if self.template:
			template = frappe.get_cached_doc("GRC Plan Template", self.template)
			if not self.plan_title:
				self.plan_title = f"{template.template_name} — {self.client}" if self.client \
					else template.template_name
			if not self.working_days and template.get("default_working_days"):
				self.working_days = template.default_working_days

		if not self.working_days:
			self.working_days = "Sun-Thu (KSA)"

	def recalculate(self):
		"""Re-date every unlocked task, then roll the totals up.

		Runs on every save, so editing a duration in the grid pushes the
		tasks behind it automatically while locked rows stay put.
		"""
		if not self.start_date or not self.get("tasks"):
			return

		rows = [t.as_dict() for t in self.get("tasks")]
		schedule(rows, self.start_date, self.working_days, self.holiday_list)

		for row, dated in zip(self.get("tasks"), rows):
			row.start_date = dated["start_date"]
			row.end_date = dated["end_date"]
			row.duration_days = dated["duration_days"]
			if row.pct_complete and row.pct_complete >= 100 and row.status != "Complete":
				row.status = "Complete"

		totals = rollup(rows)
		self.end_date = totals["end_date"]
		self.total_working_days = totals["total_working_days"]
		self.pct_complete = totals["pct_complete"]

	def compute_evm(self):
		"""v2.10.0 — cost/schedule performance, standard PMI formulas.

		Only runs when a Budget at Completion is set - plans that don't
		track budget (many engagement plans won't) simply skip this and
		keep the schedule-only view they had before.

		Actual Cost is pulled from GRC Consultant Timesheet rather than
		entered by hand: timesheets already link back to a plan via
		reference_doctype/reference_name, so this is real cost data you're
		already capturing, not a second place to maintain it.
		"""
		if not self.budget_at_completion:
			self.planned_pct_complete = 0
			self.actual_cost = 0
			self.cost_performance_index = 0
			self.schedule_performance_index = 0
			self.estimate_at_completion = 0
			return

		self.planned_pct_complete = self._planned_pct_complete()
		self.actual_cost = self._actual_cost_from_timesheets()

		bac = frappe.utils.flt(self.budget_at_completion)
		ev = bac * frappe.utils.flt(self.pct_complete) / 100.0
		pv = bac * frappe.utils.flt(self.planned_pct_complete) / 100.0
		ac = frappe.utils.flt(self.actual_cost)

		cpi = (ev / ac) if ac > 0 else 1.0
		spi = (ev / pv) if pv > 0 else 1.0
		eac = (bac / cpi) if cpi > 0 else bac

		self.cost_performance_index = round(cpi, 2)
		self.schedule_performance_index = round(spi, 2)
		self.estimate_at_completion = round(eac, 2)

	def _planned_pct_complete(self):
		"""Where the schedule says we should be today.

		Elapsed *working* days over total working days, using the same
		calendar (working week + holiday list) the scheduler dated the tasks
		with. Calendar days would overstate planned progress on every weekend
		and holiday and make SPI look better than it is.
		"""
		if not self.start_date or not self.total_working_days:
			return 0

		today = frappe.utils.getdate()
		start = frappe.utils.getdate(self.start_date)
		if today <= start:
			return 0
		if self.end_date and today >= frappe.utils.getdate(self.end_date):
			return 100

		cal = Calendar(self.working_days, self.holiday_list)
		elapsed = cal.count_working_days(start, today)
		return round(min(elapsed / int(self.total_working_days), 1.0) * 100, 2)

	def _actual_cost_from_timesheets(self):
		return frappe.db.get_value(
			"GRC Consultant Timesheet",
			{
				"reference_doctype": "GRC Project Plan",
				"reference_name": self.name,
				"billable": 1,
			},
			"sum(amount)",
		) or 0

	@frappe.whitelist()
	def load_template(self, overwrite: int = 0):
		"""Copy the template's tasks in. Refuses to silently discard work."""
		if not self.template:
			frappe.throw("Pick a plan template first.")
		if self.get("tasks") and not frappe.utils.cint(overwrite):
			frappe.throw(
				"This plan already has tasks. Re-loading the template replaces them — "
				"call load_template with overwrite=1 if that is what you want."
			)

		template = frappe.get_doc("GRC Plan Template", self.template)
		self.set("tasks", [])
		for t in template.get("tasks") or []:
			self.append("tasks", {
				"wbs": t.wbs,
				"task_title": t.task_title,
				"duration_days": t.duration_days,
				"responsible_role": t.responsible_role,
				"depends_on": t.depends_on,
				"phase": t.phase,
				"is_milestone": t.is_milestone,
				"deliverable": t.deliverable,
				"control_reference": t.control_reference,
				"status": "Not Started",
				"pct_complete": 0,
			})
		self.recalculate()
		return len(self.get("tasks"))
