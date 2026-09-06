import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months


class GRCDetectionCoverage(Document):
    def validate(self):
        # Auto-set next_validation_due 6 months out if last_validated_date is set
        if self.has_value_changed("last_validated_date") and self.last_validated_date:
            if not self.next_validation_due:
                self.next_validation_due = add_months(self.last_validated_date, 6)
