import frappe
from frappe.model.document import Document


class GRCFramework(Document):
    def validate(self):
        if not self.framework_name:
            frappe.throw("Framework Name is required.")
        if not self.effective_from:
            self.effective_from = frappe.utils.getdate()
