import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


SLA_HOURS = {
    "Critical": 4,
    "High": 24,
    "Medium": 72,
    "Low": 168,
}


class GRCIncident(Document):
    def validate(self):
        if not self.reported_on:
            self.reported_on = now_datetime()
        self._set_sla_due_date()
        self._set_sama_reportable()

    def _set_sama_reportable(self):
        """SAMA CSF 3.3.15.5 — a Medium or High classified incident must be
        reported to SAMA IT Risk Supervision immediately on identification."""
        if not self.meta.get_field("sama_reportable"):
            return
        classification = self.get("sama_classification") or self.severity
        self.sama_reportable = 1 if classification in ("Medium", "High", "Critical") else 0

    def _set_sla_due_date(self):
        if self.sla_due_date:
            return
        hours = SLA_HOURS.get(self.severity, 72)
        base = self.reported_on or now_datetime()
        self.sla_due_date = add_to_date(base, hours=hours)
