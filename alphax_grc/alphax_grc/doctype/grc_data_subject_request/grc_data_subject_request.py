
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


PDPL_RESPONSE_DAYS = 30


class GRCDataSubjectRequest(Document):
    def validate(self):
        if not self.received_on:
            self.received_on = getdate(today())
        self._set_due_date()

    def _set_due_date(self):
        """Auto-set PDPL-mandated 30-day response deadline if not already set."""
        if not self.due_date and self.received_on:
            self.due_date = add_days(getdate(self.received_on), PDPL_RESPONSE_DAYS)

        if self.due_date and getdate(self.due_date) < getdate(today()) and self.status not in ("Closed", "Rejected", "Responded"):
            frappe.msgprint(
                f"Data Subject Request response was due on {self.due_date}. "
                "PDPL requires a response within 30 days.",
                indicator="red",
                alert=True,
            )

    def before_insert(self):
        """DEPRECATED (v2.14.0): superseded by GRC DSAR Request, which carries
        identity verification, statutory clocks and fulfilment tracking.
        Blocking new records prevents requests being logged in two places and
        losing the SLA clock. Existing records remain readable; migration
        happens in patch v2_14_0_governance."""
        if frappe.flags.in_patch or frappe.flags.in_migrate or frappe.flags.in_install:
            return
        frappe.throw(frappe._(
            "GRC Data Subject Request is deprecated. Please use GRC DSAR Request "
            "instead - it tracks identity verification and statutory due dates."))
