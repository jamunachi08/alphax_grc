import frappe
from frappe.model.document import Document


class GRCPolicy(Document):
    def validate(self):
        self._sync_acknowledgement_fields()
        self._set_published_on()
        self._warn_overdue_review()
        self._validate_dates()

    def _sync_acknowledgement_fields(self):
        """Fix duplicate field: keep acknowledgement_required canonical, mirror to legacy."""
        if self.acknowledgement_required and not self.acknowledgment_required:
            self.acknowledgment_required = 1
        elif self.acknowledgment_required and not self.acknowledgement_required:
            self.acknowledgement_required = 1

    def _set_published_on(self):
        if self.publication_status == "Published" and not self.published_on:
            self.published_on = frappe.utils.getdate()

    def _warn_overdue_review(self):
        if (
            self.review_due_date
            and self.review_due_date < frappe.utils.getdate()
            and self.status not in ("Retired",)
        ):
            frappe.msgprint(
                f"Policy review was due on {self.review_due_date}. Please schedule a review.",
                indicator="orange",
                alert=True,
            )

    def _validate_dates(self):
        if self.effective_date and self.review_due_date:
            if self.review_due_date < self.effective_date:
                frappe.throw("Review Due Date cannot be before Effective Date.")
