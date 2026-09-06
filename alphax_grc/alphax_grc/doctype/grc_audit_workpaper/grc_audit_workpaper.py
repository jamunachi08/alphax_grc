
from frappe.model.document import Document
import frappe


class GRCAuditWorkpaper(Document):
    def validate(self):
        if self.sample_size and self.sample_size < 0:
            frappe.throw("Sample Size cannot be negative.")
