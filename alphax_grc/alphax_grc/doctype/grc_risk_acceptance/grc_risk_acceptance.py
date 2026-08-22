
from frappe.model.document import Document
import frappe


class GRCRiskAcceptance(Document):
    def validate(self):
        if self.acceptance_type == "Temporary" and not self.expiry_date:
            frappe.msgprint("Temporary risk acceptance should normally include an Expiry Date.")
        if self.approval_date and self.expiry_date and self.expiry_date < self.approval_date:
            frappe.throw("Expiry Date cannot be earlier than Approval Date.")
        if self.expiry_date and self.expiry_date < frappe.utils.getdate() and self.status == "Accepted":
            self.status = "Expired"
