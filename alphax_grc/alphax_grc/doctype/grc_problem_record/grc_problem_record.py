import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class GRCProblemRecord(Document):
    def validate(self):
        if not self.reported_on:
            self.reported_on = today()
        if self.status in ("Resolved", "Closed") and not self.resolved_on:
            self.resolved_on = today()
        if self.root_cause_identified and not self.root_cause_analysis:
            frappe.msgprint(
                "Root Cause Identified is checked but RCA field is empty. Please document the root cause.",
                indicator="orange", alert=True
            )
        if self.target_resolution_date and getdate(self.target_resolution_date) < getdate(today()) \
                and self.status not in ("Resolved", "Closed"):
            frappe.msgprint(
                f"Problem resolution is overdue (target: {self.target_resolution_date}).",
                indicator="red", alert=True
            )
        # Auto-increment recurrence count from linked incident
        if self.linked_incident and not self.recurrence_count:
            existing = frappe.db.count("GRC Problem Record", {"linked_incident": self.linked_incident})
            self.recurrence_count = existing
