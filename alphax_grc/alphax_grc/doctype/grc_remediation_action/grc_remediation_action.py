from frappe.model.document import Document
import frappe


class GRCRemediationAction(Document):
    def validate(self):
        pct = float(self.completion_percentage or 0)
        if pct < 0:
            pct = 0
        if pct > 100:
            pct = 100
        self.completion_percentage = pct
        if self.status in {"Resolved", "Verified", "Closed"} and pct < 100:
            self.completion_percentage = 100
        if self.status in {"Verified", "Closed"} and not self.verified_date:
            self.verified_date = frappe.utils.today()
