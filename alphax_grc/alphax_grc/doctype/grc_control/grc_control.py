import frappe
from frappe.model.document import Document


class GRCControl(Document):
    def validate(self):
        if not self.control_id:
            frappe.throw("Control ID is required.")
        if not self.control_owner:
            frappe.msgprint(
                "No Control Owner assigned. Controls without owners cannot be effectively monitored.",
                indicator="orange",
                alert=True,
            )
