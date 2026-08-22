"""GRC ISO27001 SOA — Statement of Applicability per-client tracker.

Captures applicability and implementation status per ISO 27001:2022
Annex A control. Catalog-side (the actual control text) is NOT
seeded in this app — control statements come from the client's
own certified copy of the standard. We track only:
  - control_code (e.g. 5.1)
  - control_title (e.g. Policies for information security)
  - applicable (Y/N/Under Review)
  - implemented (Y/N/Partial/In Progress/N/A)
  - justification for inclusion/exclusion
  - remarks (implementation overview)
"""

import frappe
from frappe.model.document import Document
from frappe.utils import today


class GRCISO27001SOA(Document):
    def validate(self):
        # When applicable=No, force implemented=Not Applicable for clarity
        if self.applicable == "No" and self.implemented not in (
                "Not Applicable", None, ""):
            self.implemented = "Not Applicable"

        # Stamp last_assessed when applicable or implemented changes
        if self.has_value_changed("applicable") or self.has_value_changed("implemented"):
            self.last_assessed = today()

        # Auto-set implementation_score baselines
        if self.has_value_changed("implemented"):
            score_map = {
                "Yes": 100,
                "Partial": 50,
                "In Progress": 25,
                "No": 0,
                "Not Applicable": 0,
            }
            if self.implemented in score_map:
                # Only auto-set if user hasn't deliberately set a different value
                if not self.implementation_score or self.implementation_score in (0, 25, 50, 100):
                    self.implementation_score = score_map[self.implemented]
