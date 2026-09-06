import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class GRCNCAECCReviewCalendar(Document):
    def validate(self):
        if (self.next_scheduled
                and self.status == "Scheduled"
                and getdate(self.next_scheduled) < getdate(today())):
            self.status = "Overdue"
