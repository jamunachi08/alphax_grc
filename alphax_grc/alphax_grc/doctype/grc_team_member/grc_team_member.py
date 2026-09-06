import frappe
from frappe.model.document import Document


class GRCTeamMember(Document):
    def validate(self):
        # Sync email from linked Frappe user
        if self.user and not self.email:
            email = frappe.db.get_value("User", self.user, "email")
            if email:
                self.email = email
        # Auto-count assigned risks from Risk Register
        if self.user:
            self.risks_assigned = frappe.db.count(
                "GRC Risk Register", {"risk_owner": self.user}
            )
            self.responses_assigned = frappe.db.count(
                "GRC Action Plan", {"owner": self.user, "status": ["not in", ["Completed"]]}
            )
