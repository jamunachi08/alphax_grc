import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class GRCISMSDocumentRegister(Document):
    def validate(self):
        if self.next_review_date and getdate(self.next_review_date) < getdate(today()) \
                and self.document_status in ("Published", "Approved"):
            frappe.msgprint(
                f"ISMS document '{self.document_title}' (Clause {self.clause_number}) "
                f"is overdue for review (was due {self.next_review_date}).",
                indicator="orange", alert=True
            )
