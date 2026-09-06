import frappe
from frappe.model.document import Document
from frappe.utils import today
from datetime import date


class GRCITGCAuditItem(Document):
    def validate(self):
        # Auto-set audit year
        if not self.audit_year:
            self.audit_year = date.today().year

        # Validate delivery vs files
        if self.delivery_status == 'Delivered' and not self.number_of_files:
            frappe.msgprint(
                "Artifacts marked as Delivered — please enter the number of files provided.",
                indicator="orange", alert=True
            )

        # Auto-set risk rating based on domain if not set
        if not self.risk_rating:
            high_risk_domains = ['GLBA Compliance', 'Network Security', 'Information Security Program']
            medium_risk_domains = ['Data Loss Prevention', 'Incident Response']
            if self.control_domain in high_risk_domains:
                self.risk_rating = 'High'
            elif self.control_domain in medium_risk_domains:
                self.risk_rating = 'Medium'
            else:
                self.risk_rating = 'Low'

        # Warn if overdue
        if self.delivery_status in ('Pending', 'Overdue') and self.review_status == 'Not Started':
            if self.delivery_status == 'Pending':
                frappe.msgprint(
                    f"Control item #{self.item_number} '{self.control_name}' is pending delivery.",
                    indicator="orange", alert=True
                )
