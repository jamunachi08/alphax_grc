
from frappe.model.document import Document
import frappe


class GRCEvidence(Document):
    def validate(self):
        if self.expiry_date and self.expiry_date < frappe.utils.getdate() and self.verification_status not in {"Archived", "Rejected"}:
            self.verification_status = "Expired"

        if self.verification_status == "Verified":
            if not self.attachment:
                frappe.throw("An attachment is required before marking evidence as Verified.")
            if not self.verified_on:
                self.verified_on = frappe.utils.getdate()
            if not self.verified_by:
                self.verified_by = frappe.session.user

        if self.review_due_date and self.review_due_date < frappe.utils.getdate() and self.verification_status not in {"Archived", "Rejected", "Expired"}:
            frappe.msgprint(
                f"Evidence review was due on {self.review_due_date}.",
                indicator="orange",
                alert=True,
            )
