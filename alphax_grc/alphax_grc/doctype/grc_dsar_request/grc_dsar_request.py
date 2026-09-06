"""GRC DSAR Request — PDPL data subject request workflow.

Auto-sets due_date to received_date + 30 days per PDPL Implementing
Regulation. Flags overdue when due_date is past and status not yet
Closed/Responded. Computes days_to_respond when responded.
"""

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, getdate, date_diff


# PDPL Implementing Regulation — 30 day response window
PDPL_RESPONSE_WINDOW_DAYS = 30


class GRCDSARRequest(Document):
    def validate(self):
        # Auto-set due_date from received_date
        if self.received_date and not self.due_date:
            self.due_date = add_days(self.received_date,
                                      PDPL_RESPONSE_WINDOW_DAYS)
        # If received_date changed, recompute due_date
        if self.has_value_changed("received_date") and self.received_date:
            self.due_date = add_days(self.received_date,
                                      PDPL_RESPONSE_WINDOW_DAYS)

        # Compute is_overdue flag
        terminal_statuses = {"Responded", "Closed", "Declined", "Withdrawn"}
        if self.due_date and self.status not in terminal_statuses:
            try:
                today_d = getdate(today())
                due_d = getdate(self.due_date)
                self.is_overdue = 1 if today_d > due_d else 0
            except Exception:
                self.is_overdue = 0
        else:
            self.is_overdue = 0

        # Compute days_to_respond when responded_date set
        if self.responded_date and self.received_date:
            try:
                self.days_to_respond = date_diff(
                    self.responded_date, self.received_date)
            except Exception:
                pass

        # Auto-set verification_date when identity_verified flips on
        if (self.has_value_changed("data_subject_id_verified")
                and self.data_subject_id_verified
                and not self.verification_date):
            self.verification_date = today()
