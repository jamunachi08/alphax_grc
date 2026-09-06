
import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today


class GRCVendorAssessment(Document):
    def validate(self):
        self._compute_risk_level()
        self._set_next_review_date()

    def after_save(self):
        self._push_score_to_vendor()

    def _compute_risk_level(self):
        """Derive risk_level from average of security and compliance scores."""
        scores = [s for s in [self.security_score, self.compliance_score] if s is not None]
        if not scores:
            return
        avg = sum(float(s) for s in scores) / len(scores)
        if avg >= 85:
            self.risk_level = "Low"
        elif avg >= 65:
            self.risk_level = "Medium"
        elif avg >= 40:
            self.risk_level = "High"
        else:
            self.risk_level = "Critical"

    def _set_next_review_date(self):
        if not self.next_review_date:
            self.next_review_date = add_months(getdate(today()), 12)

    def _push_score_to_vendor(self):
        """Write the latest assessment score back to the parent Vendor record."""
        if not self.vendor:
            return
        avg_score = None
        scores = [s for s in [self.security_score, self.compliance_score] if s is not None]
        if scores:
            avg_score = round(sum(float(s) for s in scores) / len(scores), 2)
        if avg_score is not None and frappe.db.exists("GRC Vendor", self.vendor):
            frappe.db.set_value("GRC Vendor", self.vendor, {
                "last_assessment_score": avg_score,
                "assessment_score": avg_score,
                "next_assessment_date": self.next_review_date,
            })
