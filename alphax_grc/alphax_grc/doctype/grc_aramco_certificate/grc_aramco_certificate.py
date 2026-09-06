import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_to_date, date_diff


class GRCAramcoCertificate(Document):
    def validate(self):
        self._validate_dates()
        self._compute_derived_fields()

    def _validate_dates(self):
        if self.issue_date and self.expiry_date:
            if getdate(self.expiry_date) <= getdate(self.issue_date):
                frappe.throw("Expiry Date must be after Issue Date.")

    def _compute_derived_fields(self):
        if self.expiry_date:
            days = date_diff(self.expiry_date, today())
            self.days_to_expiry = days
            # Renewal kickoff = 180 days before expiry
            self.renewal_kickoff_date = add_to_date(self.expiry_date, days=-180)
            # Auto-status from days
            if self.status != "Revoked":
                if days < 0:
                    self.status = "Expired"
                elif days <= 30:
                    self.status = "Expiring Soon"
                elif days <= 90 and self.renewal_status in (None, "", "Not Started"):
                    self.status = "Pending Renewal"
                else:
                    self.status = "Active"
