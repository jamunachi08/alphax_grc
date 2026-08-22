import frappe
from frappe.model.document import Document


class GRCBusinessImpactAnalysis(Document):
    def validate(self):
        for field in ("financial_impact", "operational_impact", "regulatory_impact",
                      "reputational_impact", "customer_impact"):
            v = self.get(field)
            if v is not None and v != "":
                try:
                    iv = int(v)
                    if iv < 0 or iv > 5:
                        frappe.throw(f"Impact severity '{field}' must be between 0 and 5.")
                except (ValueError, TypeError):
                    frappe.throw(f"Impact severity '{field}' must be a number 1-5.")
        # RTO must be >= RPO logically (you can't recover to a point further back than your downtime)
        if self.rto_hours and self.rpo_hours:
            if self.rto_hours < 0 or self.rpo_hours < 0:
                frappe.throw("RTO and RPO must be non-negative.")
