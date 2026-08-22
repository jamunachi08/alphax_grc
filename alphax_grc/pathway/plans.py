# Copyright (c) 2026, Neotec Integrated Solutions
"""
Plan templates shipped with the app.

Each row is (wbs, title, duration_days, responsible_role, phase, depends_on).
Duration is working days; 0 means milestone. `depends_on` is blank for the
common case of "starts after the previous task" — set it only where a task
genuinely waits on something other than the row above it.

The ISO 27001 template mirrors a real ISMS implementation plan (durations
taken from a delivered project). The SAMA template follows the four control
domains of SAMA CSF v1.0 and the maturity-3 evidence set. NCA ECC follows the
five ECC-2:2024 main domains.
"""

from __future__ import annotations

import frappe

from alphax_grc.pathway.plan_library import EXTRA_TEMPLATES

TEMPLATES = [
	{
		"name": "ISO 27001:2022 ISMS Implementation",
		"framework": "ISO 27001:2022",
		"engagement_type": "ISO 27001 Certification",
		"source": "ISO/IEC 27001:2022 clauses 4-10 + Annex A",
		"description": "Certification-track ISMS build, from management commitment to stage 2 readiness.",
		"tasks": [
			("1.0", "Project Introduction", 0, "Project Manager", "Initiation", ""),
			("1.1", "Initiate project charter", 4, "Project Manager", "Initiation", ""),
			("1.1.1", "Conduct management awareness session", 2, "GRC Consultant", "Initiation", ""),
			("1.2", "Secure management commitment (5.1)", 8, "Project Manager", "Initiation", ""),
			("1.3", "Understand organisational context (4.1, 4.2)", 6, "GRC Consultant", "Initiation", ""),
			("1.4", "Define ISMS scope (4.3)", 6, "Project Manager", "Initiation", ""),
			("2.0", "Execution", 0, "", "Execution", ""),
			("2.1", "Conduct gap assessment", 6, "GRC Consultant", "Execution", ""),
			("2.2", "Develop risk management procedure (6.1.2)", 6, "GRC Consultant", "Execution", ""),
			("2.3", "Conduct risk assessment (6.1.2)", 6, "GRC Consultant", "Execution", ""),
			("2.4", "Develop Statement of Applicability (6.1.3)", 7, "GRC Consultant", "Execution", ""),
			("3.0", "Implementation", 0, "", "Implementation", ""),
			("3.1", "Develop information security policy set (5.2)", 9, "GRC Consultant", "Implementation", ""),
			("3.2", "Develop supporting procedures", 6, "GRC Consultant", "Implementation", ""),
			("3.2.1", "Implement selected Annex A controls", 13, "IT Manager", "Implementation", ""),
			("3.2.2", "Conduct awareness and training (7.2, 7.3)", 6, "HR", "Implementation", ""),
			("4.0", "Monitoring", 0, "", "Monitoring", ""),
			("4.1", "Monitor and measure the ISMS (9.1)", 6, "IT Manager", "Monitoring", ""),
			("4.2", "Conduct internal audit (9.2)", 6, "Internal Audit", "Monitoring", ""),
			("4.3", "Conduct management review (9.3)", 3, "CISO", "Monitoring", ""),
			("4.4", "Treat non-conformities (10.2)", 4, "Project Manager", "Monitoring", ""),
			("4.5", "Implement continual improvement (10.1)", 2, "Project Manager", "Monitoring", ""),
			("4.6", "Prepare for certification audit", 5, "Project Manager", "Monitoring", "4.4"),
			("5.0", "Stage 2 audit ready", 0, "Project Manager", "Closure", ""),
		],
	},
	{
		"name": "SAMA CSF Implementation and Maturity Uplift",
		"framework": "SAMA CSF",
		"engagement_type": "Managed Compliance (ongoing)",
		"source": "SAMA Cyber Security Framework v1.0 (May 2017), domains 3.1-3.4",
		"description": (
			"Uplift to maturity level 3 (structured and formalised) across the four SAMA "
			"domains, with the documentation and evidence set a SAMA review expects."
		),
		"tasks": [
			("1.0", "Mobilisation", 0, "Project Manager", "Mobilisation", ""),
			("1.1", "Kick-off and scope confirmation", 3, "Project Manager", "Mobilisation", ""),
			("1.2", "Maturity self-assessment against all sub-domains (2.3)", 10, "GRC Consultant", "Mobilisation", ""),
			("1.3", "Gap report and maturity baseline per sub-domain", 5, "GRC Consultant", "Mobilisation", ""),
			("2.0", "3.1 Leadership and Governance", 0, "", "Governance", ""),
			("2.1", "Establish cyber security committee and charter (3.1.1)", 7, "CISO", "Governance", ""),
			("2.2", "CISO appointment, qualification and SAMA no-objection (3.1.1.9)", 10, "CISO", "Governance", ""),
			("2.3", "Define cyber security strategy and roadmap (3.1.2)", 10, "CISO", "Governance", ""),
			("2.4", "Board-endorsed cyber security policy (3.1.3)", 8, "CISO", "Governance", ""),
			("2.5", "Roles, responsibilities and RACI matrix (3.1.4)", 6, "CISO", "Governance", ""),
			("2.6", "Cyber security in project management (3.1.5)", 5, "Project Manager", "Governance", ""),
			("2.7", "Awareness programme for staff, third parties, customers (3.1.6)", 8, "HR", "Governance", ""),
			("2.8", "Role-based training programme (3.1.7)", 6, "HR", "Governance", ""),
			("3.0", "3.2 Risk Management and Compliance", 0, "", "Risk", ""),
			("3.1", "Cyber security risk management process aligned to ERM (3.2.1)", 10, "GRC Consultant", "Risk", ""),
			("3.2", "Risk register, appetite and tolerance formally approved (3.2.1.11)", 7, "CISO", "Risk", ""),
			("3.3", "Risk treatment plans and business-owner sign-off (3.2.1.3)", 8, "Business Owner", "Risk", ""),
			("3.4", "Regulatory compliance register and review process (3.2.2)", 6, "GRC Consultant", "Risk", ""),
			("3.5", "PCI DSS / EMV / SWIFT CSCF applicability review (3.2.3)", 5, "GRC Consultant", "Risk", ""),
			("3.6", "Cyber security review of critical assets and pen tests (3.2.4)", 10, "External Auditor", "Risk", ""),
			("3.7", "Cyber security audit charter and annual plan (3.2.5)", 6, "Internal Audit", "Risk", ""),
			("4.0", "3.3 Operations and Technology", 0, "", "Operations", ""),
			("4.1", "HR security: screening, NDAs, JML (3.3.1)", 6, "HR", "Operations", ""),
			("4.2", "Physical security controls and visitor logs (3.3.2)", 5, "IT Manager", "Operations", ""),
			("4.3", "Unified asset register with ownership and classification (3.3.3)", 10, "IT Manager", "Operations", ""),
			("4.4", "Cyber security architecture (3.3.4)", 10, "IT Manager", "Operations", ""),
			("4.5", "Identity and access management, MFA, privileged access (3.3.5)", 12, "IT Manager", "Operations", ""),
			("4.6", "Application security standard and SDLC (3.3.6)", 8, "IT Manager", "Operations", ""),
			("4.7", "Change management and CAB (3.3.7)", 6, "IT Manager", "Operations", ""),
			("4.8", "Infrastructure security standards and DDoS protection (3.3.8)", 12, "IT Manager", "Operations", ""),
			("4.9", "Cryptography and key management standard (3.3.9)", 8, "IT Manager", "Operations", ""),
			("4.10", "BYOD standard, MDM and user agreements (3.3.10)", 6, "IT Manager", "Operations", ""),
			("4.11", "Secure disposal standard and disposal register (3.3.11)", 4, "IT Manager", "Operations", ""),
			("4.12", "SOC and security event monitoring standard (3.3.14)", 12, "CISO", "Operations", ""),
			("4.13", "Incident management incl. SAMA notification path (3.3.15)", 10, "CISO", "Operations", ""),
			("4.14", "Threat intelligence process (3.3.16)", 6, "CISO", "Operations", ""),
			("4.15", "Vulnerability management and remediation SLAs (3.3.17)", 10, "IT Manager", "Operations", ""),
			("5.0", "3.4 Third Party Cyber Security", 0, "", "Third Party", ""),
			("5.1", "Contract and vendor management requirements (3.4.1)", 8, "Legal", "Third Party", ""),
			("5.2", "Outsourcing register and SAMA approval process (3.4.2)", 6, "Legal", "Third Party", ""),
			("5.3", "Cloud computing policy, data location and exit (3.4.3)", 8, "CISO", "Third Party", ""),
			("6.0", "Assurance and Closure", 0, "", "Closure", ""),
			("6.1", "Evidence pack assembly against the deliverable list", 10, "GRC Consultant", "Closure", ""),
			("6.2", "Internal audit of implemented controls", 8, "Internal Audit", "Closure", ""),
			("6.3", "Re-run maturity self-assessment", 6, "GRC Consultant", "Closure", ""),
			("6.4", "Management review and residual gap acceptance", 4, "CISO", "Closure", ""),
			("6.5", "Maturity level 3 achieved", 0, "CISO", "Closure", ""),
		],
	},
	{
		"name": "NCA ECC-2:2024 Implementation",
		"framework": "NCA ECC-2:2024",
		"engagement_type": "Standard NCA Engagement",
		"source": "NCA Essential Cybersecurity Controls ECC-2:2024, domains 1-5",
		"description": "ECC implementation across the five main domains, ending in an NCA-ready compliance pack.",
		"tasks": [
			("1.0", "Mobilisation", 0, "Project Manager", "Mobilisation", ""),
			("1.1", "Kick-off and scope confirmation", 3, "Project Manager", "Mobilisation", ""),
			("1.2", "ECC applicability and gap assessment", 12, "GRC Consultant", "Mobilisation", ""),
			("2.0", "Domain 1 - Governance", 0, "", "Governance", ""),
			("2.1", "Cybersecurity strategy and governance structure", 10, "CISO", "Governance", ""),
			("2.2", "Policy set drafting and approval", 12, "GRC Consultant", "Governance", ""),
			("2.3", "Roles, responsibilities and steering committee", 6, "CISO", "Governance", ""),
			("2.4", "Cybersecurity risk management process", 8, "GRC Consultant", "Governance", ""),
			("2.5", "Compliance, audit and periodic review programme", 6, "Internal Audit", "Governance", ""),
			("2.6", "HR cybersecurity and awareness programme", 8, "HR", "Governance", ""),
			("3.0", "Domain 2 - Cybersecurity Defence", 0, "", "Defence", ""),
			("3.1", "Asset management and classification", 10, "IT Manager", "Defence", ""),
			("3.2", "Identity and access management", 10, "IT Manager", "Defence", ""),
			("3.3", "Information system and network protection", 12, "IT Manager", "Defence", ""),
			("3.4", "Mobile, data protection and cryptography", 10, "IT Manager", "Defence", ""),
			("3.5", "Backup, vulnerability and penetration testing", 12, "IT Manager", "Defence", ""),
			("3.6", "Event logging, monitoring and incident management", 12, "CISO", "Defence", ""),
			("3.7", "Physical security and web application protection", 8, "IT Manager", "Defence", ""),
			("4.0", "Domain 3 - Cybersecurity Resilience", 0, "", "Resilience", ""),
			("4.1", "BCM and disaster recovery aligned to cybersecurity", 10, "IT Manager", "Resilience", ""),
			("5.0", "Domain 4 - Third Party and Cloud", 0, "", "Third Party", ""),
			("5.1", "Third-party cybersecurity requirements", 8, "Legal", "Third Party", ""),
			("5.2", "Cloud computing and hosting cybersecurity", 8, "CISO", "Third Party", ""),
			("6.0", "Domain 5 - ICS (if applicable)", 0, "", "ICS", ""),
			("6.1", "Industrial control systems protection", 10, "IT Manager", "ICS", ""),
			("7.0", "Assurance and Closure", 0, "", "Closure", ""),
			("7.1", "Evidence collection against every applicable control", 12, "GRC Consultant", "Closure", ""),
			("7.2", "Internal compliance assessment", 8, "Internal Audit", "Closure", ""),
			("7.3", "Remediation of residual gaps", 10, "IT Manager", "Closure", ""),
			("7.4", "NCA compliance pack submitted", 0, "CISO", "Closure", ""),
		],
	},
]


