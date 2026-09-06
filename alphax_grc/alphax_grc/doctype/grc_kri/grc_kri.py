import frappe
from frappe.model.document import Document


class GRCKRI(Document):
    def validate(self):
        self._evaluate_threshold()

    def _evaluate_threshold(self):
        """Auto-set status based on current vs threshold value."""
        try:
            current = float(self.current_value or 0)
            threshold = float(self.threshold_value or 0)
        except (ValueError, TypeError):
            return  # non-numeric KRIs managed manually

        if threshold <= 0:
            return

        ratio = current / threshold
        if ratio >= 1.0:
            new_status = "Breach"
        elif ratio >= 0.85:
            new_status = "Warn"
        elif ratio >= 0.70:
            new_status = "Alert"
        else:
            new_status = "OK"

        if self.status != new_status:
            self.status = new_status
            if new_status == "Breach":
                frappe.msgprint(
                    f"KRI Breach: '{self.indicator_name}' has exceeded threshold "
                    f"({self.current_value} / {self.threshold_value}). "
                    "Consider raising an incident or escalating the linked risk.",
                    indicator="red",
                    title="KRI Threshold Breached",
                )
            elif new_status == "Warn":
                frappe.msgprint(
                    f"KRI Warning: '{self.indicator_name}' is approaching threshold "
                    f"({self.current_value} / {self.threshold_value}).",
                    indicator="orange",
                    alert=True,
                )
