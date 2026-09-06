import frappe
from frappe.model.document import Document


class GRCPolicyVersion(Document):
    def validate(self):
        # v2.10.0 — a published version is a point-in-time record of what a
        # policy said; if this doctype ever gets an unrestricted "create"
        # permission granted later, no edits are still allowed past insert.
        if not self.is_new():
            frappe.throw("Policy Versions are immutable and cannot be edited after publication.")

    def on_trash(self):
        frappe.throw("Policy Versions cannot be deleted — they are the compliance record of what was published.")
