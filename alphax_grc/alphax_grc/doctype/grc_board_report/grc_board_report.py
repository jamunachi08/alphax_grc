
import frappe
from frappe.model.document import Document


class GRCBoardReport(Document):
    def validate(self):
        if not self.prepared_by:
            self.prepared_by = frappe.session.user
        self._auto_populate_metrics()

    def _auto_populate_metrics(self):
        """Pull live KPIs from the GRC data layer to populate the report."""
        def _count(doctype, filters=None):
            if not frappe.db.exists("DocType", doctype):
                return 0
            return frappe.db.count(doctype, filters or {})

        def _avg(doctype, fieldname, filters=None):
            if not frappe.db.exists("DocType", doctype):
                return 0
            values = frappe.get_all(doctype, filters=filters or {}, pluck=fieldname)
            numbers = [float(v) for v in values if v not in (None, "")]
            return round(sum(numbers) / len(numbers), 2) if numbers else 0

        self.open_risks = _count("GRC Risk Register", {
            "inherent_score": [">=", 15],
            "status": ["not in", ["Closed"]],
        })
        self.open_findings = _count("GRC Audit Finding", {
            "status": ["not in", ["Closed", "Verified"]],
        })
        self.compliance_score = _avg("GRC Assessment", "compliance_score")
        self.maturity_score = _avg("GRC Maturity Assessment", "maturity_level") * 20
        self.overdue_actions = _count("GRC Remediation Action", {
            "status": ["not in", ["Closed", "Verified"]],
            "due_date": ["<", frappe.utils.today()],
        })
