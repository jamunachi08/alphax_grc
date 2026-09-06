# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document

# SAMA CSF 1.4 — these sub-domains are excluded for member organisations
# outside the banking sector.
NON_BANK_EXCLUDED = {"3.2.3", "3.3.12", "3.3.13"}
BANK_TYPES = {"Bank", "Financial Market Infrastructure"}

TARGET_DEFAULT = 3


def level_value(label) -> int:
	"""'3 - Structured and formalized' -> 3."""
	if label in (None, ""):
		return 0
	try:
		return int(str(label).strip()[0])
	except (ValueError, IndexError):
		return 0


class GRCSAMAAssessment(Document):
	def validate(self):
		self.apply_exclusions()
		self.score()

	def apply_exclusions(self):
		"""Non-banks do not carry 3.2.3, 3.3.12 or 3.3.13."""
		if self.entity_type in BANK_TYPES:
			return
		for line in self.get("lines") or []:
			if line.subdomain in NON_BANK_EXCLUDED:
				line.applicable = 0

	def score(self):
		lines = [l for l in (self.get("lines") or []) if l.applicable]
		for line in self.get("lines") or []:
			line.meets_target = (
				1 if line.applicable
				and level_value(line.current_level) >= level_value(line.target_level or TARGET_DEFAULT)
				else 0
			)

		self.applicable_subdomains = len(lines)
		if not lines:
			self.overall_maturity = 0
			self.subdomains_at_target = 0
			self.pct_at_target = 0
			self.lowest_domain = None
			return

		levels = [level_value(l.current_level) for l in lines]
		self.overall_maturity = round(sum(levels) / len(levels), 2)
		self.subdomains_at_target = len([l for l in lines if l.meets_target])
		self.pct_at_target = round((self.subdomains_at_target / len(lines)) * 100, 1)

		by_domain: dict = {}
		for line in lines:
			domain = line.domain or (line.subdomain or "")[:3]
			by_domain.setdefault(domain, []).append(level_value(line.current_level))
		averages = {d: sum(v) / len(v) for d, v in by_domain.items() if v}
		if averages:
			self.lowest_domain = min(averages, key=averages.get)

	@frappe.whitelist()
	def load_subdomains(self):
		"""Populate every active sub-domain from the catalogue."""
		if self.get("lines"):
			frappe.throw("This assessment already has lines.")

		rows = frappe.get_all(
			"GRC SAMA Subdomain", filters={"is_active": 1},
			fields=["name", "domain", "excluded_for_non_banks"], order_by="name asc",
		)
		if not rows:
			frappe.throw("The SAMA sub-domain catalogue is empty. Run bench migrate to seed it.")

		non_bank = self.entity_type not in BANK_TYPES
		for row in rows:
			self.append("lines", {
				"subdomain": row.name,
				"domain": row.domain,
				"current_level": "0 - Non-existent",
				"target_level": "3 - Structured and formalized",
				"applicable": 0 if (non_bank and row.excluded_for_non_banks) else 1,
			})
		self.score()
		return len(self.get("lines"))
