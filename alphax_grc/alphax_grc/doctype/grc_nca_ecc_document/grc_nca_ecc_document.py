import frappe
from frappe.model.document import Document


class GRCNCAECCDocument(Document):
    def validate(self):
        # Auto-set approved_on when status flips to Approved
        if self.status == "Approved" and not self.approved_on:
            self.approved_on = frappe.utils.today()
