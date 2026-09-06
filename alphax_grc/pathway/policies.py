# Copyright (c) 2026, Neotec Integrated Solutions
"""
Global policy library shipped with the app.

AlphaX GRC's own `GRC NCA Policy Library` (35 NCA template pointers) is seeded
inside `bootstrap_grc()`, which swallows any seeder that fails — so on a site
where that step errored, the list is simply empty with no trace in the UI.
This catalogue is owned by this app, seeded idempotently from `after_migrate`,
and does not depend on the base app's bootstrap succeeding.

Entries are the policy *set*, not the policy text: title, category, purpose,
review cycle, and framework mapping. `adopt_for_client()` instantiates them as
client-scoped `GRC Policy` records.

Rows are (code, title, title_ar, category, source, mandatory, review_months,
owner_role, purpose, [(framework, reference), ...]).
"""

from __future__ import annotations

import frappe

CATALOGUE = [
	# ---- Information Security: governance -------------------------------
	("NEO-POL-ISMS-01", "Information Security Policy", "سياسة أمن المعلومات",
	 "Information Security", "ISO", 1, 12, "CISO",
	 "Apex statement of management intent and direction for information security.",
	 [("ISO 27001:2022", "5.2"), ("NCA ECC-2:2024", "1-3-1"), ("SAMA CSF", "3.1.1")]),
	("NEO-POL-ISMS-02", "Cybersecurity Roles and Responsibilities", "سياسة الأدوار والمسؤوليات السيبرانية",
	 "Information Security", "NCA", 1, 12, "CISO",
	 "Defines accountability for cybersecurity across the organisation, including the steering committee.",
	 [("NCA ECC-2:2024", "1-4-1"), ("ISO 27001:2022", "A.5.2")]),
	("NEO-POL-ISMS-03", "Cybersecurity Strategy and Roadmap", "الاستراتيجية وخارطة الطريق السيبرانية",
	 "Information Security", "NCA", 0, 24, "CISO",
	 "Multi-year direction, objectives, and investment plan for the cybersecurity programme.",
	 [("NCA ECC-2:2024", "1-1-1")]),
	("NEO-POL-ISMS-04", "Acceptable Use Policy", "سياسة الاستخدام المقبول",
	 "Information Security", "ISO", 1, 12, "CISO",
	 "Rules for the acceptable use of organisational assets, systems, and networks by all personnel.",
	 [("ISO 27001:2022", "A.5.10"), ("NCA ECC-2:2024", "2-1-3")]),
	("NEO-POL-ISMS-05", "Asset Management Policy", "سياسة إدارة الأصول",
	 "Information Security", "ISO", 1, 12, "IT Manager",
	 "Identification, ownership, classification, and lifecycle handling of information assets.",
	 [("ISO 27001:2022", "A.5.9"), ("NCA ECC-2:2024", "2-1-1")]),
	("NEO-POL-ISMS-06", "Information Classification and Handling Policy", "سياسة تصنيف ومعالجة المعلومات",
	 "Information Security", "ISO", 1, 12, "CISO",
	 "Classification tiers and the handling, labelling, and transmission rules that follow from them.",
	 [("ISO 27001:2022", "A.5.12"), ("NCA ECC-2:2024", "2-7-1"), ("SDAIA PDPL", "Art. 19")]),

	# ---- Information Security: access -----------------------------------
	("NEO-POL-IAM-01", "Access Control Policy", "سياسة التحكم في الوصول",
	 "Information Security", "ISO", 1, 12, "IT Manager",
	 "Provisioning, review, and revocation of logical access on least-privilege and need-to-know.",
	 [("ISO 27001:2022", "A.5.15"), ("NCA ECC-2:2024", "2-2-1"), ("SAMA CSF", "3.3.5")]),
	("NEO-POL-IAM-02", "Identity and Authentication Policy", "سياسة الهوية والمصادقة",
	 "Information Security", "Neotec Standard", 1, 12, "IT Manager",
	 "Identity lifecycle, password standards, and multi-factor authentication requirements.",
	 [("ISO 27001:2022", "A.5.17"), ("NCA ECC-2:2024", "2-2-3")]),
	("NEO-POL-IAM-03", "Privileged Access Management Policy", "سياسة إدارة الوصول المميز",
	 "Information Security", "NCA", 1, 12, "IT Manager",
	 "Additional controls over administrative, root, and service accounts including session monitoring.",
	 [("NCA ECC-2:2024", "2-2-3"), ("ISO 27001:2022", "A.8.2")]),
	("NEO-POL-IAM-04", "Remote Access and Teleworking Policy", "سياسة الوصول عن بُعد والعمل عن بُعد",
	 "Information Security", "ISO", 0, 12, "IT Manager",
	 "Conditions and safeguards for access to corporate systems from outside the network perimeter.",
	 [("ISO 27001:2022", "A.6.7"), ("NCA ECC-2:2024", "2-15-1")]),

	# ---- Information Security: technical --------------------------------
	("NEO-POL-SEC-01", "Cryptography and Key Management Policy", "سياسة التشفير وإدارة المفاتيح",
	 "Information Security", "ISO", 1, 12, "CISO",
	 "Approved algorithms, key lifecycle, and where encryption is mandatory at rest and in transit.",
	 [("ISO 27001:2022", "A.8.24"), ("NCA ECC-2:2024", "2-8-1"), ("SDAIA PDPL", "Art. 19")]),
	("NEO-POL-SEC-02", "Network Security Policy", "سياسة أمن الشبكات",
	 "Information Security", "ISO", 1, 12, "IT Manager",
	 "Segmentation, perimeter controls, and secure configuration of network infrastructure.",
	 [("ISO 27001:2022", "A.8.20"), ("NCA ECC-2:2024", "2-5-1")]),
	("NEO-POL-SEC-03", "Malware Protection Policy", "سياسة الحماية من البرمجيات الضارة",
	 "Information Security", "NCA", 1, 12, "IT Manager",
	 "Anti-malware coverage, update cadence, and response to detections across all endpoints.",
	 [("NCA ECC-2:2024", "2-3-1"), ("ISO 27001:2022", "A.8.7")]),
	("NEO-POL-SEC-04", "Secure Configuration and Hardening Policy", "سياسة التهيئة الآمنة والتحصين",
	 "Information Security", "Neotec Standard", 0, 12, "IT Manager",
	 "Baseline hardening standards for servers, endpoints, databases, and cloud workloads.",
	 [("NCA ECC-2:2024", "2-3-2"), ("ISO 27001:2022", "A.8.9")]),
	("NEO-POL-SEC-05", "Vulnerability and Patch Management Policy", "سياسة إدارة الثغرات والتحديثات",
	 "Information Security", "ISO", 1, 12, "IT Manager",
	 "Scanning cadence, severity-based remediation SLAs, and exception handling.",
	 [("ISO 27001:2022", "A.8.8"), ("NCA ECC-2:2024", "2-10-1"), ("PCI DSS", "6.3")]),
	("NEO-POL-SEC-06", "Logging and Security Monitoring Policy", "سياسة التسجيل والمراقبة الأمنية",
	 "Information Security", "ISO", 1, 12, "SOC Manager",
	 "What is logged, how long it is retained, and how events are monitored and escalated.",
	 [("ISO 27001:2022", "A.8.15"), ("NCA ECC-2:2024", "2-12-1"), ("SAMA CSF", "3.3.13")]),
	("NEO-POL-SEC-07", "Secure Software Development Policy", "سياسة التطوير الآمن للبرمجيات",
	 "Information Security", "ISO", 0, 12, "Head of Applications",
	 "Security requirements across the SDLC including code review, testing, and release gates.",
	 [("ISO 27001:2022", "A.8.25"), ("NCA ECC-2:2024", "2-6-1")]),
	("NEO-POL-SEC-08", "Cloud Computing Security Policy", "سياسة أمن الحوسبة السحابية",
	 "Information Security", "NCA", 1, 12, "CISO",
	 "Shared-responsibility boundaries, tenancy, data residency, and cloud provider assurance.",
	 [("NCA ECC-2:2024", "4-1-1"), ("ISO 27001:2022", "A.5.23")]),
	("NEO-POL-SEC-09", "Mobile Device and BYOD Policy", "سياسة الأجهزة المحمولة",
	 "Information Security", "ISO", 0, 12, "IT Manager",
	 "Enrolment, containerisation, and wipe rights for corporate and personally-owned devices.",
	 [("ISO 27001:2022", "A.8.1"), ("NCA ECC-2:2024", "2-16-1")]),
	("NEO-POL-SEC-10", "Removable Media Policy", "سياسة الوسائط القابلة للإزالة",
	 "Information Security", "ISO", 0, 24, "IT Manager",
	 "Restrictions, encryption, and disposal requirements for removable storage.",
	 [("ISO 27001:2022", "A.7.10")]),
	("NEO-POL-SEC-11", "Physical and Environmental Security Policy", "سياسة الأمن المادي والبيئي",
	 "Information Security", "ISO", 1, 12, "Facilities Manager",
	 "Perimeter, entry control, and environmental protection for facilities and data centres.",
	 [("ISO 27001:2022", "A.7.1"), ("NCA ECC-2:2024", "2-14-1")]),
	("NEO-POL-SEC-12", "Backup and Restoration Policy", "سياسة النسخ الاحتياطي والاسترجاع",
	 "Information Security", "ISO", 1, 12, "IT Manager",
	 "Backup scope, frequency, offsite storage, encryption, and restoration testing.",
	 [("ISO 27001:2022", "A.8.13"), ("NCA ECC-2:2024", "2-9-1")]),
	("NEO-POL-SEC-13", "Email and Internet Usage Policy", "سياسة استخدام البريد الإلكتروني والإنترنت",
	 "Information Security", "Neotec Standard", 0, 24, "IT Manager",
	 "Acceptable use, filtering, and phishing-reporting expectations for messaging and browsing.",
	 [("NCA ECC-2:2024", "2-4-1")]),
	("NEO-POL-SEC-14", "Clear Desk and Clear Screen Policy", "سياسة المكتب النظيف والشاشة النظيفة",
	 "Information Security", "ISO", 0, 24, "CISO",
	 "Handling of physical documents and unattended sessions in shared workspaces.",
	 [("ISO 27001:2022", "A.7.7")]),

	# ---- Privacy ---------------------------------------------------------
	("NEO-POL-PRV-01", "Personal Data Protection Policy", "سياسة حماية البيانات الشخصية",
	 "Privacy", "SDAIA PDPL", 1, 12, "Data Protection Officer",
	 "How personal data is collected, processed, retained, and protected under PDPL.",
	 [("SDAIA PDPL", "Art. 4"), ("ISO 27701", "6.2"), ("GDPR", "Art. 24")]),
	("NEO-POL-PRV-02", "Privacy Notice and Consent Policy", "سياسة الإشعار والموافقة",
	 "Privacy", "SDAIA PDPL", 1, 12, "Data Protection Officer",
	 "Transparency obligations and the lawful basis and consent mechanics for processing.",
	 [("SDAIA PDPL", "Art. 12"), ("GDPR", "Art. 13")]),
	("NEO-POL-PRV-03", "Data Subject Rights Policy", "سياسة حقوق أصحاب البيانات",
	 "Privacy", "SDAIA PDPL", 1, 12, "Data Protection Officer",
	 "Intake, verification, and fulfilment of access, correction, and erasure requests within statutory deadlines.",
	 [("SDAIA PDPL", "Art. 4"), ("GDPR", "Art. 15")]),
	("NEO-POL-PRV-04", "Data Retention and Disposal Policy", "سياسة الاحتفاظ بالبيانات وإتلافها",
	 "Privacy", "ISO", 1, 12, "Data Protection Officer",
	 "Retention schedules by record class and secure disposal at end of life.",
	 [("SDAIA PDPL", "Art. 18"), ("ISO 27001:2022", "A.5.33")]),
	("NEO-POL-PRV-05", "Cross-Border Data Transfer Policy", "سياسة نقل البيانات خارج المملكة",
	 "Privacy", "SDAIA PDPL", 1, 12, "Data Protection Officer",
	 "Conditions, assessments, and approvals required before personal data leaves the Kingdom.",
	 [("SDAIA PDPL", "Art. 29"), ("GDPR", "Art. 44")]),
	("NEO-POL-PRV-06", "Privacy Impact Assessment Policy", "سياسة تقييم أثر الخصوصية",
	 "Privacy", "SDAIA PDPL", 0, 12, "Data Protection Officer",
	 "When a DPIA is triggered, who performs it, and how residual risk is accepted.",
	 [("SDAIA PDPL", "Art. 22"), ("GDPR", "Art. 35"), ("ISO 27701", "7.2.5")]),
	("NEO-POL-PRV-07", "Personal Data Breach Notification Policy", "سياسة الإبلاغ عن خرق البيانات الشخصية",
	 "Privacy", "SDAIA PDPL", 1, 12, "Data Protection Officer",
	 "Assessment, regulator notification, and data-subject communication after a personal data breach.",
	 [("SDAIA PDPL", "Art. 20"), ("GDPR", "Art. 33")]),

	# ---- Risk ------------------------------------------------------------
	("NEO-POL-RSK-01", "Enterprise Risk Management Policy", "سياسة إدارة المخاطر المؤسسية",
	 "Risk", "ISO", 1, 12, "Chief Risk Officer",
	 "Risk governance, appetite, scoring methodology, and escalation thresholds.",
	 [("ISO 27001:2022", "6.1"), ("NCA ECC-2:2024", "1-5-1"), ("NIST CSF 2.0", "GV.RM")]),
	("NEO-POL-RSK-02", "Information Security Risk Assessment Policy", "سياسة تقييم مخاطر أمن المعلومات",
	 "Risk", "ISO", 1, 12, "CISO",
	 "Assessment cadence, methodology, and the treatment options available to risk owners.",
	 [("ISO 27001:2022", "8.2"), ("NCA ECC-2:2024", "1-5-1")]),
	("NEO-POL-RSK-03", "Risk Acceptance and Exception Policy", "سياسة قبول المخاطر والاستثناءات",
	 "Risk", "Neotec Standard", 0, 12, "Chief Risk Officer",
	 "Who may accept residual risk, for how long, and what compensating controls are required.",
	 [("ISO 27001:2022", "6.1.3"), ("SAMA CSF", "3.1.4")]),
	("NEO-POL-RSK-04", "Third Party and Supplier Security Policy", "سياسة أمن الأطراف الخارجية",
	 "Risk", "ISO", 1, 12, "Procurement Manager",
	 "Due diligence, contractual security clauses, and ongoing monitoring of suppliers.",
	 [("ISO 27001:2022", "A.5.19"), ("NCA ECC-2:2024", "4-2-1"), ("Aramco SACS-002", "3.1")]),
	("NEO-POL-RSK-05", "Business Continuity Policy", "سياسة استمرارية الأعمال",
	 "Risk", "ISO", 1, 12, "BCM Manager",
	 "BCMS scope, RTO/RPO setting, and the exercise and review programme.",
	 [("ISO 22301", "5.2"), ("NCA ECC-2:2024", "2-13-1")]),
	("NEO-POL-RSK-06", "Disaster Recovery Policy", "سياسة التعافي من الكوارث",
	 "Risk", "ISO", 1, 12, "IT Manager",
	 "ICT recovery objectives, failover arrangements, and DR testing requirements.",
	 [("ISO 22301", "8.4"), ("NCA ECC-2:2024", "2-13-3")]),

	# ---- Compliance ------------------------------------------------------
	("NEO-POL-CMP-01", "Compliance and Regulatory Obligations Policy", "سياسة الامتثال والالتزامات التنظيمية",
	 "Compliance", "Neotec Standard", 1, 12, "Compliance Officer",
	 "Identification, tracking, and attestation of statutory and regulatory obligations.",
	 [("ISO 27001:2022", "A.5.31"), ("NCA ECC-2:2024", "1-6-1")]),
	("NEO-POL-CMP-02", "Internal Audit Policy", "سياسة التدقيق الداخلي",
	 "Compliance", "ISO", 1, 12, "Head of Internal Audit",
	 "Audit universe, independence, planning, and follow-up on findings.",
	 [("ISO 27001:2022", "9.2"), ("NCA ECC-2:2024", "1-7-1")]),
	("NEO-POL-CMP-03", "Evidence and Records Management Policy", "سياسة إدارة الأدلة والسجلات",
	 "Compliance", "Neotec Standard", 0, 12, "Compliance Officer",
	 "How control evidence is collected, timestamped, retained, and made audit-ready.",
	 [("ISO 27001:2022", "7.5"), ("NCA ECC-2:2024", "1-6-2")]),
	("NEO-POL-CMP-04", "Document and Version Control Policy", "سياسة ضبط الوثائق والإصدارات",
	 "Compliance", "ISO", 0, 24, "Compliance Officer",
	 "Approval, versioning, distribution, and withdrawal of controlled documents.",
	 [("ISO 27001:2022", "7.5.2")]),
	("NEO-POL-CMP-05", "Management Review Policy", "سياسة المراجعة الإدارية",
	 "Compliance", "ISO", 0, 12, "CISO",
	 "Frequency, inputs, and required outputs of management review of the ISMS.",
	 [("ISO 27001:2022", "9.3")]),
	("NEO-POL-CMP-06", "AI Governance Policy", "سياسة حوكمة الذكاء الاصطناعي",
	 "Compliance", "ISO", 0, 12, "Chief Data Officer",
	 "Accountable use, impact assessment, and human oversight of AI systems.",
	 [("ISO 42001", "5.2"), ("SDAIA PDPL", "Art. 4")]),

	# ---- HR --------------------------------------------------------------
	("NEO-POL-HR-01", "Personnel Security and Screening Policy", "سياسة أمن الموظفين والفحص",
	 "HR", "ISO", 1, 12, "HR Director",
	 "Pre-employment screening, terms of employment, and role-change controls.",
	 [("ISO 27001:2022", "A.6.1"), ("NCA ECC-2:2024", "1-9-1")]),
	("NEO-POL-HR-02", "Security Awareness and Training Policy", "سياسة التوعية والتدريب الأمني",
	 "HR", "NCA", 1, 12, "CISO",
	 "Mandatory awareness curriculum, frequency, and completion tracking for all personnel.",
	 [("NCA ECC-2:2024", "1-10-1"), ("ISO 27001:2022", "A.6.3")]),
	("NEO-POL-HR-03", "Disciplinary and Sanctions Policy", "سياسة الجزاءات والتأديب",
	 "HR", "ISO", 0, 24, "HR Director",
	 "Consequences of security policy violations, applied consistently and proportionately.",
	 [("ISO 27001:2022", "A.6.4")]),
	("NEO-POL-HR-04", "Confidentiality and Non-Disclosure Policy", "سياسة السرية وعدم الإفشاء",
	 "HR", "ISO", 1, 24, "Legal Counsel",
	 "NDA requirements for employees, contractors, and third parties, and their duration.",
	 [("ISO 27001:2022", "A.6.6")]),
	("NEO-POL-HR-05", "Joiner Mover Leaver Policy", "سياسة الالتحاق والنقل والمغادرة",
	 "HR", "Neotec Standard", 0, 12, "HR Director",
	 "Coordinated onboarding, transfer, and offboarding of access, assets, and credentials.",
	 [("ISO 27001:2022", "A.6.5"), ("NCA ECC-2:2024", "1-9-3")]),

	# ---- Operations ------------------------------------------------------
	("NEO-POL-OPS-01", "Change Management Policy", "سياسة إدارة التغيير",
	 "Operations", "ISO", 1, 12, "IT Manager",
	 "Request, assessment, approval, and back-out of changes to production systems.",
	 [("ISO 27001:2022", "A.8.32"), ("NCA ECC-2:2024", "2-6-2")]),
	("NEO-POL-OPS-02", "Incident Management Policy", "سياسة إدارة الحوادث",
	 "Operations", "ISO", 1, 12, "SOC Manager",
	 "Detection, classification, response, and regulatory notification for security incidents.",
	 [("ISO 27001:2022", "A.5.24"), ("NCA ECC-2:2024", "2-11-1"), ("SAMA CSF", "3.3.15")]),
	("NEO-POL-OPS-03", "Capacity and Availability Management Policy", "سياسة إدارة السعة والتوافر",
	 "Operations", "ISO", 0, 24, "IT Manager",
	 "Monitoring and forecasting of resource capacity to sustain agreed service levels.",
	 [("ISO 27001:2022", "A.8.6")]),
	("NEO-POL-OPS-04", "Asset Disposal and Media Sanitisation Policy", "سياسة إتلاف الأصول وتطهير الوسائط",
	 "Operations", "ISO", 0, 24, "IT Manager",
	 "Sanitisation standards and certificates of destruction before assets leave custody.",
	 [("ISO 27001:2022", "A.7.14"), ("NCA ECC-2:2024", "2-1-4")]),
	("NEO-POL-OPS-05", "Outsourcing and Managed Services Policy", "سياسة الإسناد والخدمات المُدارة",
	 "Operations", "NCA", 0, 12, "Procurement Manager",
	 "Approval, security requirements, and exit planning for outsourced ICT services.",
	 [("NCA ECC-2:2024", "4-2-2"), ("SAMA CSF", "3.3.16")]),
]


