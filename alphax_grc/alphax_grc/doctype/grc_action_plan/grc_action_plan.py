import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class GRCActionPlan(Document):
    def validate(self):
        pct = float(self.completion_pct or 0)
        pct = max(0.0, min(100.0, pct))
        self.completion_pct = pct
        if self.status == "Completed" and pct < 100:
            self.completion_pct = 100
        if self.status == "Completed" and not self.completed_date:
            self.completed_date = today()
        if self.due_date and getdate(self.due_date) < getdate(today()) \
                and self.status not in ("Completed", "On Hold"):
            frappe.msgprint(
                f"Action Plan '{self.action_title}' is overdue.",
                indicator="orange", alert=True
            )
