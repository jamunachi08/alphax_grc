# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document


class GRCSAMAWaiver(Document):
	def validate(self):
		# Appendix E requires compensating controls on a waiver; Appendix C
		# requires a proposal on an update request. SAMA will not begin its
		# review until the required fields are filled.
		if self.request_type == "Waiver" and not (self.compensating_controls or "").strip():
			frappe.throw(
				"A waiver request must describe the available or suggested compensating "
				"controls (SAMA CSF Appendix E)."
			)
		if self.request_type == "Framework Update" and not (self.proposal or "").strip():
			frappe.throw(
				"A framework update request must carry a proposal (SAMA CSF Appendix C)."
			)

		# The approval chain runs CISO -> committee -> CEO/MD to SAMA.
		if self.status in ("Committee Approval", "Submitted to SAMA", "Approved") and not self.ciso_approver:
			frappe.throw("CISO approval is required before the request goes to the committee.")
		if self.status in ("Submitted to SAMA", "Approved") and not self.committee_approver:
			frappe.throw("Cyber security committee approval is required before submission to SAMA.")
		if self.status == "Approved" and not self.sama_reference:
			frappe.throw("Record the SAMA reference before marking the request approved.")
