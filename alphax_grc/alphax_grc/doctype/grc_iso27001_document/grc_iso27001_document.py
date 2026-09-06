import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_months


class GRCISO27001Document(Document):
    def validate(self):
        if not self.next_review and self.last_reviewed:
            self.next_review = str(add_months(getdate(self.last_reviewed), 12))
        if self.status == 'Published' and not self.last_reviewed:
            self.last_reviewed = today()
