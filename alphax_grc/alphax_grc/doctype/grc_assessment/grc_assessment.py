from frappe.model.document import Document
import frappe


class GRCAssessment(Document):
    def validate(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw('End Date cannot be before Start Date.')