def _log_title(text: str) -> str:
	return text[:140]


def seed_global_policies():
	"""Idempotent: inserts what's missing, refreshes titles and mappings in place."""
	if not frappe.db.exists("DocType", "GRC Global Policy"):
		return

	for order, row in enumerate(CATALOGUE, start=1):
		(code, title, title_ar, category, source, mandatory, months, owner_role, purpose,
		 mappings) = row
		try:
			_upsert_policy(code, title, title_ar, category, source, mandatory, months,
						   owner_role, purpose, mappings, order)
		except Exception:
			frappe.log_error(
				title=_log_title(f"Global policy seed failed: {code}"),
				message=frappe.get_traceback(),
			)


def _upsert_policy(code, title, title_ar, category, source, mandatory, months, owner_role,
				   purpose, mappings, order):
	if frappe.db.exists("GRC Global Policy", code):
		doc = frappe.get_doc("GRC Global Policy", code)
		# Respect local edits to the narrative fields; only refresh structure.
		doc.policy_title = doc.policy_title or title
		doc.purpose = doc.purpose or purpose
	else:
		doc = frappe.new_doc("GRC Global Policy")
		doc.policy_code = code
		doc.policy_title = title
		doc.purpose = purpose

	doc.policy_title_ar = doc.get("policy_title_ar") or title_ar
	doc.category = category
	doc.source = source
	doc.is_mandatory = mandatory
	doc.is_active = 1
	doc.review_cycle_months = months
	doc.default_owner_role = owner_role
	doc.display_order = order

	existing_map = {(m.framework, (m.reference or "").strip()) for m in doc.get("framework_mappings") or []}
	for framework, reference in mappings:
		if (framework, reference) not in existing_map:
			doc.append("framework_mappings", {"framework": framework, "reference": reference})

	doc.flags.ignore_permissions = True
	doc.flags.ignore_mandatory = True
	if doc.is_new():
		doc.insert(ignore_permissions=True)
	else:
		doc.save(ignore_permissions=True)


