# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document


class GRCPlanTemplate(Document):
	def validate(self):
		self.check_wbs()
		self.roll_up()

	def check_wbs(self):
		"""A template with a broken WBS produces a broken schedule, so catch it
		here rather than in every plan generated from it."""
		seen, duplicates = set(), []
		for row in self.get("tasks") or []:
			if not row.wbs:
				frappe.throw(f"Row {row.idx}: every task needs a WBS number.")
			if row.wbs in seen:
				duplicates.append(row.wbs)
			seen.add(row.wbs)

			if (row.duration_days or 0) < 0:
				frappe.throw(f"WBS {row.wbs}: duration cannot be negative.")
			if not row.duration_days and not row.is_milestone:
				# A zero-day task is a milestone whether or not it was ticked.
				row.is_milestone = 1
			if row.is_milestone and row.duration_days:
				row.duration_days = 0

		if duplicates:
			frappe.throw("Duplicate WBS number(s): " + ", ".join(sorted(set(duplicates))))

		for row in self.get("tasks") or []:
			if row.depends_on and row.depends_on not in seen:
				frappe.throw(
					f"WBS {row.wbs} depends on {row.depends_on}, which is not in this template."
				)
			if row.depends_on == row.wbs:
				frappe.throw(f"WBS {row.wbs} cannot depend on itself.")

	def roll_up(self):
		tasks = self.get("tasks") or []
		self.task_count = len(tasks)
		self.indicative_duration_days = sum(int(t.duration_days or 0) for t in tasks)
		self.phase_count = len({t.phase for t in tasks if t.phase})

	@frappe.whitelist()
	def create_plan(self, client: str, start_date=None, engagement: str | None = None):
		"""Spin up a project plan from this template with the defaults filled in."""
		if not frappe.db.exists("GRC Client Profile", client):
			frappe.throw(f"Client {client} not found.")

		plan = frappe.new_doc("GRC Project Plan")
		plan.client = client
		plan.engagement = engagement
		plan.template = self.name
		plan.plan_title = f"{self.template_name} — {client}"
		plan.start_date = start_date or frappe.utils.nowdate()
		plan.working_days = self.default_working_days or "Sun-Thu (KSA)"
		plan.status = "Draft"
		plan.load_template()
		plan.insert(ignore_permissions=True)
		return plan.name
