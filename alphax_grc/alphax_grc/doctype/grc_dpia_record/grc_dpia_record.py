"""GRC DPIA Record — Data Protection Impact Assessment.

Structured per PDPL Implementing Regulation Article 11 (DPIA threshold
and content) and informed by GDPR Article 35.

Auto-derives inherent_risk_level from likelihood × impact using the
same NIST SP 800-30 matrix as the CRQ doctype.
"""

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months


# Mirror of the CRQ matrix — intentional, for consistency
_RISK_MATRIX = {
    ("Very Low", "Very Low"):     "Low",
    ("Very Low", "Low"):          "Low",
    ("Very Low", "Medium"):       "Low",
    ("Very Low", "High"):         "Low",
    ("Very Low", "Very High"):    "Low",
    ("Low", "Very Low"):          "Low",
    ("Low", "Low"):               "Low",
    ("Low", "Medium"):             "Low",
    ("Low", "High"):              "Moderate",
    ("Low", "Very High"):         "Moderate",
    ("Medium", "Very Low"):       "Low",
    ("Medium", "Low"):            "Low",
    ("Medium", "Medium"):         "Moderate",
    ("Medium", "High"):           "Moderate",
    ("Medium", "Very High"):      "High",
    ("High", "Very Low"):         "Low",
    ("High", "Low"):              "Moderate",
    ("High", "Medium"):           "Moderate",
    ("High", "High"):             "High",
    ("High", "Very High"):        "Very High",
    ("Very High", "Very Low"):    "Low",
    ("Very High", "Low"):         "Moderate",
    ("Very High", "Medium"):      "High",
    ("Very High", "High"):        "Very High",
    ("Very High", "Very High"):   "Very High",
}


class GRCDPIARecord(Document):
    def validate(self):
        # Auto-classify inherent risk
        if self.likelihood and self.impact:
            self.inherent_risk_level = _RISK_MATRIX.get(
                (self.likelihood, self.impact), "Low")

        # Default residual to inherent if not set
        if not self.residual_risk_level and self.inherent_risk_level:
            self.residual_risk_level = self.inherent_risk_level

        # If High or Very High inherent risk, mark as high-risk
        if self.inherent_risk_level in ("High", "Very High"):
            self.is_high_risk = 1

        # Auto-set next review due 12 months from dpia_date if approved
        if (self.has_value_changed("status")
                and self.status == "Approved"
                and self.dpia_date
                and not self.next_review_due):
            self.next_review_due = add_months(self.dpia_date, 12)
