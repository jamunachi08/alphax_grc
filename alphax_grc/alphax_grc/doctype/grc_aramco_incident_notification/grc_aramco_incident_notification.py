
import frappe
from frappe.model.document import Document

class GRCAramcoIncidentNotification(Document):
    def validate(self):
        if hasattr(self, "coverage_score") and self.coverage_score is not None:
            self.coverage_score = max(0, min(float(self.coverage_score or 0), 100))
