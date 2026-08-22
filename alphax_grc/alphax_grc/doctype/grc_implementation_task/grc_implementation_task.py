import frappe
from frappe.model.document import Document
from frappe.utils import today


class GRCImplementationTask(Document):
    def validate(self):
        # Auto-set completed_date when status flips to Completed
        if self.has_value_changed("status"):
            if self.status == "Completed" and not self.completed_date:
                self.completed_date = today()
            elif self.status != "Completed":
                self.completed_date = None
