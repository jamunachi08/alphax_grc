from frappe.model.document import Document
import frappe


class GRCAuditFinding(Document):
    def validate(self):
        if self.status in {"Verified", "Closed"} and not self.closure_evidence:
            frappe.msgprint("Closure evidence is recommended before verification or closure.")
        if self.status == "Closed" and not self.closed_on:
            self.closed_on = frappe.utils.now_datetime()
        if self.due_date and self.closed_on and str(self.closed_on.date()) < str(self.due_date):
            pass
