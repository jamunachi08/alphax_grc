import frappe
from frappe.model.document import Document


class GRCGDPRControl(Document):
    def validate(self):
        # Auto-set last_assessed when status changes
        if self.has_value_changed("compliance_status"):
            self.last_assessed = frappe.utils.today()
