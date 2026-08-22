import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class GRCTechnologyControl(Document):
    def validate(self):
        if self.next_review_date and getdate(self.next_review_date) < getdate(today()) \
                and self.implementation_status == "Implemented":
            frappe.msgprint(
                f"Technology control '{self.control_name}' review is overdue.",
                indicator="orange", alert=True
            )
