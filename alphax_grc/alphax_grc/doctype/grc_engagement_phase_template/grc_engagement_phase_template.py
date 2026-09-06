import frappe
from frappe.model.document import Document


class GRCEngagementPhaseTemplate(Document):
    def validate(self):
        if self.phase_number is not None and self.phase_number < 1:
            frappe.throw("Phase number must be at least 1")