def import_from_nca_library():
	"""Fold AlphaX GRC's own NCA template pointers into the same list.

	The base app ships `GRC NCA Policy Library` with 35 NCA template entries.
	Where they exist, mirror them here as `source = NCA` so consultants work
	from one list instead of two. Titles already in the catalogue are skipped.
	"""
	if not frappe.db.exists("DocType", "GRC NCA Policy Library"):
		return 0

	CATEGORY_MAP = {
		"Governance": "Compliance",
		"Access": "Information Security",
		"Asset": "Information Security",
		"Network": "Information Security",
		"Application": "Information Security",
		"Data": "Privacy",
		"Physical": "Information Security",
		"Third Party": "Risk",
		"Resilience": "Risk",
		"Incident": "Operations",
		"Monitoring": "Information Security",
		"Vulnerability": "Information Security",
		"Other": "Compliance",
	}

	known_titles = {
		t.lower() for t in frappe.get_all("GRC Global Policy", pluck="policy_title") if t
	}
	imported = 0

	for row in frappe.get_all(
		"GRC NCA Policy Library",
		filters={"is_active": 1},
		fields=["template_code", "template_name", "template_name_ar", "category", "ecc_controls"],
	):
		if (row.template_name or "").lower() in known_titles:
			continue
		code = f"NCA-{row.template_code}"[:140]
		if frappe.db.exists("GRC Global Policy", code):
			continue
		try:
			doc = frappe.new_doc("GRC Global Policy")
			doc.policy_code = code
			doc.policy_title = row.template_name
			doc.policy_title_ar = row.template_name_ar
			doc.category = CATEGORY_MAP.get(row.category, "Compliance")
			doc.source = "NCA"
			doc.is_active = 1
			doc.review_cycle_months = 12
			doc.display_order = 900 + imported
			doc.purpose = "Imported from the NCA template library shipped with AlphaX GRC."
			if row.ecc_controls:
				doc.append("framework_mappings",
						   {"framework": "NCA ECC-2:2024", "reference": row.ecc_controls})
			doc.flags.ignore_mandatory = True
			doc.insert(ignore_permissions=True)
			imported += 1
		except Exception:
			frappe.log_error(
				title=_log_title(f"NCA policy import failed: {row.template_code}"),
				message=frappe.get_traceback(),
			)

	return imported
