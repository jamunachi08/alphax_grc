import frappe
from frappe.model.document import Document


class GRCISO22301Catalog(Document):
    def validate(self):
        # Auto-fill section_label from section_number
        if self.section_number and not self.section_label:
            mapping = {
                "4 Context": "Context of the Organization",
                "5 Leadership": "Leadership",
                "6 Planning": "Planning",
                "7 Support": "Support",
                "8 Operation": "Operation",
                "9 Performance Evaluation": "Performance Evaluation",
                "10 Improvement": "Improvement",
            }
            self.section_label = mapping.get(self.section_number, "")
