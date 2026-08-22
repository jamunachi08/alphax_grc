from frappe.model.document import Document
import frappe


class GRCControlLibrary(Document):
    def validate(self):
        self.maturity_level = int(self.maturity_level or 0)
        if self.maturity_level < 0:
            self.maturity_level = 0
        if self.maturity_level > 5:
            self.maturity_level = 5
        self.weight = float(self.weight or 0) or 1
        frameworks = []
        for row in self.framework_mappings or []:
            if row.framework and row.framework not in frameworks:
                frameworks.append(row.framework)
        if self.primary_framework and self.primary_framework not in frameworks:
            self.append('framework_mappings', {'framework': self.primary_framework})
