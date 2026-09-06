import frappe
from frappe.model.document import Document


class GRCRiskControlMatrix(Document):
    def validate(self):
        if self.status == "Approved" and not self.approval_date:
            self.approval_date = frappe.utils.today()
