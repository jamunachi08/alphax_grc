# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document
from frappe.utils import add_months, nowdate


class GRCGlobalPolicy(Document):
	def validate(self):
		if self.review_cycle_months is not None and self.review_cycle_months < 0:
			frappe.throw("Review Cycle (Months) cannot be negative.")
		self._dedupe_mappings()

	def _dedupe_mappings(self):
		seen = set()
		kept = []
		for row in self.get("framework_mappings") or []:
			key = (row.framework, (row.reference or "").strip().lower())
			if key in seen:
				continue
			seen.add(key)
			kept.append(row)
		if len(kept) != len(self.get("framework_mappings") or []):
			self.set("framework_mappings", kept)
			for idx, row in enumerate(kept, start=1):
				row.idx = idx

	def adopt_for_client(self, client: str, owner: str | None = None):
		"""Create a client-scoped GRC Policy from this library entry.

		Returns the existing policy if one with the same title already exists
		for that client, so bulk adoption is safe to re-run.
		"""
		existing = frappe.db.get_value(
			"GRC Policy", {"client": client, "policy_title": self.policy_title}
		)
		if existing:
			return frappe.get_doc("GRC Policy", existing), False

		policy = frappe.new_doc("GRC Policy")
		policy.client = client
		policy.policy_title = self.policy_title
		policy.policy_category = self.category
		policy.version_no = "1.0"
		policy.status = "Draft"
		policy.publication_status = "Draft"
		policy.summary = self.summary or self.purpose or ""
		if owner:
			policy.policy_owner = owner
		if self.review_cycle_months:
			policy.review_due_date = add_months(nowdate(), self.review_cycle_months)
		for fieldname in ("acknowledgement_required", "acknowledgment_required"):
			if policy.meta.get_field(fieldname):
				policy.set(fieldname, self.acknowledgement_required or 0)

		policy.flags.ignore_permissions = True
		policy.insert(ignore_permissions=True)
		return policy, True
