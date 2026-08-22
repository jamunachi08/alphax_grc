import frappe
from frappe.model.document import Document


class GRCEvidenceRuleEvaluation(Document):
    def validate(self):
        # v2.10.0 — these records exist to prove what an automated control
        # check found at a point in time; editing one after creation would
        # defeat that purpose, so only creation is allowed.
        if not self.is_new():
            frappe.throw("Evidence Rule Evaluations are immutable and cannot be edited after creation.")

    def on_trash(self):
        frappe.throw("Evidence Rule Evaluations cannot be deleted — they are the evidence trail.")


@frappe.whitelist()
def verify_rule_chain(rule: str) -> dict:
    """Re-walk the full evaluation history for a rule and confirm nothing
    was altered after the fact. Surfaced on the GRC Evidence Rule form so an
    auditor can check integrity with one click before relying on the log."""
    from alphax_grc.integrity import verify_chain

    return verify_chain(
        "GRC Evidence Rule Evaluation",
        {"rule": rule},
        part_fields=["rule", "evaluated_at", "pass_count", "fail_count", "evaluation_status"],
    )