TEMPLATES = TEMPLATES + EXTRA_TEMPLATES


def _log_title(text: str) -> str:
	return text[:140]


def seed_plan_templates():
	"""Idempotent. Local edits to task rows are kept once a template exists."""
	if not frappe.db.exists("DocType", "GRC Plan Template"):
		return

	for spec in TEMPLATES:
		try:
			_upsert(spec)
		except Exception:
			frappe.log_error(
				title=_log_title(f"Plan template seed failed: {spec['name']}"),
				message=frappe.get_traceback(),
			)


def _upsert(spec: dict):
	if frappe.db.exists("GRC Plan Template", spec["name"]):
		doc = frappe.get_doc("GRC Plan Template", spec["name"])
		if doc.get("tasks"):
			# Someone may have tuned the durations for their own delivery.
			return
	else:
		doc = frappe.new_doc("GRC Plan Template")
		doc.template_name = spec["name"]
		doc.flags.name_set = True

	doc.framework = spec["framework"]
	doc.engagement_type = spec["engagement_type"]
	doc.description = spec["description"]
	doc.source_reference = spec["source"]
	doc.is_active = 1

	doc.set("tasks", [])
	for wbs, title, days, role, phase, depends in spec["tasks"]:
		doc.append("tasks", {
			"wbs": wbs,
			"task_title": title,
			"duration_days": days,
			"responsible_role": role or None,
			"phase": phase,
			"depends_on": depends or None,
			"is_milestone": 1 if days == 0 else 0,
		})

	doc.flags.ignore_permissions = True
	doc.flags.ignore_mandatory = True
	if doc.is_new():
		doc.insert(ignore_permissions=True)
	else:
		doc.save(ignore_permissions=True)
