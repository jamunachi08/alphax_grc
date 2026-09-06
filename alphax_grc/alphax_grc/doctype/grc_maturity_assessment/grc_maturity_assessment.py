
from frappe.model.document import Document
import frappe


class GRCMaturityAssessment(Document):
    def validate(self):
        self.maturity_level = int(self.maturity_level or 0)
        if self.maturity_level < 0 or self.maturity_level > 5:
            frappe.throw("Maturity Level must be between 0 and 5.")
        self.weight = float(self.weight or 0)
        self.weighted_score = round(self.maturity_level * self.weight, 2)
