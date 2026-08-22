import frappe
from frappe.model.document import Document


class GRCPDPLControl(Document):
    def validate(self):
        if self.has_value_changed("compliance_status") and self.compliance_status:
            self.last_assessed = frappe.utils.today()
