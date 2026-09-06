from frappe.model.document import Document
import frappe


class GRCAuditPlan(Document):
    def validate(self):
        if self.planned_start_date and self.planned_end_date and self.planned_start_date > self.planned_end_date:
            frappe.throw('Planned End Date cannot be before Planned Start Date.')
