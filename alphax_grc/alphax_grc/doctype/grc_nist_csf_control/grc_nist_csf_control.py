import frappe
from frappe.model.document import Document


class GRCNISTCSFControl(Document):
    def validate(self):
        if self.has_value_changed("implementation_tier"):
            self.last_assessed = frappe.utils.today()
