
from frappe.model.document import Document
import frappe


class GRCException(Document):
    def validate(self):
        if self.approval_date and self.expiry_date and self.expiry_date < self.approval_date:
            frappe.throw("Expiry Date cannot be earlier than Approval Date.")
        if self.expiry_date and self.expiry_date < frappe.utils.getdate():
            if self.status in {"Approved", "Active"}:
                self.status = "Expired"
