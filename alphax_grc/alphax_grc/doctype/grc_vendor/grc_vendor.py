import frappe
from frappe.model.document import Document
from frappe.utils import add_months, add_days, getdate, today


REVIEW_MONTHS = {
    "Monthly": 1,
    "Quarterly": 3,
    "Half-Yearly": 6,
    "Yearly": 12,
}


class GRCVendor(Document):
    def validate(self):
        self._set_next_review_date()
        self._handle_blocked_status()

    def _set_next_review_date(self):
        if self.review_frequency and not self.next_review_date:
            months = REVIEW_MONTHS.get(self.review_frequency, 12)
            self.next_review_date = add_months(getdate(today()), months)

    def _handle_blocked_status(self):
        if self.blocked_vendor and self.status not in ("Blocked", "Inactive"):
            self.status = "Blocked"
        if self.status == "Blocked" and not self.blocked_vendor:
            self.blocked_vendor = 1
