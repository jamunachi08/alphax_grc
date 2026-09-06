import frappe
from frappe.utils import today, add_days

ROLES = [
    "GRC Executive",
    "GRC Admin",
    "Compliance Officer",
    "GRC Assessor",
    "GRC Auditor",
    "Risk Owner",
    "Vendor Owner",
    "Privacy Officer",
    "Aramco Compliance Owner",
]

FRAMEWORKS = [
    ("NCA ECC", "Cybersecurity", "Regulator"),
    ("SAMA CSF", "Cybersecurity", "Regulator"),
    ("PDPL", "Privacy", "Regulator"),
    ("CST CRF", "Cybersecurity", "Regulator"),
    ("Aramco Third Party Standard", "Cybersecurity", "Standard Body"),
    ("CMA Governance", "Governance", "Regulator"),
    ("ISO 27001", "Security", "Standard Body"),
    ("ISO 31000", "Risk", "Standard Body"),
]

PACKS = [
    {"pack_name": "NCA ECC Pack", "pack_name_ar": "حزمة ضوابط NCA ECC", "pack_code": "NCA_ECC", "category": "National", "mandatory_controls": 108, "coverage_score": 82},
    {"pack_name": "SAMA CSF Pack", "pack_name_ar": "حزمة إطار SAMA CSF", "pack_code": "SAMA_CSF", "category": "Sectoral", "mandatory_controls": 0, "coverage_score": 78},
    {"pack_name": "PDPL Privacy Pack", "pack_name_ar": "حزمة خصوصية PDPL", "pack_code": "PDPL", "category": "Privacy", "mandatory_controls": 0, "coverage_score": 74},
    {"pack_name": "Aramco Third-Party Pack", "pack_name_ar": "حزمة أرامكو للطرف الثالث", "pack_code": "ARAMCO_TP", "category": "Cybersecurity", "mandatory_controls": 0, "coverage_score": 69},
]

OBLIGATIONS = [
    {"obligation_title": "Maintain continuous ECC compliance monitoring", "obligation_title_ar": "الحفاظ على المراقبة المستمرة للامتثال لضوابط ECC", "framework": "NCA ECC", "domain": "Governance", "status": "In Progress"},
    {"obligation_title": "Run SAMA maturity self-assessment", "obligation_title_ar": "تنفيذ التقييم الذاتي لمستوى النضج وفق SAMA", "framework": "SAMA CSF", "domain": "Maturity", "status": "Pending Review"},
    {"obligation_title": "Maintain PDPL processing register", "obligation_title_ar": "الحفاظ على سجل معالجة البيانات وفق PDPL", "framework": "PDPL", "domain": "Privacy", "status": "Open"},
    {"obligation_title": "Track Aramco third-party incident notifications", "obligation_title_ar": "متابعة إشعارات حوادث الأمن السيبراني الخاصة بأرامكو", "framework": "Aramco Third Party Standard", "domain": "Third Party", "status": "Open"},
]

PRIVACY_ACTIVITIES = [
    {"activity_name": "Employee personal data administration", "activity_name_ar": "إدارة بيانات الموظفين الشخصية", "controller_name": "AlphaX", "purpose": "HR administration", "legal_basis": "Employment", "retention_period": "7 Years", "status": "Active"},
    {"activity_name": "Customer onboarding and KYC", "activity_name_ar": "تهيئة العميل ومتطلبات اعرف عميلك", "controller_name": "AlphaX", "purpose": "Contract onboarding", "legal_basis": "Contract", "retention_period": "10 Years", "status": "Active"},
]

SAMPLE_POLICIES = [
    {"policy_title": "Information Security Policy", "policy_category": "Information Security", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Top-level global information security policy covering governance, risk management, legal compliance, and protection of confidentiality, integrity, and availability."},
    {"policy_title": "Access Control Policy", "policy_category": "Information Security", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines joiner-mover-leaver control, least privilege, segregation of duties, privileged access, MFA, and periodic access review expectations."},
    {"policy_title": "Password and Authentication Policy", "policy_category": "Information Security", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines password hygiene, MFA, authentication standards, password reset, lockout, and credential protection requirements."},
    {"policy_title": "Acceptable Use Policy", "policy_category": "Information Security", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines acceptable use of devices, internet, email, removable media, and user responsibilities."},
    {"policy_title": "Data Classification and Handling Policy", "policy_category": "Compliance", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines classification levels, labeling, handling, transfer, retention, and destruction expectations."},
    {"policy_title": "Cryptography Policy", "policy_category": "Information Security", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines encryption requirements for data at rest and in transit, key management, and certificate usage."},
    {"policy_title": "Logging and Monitoring Policy", "policy_category": "Operations", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines event logging, monitoring, retention, review, escalation, and security operations expectations."},
    {"policy_title": "Vulnerability and Patch Management Policy", "policy_category": "Operations", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines vulnerability scanning, risk-based remediation, patch timelines, exceptions, and verification."},
    {"policy_title": "Secure Development and Change Management Policy", "policy_category": "Operations", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines SDLC security, code review, test requirements, change approvals, back-out plans, and segregation of environments."},
    {"policy_title": "Incident Response Policy", "policy_category": "Operations", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines incident classification, reporting, triage, response, escalation, evidence preservation, and lessons learned processes."},
    {"policy_title": "Business Continuity and Disaster Recovery Policy", "policy_category": "Operations", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines resilience, BCP/DR testing, backup expectations, recovery targets, and ICT readiness for disruption."},
    {"policy_title": "Privacy and Personal Data Protection Policy", "policy_category": "Privacy", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines controller and processor obligations, lawful processing, data subject rights, retention, disclosure, transfer, and destruction aligned to PDPL."},
    {"policy_title": "Third-Party Security Policy", "policy_category": "Compliance", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines due diligence, supplier security clauses, cloud security, outsourcing oversight, and continuous vendor review."},
    {"policy_title": "Remote Working Policy", "policy_category": "HR", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines secure remote access, home working controls, device use, and user responsibilities."},
    {"policy_title": "Data Retention and Secure Disposal Policy", "policy_category": "Compliance", "version_no": "1.0", "status": "Approved", "publication_status": "Published", "effective_date": today(), "review_due_date": add_days(today(), 365), "acknowledgement_required": 1, "summary": "Defines retention schedules, archival handling, media sanitization, deletion, and secure disposal."},
]

PAGES = [
    ("grc-lifecycle", "GRC Lifecycle"),
    ("grc-command-center", "GRC Command Center"),
    ("grc-risk-dashboard", "GRC Risk Dashboard"),
    ("grc-kpi-dashboard", "KPI Dashboard"),
    ("grc-nca-templates", "NCA Templates Library"),
    ("grc-aramco-ccc", "Aramco CCC"),
    ("grc-ecc2-dashboard", "NCA ECC-2:2024"),
    ("grc-reports", "GRC Reports"),
    ("grc-help", "GRC Help"),
    ("grc-v04-help", "GRC v0.4 Help"),
    ("grc-neo-hub", "GRC Neo Hub"),
    ("grc-itgc-program", "ITGC Audit Programme"),
    ("grc-asset-dashboard", "Asset Inventory Dashboard"),
    # v1.7.0
    ("grc-iso42001-dashboard", "ISO 42001 — AI Management System"),
    ("grc-ccm-dashboard", "Continuous Control Monitoring"),
    # v1.8.0 — the consultant cockpit (new default landing)
    ("grc-consultant-inbox", "Consultant Cockpit"),
    # v1.9.0 — EGRC fixes + GDPR
    ("grc-enterprise-risk-summary", "Enterprise Risk Summary"),
    ("grc-gdpr-dashboard", "GDPR — EU Data Protection"),
    # v2.0.0 — Annual audit calendar
    ("grc-annual-audit-calendar", "Annual Audit Calendar"),
    # v2.1.0 — Framework expansion
    ("grc-nist-csf-dashboard", "NIST CSF 2.0 Dashboard"),
    ("grc-iso22301-dashboard", "ISO 22301 BCMS Dashboard"),
    # v2.1.1 — Cyber Risk Quantification
    ("grc-crq-dashboard", "Cyber Risk Quantification"),
    # v2.2.0 — PDPL Privacy Pack
    ("grc-pdpl-dashboard", "PDPL — KSA Privacy"),
]



ASSESSMENT_TEMPLATES = [
    # -----------------------------------------------------------------------
    # 1. Governance Discovery
    # -----------------------------------------------------------------------
    {
        "template_name": "Governance Discovery Questionnaire",
        "template_name_ar": "استبيان اكتشاف الحوكمة",
        "template_code": "GOV_DISCOVERY",
        "assessment_area": "Governance",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess governance structure, RACI, policy ownership, approval hierarchy, and management review readiness.",
        "questions": [
            {"section": "Governance Structure", "question_code": "GOV-01", "question_text": "Is there an approved information security or integrated governance charter?", "question_text_ar": "هل يوجد ميثاق حوكمة معتمد لأمن المعلومات أو حوكمة متكاملة؟", "framework_reference": "ISO 27001 A.5.1", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Approved charter or top-level policy."},
            {"section": "Governance Structure", "question_code": "GOV-02", "question_text": "Are executive roles and responsibilities defined using a RACI or similar matrix?", "question_text_ar": "هل يتم تعريف الأدوار والمسؤوليات التنفيذية باستخدام مصفوفة RACI أو ما شابه؟", "framework_reference": "ISO 27001 A.5.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "RACI matrix and job responsibilities."},
            {"section": "Governance Structure", "question_code": "GOV-03", "question_text": "Is there a dedicated GRC or information security committee with defined terms of reference?", "question_text_ar": "هل توجد لجنة متخصصة للحوكمة والمخاطر والامتثال أو أمن المعلومات بشروط مرجعية محددة؟", "framework_reference": "ISO 27001 A.5.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Committee charter and meeting minutes."},
            {"section": "Policy Governance", "question_code": "GOV-04", "question_text": "Are policies reviewed at planned intervals and when significant changes occur?", "question_text_ar": "هل تتم مراجعة السياسات في فترات مخططة وعند حدوث تغييرات جوهرية؟", "framework_reference": "ISO 27001 A.5.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Policy review calendar and version history."},
            {"section": "Policy Governance", "question_code": "GOV-05", "question_text": "Is there a policy hierarchy (framework → policy → procedure → standard)?", "question_text_ar": "هل توجد هرمية للسياسات (إطار → سياسة → إجراء → معيار)؟", "framework_reference": "ISO 27001 A.5.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Document control register showing hierarchy."},
            {"section": "Policy Governance", "question_code": "GOV-06", "question_text": "Are policies formally communicated and acknowledged by all relevant staff?", "question_text_ar": "هل يتم إبلاغ السياسات رسمياً والاعتراف بها من قِبل جميع الموظفين المعنيين؟", "framework_reference": "ISO 27001 A.6.3", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Acknowledgement log or LMS completion records."},
            {"section": "Management Oversight", "question_code": "GOV-07", "question_text": "Are management reviews documented with decisions, actions, and ownership?", "question_text_ar": "هل يتم توثيق مراجعات الإدارة بالقرارات والإجراءات ومالكي التنفيذ؟", "framework_reference": "ISO 27001 Clause 9.3", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Management review minutes and action tracker."},
            {"section": "Management Oversight", "question_code": "GOV-08", "question_text": "Is there a documented GRC strategy or roadmap aligned to business objectives?", "question_text_ar": "هل توجد استراتيجية أو خارطة طريق موثقة للحوكمة مرتبطة بأهداف العمل؟", "framework_reference": "ISO 27001 Clause 6.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Strategy document or roadmap."},
            {"section": "Exception Handling", "question_code": "GOV-09", "question_text": "Is there a formal policy exception process with risk and mitigation analysis?", "question_text_ar": "هل توجد عملية رسمية لاستثناءات السياسات مع تحليل المخاطر والإجراءات التعويضية؟", "framework_reference": "Risk Governance", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Exception memo or waiver register."},
            {"section": "Exception Handling", "question_code": "GOV-10", "question_text": "Are exceptions tracked, time-bound, and reviewed before expiry?", "question_text_ar": "هل يتم تتبع الاستثناءات وتحديدها بفترات زمنية ومراجعتها قبل انتهاء الصلاحية؟", "framework_reference": "Risk Governance", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Exception register with expiry dates and review evidence."},
            {"section": "Awareness & Training", "question_code": "GOV-11", "question_text": "Is there a mandatory annual security awareness training programme with completion tracking?", "question_text_ar": "هل يوجد برنامج إلزامي للتوعية الأمنية السنوية مع تتبع الإتمام؟", "framework_reference": "ISO 27001 A.6.3", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Training completion records."},
            {"section": "Awareness & Training", "question_code": "GOV-12", "question_text": "Does the training programme cover phishing, social engineering, and data handling?", "question_text_ar": "هل يغطي برنامج التدريب التصيد الاحتيالي والهندسة الاجتماعية والتعامل مع البيانات؟", "framework_reference": "ISO 27001 A.6.3", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Training content syllabus."},
            {"section": "Board Reporting", "question_code": "GOV-13", "question_text": "Is GRC status reported to the board or senior leadership at least quarterly?", "question_text_ar": "هل يتم الإبلاغ عن حالة الحوكمة لمجلس الإدارة أو القيادة العليا مرة كل ربع سنة على الأقل؟", "framework_reference": "CMA Governance / NCA ECC", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Board report or dashboard showing GRC metrics."},
            {"section": "Board Reporting", "question_code": "GOV-14", "question_text": "Are board reports bilingual (Arabic and English) as required for Saudi-regulated entities?", "question_text_ar": "هل تصدر تقارير مجلس الإدارة باللغتين العربية والإنجليزية وفق متطلبات الجهات التنظيمية السعودية؟", "framework_reference": "NCA ECC / CMA", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Sample bilingual board report."},
            {"section": "Continuous Improvement", "question_code": "GOV-15", "question_text": "Is there a documented process for lessons learned and continuous improvement of the GRC programme?", "question_text_ar": "هل توجد عملية موثقة للدروس المستفادة والتحسين المستمر لبرنامج الحوكمة؟", "framework_reference": "ISO 27001 Clause 10", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Improvement log or after-action reviews."},
        ],
    },
    # -----------------------------------------------------------------------
    # 2. IAM and Access Review
    # -----------------------------------------------------------------------
    {
        "template_name": "IAM and Access Review Questionnaire",
        "template_name_ar": "استبيان إدارة الهوية والوصول ومراجعة الصلاحيات",
        "template_code": "IAM_REVIEW",
        "assessment_area": "IAM",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess IAM lifecycle maturity across request, approval, provisioning, review, SoD, and de-provisioning.",
        "questions": [
            {"section": "Access Lifecycle", "question_code": "IAM-01", "question_text": "Is there a formal joiner-mover-leaver (JML) process documented and enforced?", "question_text_ar": "هل توجد عملية رسمية لإدارة دورة حياة المستخدمين (انضمام/انتقال/مغادرة) موثقة ومطبقة؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 3, "expected_evidence": "JML process document and HR-IT SLA."},
            {"section": "Access Lifecycle", "question_code": "IAM-02", "question_text": "Are access requests made through a formal ticketing or ITSM system with manager approval?", "question_text_ar": "هل تُقدَّم طلبات الوصول عبر نظام رسمي لإدارة الخدمات مع موافقة المدير المختص؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 3, "expected_evidence": "ITSM workflow screenshot or access request form."},
            {"section": "Access Lifecycle", "question_code": "IAM-03", "question_text": "Are leavers' accounts disabled within 24 hours of their departure date?", "question_text_ar": "هل يتم تعطيل حسابات المغادرين خلال 24 ساعة من تاريخ المغادرة؟", "framework_reference": "NCA ECC 2-10", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Leaver checklist and AD/IAM deprovisioning report."},
            {"section": "Privileged Access", "question_code": "IAM-04", "question_text": "Are privileged accounts (admin, root, service) inventoried and subject to enhanced controls?", "question_text_ar": "هل يتم جرد الحسابات المميزة (المسؤول، الجذر، الخدمة) وتطبيق ضوابط معززة عليها؟", "framework_reference": "NCA ECC 2-10 / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Privileged account inventory and PAM evidence."},
            {"section": "Privileged Access", "question_code": "IAM-05", "question_text": "Is a Privileged Access Management (PAM) solution in place for critical systems?", "question_text_ar": "هل يوجد حل لإدارة الوصول المميز للأنظمة الحساسة؟", "framework_reference": "NCA ECC 2-10", "response_type": "Yes / No", "weight": 3, "expected_evidence": "PAM tool deployment evidence and session logs."},
            {"section": "Privileged Access", "question_code": "IAM-06", "question_text": "Are shared/generic accounts prohibited, or where permitted, are they justified and monitored?", "question_text_ar": "هل يُحظر استخدام الحسابات المشتركة/العامة، أو عند السماح بها هل تكون مبررة ومراقبة؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Policy on shared accounts and monitoring logs."},
            {"section": "MFA & Authentication", "question_code": "IAM-07", "question_text": "Is multi-factor authentication (MFA) enforced for all remote access and privileged accounts?", "question_text_ar": "هل يتم تطبيق المصادقة متعددة العوامل لجميع الوصول عن بُعد والحسابات المميزة؟", "framework_reference": "NCA ECC 2-10 / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "MFA configuration evidence and exceptions list."},
            {"section": "MFA & Authentication", "question_code": "IAM-08", "question_text": "Is MFA enforced for cloud services, email (O365/Google Workspace), and critical applications?", "question_text_ar": "هل يتم تطبيق المصادقة متعددة العوامل للخدمات السحابية والبريد الإلكتروني والتطبيقات الحساسة؟", "framework_reference": "NCA ECC", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Conditional access policies and MFA enrolment report."},
            {"section": "Access Reviews", "question_code": "IAM-09", "question_text": "Are periodic access reviews (at least quarterly) conducted for all systems?", "question_text_ar": "هل تُجرى مراجعات دورية للوصول (ربع سنوية على الأقل) لجميع الأنظمة؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Access review reports and recertification records."},
            {"section": "Access Reviews", "question_code": "IAM-10", "question_text": "Are access review findings (excess/stale access) remediated within a defined SLA?", "question_text_ar": "هل تُعالَج نتائج مراجعة الوصول (الوصول الزائد/المهجور) ضمن SLA محدد؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Remediation tracker showing closures within SLA."},
            {"section": "Segregation of Duties", "question_code": "IAM-11", "question_text": "Has a Segregation of Duties (SoD) matrix been defined and implemented for critical processes?", "question_text_ar": "هل تم تعريف مصفوفة فصل المهام وتطبيقها للعمليات الحساسة؟", "framework_reference": "ISO 27001 A.5.3", "response_type": "Yes / No", "weight": 3, "expected_evidence": "SoD matrix and conflict report."},
            {"section": "Segregation of Duties", "question_code": "IAM-12", "question_text": "Are SoD conflicts detected and remediated in ERP (SAP, Oracle, ERPNext) and financial systems?", "question_text_ar": "هل يتم اكتشاف ومعالجة تعارضات فصل المهام في أنظمة ERP والأنظمة المالية؟", "framework_reference": "ISO 27001 A.5.3", "response_type": "Yes / No", "weight": 3, "expected_evidence": "SoD conflict remediation evidence."},
            {"section": "Identity Governance", "question_code": "IAM-13", "question_text": "Is an Identity Governance and Administration (IGA) solution or process in place?", "question_text_ar": "هل يوجد حل أو عملية لحوكمة الهوية والإدارة؟", "framework_reference": "SAMA CSF", "response_type": "Yes / No", "weight": 2, "expected_evidence": "IGA tool or manual recertification process evidence."},
            {"section": "Identity Governance", "question_code": "IAM-14", "question_text": "Are service accounts, API keys, and non-human identities inventoried and governed?", "question_text_ar": "هل يتم جرد وإدارة حسابات الخدمات ومفاتيح API والهويات غير البشرية؟", "framework_reference": "ISO 27001 A.5.18", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Service account register and rotation schedule."},
            {"section": "Identity Governance", "question_code": "IAM-15", "question_text": "Are password policies enforced technically (length, complexity, expiry, history)?", "question_text_ar": "هل تُطبَّق سياسات كلمات المرور تقنياً (الطول، التعقيد، الانتهاء، السجل)؟", "framework_reference": "NCA ECC 2-10", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Group Policy or IdP password policy settings."},
        ],
    },
    # -----------------------------------------------------------------------
    # 3. BCP / DR
    # -----------------------------------------------------------------------
    {
        "template_name": "BCP and Disaster Recovery Questionnaire",
        "template_name_ar": "استبيان استمرارية الأعمال والتعافي من الكوارث",
        "template_code": "BCP_DRP",
        "assessment_area": "BCP / DR",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess BCP/DR programme maturity across planning, testing, RTO/RPO, and ICT readiness.",
        "questions": [
            {"section": "BCP Framework", "question_code": "BCP-01", "question_text": "Is there an approved Business Continuity Policy and Management System (BCMS)?", "question_text_ar": "هل توجد سياسة معتمدة لاستمرارية الأعمال ونظام إدارة متكامل؟", "framework_reference": "ISO 22301 / NCA ECC 2-13", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Approved BCP policy and BCMS documentation."},
            {"section": "BCP Framework", "question_code": "BCP-02", "question_text": "Has a Business Impact Analysis (BIA) been completed and reviewed in the last 12 months?", "question_text_ar": "هل تم إجراء تحليل أثر الأعمال ومراجعته خلال الـ 12 شهراً الماضية؟", "framework_reference": "ISO 22301 Clause 8.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "BIA report with RTO/RPO targets."},
            {"section": "BCP Framework", "question_code": "BCP-03", "question_text": "Are Recovery Time Objectives (RTOs) and Recovery Point Objectives (RPOs) defined for all critical systems?", "question_text_ar": "هل تم تحديد أهداف وقت الاسترداد ونقاط الاسترداد لجميع الأنظمة الحساسة؟", "framework_reference": "ISO 22301 / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "RTO/RPO register linked to BIA."},
            {"section": "Backup & Recovery", "question_code": "BCP-04", "question_text": "Are automated backups performed and verified for all critical systems and data?", "question_text_ar": "هل تُنفَّذ النسخ الاحتياطية التلقائية ويتم التحقق منها لجميع الأنظمة والبيانات الحساسة؟", "framework_reference": "ISO 27001 A.8.13", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Backup schedule, retention policy, and restore test reports."},
            {"section": "Backup & Recovery", "question_code": "BCP-05", "question_text": "Are backups stored offsite or in a geographically separate cloud region?", "question_text_ar": "هل تُخزَّن النسخ الاحتياطية خارج الموقع أو في منطقة سحابية منفصلة جغرافياً؟", "framework_reference": "NCA ECC 2-13", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Offsite/cloud backup configuration evidence."},
            {"section": "Backup & Recovery", "question_code": "BCP-06", "question_text": "Are full restore tests conducted at least annually to verify RTO/RPO can be met?", "question_text_ar": "هل تُجرى اختبارات استعادة كاملة مرة واحدة على الأقل سنوياً للتحقق من تحقيق أهداف الاسترداد؟", "framework_reference": "ISO 27001 A.8.13 / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Restore test reports with pass/fail results."},
            {"section": "DR Plan", "question_code": "BCP-07", "question_text": "Is there a documented Disaster Recovery Plan (DRP) covering ICT systems?", "question_text_ar": "هل توجد خطة موثقة للتعافي من الكوارث تغطي أنظمة تقنية المعلومات والاتصالات؟", "framework_reference": "NCA ECC 2-13", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Approved DRP document."},
            {"section": "DR Plan", "question_code": "BCP-08", "question_text": "Is there a designated DR site (warm/hot standby or cloud failover) for critical systems?", "question_text_ar": "هل يوجد موقع تعافٍ مخصص (احتياطي دافئ/ساخن أو تحويل سحابي) للأنظمة الحساسة؟", "framework_reference": "SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "DR site contract, configuration, or cloud DR evidence."},
            {"section": "Testing", "question_code": "BCP-09", "question_text": "Are BCP/DR exercises (tabletop or full simulation) conducted at least annually?", "question_text_ar": "هل تُجرى تمارين استمرارية الأعمال/التعافي من الكوارث (طاولة المناقشة أو محاكاة كاملة) مرة سنوياً على الأقل؟", "framework_reference": "ISO 22301 Clause 8.5", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Exercise scenario, participant list, and lessons learned."},
            {"section": "Testing", "question_code": "BCP-10", "question_text": "Are lessons learned from BCP/DR tests formally captured and acted upon?", "question_text_ar": "هل يتم توثيق الدروس المستفادة من اختبارات الاستمرارية والتعافي والعمل بها رسمياً؟", "framework_reference": "ISO 22301 Clause 10", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Post-exercise report and improvement action log."},
            {"section": "Crisis Management", "question_code": "BCP-11", "question_text": "Is there a Crisis Management Team (CMT) with defined roles, escalation paths, and contact lists?", "question_text_ar": "هل توجد فرقة إدارة أزمات بأدوار محددة ومسارات تصعيد وقوائم اتصال؟", "framework_reference": "ISO 22301", "response_type": "Yes / No", "weight": 2, "expected_evidence": "CMT structure document and emergency contact list."},
            {"section": "Crisis Management", "question_code": "BCP-12", "question_text": "Does the BCP cover people (remote work, alternate facilities) as well as technology?", "question_text_ar": "هل تغطي خطة استمرارية الأعمال الأفراد (العمل عن بُعد، المرافق البديلة) إلى جانب التقنية؟", "framework_reference": "ISO 22301", "response_type": "Yes / No", "weight": 2, "expected_evidence": "People continuity provisions in BCP."},
            {"section": "Supply Chain Continuity", "question_code": "BCP-13", "question_text": "Are critical supplier dependencies identified and included in the BIA and BCP?", "question_text_ar": "هل يتم تحديد الاعتمادية على الموردين الحساسين وإدراجها في تحليل أثر الأعمال وخطة الاستمرارية؟", "framework_reference": "ISO 22301 / NCA ECC", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Supplier dependency mapping in BIA."},
            {"section": "Regulatory Notification", "question_code": "BCP-14", "question_text": "Are regulatory notification obligations (e.g., NCA 72-hour cyber incident reporting) documented and rehearsed?", "question_text_ar": "هل يتم توثيق وتمرين التزامات الإبلاغ التنظيمي (كالإبلاغ عن الحوادث السيبرانية خلال 72 ساعة لـ NCA)؟", "framework_reference": "NCA ECC / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Notification procedure and drill evidence."},
            {"section": "Plan Maintenance", "question_code": "BCP-15", "question_text": "Are BCP/DR plans reviewed and updated at least annually or after a major change?", "question_text_ar": "هل تتم مراجعة وتحديث خطط الاستمرارية والتعافي مرة سنوياً على الأقل أو بعد أي تغيير جوهري؟", "framework_reference": "ISO 22301", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Plan version history and review log."},
        ],
    },
    # -----------------------------------------------------------------------
    # 4. Privacy and PDPL
    # -----------------------------------------------------------------------
    {
        "template_name": "Privacy and Data Protection Questionnaire",
        "template_name_ar": "استبيان الخصوصية وحماية البيانات",
        "template_code": "PRIVACY_PDPL",
        "assessment_area": "Privacy",
        "framework": "PDPL",
        "country_scope": "Saudi Arabia",
        "industry_scope": "All Industries",
        "objective": "Assess PDPL compliance maturity across lawful basis, data subject rights, transfers, and breach management.",
        "questions": [
            {"section": "Lawful Basis", "question_code": "PRI-01", "question_text": "Is a lawful basis documented for every personal data processing activity?", "question_text_ar": "هل يوجد أساس قانوني موثق لكل نشاط معالجة للبيانات الشخصية؟", "framework_reference": "PDPL Article 5", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Processing register with legal basis column."},
            {"section": "Lawful Basis", "question_code": "PRI-02", "question_text": "Where consent is the lawful basis, is it freely given, specific, informed, and withdrawable?", "question_text_ar": "عندما تكون الموافقة هي الأساس القانوني، هل تُمنح بحرية وبشكل محدد ومستنير وقابلة للسحب؟", "framework_reference": "PDPL Article 5-6", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Consent forms and withdrawal mechanism evidence."},
            {"section": "Processing Register", "question_code": "PRI-03", "question_text": "Is a Record of Processing Activities (RoPA) maintained and regularly updated?", "question_text_ar": "هل يتم الاحتفاظ بسجل أنشطة المعالجة وتحديثه بانتظام؟", "framework_reference": "PDPL Article 12", "response_type": "Yes / No", "weight": 3, "expected_evidence": "RoPA document with last review date."},
            {"section": "Processing Register", "question_code": "PRI-04", "question_text": "Does the RoPA include purpose, legal basis, categories, retention, and recipients for each activity?", "question_text_ar": "هل يشمل سجل الأنشطة الغرض والأساس القانوني والفئات وفترة الاحتفاظ والمستلمين لكل نشاط؟", "framework_reference": "PDPL Article 12", "response_type": "Yes / No", "weight": 2, "expected_evidence": "RoPA completeness check."},
            {"section": "Data Subject Rights", "question_code": "PRI-05", "question_text": "Is there a process to receive and respond to data subject requests (access, correction, deletion) within 30 days?", "question_text_ar": "هل توجد عملية لاستقبال والرد على طلبات أصحاب البيانات (الوصول، التصحيح، الحذف) خلال 30 يوماً؟", "framework_reference": "PDPL Article 7-10", "response_type": "Yes / No", "weight": 3, "expected_evidence": "DSR process document and response log."},
            {"section": "Data Subject Rights", "question_code": "PRI-06", "question_text": "Are data subject requests logged, tracked, and responded to within the PDPL statutory deadline?", "question_text_ar": "هل يتم تسجيل وتتبع طلبات أصحاب البيانات والرد عليها ضمن الموعد القانوني المحدد في PDPL؟", "framework_reference": "PDPL Article 7", "response_type": "Yes / No", "weight": 3, "expected_evidence": "DSR tracker with response timestamps."},
            {"section": "Cross-Border Transfers", "question_code": "PRI-07", "question_text": "Are cross-border data transfers assessed and approved before data leaves Saudi Arabia?", "question_text_ar": "هل يتم تقييم واعتماد نقل البيانات عبر الحدود قبل خروج البيانات من المملكة العربية السعودية؟", "framework_reference": "PDPL Article 29", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Transfer impact assessment and SDAIA approval evidence."},
            {"section": "Cross-Border Transfers", "question_code": "PRI-08", "question_text": "Are data transfer agreements (DTAs) or standard contractual clauses in place with overseas processors?", "question_text_ar": "هل توجد اتفاقيات نقل بيانات أو شروط تعاقدية قياسية مع المعالجين في الخارج؟", "framework_reference": "PDPL Article 29", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Signed DTAs or SCCs."},
            {"section": "Data Retention", "question_code": "PRI-09", "question_text": "Is a data retention schedule defined and enforced with automated deletion or archival?", "question_text_ar": "هل تم تحديد جدول الاحتفاظ بالبيانات وتطبيقه مع الحذف أو الأرشفة الآلية؟", "framework_reference": "PDPL Article 18", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Retention schedule and deletion/archival logs."},
            {"section": "Data Breach", "question_code": "PRI-10", "question_text": "Is there a documented personal data breach procedure aligned to the PDPL 72-hour notification requirement?", "question_text_ar": "هل توجد إجراءات موثقة لانتهاكات البيانات الشخصية بما يتوافق مع متطلب الإبلاغ خلال 72 ساعة وفق PDPL؟", "framework_reference": "PDPL Article 24", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Breach notification SOP and drill evidence."},
            {"section": "Data Breach", "question_code": "PRI-11", "question_text": "Have any personal data breaches occurred, and if so, were they notified to SDAIA and affected individuals?", "question_text_ar": "هل حدثت أي انتهاكات للبيانات الشخصية، وإن كانت كذلك هل تم إخطار الهيئة السعودية للبيانات والذكاء الاصطناعي والأفراد المتأثرين؟", "framework_reference": "PDPL Article 24", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Breach register and notification records."},
            {"section": "Privacy by Design", "question_code": "PRI-12", "question_text": "Is Privacy by Design and by Default incorporated in new system and product development?", "question_text_ar": "هل يتم دمج مبدأ الخصوصية بالتصميم والافتراضية في تطوير الأنظمة والمنتجات الجديدة؟", "framework_reference": "PDPL / ISO 29101", "response_type": "Yes / No", "weight": 2, "expected_evidence": "SDLC privacy checklist and DPIA reports."},
            {"section": "Data Processing Agreements", "question_code": "PRI-13", "question_text": "Are Data Processing Agreements (DPAs) in place with all third-party processors handling personal data?", "question_text_ar": "هل توجد اتفاقيات معالجة بيانات مع جميع الأطراف الثالثة التي تعالج البيانات الشخصية؟", "framework_reference": "PDPL Article 28", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Signed DPAs and processor inventory."},
            {"section": "Privacy Officer", "question_code": "PRI-14", "question_text": "Is a Privacy Officer or Data Protection Officer (DPO) appointed with documented responsibilities?", "question_text_ar": "هل تم تعيين مسؤول خصوصية أو مسؤول حماية بيانات بمسؤوليات موثقة؟", "framework_reference": "PDPL Article 30", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Appointment letter and role description."},
            {"section": "Staff Awareness", "question_code": "PRI-15", "question_text": "Have all staff handling personal data received PDPL-specific training in the last 12 months?", "question_text_ar": "هل تلقى جميع الموظفين الذين يتعاملون مع البيانات الشخصية تدريباً خاصاً بـ PDPL خلال الـ 12 شهراً الماضية؟", "framework_reference": "PDPL", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Training completion records and curriculum."},
        ],
    },
    # -----------------------------------------------------------------------
    # 5. OT / ICS Cybersecurity
    # -----------------------------------------------------------------------
    {
        "template_name": "OT ICS Cybersecurity Questionnaire",
        "template_name_ar": "استبيان الأمن السيبراني للأنظمة التشغيلية والتحكم الصناعي",
        "template_code": "OT_ICS_CSCC",
        "assessment_area": "OT / ICS",
        "framework": "NCA ECC",
        "country_scope": "Saudi Arabia",
        "industry_scope": "Energy, Utilities, Manufacturing",
        "objective": "Assess OT/ICS cybersecurity maturity aligned to NCA ECC, IEC 62443, and Aramco Third Party Standard.",
        "questions": [
            {"section": "OT Asset Inventory", "question_code": "OT-01", "question_text": "Is a complete and up-to-date inventory of all OT/ICS assets maintained?", "question_text_ar": "هل يتم الاحتفاظ بجرد كامل ومحدث لجميع أصول الأنظمة التشغيلية والتحكم الصناعي؟", "framework_reference": "IEC 62443-2-1 / NCA ECC 2-1", "response_type": "Yes / No", "weight": 3, "expected_evidence": "OT asset register with firmware versions and owners."},
            {"section": "Network Segmentation", "question_code": "OT-02", "question_text": "Are OT/ICS networks segregated from IT corporate networks using firewalls or DMZ?", "question_text_ar": "هل يتم عزل شبكات الأنظمة التشغيلية عن شبكات تقنية المعلومات باستخدام جدران حماية أو منطقة محايدة؟", "framework_reference": "IEC 62443 / NCA ECC 2-6", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Network architecture diagram showing OT/IT segmentation."},
            {"section": "Network Segmentation", "question_code": "OT-03", "question_text": "Are Purdue model or equivalent zone and conduit principles implemented?", "question_text_ar": "هل يتم تطبيق نموذج بوردو أو ما يعادله من مبادئ المناطق والقنوات؟", "framework_reference": "IEC 62443-3-2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Zone and conduit model diagram and firewall rules."},
            {"section": "Remote Access", "question_code": "OT-04", "question_text": "Is remote access to OT environments restricted, authenticated (MFA), logged, and monitored?", "question_text_ar": "هل يتم تقييد الوصول عن بُعد لبيئات الأنظمة التشغيلية مع المصادقة والتسجيل والمراقبة؟", "framework_reference": "NCA ECC 2-10 / IEC 62443", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Remote access policy, session logs, and MFA evidence."},
            {"section": "Patch Management", "question_code": "OT-05", "question_text": "Is there a risk-based OT patch management programme with vendor-approved procedures?", "question_text_ar": "هل يوجد برنامج لإدارة التحديثات لأنظمة OT قائم على المخاطر مع إجراءات معتمدة من الموردين؟", "framework_reference": "NCA ECC 2-7", "response_type": "Yes / No", "weight": 3, "expected_evidence": "OT patching schedule and last patch cycle evidence."},
            {"section": "Patch Management", "question_code": "OT-06", "question_text": "Are unpatched or end-of-life OT systems inventoried with compensating controls documented?", "question_text_ar": "هل يتم جرد أنظمة OT غير المُحدَّثة أو منتهية الصيانة مع توثيق الضوابط التعويضية؟", "framework_reference": "IEC 62443", "response_type": "Yes / No", "weight": 2, "expected_evidence": "EOL/unpatched system register and compensating controls."},
            {"section": "Monitoring & Detection", "question_code": "OT-07", "question_text": "Is OT-specific network monitoring and anomaly detection (e.g., Claroty, Dragos, Nozomi) deployed?", "question_text_ar": "هل يتم نشر مراقبة شبكية واكتشاف شذوذات خاصة بـ OT؟", "framework_reference": "NCA ECC 2-9 / IEC 62443", "response_type": "Yes / No", "weight": 3, "expected_evidence": "OT monitoring tool deployment evidence and alert examples."},
            {"section": "Monitoring & Detection", "question_code": "OT-08", "question_text": "Are OT security events correlated with IT security events in a unified SOC or SIEM?", "question_text_ar": "هل يتم ربط أحداث أمن OT مع أحداث أمن IT في مركز عمليات موحد أو نظام SIEM؟", "framework_reference": "NCA ECC 2-9", "response_type": "Yes / No", "weight": 2, "expected_evidence": "SIEM integration evidence and OT use cases."},
            {"section": "Incident Response", "question_code": "OT-09", "question_text": "Is there an OT-specific incident response plan with safety and production impact considerations?", "question_text_ar": "هل توجد خطة استجابة للحوادث خاصة بأنظمة OT تراعي اعتبارات السلامة وتأثير الإنتاج؟", "framework_reference": "NCA ECC 2-11", "response_type": "Yes / No", "weight": 3, "expected_evidence": "OT IRP document and drill record."},
            {"section": "Physical Security", "question_code": "OT-10", "question_text": "Is physical access to control rooms, substations, and HMI consoles restricted and logged?", "question_text_ar": "هل يتم تقييد وتسجيل الوصول المادي إلى غرف التحكم والمحطات الفرعية ووحدات الواجهة البشرية؟", "framework_reference": "IEC 62443 / NCA ECC 2-12", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Access control logs and CCTV policy."},
            {"section": "Supply Chain OT", "question_code": "OT-11", "question_text": "Are OT vendors and integrators subject to security requirements and periodic reassessment?", "question_text_ar": "هل يخضع موردو وفنيو أنظمة OT لمتطلبات أمنية وإعادة تقييم دورية؟", "framework_reference": "Aramco Third Party Standard", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Vendor security requirements and assessment reports."},
            {"section": "Vulnerability Management", "question_code": "OT-12", "question_text": "Are OT-specific vulnerability feeds (ICS-CERT, vendor advisories) monitored and acted upon?", "question_text_ar": "هل يتم مراقبة مصادر الثغرات الخاصة بأنظمة OT والتصرف بناءً عليها؟", "framework_reference": "IEC 62443 / NCA ECC 2-7", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Vulnerability feed subscription and response log."},
            {"section": "Safe Configuration", "question_code": "OT-13", "question_text": "Are OT components hardened using vendor-approved or industry-standard secure configurations?", "question_text_ar": "هل تُقوَّى مكونات OT باستخدام إعدادات آمنة معتمدة من الموردين أو المعايير الصناعية؟", "framework_reference": "IEC 62443 / CIS", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Hardening checklists and configuration audit reports."},
            {"section": "Safe Configuration", "question_code": "OT-14", "question_text": "Are default credentials changed on all OT devices before deployment?", "question_text_ar": "هل يتم تغيير بيانات الاعتماد الافتراضية على جميع أجهزة OT قبل النشر؟", "framework_reference": "IEC 62443", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Commissioning checklist with credential change verification."},
            {"section": "Awareness", "question_code": "OT-15", "question_text": "Do OT operators and engineers receive cybersecurity training relevant to ICS environments?", "question_text_ar": "هل يتلقى مشغلو ومهندسو OT تدريباً على الأمن السيبراني المتعلق ببيئات ICS؟", "framework_reference": "NCA ECC", "response_type": "Yes / No", "weight": 2, "expected_evidence": "OT security training records."},
        ],
    },
    # -----------------------------------------------------------------------
    # 6. AI Governance
    # -----------------------------------------------------------------------
    {
        "template_name": "AI Governance Questionnaire",
        "template_name_ar": "استبيان حوكمة الذكاء الاصطناعي",
        "template_code": "AI_GOV_42001",
        "assessment_area": "AI Governance",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess AI governance readiness for policy, risk, impact assessment, monitoring, and audit readiness aligned to ISO 42001 and emerging Saudi AI regulations.",
        "questions": [
            {"section": "AI Policy", "question_code": "AI-01", "question_text": "Is there an approved AI Policy covering acceptable use, prohibited uses, and ethical principles?", "question_text_ar": "هل توجد سياسة ذكاء اصطناعي معتمدة تغطي الاستخدام المقبول والمحظور والمبادئ الأخلاقية؟", "framework_reference": "ISO 42001 Clause 5.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Approved AI policy document."},
            {"section": "AI Policy", "question_code": "AI-02", "question_text": "Does the AI policy address data quality, bias prevention, transparency, and explainability?", "question_text_ar": "هل تتناول سياسة الذكاء الاصطناعي جودة البيانات والوقاية من التحيز والشفافية وقابلية التفسير؟", "framework_reference": "ISO 42001 A.6.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Policy content review covering these areas."},
            {"section": "AI Risk", "question_code": "AI-03", "question_text": "Is AI risk assessment performed before deploying AI systems into production?", "question_text_ar": "هل يتم إجراء تقييم مخاطر الذكاء الاصطناعي قبل نشر أنظمة الذكاء الاصطناعي في الإنتاج؟", "framework_reference": "ISO 42001 Clause 6.1.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "AI risk assessment methodology and completed assessments."},
            {"section": "AI Risk", "question_code": "AI-04", "question_text": "Is there an AI system inventory covering all models, vendors, and use cases?", "question_text_ar": "هل يوجد جرد لأنظمة الذكاء الاصطناعي يغطي جميع النماذج والموردين وحالات الاستخدام؟", "framework_reference": "ISO 42001 A.5.1", "response_type": "Yes / No", "weight": 3, "expected_evidence": "AI system register with risk classification."},
            {"section": "AI Impact Assessment", "question_code": "AI-05", "question_text": "Are AI Impact Assessments (AIIAs) performed for high-risk AI systems affecting individuals or public safety?", "question_text_ar": "هل تُجرى تقييمات أثر الذكاء الاصطناعي للأنظمة عالية المخاطر التي تؤثر على الأفراد أو السلامة العامة؟", "framework_reference": "ISO 42001 A.5.2-A.5.5", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Completed AIIA reports for high-risk systems."},
            {"section": "AI Impact Assessment", "question_code": "AI-06", "question_text": "Are societal impacts (bias, discrimination, misinformation) assessed for AI outputs?", "question_text_ar": "هل يتم تقييم التأثيرات المجتمعية (التحيز، التمييز، المعلومات المضللة) لمخرجات الذكاء الاصطناعي؟", "framework_reference": "ISO 42001 A.5.4", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Bias assessment and fairness testing reports."},
            {"section": "Third-Party AI", "question_code": "AI-07", "question_text": "Are third-party AI tools and LLMs assessed for privacy, data leakage, and compliance risks before use?", "question_text_ar": "هل يتم تقييم أدوات الذكاء الاصطناعي الخارجية ونماذج اللغة الكبيرة لمخاطر الخصوصية وتسريب البيانات والامتثال قبل الاستخدام؟", "framework_reference": "ISO 42001 A.8", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Third-party AI assessment records."},
            {"section": "Third-Party AI", "question_code": "AI-08", "question_text": "Are employees prohibited from submitting confidential, personal, or regulated data to public AI tools (e.g., ChatGPT)?", "question_text_ar": "هل يُحظر على الموظفين إدخال بيانات سرية أو شخصية أو خاضعة للتنظيم في أدوات الذكاء الاصطناعي العامة؟", "framework_reference": "PDPL / AI Policy", "response_type": "Yes / No", "weight": 3, "expected_evidence": "AI use policy with data handling rules and DLP controls."},
            {"section": "AI Monitoring", "question_code": "AI-09", "question_text": "Are AI models monitored for performance degradation, drift, and accuracy over time?", "question_text_ar": "هل تُراقَب نماذج الذكاء الاصطناعي لرصد تدهور الأداء والانجراف والدقة بمرور الوقت؟", "framework_reference": "ISO 42001 Clause 9.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Model monitoring logs and performance dashboards."},
            {"section": "AI Monitoring", "question_code": "AI-10", "question_text": "Is there a process to detect, investigate, and remediate AI-generated harmful or incorrect outputs?", "question_text_ar": "هل توجد عملية لاكتشاف والتحقيق في المخرجات الضارة أو غير الصحيحة للذكاء الاصطناعي ومعالجتها؟", "framework_reference": "ISO 42001 Clause 10", "response_type": "Yes / No", "weight": 2, "expected_evidence": "AI incident log and remediation procedure."},
            {"section": "Human Oversight", "question_code": "AI-11", "question_text": "Are human-in-the-loop controls applied to high-risk AI decisions (e.g., hiring, credit, medical)?", "question_text_ar": "هل تُطبَّق ضوابط الإشراف البشري على قرارات الذكاء الاصطناعي عالية المخاطر كالتوظيف والائتمان والرعاية الصحية؟", "framework_reference": "ISO 42001 A.5.6", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Process documentation showing human review checkpoints."},
            {"section": "AI Governance", "question_code": "AI-12", "question_text": "Is there a designated AI Ethics or AI Governance committee with defined responsibilities?", "question_text_ar": "هل توجد لجنة أخلاقيات ذكاء اصطناعي أو حوكمة ذكاء اصطناعي مخصصة بمسؤوليات محددة؟", "framework_reference": "ISO 42001 Clause 5.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Committee TOR and meeting records."},
            {"section": "Transparency", "question_code": "AI-13", "question_text": "Are users informed when they are interacting with or impacted by an AI system?", "question_text_ar": "هل يتم إعلام المستخدمين عند تفاعلهم مع نظام ذكاء اصطناعي أو تأثرهم به؟", "framework_reference": "ISO 42001 / PDPL", "response_type": "Yes / No", "weight": 2, "expected_evidence": "AI disclosure statements and user notifications."},
            {"section": "Regulatory Compliance", "question_code": "AI-14", "question_text": "Are emerging Saudi AI regulations (SDAIA AI Ethics Principles, NCA AI guidelines) monitored and incorporated?", "question_text_ar": "هل يتم رصد لوائح الذكاء الاصطناعي السعودية الناشئة (مبادئ أخلاقيات الذكاء الاصطناعي لـ SDAIA، وإرشادات NCA) ودمجها؟", "framework_reference": "SDAIA / NCA", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Regulatory horizon scanning log and compliance gap assessment."},
            {"section": "AI Training Data", "question_code": "AI-15", "question_text": "Are training datasets assessed for bias, provenance, licensing, and personal data inclusion?", "question_text_ar": "هل تُقيَّم مجموعات بيانات التدريب من حيث التحيز والمصدر والترخيص وتضمين البيانات الشخصية؟", "framework_reference": "ISO 42001 A.6 / PDPL", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Data provenance documentation and bias testing results."},
        ],
    },
    # -----------------------------------------------------------------------
    # 7. Integrated Compliance
    # -----------------------------------------------------------------------
    {
        "template_name": "Integrated Compliance and Common Controls Questionnaire",
        "template_name_ar": "استبيان الامتثال المتكامل والضوابط المشتركة",
        "template_code": "INTG_COMPLIANCE",
        "assessment_area": "Compliance",
        "framework": "NCA ECC",
        "country_scope": "Saudi Arabia",
        "industry_scope": "All Industries",
        "objective": "Assess cross-framework compliance maturity covering NCA ECC, SAMA CSF, ISO 27001 common controls.",
        "questions": [
            {"section": "Asset Management", "question_code": "INT-01", "question_text": "Is there a complete and regularly updated asset inventory covering hardware, software, and data assets?", "question_text_ar": "هل يوجد جرد أصول كامل ومحدث بانتظام يشمل الأجهزة والبرامج وأصول البيانات؟", "framework_reference": "ISO 27001 A.5.9 / NCA ECC 2-1", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Asset register with classification, owner, and location."},
            {"section": "Asset Management", "question_code": "INT-02", "question_text": "Are information assets classified according to sensitivity (Public, Internal, Confidential, Restricted)?", "question_text_ar": "هل يتم تصنيف أصول المعلومات وفق درجة الحساسية (عام، داخلي، سري، مقيد)؟", "framework_reference": "ISO 27001 A.5.12 / NCA ECC 2-2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Classification policy and labelled asset examples."},
            {"section": "Vulnerability Management", "question_code": "INT-03", "question_text": "Are regular vulnerability scans (at least quarterly) performed across all in-scope systems?", "question_text_ar": "هل تُجرى فحوصات منتظمة للثغرات (ربع سنوية على الأقل) لجميع الأنظمة المعنية؟", "framework_reference": "NCA ECC 2-7 / ISO 27001 A.8.8", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Scan reports and remediation tracking."},
            {"section": "Vulnerability Management", "question_code": "INT-04", "question_text": "Are critical/high vulnerabilities remediated within defined SLAs (e.g., Critical < 7 days)?", "question_text_ar": "هل تُعالَج الثغرات الحرجة/العالية ضمن مستويات خدمة محددة (مثل: حرجة < 7 أيام)؟", "framework_reference": "NCA ECC 2-7", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Vulnerability SLA policy and closure report."},
            {"section": "Penetration Testing", "question_code": "INT-05", "question_text": "Is annual penetration testing conducted by qualified testers on all critical systems?", "question_text_ar": "هل يتم إجراء اختبار اختراق سنوي من قِبل مختبرين مؤهلين لجميع الأنظمة الحساسة؟", "framework_reference": "NCA ECC 2-7 / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Pentest report and remediation tracker."},
            {"section": "Logging & Monitoring", "question_code": "INT-06", "question_text": "Are security events logged centrally in a SIEM with defined retention (at least 12 months)?", "question_text_ar": "هل تُسجَّل أحداث الأمن مركزياً في نظام SIEM مع فترة احتفاظ محددة (12 شهراً على الأقل)؟", "framework_reference": "NCA ECC 2-9 / ISO 27001 A.8.15", "response_type": "Yes / No", "weight": 3, "expected_evidence": "SIEM configuration and log retention policy."},
            {"section": "Logging & Monitoring", "question_code": "INT-07", "question_text": "Are SIEM alerts triaged and investigated by a SOC or equivalent team with defined SLAs?", "question_text_ar": "هل يتم فرز والتحقيق في تنبيهات SIEM من قِبل فريق عمليات أمن أو ما يعادله ضمن مستويات خدمة محددة؟", "framework_reference": "NCA ECC 2-9", "response_type": "Yes / No", "weight": 3, "expected_evidence": "SOC runbook and alert triage metrics."},
            {"section": "Change Management", "question_code": "INT-08", "question_text": "Are all changes to production systems processed through a formal change management process?", "question_text_ar": "هل تمر جميع التغييرات على أنظمة الإنتاج عبر عملية إدارة تغيير رسمية؟", "framework_reference": "ISO 27001 A.8.32 / NCA ECC", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Change management policy and change request log."},
            {"section": "Endpoint Security", "question_code": "INT-09", "question_text": "Is EDR/antimalware deployed and actively monitored on all endpoints and servers?", "question_text_ar": "هل يتم نشر ومراقبة اكتشاف نقاط النهاية والاستجابة لها على جميع الأجهزة والخوادم؟", "framework_reference": "NCA ECC 2-7 / ISO 27001 A.8.7", "response_type": "Yes / No", "weight": 3, "expected_evidence": "EDR deployment coverage report and alert examples."},
            {"section": "Encryption", "question_code": "INT-10", "question_text": "Is data encrypted at rest and in transit for all sensitive and confidential information?", "question_text_ar": "هل يتم تشفير البيانات أثناء التخزين والنقل لجميع المعلومات الحساسة والسرية؟", "framework_reference": "ISO 27001 A.8.24 / NCA ECC 2-3", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Encryption policy and TLS/disk encryption configuration."},
            {"section": "Email Security", "question_code": "INT-11", "question_text": "Are email security controls (SPF, DKIM, DMARC, anti-phishing) configured and verified?", "question_text_ar": "هل يتم تكوين والتحقق من ضوابط أمن البريد الإلكتروني (SPF وDKIM وDMARC ومكافحة التصيد)؟", "framework_reference": "NCA ECC 2-6", "response_type": "Yes / No", "weight": 2, "expected_evidence": "DNS record check and email gateway configuration."},
            {"section": "Cloud Security", "question_code": "INT-12", "question_text": "Are cloud environments governed by a Cloud Security Policy and reviewed against CIS or CSP benchmarks?", "question_text_ar": "هل تخضع بيئات السحابة لسياسة أمان سحابية ومراجعة مقارنة بمعايير CIS أو الموردين السحابيين؟", "framework_reference": "NCA CSCC / ISO 27001 A.5.23", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Cloud security policy and CSPM scan reports."},
            {"section": "Supplier Security", "question_code": "INT-13", "question_text": "Do supplier contracts include minimum cybersecurity requirements and right-to-audit clauses?", "question_text_ar": "هل تتضمن عقود الموردين متطلبات أمن سيبراني دنيا وبنود حق التدقيق؟", "framework_reference": "ISO 27001 A.5.20 / Aramco TP Standard", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Standard contract clauses or MSA template."},
            {"section": "Compliance Monitoring", "question_code": "INT-14", "question_text": "Is compliance with regulatory obligations tracked, evidenced, and reported on a regular cadence?", "question_text_ar": "هل يتم تتبع وتوثيق والإبلاغ عن الامتثال للالتزامات التنظيمية بصفة منتظمة؟", "framework_reference": "NCA ECC / SAMA CSF / PDPL", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Compliance tracker and management reports."},
            {"section": "Compliance Monitoring", "question_code": "INT-15", "question_text": "Is there a regulatory horizon scanning process to identify and assess upcoming changes in laws and standards?", "question_text_ar": "هل توجد عملية لرصد الأفق التنظيمي لتحديد وتقييم التغييرات القادمة في القوانين والمعايير؟", "framework_reference": "ISO 27001 A.5.31", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Horizon scanning log and impact assessments."},
        ],
    },
    # -----------------------------------------------------------------------
    # 8. Vendor and Third-Party Risk
    # -----------------------------------------------------------------------
    {
        "template_name": "Vendor and Third-Party Risk Questionnaire",
        "template_name_ar": "استبيان مخاطر الموردين والأطراف الثالثة",
        "template_code": "VENDOR_RISK",
        "assessment_area": "Vendor Risk",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess third-party risk management maturity across due diligence, contracts, monitoring, and Aramco standard alignment.",
        "questions": [
            {"section": "Due Diligence", "question_code": "VEN-01", "question_text": "Is a formal third-party risk assessment performed before onboarding any new vendor?", "question_text_ar": "هل يتم إجراء تقييم رسمي لمخاطر الطرف الثالث قبل إدراج أي مورد جديد؟", "framework_reference": "ISO 27001 A.5.19 / Aramco TP Standard", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Vendor onboarding form and pre-assessment questionnaire."},
            {"section": "Due Diligence", "question_code": "VEN-02", "question_text": "Is vendor criticality and data handling classified (critical/high/medium/low) during due diligence?", "question_text_ar": "هل يتم تصنيف أهمية المورد وحجم التعامل مع البيانات خلال عملية العناية الواجبة؟", "framework_reference": "Aramco TP Standard / PDPL", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Criticality classification matrix and completed assessments."},
            {"section": "Contracts", "question_code": "VEN-03", "question_text": "Do supplier contracts include security, privacy, breach notification, and audit rights clauses?", "question_text_ar": "هل تتضمن عقود الموردين بنوداً للأمن والخصوصية والإبلاغ عن الاختراقات وحقوق التدقيق؟", "framework_reference": "ISO 27001 A.5.20", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Standard contract clauses or MSA templates."},
            {"section": "Contracts", "question_code": "VEN-04", "question_text": "Are SLAs and KPIs for security performance defined and measured in vendor contracts?", "question_text_ar": "هل يتم تحديد وقياس مستويات الخدمة ومؤشرات أداء الأمن في عقود الموردين؟", "framework_reference": "ISO 27001 A.5.20", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Contract SLA clauses and performance reports."},
            {"section": "Monitoring", "question_code": "VEN-05", "question_text": "Are third-party services periodically monitored, reviewed, and re-assessed based on risk?", "question_text_ar": "هل تتم مراقبة خدمات الأطراف الثالثة ومراجعتها وإعادة تقييمها بصفة دورية بناءً على المخاطر؟", "framework_reference": "ISO 27001 A.5.22", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Vendor review calendar and reassessment evidence."},
            {"section": "Monitoring", "question_code": "VEN-06", "question_text": "Are critical vendors required to provide independent assurance (SOC 2, ISO 27001, SAMA CSF)?", "question_text_ar": "هل يُطلب من الموردين الحساسين تقديم ضمان مستقل (SOC 2، ISO 27001، SAMA CSF)؟", "framework_reference": "SAMA CSF / ISO 27001 A.5.22", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Assurance reports or certification copies from critical vendors."},
            {"section": "Cloud", "question_code": "VEN-07", "question_text": "Are cloud services assessed for data protection, residency, resilience, and shared responsibility?", "question_text_ar": "هل تُقيَّم الخدمات السحابية من ناحية حماية البيانات وإقامة البيانات والمرونة ومسؤوليات المشاركة؟", "framework_reference": "NCA CSCC / ISO 27001 A.5.23", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Cloud risk assessment and shared responsibility matrix."},
            {"section": "Cloud", "question_code": "VEN-08", "question_text": "Are cloud data residency requirements (Saudi Arabia or GCC) verified for regulated data?", "question_text_ar": "هل يتم التحقق من متطلبات إقامة البيانات السحابية (السعودية أو دول مجلس التعاون الخليجي) للبيانات الخاضعة للتنظيم؟", "framework_reference": "PDPL / NCA CSCC", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Cloud provider data residency agreement and configuration."},
            {"section": "Subcontracting", "question_code": "VEN-09", "question_text": "Is subcontracting by key vendors controlled, notified, and subject to equivalent security requirements?", "question_text_ar": "هل يتم التحكم في تعاقد الموردين الرئيسيين من الباطن وإخطاره وتطبيق متطلبات أمنية مماثلة؟", "framework_reference": "Aramco TP Standard / ISO 27001 A.5.19", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Sub-contractor clause in contracts and approval process."},
            {"section": "Incident Management", "question_code": "VEN-10", "question_text": "Are vendors contractually required to notify you of security incidents within 24-72 hours?", "question_text_ar": "هل يُلزَم الموردون تعاقدياً بإخطارك بالحوادث الأمنية خلال 24-72 ساعة؟", "framework_reference": "NCA ECC / PDPL", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Incident notification clause in contracts."},
            {"section": "Offboarding", "question_code": "VEN-11", "question_text": "Is there a formal vendor offboarding process covering data return, deletion, and access revocation?", "question_text_ar": "هل توجد عملية رسمية لإنهاء علاقة المورد تشمل إعادة البيانات وحذفها وإلغاء الوصول؟", "framework_reference": "ISO 27001 A.5.19 / PDPL", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Offboarding checklist and data destruction certificate."},
            {"section": "Aramco Alignment", "question_code": "VEN-12", "question_text": "For Aramco-related engagements, is the Third Party Profile registered and current in the Aramco system?", "question_text_ar": "للمشاركات المرتبطة بأرامكو، هل تم تسجيل ملف الطرف الثالث وهو محدّث في نظام أرامكو؟", "framework_reference": "Aramco Third Party Standard", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Aramco third-party profile and current assessment status."},
            {"section": "Aramco Alignment", "question_code": "VEN-13", "question_text": "Has the organisation completed the Aramco Cybersecurity Third Party Assessment and received a score?", "question_text_ar": "هل أكملت المؤسسة تقييم الأمن السيبراني لأطراف أرامكو الثالثة وحصلت على نتيجة؟", "framework_reference": "Aramco Third Party Standard", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Aramco assessment report and score letter."},
            {"section": "Concentration Risk", "question_code": "VEN-14", "question_text": "Is concentration risk (over-dependence on single vendors) identified and mitigated?", "question_text_ar": "هل يتم تحديد ومعالجة مخاطر التركيز (الاعتماد المفرط على موردين بعينهم)؟", "framework_reference": "SAMA CSF / ISO 31000", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Concentration risk analysis and mitigation plans."},
            {"section": "Performance Reporting", "question_code": "VEN-15", "question_text": "Is third-party risk status reported to senior management at least quarterly?", "question_text_ar": "هل يتم الإبلاغ عن حالة مخاطر الأطراف الثالثة للإدارة العليا ربع سنوياً على الأقل؟", "framework_reference": "ISO 27001 A.5.22", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Third-party risk management report."},
        ],
    },
    # -----------------------------------------------------------------------
    # 9. Audit Readiness
    # -----------------------------------------------------------------------
    {
        "template_name": "Audit Readiness Questionnaire",
        "template_name_ar": "استبيان جاهزية التدقيق",
        "template_code": "AUDIT_READY",
        "assessment_area": "Audit Readiness",
        "framework": "ISO 27001",
        "country_scope": "Global",
        "industry_scope": "All Industries",
        "objective": "Assess audit planning readiness, evidence availability, findings management, and management action planning.",
        "questions": [
            {"section": "Audit Planning", "question_code": "AUD-01", "question_text": "Is there an annual or periodic internal audit plan with scope, objectives, and timelines?", "question_text_ar": "هل توجد خطة تدقيق داخلي سنوية أو دورية تتضمن النطاق والأهداف والجداول الزمنية؟", "framework_reference": "ISO 27001 Clause 9.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Internal audit programme or planning document."},
            {"section": "Audit Planning", "question_code": "AUD-02", "question_text": "Is the audit scope risk-based and aligned to the current regulatory and threat landscape?", "question_text_ar": "هل يعتمد نطاق التدقيق على المخاطر ويتوافق مع البيئة التنظيمية وبيئة التهديدات الحالية؟", "framework_reference": "ISO 27001 Clause 9.2", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Audit universe and risk-based planning rationale."},
            {"section": "Audit Planning", "question_code": "AUD-03", "question_text": "Is internal audit independent from operational management and adequately resourced?", "question_text_ar": "هل يتمتع التدقيق الداخلي باستقلالية عن الإدارة التشغيلية وهل يتمتع بموارد كافية؟", "framework_reference": "IIA Standards", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Audit charter confirming independence and resource plan."},
            {"section": "Audit Methodology", "question_code": "AUD-04", "question_text": "Are sample selection, walkthrough, and evidence review methodologies documented?", "question_text_ar": "هل تم توثيق منهجيات اختيار العينات والجولات التوضيحية ومراجعة الأدلة؟", "framework_reference": "Audit Methodology", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Audit methodology document and workpaper templates."},
            {"section": "Audit Methodology", "question_code": "AUD-05", "question_text": "Are audit workpapers reviewed and signed off by an audit supervisor before report issuance?", "question_text_ar": "هل تتم مراجعة أوراق عمل التدقيق والتوقيع عليها من قِبل مشرف التدقيق قبل إصدار التقرير؟", "framework_reference": "IIA Standards", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Signed workpapers and review evidence."},
            {"section": "Evidence Management", "question_code": "AUD-06", "question_text": "Is audit evidence collected, stored securely, and retained for at least 5 years?", "question_text_ar": "هل يتم جمع أدلة التدقيق وتخزينها بأمان والاحتفاظ بها لمدة 5 سنوات على الأقل؟", "framework_reference": "ISO 27001 / NCA ECC", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Evidence retention policy and secure storage evidence."},
            {"section": "Evidence Management", "question_code": "AUD-07", "question_text": "Is evidence tagged and cross-referenced to specific control requirements?", "question_text_ar": "هل يتم وسم الأدلة وربطها بالإشارة الخلبية بمتطلبات ضوابط محددة؟", "framework_reference": "ISO 27001", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Evidence register with control mapping."},
            {"section": "Findings Management", "question_code": "AUD-08", "question_text": "Are audit findings risk-rated (Critical/High/Medium/Low) and linked to management action plans?", "question_text_ar": "هل يتم تصنيف نتائج التدقيق حسب المخاطر وربطها بخطط الإجراءات الإدارية؟", "framework_reference": "IIA / ISO 27001", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Findings register with ratings and MAP tracker."},
            {"section": "Findings Management", "question_code": "AUD-09", "question_text": "Are remediation actions tracked with owners, due dates, and evidence of completion?", "question_text_ar": "هل يتم تتبع إجراءات المعالجة مع المالكين وتواريخ الاستحقاق وأدلة الإتمام؟", "framework_reference": "ISO 27001 Clause 10", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Remediation tracker with closure evidence."},
            {"section": "Findings Management", "question_code": "AUD-10", "question_text": "Are repeat findings tracked and subject to escalation if recurring in successive audit cycles?", "question_text_ar": "هل يتم تتبع النتائج المتكررة وتصعيدها إذا تكررت في دورات تدقيق متتالية؟", "framework_reference": "IIA Standards", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Repeat findings analysis and escalation records."},
            {"section": "Reporting", "question_code": "AUD-11", "question_text": "Are audit results, responses, and final reports formally approved and distributed?", "question_text_ar": "هل يتم اعتماد نتائج التدقيق والاستجابات والتقارير النهائية وتوزيعها رسمياً؟", "framework_reference": "IIA / ISO 27001", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Approved reports and distribution evidence."},
            {"section": "Reporting", "question_code": "AUD-12", "question_text": "Is the audit report presented to senior management or the audit committee with management response?", "question_text_ar": "هل يتم تقديم تقرير التدقيق للإدارة العليا أو لجنة التدقيق مع رد الإدارة؟", "framework_reference": "IIA Standards", "response_type": "Yes / No", "weight": 3, "expected_evidence": "Audit committee meeting minutes with report presentation."},
            {"section": "External Audit", "question_code": "AUD-13", "question_text": "Are external assessments (ISO 27001, NCA ECC, SAMA CSF) planned and actioned at least every 2-3 years?", "question_text_ar": "هل يتم التخطيط لإجراء التقييمات الخارجية (ISO 27001، NCA ECC، SAMA CSF) والعمل بها كل 2-3 سنوات على الأقل؟", "framework_reference": "NCA ECC / SAMA CSF", "response_type": "Yes / No", "weight": 3, "expected_evidence": "External assessment schedule and last report."},
            {"section": "Continuous Assurance", "question_code": "AUD-14", "question_text": "Is automated continuous control monitoring (CCM) in place for key controls?", "question_text_ar": "هل توجد مراقبة مستمرة وآلية للضوابط الرئيسية؟", "framework_reference": "ISO 27001 Clause 9.1", "response_type": "Yes / No", "weight": 2, "expected_evidence": "CCM tool or automated testing evidence."},
            {"section": "Audit Resources", "question_code": "AUD-15", "question_text": "Do internal auditors hold or are they pursuing relevant certifications (CISA, CIA, CISM, ISO 27001 LA)?", "question_text_ar": "هل يحمل المدققون الداخليون شهادات ذات صلة أو يسعون للحصول عليها (CISA، CIA، CISM، ISO 27001 LA)؟", "framework_reference": "IIA Standards", "response_type": "Yes / No", "weight": 2, "expected_evidence": "Auditor CVs and certification records."},
        ],
    },
]

RETIRED_APPS = ("alphax_grc_evidence_automation",)


def assert_module_ownership():
    """Fail fast and legibly when another bench app claims our modules.

    Frappe builds the module -> app map in setup_module_map() from
    `sites/apps.txt` (EVERY app on the bench, installed on this site or not)
    and each app's `modules.txt` on disk. Last app wins, and frappe only
    emits a warnings.warn() that nobody sees:

        WARNING: module `x` found in apps `a` and `b`

    So while the retired alphax_grc_evidence_automation app is still present
    on the bench, its modules.txt keeps claiming "GRC Evidence Automation",
    and doctype sync tries to import our controllers out of that package.
    No code in this app can override it: the map is built long before any
    app code runs. The only fix is removing the retired app from the bench.

    This turns the resulting ImportError at 95% into a readable failure at 0%.
    """
    try:
        our_modules = frappe.get_module_list("alphax_grc")
    except Exception:
        return

    conflicts = []
    for module in our_modules:
        try:
            owner = frappe.get_module_app(frappe.scrub(module))
        except Exception:
            continue
        if owner and owner != "alphax_grc":
            conflicts.append((module, owner))

    if not conflicts:
        return

    lines = [f"  - '{m}' is claimed by app '{a}'" for m, a in conflicts]
    apps = sorted({a for _m, a in conflicts})
    frappe.throw(
        "AlphaX GRC cannot install while another app on this bench declares "
        "the same module(s):\n\n" + "\n".join(lines) + "\n\n"
        "Frappe resolves a module to an app from sites/apps.txt plus each "
        "app's modules.txt, so the last app on the bench wins and this app's "
        "controllers get imported from the wrong package.\n\n"
        "Remove " + ", ".join(apps) + " from the bench group and deploy again. "
        "It does not need uninstalling from the site if it was never "
        "successfully installed.",
        title="Module name conflict on this bench",
    )


def retire_legacy_module_defs():
    """Reclaim modules left behind by the retired add-on app.

    Frappe resolves module -> app at runtime from `tabModule Def`.app_name
    (cached as frappe.local.module_app). A failed install of
    alphax_grc_evidence_automation leaves its Module Def rows on the site:
    the install aborts before the app is registered in installed_apps, so
    there is nothing to uninstall and nothing cleans them up.

    The next `bench install-app alphax_grc` then syncs GRC Evidence Automation
    doctypes, asks Module Def which app owns that module, gets the retired app
    name, and dies with:

        ImportError: No module named
        'alphax_grc_evidence_automation.grc_evidence_automation.doctype...'

    Repointing the row is safer than deleting it: the DocType rows already
    reference the module by name, and a delete would have to cascade through
    them. Runs in before_install (which executes ahead of sync_for) and again
    as a pre_model_sync patch so upgrades are covered too.
    """
    try:
        rows = frappe.get_all(
            "Module Def",
            filters={"app_name": ["in", list(RETIRED_APPS)]},
            fields=["name", "app_name"],
        )
    except Exception:
        return 0

    if not rows:
        return 0

    for row in rows:
        frappe.db.set_value("Module Def", row.name, "app_name", "alphax_grc",
                            update_modified=False)

    frappe.db.commit()

    # NEVER delattr on frappe.local. It is a werkzeug Local: deleting an
    # attribute does not reset it to a default, it makes every later read
    # raise AttributeError. frappe.local.module_app is populated once by
    # setup_module_map() during frappe.init() and nothing re-populates it
    # lazily, so deleting it broke the very next frappe.new_doc() call:
    #
    #     File "frappe/modules/utils.py", line 299, in get_module_app
    #         app = frappe.local.module_app.get(scrub(module))
    #     AttributeError: module_app
    #
    # Module -> app resolution comes from modules.txt on disk, not from the
    # Module Def rows repointed above, so there is nothing to invalidate here.
    # Clearing site caches is enough and leaves frappe.local intact.
    try:
        frappe.clear_cache()
    except Exception:
        pass

    try:
        frappe.log_error(
            title="AlphaX GRC v2.3.1: reclaimed %d module(s) from retired app" % len(rows),
            message="Repointed to alphax_grc: " + ", ".join(r.name for r in rows),
        )
    except Exception:
        pass

    return len(rows)


def before_install():
    """Cloud-safe pre-install guard for stale legacy Page fixtures.

    Note: bench install-app runs sync_fixtures BEFORE before_install, so this
    guard is primarily for re-install / migrate scenarios where a stale
    grc_pages.json may still be on disk. The shipped fixtures/grc_pages.json
    is empty ([]) which prevents the original Developer-Mode crash on a
    fresh install.
    """
    assert_module_ownership()
    retire_legacy_module_defs()
    neutralize_legacy_page_fixtures()


def neutralize_legacy_page_fixtures():
    """Empty out any stale grc_pages.json that still contains standard=Yes
    Page records. We rewrite the file to '[]' so the next sync_fixtures pass
    is a no-op instead of throwing 'Not in Developer Mode'.
    """
    import os
    import json

    base_dir = os.path.dirname(__file__)
    candidate_paths = [
        os.path.join(base_dir, "fixtures", "grc_pages.json"),
        os.path.join(base_dir, "alphax_grc", "fixtures", "grc_pages.json"),
    ]

    for path in candidate_paths:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            # Already empty array — nothing to do
            if content in ("[]", ""):
                continue
            try:
                docs = json.loads(content)
            except Exception:
                docs = []
            needs_rewrite = False
            for doc in docs if isinstance(docs, list) else []:
                if doc.get("doctype") == "Page" and doc.get("standard") == "Yes":
                    needs_rewrite = True
                    break
            if needs_rewrite:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("[]\n")
                try:
                    frappe.logger().info(
                        f"AlphaX GRC: Neutralized stale Page fixtures at {path}"
                    )
                except Exception:
                    pass
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"AlphaX GRC legacy page fixture neutralization failed: {path}")
            except Exception:
                pass


def after_install():
    bootstrap_grc()
    run_pathway_setup()


def before_migrate():
    assert_module_ownership()


def after_migrate():
    bootstrap_grc()
    # v1.9.7 — recreate any doctypes missing from the database (e.g. deleted
    # in earlier versions). Must run BEFORE the workspace repair because the
    # workspace contains Link references that need the doctypes to exist.
    try:
        v197_recreate_missing_doctypes()
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC v1.9.7: doctype recovery failed (non-fatal)")
        except Exception:
            pass
    # v1.9.6 — workspace + theme repair runs AFTER doctype migration completes.
    # Wrapped to NEVER raise — if repair fails we log and move on; we never
    # leave the user with a half-migrated site because a workspace touch-up
    # threw an exception.
    try:
        v194_run_repair_on_migrate()
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC v1.9.6: post-migrate repair failed (non-fatal)")
        except Exception:
            pass
    # v2.3.0 — GRC Evidence Automation module
    run_pathway_setup()


def run_pathway_setup():
    """Seed the GRC Evidence Automation module.

    Deliberately NOT a step inside bootstrap_grc(): that helper swallows any
    step that raises, which is how the NCA library seeding failures went
    unnoticed for so long. Failures here are logged with a title that says
    which seeder broke.
    """
    try:
        from alphax_grc.pathway.setup import seed_all
        seed_all()
    except Exception:
        try:
            frappe.log_error(
                title="AlphaX GRC v2.3.0: pathway setup failed",
                message=frappe.get_traceback(),
            )
        except Exception:
            pass


def bootstrap_grc():
    """Install bootstrap — resilient: a single seeder failing (e.g. stale pyc
    or data-shape drift) logs the error but does not abort the whole install."""
    import sys as _sys
    steps = [
        "create_roles", "create_default_frameworks", "create_framework_packs",
        "create_obligations", "create_privacy_activities",
        "create_assessment_templates", "create_sample_policies",
        "ensure_pages_exist", "ensure_workspace", "ensure_reports",
        "create_settings_if_missing", "install_workflows", "install_print_formats",
        "seed_theme_settings", "seed_sample_dr_plans", "seed_sample_problem_records",
        "seed_language_settings", "seed_nca_ecc_technology_controls",
        "seed_isms_document_register", "seed_sample_it_audit_program",
        "seed_itgc_audit_items", "seed_asset_inventory_v2",
        "seed_nca_ecc_controls_full_v2",
        # v1.3.0 — Multi-tenant + NCA ECC trackers + BIA + RCM
        "seed_default_client_profile",
        "seed_nca_ecc_documents",
        "seed_nca_ecc_tool_mappings",
        "seed_nca_ecc_review_calendar",
        "seed_sample_bia",
        "seed_sample_rcm",
        "backfill_client_on_existing_records",
        # v1.4.0 — Threats, Vulnerabilities, KPIs, NCA Library
        "seed_threat_catalogue",
        "seed_sample_vulnerabilities",
        "seed_sample_kpis",
        "seed_nca_policy_library",
        "seed_nca_standard_library",
        "seed_nca_procedure_library",
        "seed_nca_form_library",
        # v1.4.3 — Aramco CCC
        "seed_aramco_sacs002_controls",
        "seed_aramco_audit_firms",
        "seed_sample_aramco_certificate",
        "seed_sample_ccc_engagement",
        # v1.5.0 — ECC-2:2024 master catalog
        "seed_ecc2_2024_catalog",
        # v1.7.0 — ISO 42001 catalog + sample evidence rules
        "seed_iso42001_catalog",
        "seed_sample_evidence_rules",
        "seed_branded_print_formats",
        # v1.8.0 — Engagement phase templates
        "seed_engagement_phase_templates",
        # v1.9.0 — GDPR catalog
        "seed_gdpr_catalog",
        # v1.9.1 — apply Odoo Mauve theme as new default (idempotent)
        "seed_v191_apply_odoo_mauve",
        # v2.0.0 — Standard CISO KPI seed pack
        "seed_standard_ciso_kpis",
        # v2.1.0 — Framework expansion
        "seed_nist_csf_catalog",
        "seed_iso22301_catalog",
        # v2.2.0 — PDPL Privacy Pack
        "seed_pdpl_catalog",
        # v1.3.2 — pre-compute the dashboard snapshot for the demo client
        # (run last so all seed data is included in the first snapshot)
        "seed_initial_snapshots",
    ]
    mod = _sys.modules[__name__]
    for step_name in steps:
        fn = getattr(mod, step_name, None)
        if not callable(fn):
            try:
                frappe.logger().warning(
                    f"AlphaX GRC bootstrap: skipping unknown step '{step_name}' "
                    f"(likely stale bytecode cache — clear __pycache__)."
                )
            except Exception:
                pass
            continue
        try:
            fn()
        except Exception:
            try:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"AlphaX GRC bootstrap step failed: {step_name}",
                )
                frappe.logger().warning(
                    f"AlphaX GRC bootstrap: step '{step_name}' failed but "
                    f"install will continue; see Error Log."
                )
            except Exception:
                pass
    try:
        frappe.db.commit()
    except Exception:
        pass


def safe_insert(doc_dict, exists_filters=None):
    try:
        if exists_filters and frappe.db.exists(doc_dict["doctype"], exists_filters):
            return None
        doc = frappe.get_doc(doc_dict)
        doc.flags.ignore_permissions = True
        return doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
    except frappe.exceptions.DuplicateEntryError:
        return None  # already exists, ignore
    except frappe.exceptions.ValidationError as e:
        # Production mode restrictions (e.g. inserting system doctypes)
        # Log only if it's not a "Not in Developer Mode" type error
        err = str(e)
        if "Developer Mode" not in err and "duplicate" not in err.lower():
            frappe.log_error(str(e), f"AlphaX GRC seed validation: {doc_dict.get('doctype')}")
        return None
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"AlphaX GRC seed failed: {doc_dict.get('doctype')} / {doc_dict.get('name') or doc_dict.get('title') or doc_dict.get('policy_title') or doc_dict.get('framework_name')}")
        return None


def create_roles():
    for role_name in ROLES:
        if not frappe.db.exists("Role", role_name):
            safe_insert({"doctype": "Role", "role_name": role_name})


def create_default_frameworks():
    for framework_name, category, owner_type in FRAMEWORKS:
        if not frappe.db.exists("GRC Framework", {"framework_name": framework_name}):
            safe_insert({
                "doctype": "GRC Framework",
                "framework_name": framework_name,
                "category": category,
                "status": "Active",
                "owner_type": owner_type,
            }, {"framework_name": framework_name})


def _framework_name_to_docname(name):
    record = frappe.db.get_value("GRC Framework", {"framework_name": name}, "name")
    return record or name


def create_framework_packs():
    if not frappe.db.exists("DocType", "GRC Framework Pack"):
        return
    for item in PACKS:
        if frappe.db.exists("GRC Framework Pack", {"pack_code": item["pack_code"]}):
            continue
        try:
            doc = frappe.get_doc({"doctype": "GRC Framework Pack", **item, "status": "Active"})
            if item["pack_code"] == "NCA_ECC":
                doc.append("frameworks", {"framework": _framework_name_to_docname("NCA ECC")})
            elif item["pack_code"] == "SAMA_CSF":
                doc.append("frameworks", {"framework": _framework_name_to_docname("SAMA CSF")})
            elif item["pack_code"] == "PDPL":
                doc.append("frameworks", {"framework": _framework_name_to_docname("PDPL")})
            elif item["pack_code"] == "ARAMCO_TP":
                doc.append("frameworks", {"framework": _framework_name_to_docname("Aramco Third Party Standard")})
            doc.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"AlphaX GRC pack seed failed: {item['pack_code']}")


def create_obligations():
    if not frappe.db.exists("DocType", "GRC Regulatory Obligation"):
        return
    for item in OBLIGATIONS:
        safe_insert({
            "doctype": "GRC Regulatory Obligation",
            **item,
            "framework": _framework_name_to_docname(item["framework"]),
        }, {"obligation_title": item["obligation_title"]})


def create_privacy_activities():
    if not frappe.db.exists("DocType", "GRC Privacy Processing Activity"):
        return
    for item in PRIVACY_ACTIVITIES:
        safe_insert({"doctype": "GRC Privacy Processing Activity", **item}, {"activity_name": item["activity_name"]})





def create_assessment_templates():
    if not frappe.db.exists("DocType", "GRC Assessment Template"):
        return
    for item in ASSESSMENT_TEMPLATES:
        if frappe.db.exists("GRC Assessment Template", {"template_code": item["template_code"]}):
            continue
        try:
            payload = {k: v for k, v in item.items() if k != "questions"}
            doc = frappe.get_doc({"doctype": "GRC Assessment Template", **payload})
            framework_name = item.get("framework")
            if framework_name and frappe.db.exists("GRC Framework", {"framework_name": framework_name}):
                doc.framework = _framework_name_to_docname(framework_name)
            for q in item.get("questions", []):
                doc.append("questions", q)
            doc.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"AlphaX GRC assessment template seed failed: {item.get('template_code')}")
def create_sample_policies():
    if not frappe.db.exists("DocType", "GRC Policy"):
        return
    owner = frappe.session.user if frappe.session.user and frappe.session.user != "Guest" else "Administrator"
    for item in SAMPLE_POLICIES:
        if not frappe.db.exists("GRC Policy", {"policy_title": item["policy_title"]}):
            payload = {"doctype": "GRC Policy", **item, "policy_owner": owner}
            safe_insert(payload, {"policy_title": item["policy_title"]})


def ensure_pages_exist():
    """
    Pages are auto-loaded from the app's page/ folder by bench migrate.
    In production (Frappe Cloud) we cannot insert Page records directly.
    This function is intentionally a no-op — the page/ folder structure handles it.
    """
    return  # handled by Frappe's module sync from page/ folder


def create_settings_if_missing():
    if frappe.db.exists("AlphaX GRC Settings", "AlphaX GRC Settings"):
        return
    if not frappe.db.exists("DocType", "AlphaX GRC Settings"):
        return
    safe_insert({
        "doctype": "AlphaX GRC Settings",
        "default_risk_matrix": "5x5",
        "default_review_frequency": "Quarterly",
        "enable_incident_management": 1,
        "enable_control_library": 1,
        "enable_policy_management": 1,
        "enable_vendor_risk": 1,
        "enable_audit_management": 1,
        "saudi_focus_frameworks": "NCA ECC, SAMA CSF, PDPL, CST CRF, Aramco Third Party Standard, ISO 27001, ISO 31000",
    }, "AlphaX GRC Settings")


# ---------------------------------------------------------------------------
# Workflow installation
# ---------------------------------------------------------------------------

def install_workflows():
    """Seed Audit Finding and Exception workflows from JSON definitions."""
    import json, os
    workflow_dir = os.path.join(os.path.dirname(__file__), "alphax_grc", "workflow")
    if not os.path.isdir(workflow_dir):
        return
    for fname in os.listdir(workflow_dir):
        if not fname.endswith(".json"):
            continue
        try:
            fpath = os.path.join(workflow_dir, fname)
            with open(fpath) as f:
                wf_data = json.load(f)
            wf_name = wf_data.get("name")
            if not wf_name:
                continue
            if frappe.db.exists("Workflow", wf_name):
                continue
            doc = frappe.get_doc({"doctype": "Workflow", **wf_data})
            doc.flags.ignore_permissions = True
            doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
        except frappe.exceptions.ValidationError:
            pass  # silently skip if production restrictions apply
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"AlphaX GRC workflow install failed: {fname}")


# ---------------------------------------------------------------------------
# Print format installation
# ---------------------------------------------------------------------------

def install_print_formats():
    """
    Print Formats are auto-loaded from alphax_grc/print_format/ during bench migrate.
    In production (Frappe Cloud) direct insertion is not allowed.
    """
    return  # handled by Frappe module sync
def seed_theme_settings():
    """Create GRC Theme Settings singleton with defaults if not present.
    v1.9.1: New default is Odoo Mauve."""
    if not frappe.db.exists("DocType", "GRC Theme Settings"):
        return
    if frappe.db.exists("GRC Theme Settings", "GRC Theme Settings"):
        return
    try:
        doc = frappe.get_doc({
            "doctype": "GRC Theme Settings",
            "theme_preset": "Odoo Mauve",
        })
        doc.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "AlphaX GRC theme settings seed failed")


def seed_v191_apply_odoo_mauve():
    """v1.9.1 one-time migration: apply Odoo Mauve to existing installs.
    Runs once. Records its run via the Singles table so it's idempotent.
    Skips if the user has set theme_preset to 'Custom' (means they have
    deliberately customized colors)."""
    if not frappe.db.exists("DocType", "GRC Theme Settings"):
        return
    if not frappe.db.exists("GRC Theme Settings", "GRC Theme Settings"):
        return

    # Check if we've already run this migration (look for a flag)
    flag_name = "v1.9.1_odoo_mauve_applied"
    flag_val = frappe.db.get_default(flag_name)
    if flag_val:
        return

    try:
        doc = frappe.get_doc("GRC Theme Settings", "GRC Theme Settings")
        if doc.theme_preset == "Custom":
            # User deliberately customized — leave alone, just mark migration run
            frappe.db.set_default(flag_name, "skipped-custom")
            frappe.db.commit()
            return
        previous_preset = doc.theme_preset
        doc.theme_preset = "Odoo Mauve"
        doc.save(ignore_permissions=True)
        frappe.db.set_default(flag_name, "applied")
        frappe.db.commit()
        try:
            frappe.logger().info(
                f"AlphaX GRC v1.9.1: switched theme from {previous_preset} "
                f"to Odoo Mauve")
        except Exception:
            pass
    except Exception:
        frappe.log_error(frappe.get_traceback(),
                         "AlphaX GRC v1.9.1 Odoo Mauve migration failed")


def seed_sample_dr_plans():
    """Seed one sample DR Plan to demonstrate the structure."""
    if not frappe.db.exists("DocType", "GRC DR Plan"):
        return
    if frappe.db.exists("GRC DR Plan", {"plan_title": "IT Systems Disaster Recovery Plan"}):
        return
    safe_insert({
        "doctype": "GRC DR Plan",
        "plan_title": "IT Systems Disaster Recovery Plan",
        "version": "1.0",
        "status": "Draft",
        "rto_hours": 4.0,
        "rpo_hours": 1.0,
        "dr_scope": "This plan covers the recovery of all Tier-1 IT systems including ERP, email, file servers, and security platforms following a major disruption event.",
        "initiation_criteria": "Plan is initiated when: (1) a Tier-1 system is unavailable for more than 30 minutes, (2) a Severity-Critical incident is declared, or (3) the Crisis Management Team (CMT) formally invokes DR.",
        "dr_steps": "1. Declare DR event and notify CMT.\n2. Activate backup infrastructure.\n3. Restore from last clean backup per RPO.\n4. Validate system integrity.\n5. Notify stakeholders of recovery status.\n6. Resume normal operations.\n7. Initiate post-incident review.",
        "communications_plan": "Internal: CMT notified within 15 minutes via emergency contact list.\nExternal: Customers and regulators notified within RTO window as per SLA and NCA 72-hour requirement.",
        "lessons_learned": "Document lessons after each DR test or real activation. Update this plan within 30 days of any test.",
    }, {"plan_title": "IT Systems Disaster Recovery Plan"})


def seed_sample_problem_records():
    """Seed sample problem records."""
    if not frappe.db.exists("DocType", "GRC Problem Record"):
        return
    samples = [
        {"problem_title": "Recurring email system authentication failures", "priority": "High",
         "status": "In Investigation", "category": "Application",
         "symptoms": "Users report intermittent authentication failures when accessing email from external networks. Occurs 3-4 times per week during peak hours.",
         "known_error": 0, "root_cause_identified": 0},
        {"problem_title": "SIEM false positive alert rate exceeding 40%", "priority": "Medium",
         "status": "RCA Complete", "category": "Cybersecurity",
         "symptoms": "Security team is overwhelmed by false positive alerts from SIEM. Alert-to-incident ratio is 40:1, causing fatigue and missed real alerts.",
         "root_cause_identified": 1,
         "root_cause_analysis": "SIEM correlation rules were not tuned after network segment changes in Q3. Rules are triggering on legitimate traffic patterns from new cloud services.",
         "workaround": "Manually suppress known-good traffic sources in SIEM dashboard.",
         "permanent_fix": "Re-tune all SIEM correlation rules. Implement automated rule tuning process. Create dedicated suppression list for approved cloud services."},
    ]
    for s in samples:
        if not frappe.db.exists("GRC Problem Record", {"problem_title": s["problem_title"]}):
            safe_insert({"doctype": "GRC Problem Record", **s}, {"problem_title": s["problem_title"]})


# ---------------------------------------------------------------------------
# v1.0.0: New seeding — IT Audit Program, Technology Controls, ISMS Register, Language
# ---------------------------------------------------------------------------

def seed_language_settings():
    """Seed default language settings (bilingual EN+AR, LTR)."""
    if not frappe.db.exists("DocType", "GRC Language Settings"):
        return
    if frappe.db.exists("GRC Language Settings", "GRC Language Settings"):
        return
    try:
        doc = frappe.get_doc({
            "doctype": "GRC Language Settings",
            "primary_language": "English",
            "text_direction": "LTR (Left to Right)",
            "enable_bilingual_labels": 1,
            "date_format": "DD/MM/YYYY",
            "report_language": "Bilingual (EN + AR)",
            "dashboard_language": "Bilingual (EN + AR)",
            "currency_symbol": "SAR",
        })
        doc.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "AlphaX GRC language settings seed failed")


def seed_nca_ecc_technology_controls():
    """Seed NCA ECC-2:2024 technology control mappings."""
    if not frappe.db.exists("DocType", "GRC Technology Control"):
        return
    if frappe.db.count("GRC Technology Control") > 0:
        return
    nca_controls = [
        {"control_number": "1.3-1.5", "control_name": "Cybersecurity Policies & Risk", "main_domain": "Governance",
         "required_technology_type": "GRC Solutions", "technology_category": "GRC / Policy Management",
         "vendor_examples": "ServiceNow GRC, RSA Archer, CyberImtithal",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "1.10", "control_name": "Security Awareness & Training", "main_domain": "Governance",
         "required_technology_type": "Security Awareness Systems", "technology_category": "Security Awareness",
         "vendor_examples": "KnowBe4, Proofpoint, PhishRod",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.1", "control_name": "Asset Management", "main_domain": "Defense",
         "required_technology_type": "ITAM / CAASM", "technology_category": "Asset Management",
         "vendor_examples": "ServiceNow ITAM, Axonius, ManageEngine",
         "nca_pillar": "Zero Trust Architecture", "implementation_status": "Not Implemented"},
        {"control_number": "2.2", "control_name": "Identity & Access Management (IAM)", "main_domain": "Defense",
         "required_technology_type": "IAM / PAM / IGA", "technology_category": "Identity & Access Management",
         "vendor_examples": "CyberArk, SailPoint, Okta, BeyondTrust",
         "nca_pillar": "Zero Trust Architecture", "implementation_status": "Not Implemented"},
        {"control_number": "2.3", "control_name": "Systems Protection (EDR/XDR)", "main_domain": "Defense",
         "required_technology_type": "EDR / XDR", "technology_category": "Endpoint Detection & Response",
         "vendor_examples": "CrowdStrike, SentinelOne, Trend Micro",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.3", "control_name": "Data Protection (DLP/DSPM)", "main_domain": "Defense",
         "required_technology_type": "DLP / DSPM / Purview", "technology_category": "Data Protection / DLP",
         "vendor_examples": "Forcepoint, Varonis, Microsoft Purview",
         "nca_pillar": "Data Sovereignty & Privacy", "implementation_status": "Not Implemented"},
        {"control_number": "2.4", "control_name": "Email Security", "main_domain": "Defense",
         "required_technology_type": "Cloud Email Security (SEG)", "technology_category": "Email Security",
         "vendor_examples": "Proofpoint, Mimecast, Ironscales",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.5", "control_name": "Network Security (NGFW/NAC/ZTNA)", "main_domain": "Defense",
         "required_technology_type": "NGFW / NAC / ZTNA", "technology_category": "Network Security",
         "vendor_examples": "Palo Alto, Fortinet, Cisco, Illumio",
         "nca_pillar": "Zero Trust Architecture", "implementation_status": "Not Implemented"},
        {"control_number": "2.5", "control_name": "Web & Application Security (WAF/WAAP)", "main_domain": "Defense",
         "required_technology_type": "WAF / WAAP / API Security", "technology_category": "Web & App Security",
         "vendor_examples": "F5, Imperva, Akamai, Cloudflare",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.10", "control_name": "Vulnerability Management (RBVM)", "main_domain": "Defense",
         "required_technology_type": "RBVM / VM", "technology_category": "Vulnerability Management",
         "vendor_examples": "Tenable, Qualys, Rapid7",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.11", "control_name": "Penetration Testing (BAS)", "main_domain": "Defense",
         "required_technology_type": "BAS / Pentest Tools", "technology_category": "Penetration Testing",
         "vendor_examples": "XM Cyber, Pentera, Metasploit",
         "nca_pillar": "Automation & AI", "implementation_status": "Not Implemented"},
        {"control_number": "2.9", "control_name": "Backup & Recovery (DR)", "main_domain": "Resilience",
         "required_technology_type": "Immutable Backup / DR", "technology_category": "Backup & Recovery",
         "vendor_examples": "Veeam, Cohesity, Rubrik, Veritas",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "2.12", "control_name": "Security Monitoring (SIEM/SOAR)", "main_domain": "Resilience",
         "required_technology_type": "Next-Gen SIEM / SOAR", "technology_category": "Security Monitoring / SIEM",
         "vendor_examples": "Splunk, Microsoft Sentinel, IBM QRadar",
         "nca_pillar": "Automation & AI", "implementation_status": "Not Implemented"},
        {"control_number": "3.1", "control_name": "Supply Chain Security (TPRM/VRM)", "main_domain": "External Parties",
         "required_technology_type": "TPRM / VRM", "technology_category": "Third-Party Risk Management",
         "vendor_examples": "BitSight, SecurityScorecard",
         "nca_pillar": "Cyber Resilience", "implementation_status": "Not Implemented"},
        {"control_number": "4.2", "control_name": "Cloud Security (CSPM/CWPP/CNAPP)", "main_domain": "Technical Systems",
         "required_technology_type": "CSPM / CWPP / CNAPP", "technology_category": "Cloud Security",
         "vendor_examples": "Wiz, Prisma Cloud, Orca Security",
         "nca_pillar": "Data Sovereignty & Privacy", "implementation_status": "Not Implemented"},
    ]
    for ctrl in nca_controls:
        safe_insert({"doctype": "GRC Technology Control", **ctrl}, {"control_number": ctrl["control_number"], "control_name": ctrl["control_name"]})


def seed_isms_document_register():
    """Seed ISO 27001:2022 mandatory document register (all clauses 4-10 + Annex A)."""
    if not frappe.db.exists("DocType", "GRC ISMS Document Register"):
        return
    if frappe.db.count("GRC ISMS Document Register") > 0:
        return
    mandatory_docs = [
        # Clause 4-10 mandatory records
        ("4.1", "Context of the Organization", "Internal & External Issue Register", "Register / Log", "Clause 4 - Context"),
        ("4.2", "Needs & Expectations of Interested Parties", "Needs & Expectations Register", "Register / Log", "Clause 4 - Context"),
        ("4.3", "ISMS Scope", "ISMS Scope Document", "Manual", "Clause 4 - Context"),
        ("4.4", "ISMS Manual", "ISMS Manual", "Manual", "Clause 4 - Context"),
        ("5.2", "Information Security Policy", "Information Security Policy", "Policy", "Clause 5 - Leadership"),
        ("5.3", "Roles & Responsibilities", "Roles & Responsibilities Document", "Policy", "Clause 5 - Leadership"),
        ("6.1.1", "Risk Assessment Methodology", "Risk Assessment Methodology", "Procedure", "Clause 6 - Planning"),
        ("6.1.2/6.1.3", "Information Security Risk Register", "Risk Register", "Register / Log", "Clause 6 - Planning"),
        ("6.1.3(d)", "Statement of Applicability", "Statement of Applicability", "Report", "Clause 6 - Planning"),
        ("6.2", "ISMS Objectives Register", "Functional Level Objectives Register", "Register / Log", "Clause 6 - Planning"),
        ("7.2", "Competency Matrix", "Competency Matrix", "Register / Log", "Clause 7 - Support"),
        ("7.3", "Security Awareness Presentation", "InfoSec Awareness Presentation", "Presentation", "Clause 7 - Support"),
        ("7.4", "Communication Contact List", "Communication Contact List", "Register / Log", "Clause 7 - Support"),
        ("7.5", "ISMS Document Handling Policy", "ISMS Document Handling Policy", "Policy", "Clause 7 - Support"),
        ("9.1", "KPI Matrix", "KPI Matrix", "Register / Log", "Clause 9 - Performance"),
        ("9.2", "Internal Audit Procedure", "Internal Audit Procedure", "Procedure", "Clause 9 - Performance"),
        ("9.2.1", "Internal Audit Report", "Internal Audit Report", "Report", "Clause 9 - Performance"),
        ("9.2.2", "Internal Audit Schedule", "Internal Audit Schedule", "Plan", "Clause 9 - Performance"),
        ("9.3", "Management Review Presentation", "Management Review Presentation", "Presentation", "Clause 9 - Performance"),
        ("9.3.3", "Management Review Minutes", "Management Review Minutes", "Register / Log", "Clause 9 - Performance"),
        ("10.2", "CAPA Register", "Corrective Action Register", "Register / Log", "Clause 10 - Improvement"),
        # Key Annex A documents
        ("A.5.7", "Threat Intelligence Policy", "Threat Intelligence Policy & Procedure", "Policy", "A.5 Organizational Controls"),
        ("A.5.9", "Asset Register", "Asset Register", "Register / Log", "A.5 Organizational Controls"),
        ("A.5.15", "Access Control Policy", "Access Control Policy & Procedure", "Policy", "A.5 Organizational Controls"),
        ("A.5.19-5.22", "Supplier Relationship Policy", "Supplier Relationship Policy & Procedure", "Policy", "A.5 Organizational Controls"),
        ("A.5.23", "Cloud Security Policy", "Cloud Security Policy", "Policy", "A.5 Organizational Controls"),
        ("A.5.24-5.28", "Incident Management Policy", "Incident Response Plan & Playbooks", "Plan", "A.5 Organizational Controls"),
        ("A.5.29-5.30", "Business Continuity Plan", "Business Continuity Plan & BIA", "Plan", "A.5 Organizational Controls"),
        ("A.6.1", "HR Security Policy", "HR Security Policy", "Policy", "A.6 People Controls"),
        ("A.6.6", "NDA Template", "NDA / Employee Agreement Template", "Template", "A.6 People Controls"),
        ("A.6.7", "Teleworking Policy", "Teleworking / Remote Work Policy", "Policy", "A.6 People Controls"),
        ("A.7.1-7.13", "Physical Security Policy", "Physical & Environmental Security Policy", "Policy", "A.7 Physical Controls"),
        ("A.8.1", "Endpoint Security Policy", "Endpoint Security Policy & Procedure", "Policy", "A.8 Technological Controls"),
        ("A.8.8", "Vulnerability Management Policy", "Vulnerability & Patch Management Policy", "Policy", "A.8 Technological Controls"),
        ("A.8.9", "Configuration Management Policy", "Configuration Management Policy & Baseline", "Policy", "A.8 Technological Controls"),
        ("A.8.13", "Backup & Retention Policy", "Backup & Retention Policy & Procedure", "Policy", "A.8 Technological Controls"),
        ("A.8.15-8.16", "Logging & Monitoring Policy", "Logging & Monitoring Policy & Procedure", "Policy", "A.8 Technological Controls"),
        ("A.8.24", "Cryptographic Policy", "Cryptographic Policy & Key Management", "Policy", "A.8 Technological Controls"),
        ("A.8.25-8.29", "Secure Development Policy", "SDLC / Application Security Policy", "Policy", "A.8 Technological Controls"),
        ("A.8.32", "Change Management Policy", "Change Management Policy & Procedure", "Policy", "A.8 Technological Controls"),
    ]
    for clause, clause_name, title, doc_type, section in mandatory_docs:
        safe_insert({
            "doctype": "GRC ISMS Document Register",
            "clause_number": clause,
            "clause_name": clause_name,
            "document_title": title,
            "document_type": doc_type,
            "iso_section": section,
            "document_status": "Not Started",
            "mandatory": 1,
            "version": "1.0",
        }, {"clause_number": clause, "document_title": title})


def seed_sample_it_audit_program():
    """Seed one sample IT audit program with key controls."""
    if not frappe.db.exists("DocType", "GRC IT Audit Program"):
        return
    if frappe.db.exists("GRC IT Audit Program", {"program_title": "Annual IT General Controls Audit 2025"}):
        return
    safe_insert({
        "doctype": "GRC IT Audit Program",
        "program_title": "Annual IT General Controls Audit 2025",
        "audit_year": "2025",
        "status": "Planning",
        "in_scope_glba": 1, "in_scope_dlp": 1, "in_scope_patch": 1,
        "in_scope_vendor": 1, "in_scope_network": 1, "in_scope_isp": 1, "in_scope_ir": 1,
    }, {"program_title": "Annual IT General Controls Audit 2025"})


# ---------------------------------------------------------------------------
# v1.2.0: ITGC audit items seeding (146 controls from Shahidul Islam framework)
# ---------------------------------------------------------------------------

def seed_itgc_audit_items():
    """Seed all 146 IT General Controls Audit Program items from Shahidul Islam v1.0 (CISA, CISM, CISSP, CCSP)."""
    if not frappe.db.exists("DocType", "GRC ITGC Audit Item"):
        return
    if frappe.db.count("GRC ITGC Audit Item") >= 140:
        return  # Already seeded
    from datetime import date
    year = date.today().year
    items = [
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"02.a","item_number":1,"control_name":"Board and management oversight","requested_artifacts":"Provide copy  of BoD/SLT meeting minutes and packages the past 12 months describing the overall status and compliance of the Information Security Program (Appendix A, III.F.) for the past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":1,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"02.b","item_number":2,"control_name":"Board and management oversight","requested_artifacts":"Provide copy of Supervisory Committee meeting minutes/agendas past 12 months.","delivery_status":"Delivered","number_of_files":4,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"02.c","item_number":3,"control_name":"Board and management oversight","requested_artifacts":"Provide copy of reports and minutes from IT Steering Committee past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"02.d","item_number":4,"control_name":"Board and management oversight","requested_artifacts":"Q:  How have the organizational changes in past year impacted our Information Security Program and processes?","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"03.a","item_number":5,"control_name":"Employee education and security awareness/training","requested_artifacts":"Provide copy of phishing tests and results past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"03.b","item_number":6,"control_name":"Employee education and security awareness/training","requested_artifacts":"Provide copy of company Call Center procedures to authenticate members who call in.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"03.c","item_number":7,"control_name":"Employee education and security awareness/training","requested_artifacts":"Provide a list of company security awareness training and training records for past 12 months.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"05.a","item_number":8,"control_name":"Risk Management","requested_artifacts":"Provide copy of Risk Management (ERM) program documentation, policies and procedures.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":1,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"05.b","item_number":9,"control_name":"Risk Management","requested_artifacts":"Provide copy of any risk assessments conducted in the past year.","delivery_status":"Delivered","number_of_files":33,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"05.c","item_number":10,"control_name":"Risk Management","requested_artifacts":"Provide copy of risk register showing all IT related items or copies of any other risk tracking spreadsheets.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"05.d","item_number":11,"control_name":"Risk Management","requested_artifacts":"Provide a list of critical IT assets and their identified security risks in priority order.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"05.e","item_number":12,"control_name":"Risk Management","requested_artifacts":"Provide copy of ERM minutes/agendas and reports.","delivery_status":"Delivered","number_of_files":3,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"06.a","item_number":13,"control_name":"User Access Management","requested_artifacts":"Provide copy of financial core application user accounts and permissions, last logon.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"06.b","item_number":14,"control_name":"User Access Management","requested_artifacts":"Provide copy of financial core HOST computer user accounts, permissions, and last logon.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"06.c","item_number":15,"control_name":"User Access Management","requested_artifacts":"Provide copy of policies and procedures pertaining to authentication and authorization.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"06.d","item_number":16,"control_name":"User Access Management","requested_artifacts":"Provide copy of remote access policies and procedures and explanation of the use of Multi-Factor Authentication.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"09.a","item_number":17,"control_name":"Monitoring and Logging","requested_artifacts":"Provide copy of Vulnerability Management policies and procedures.","delivery_status":"Delivered","number_of_files":4,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":1,"time_preventative":0,"time_detective":1,"time_corrective":1,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"09.b","item_number":18,"control_name":"User Access Management","requested_artifacts":"Provide copy of Log Mgmt policies and procedures including roles and responsibilities.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"09.c","item_number":19,"control_name":"User Access Management","requested_artifacts":"Provide copy of vulnerability assessment report past 12 months.","delivery_status":"Delivered","number_of_files":144,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"09.d","item_number":20,"control_name":"User Access Management","requested_artifacts":"Provide copy of SIEM configuration - Log Sources and events.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"09.e","item_number":21,"control_name":"User Access Management","requested_artifacts":"Provide copy of SIEM configuration - Alerts/Notification rules.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"GLBA Compliance","section_code":"GLBA","section_id":"10","item_number":22,"control_name":"Annual compliance review","requested_artifacts":"Provide copy of annual compliance risk assessment.","delivery_status":"Not Applicable","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"01.a","item_number":23,"control_name":"Data Loss Prevention strategy","requested_artifacts":"Provide copy of policies and procedures for data loss prevention and data governance.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"01.b","item_number":24,"control_name":"Data Loss Prevention strategy","requested_artifacts":"Provide a copy of the DLP architecture and process/data flow.","delivery_status":"Delivered","number_of_files":4,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"01.c","item_number":25,"control_name":"Data Loss Prevention strategy","requested_artifacts":"Provide an explanation of the roles and responsibilities for DLP processing.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"01.d","item_number":26,"control_name":"Data Loss Prevention strategy","requested_artifacts":"Provide an explanation of cloud DLP controls and how DLP works in the cloud.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"01.e","item_number":27,"control_name":"Data Loss Prevention strategy","requested_artifacts":"Provide copy of report or dashboard showing KPI's for DLP solution.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"02.a","item_number":28,"control_name":"Processes for locating and classifying sensitive data (Restricted)","requested_artifacts":"Provide procedures and process diagrams for locating, identifying, classifying and tracking restricted member data.","delivery_status":"Delivered","number_of_files":3,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"02.b","item_number":29,"control_name":"Processes for locating and classifying sensitive data (Restricted)","requested_artifacts":"Provide an explanation on the timing of DLP scans and remediation efforts.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"02.c","item_number":30,"control_name":"Processes for locating and classifying sensitive data (Restricted)","requested_artifacts":"Provide list of any information system components we are exempting from DLP scans, their risk impact and how this is being tracked/reviewed (e.g. SQL DB's, Miser Unisys Host, linux appliances,..).","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"02.d","item_number":31,"control_name":"Processes for locating and classifying sensitive data (Restricted)","requested_artifacts":"Provide an explanation of any encrypted data the DLP system is unable to scan.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"03.a","item_number":32,"control_name":"Firewall and Proxy controls to block uploads, filesharing, email sites","requested_artifacts":"Provide a copy of firewall policy and procedures.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"03.b","item_number":33,"control_name":"Firewall and Proxy controls to block uploads, filesharing, email sites","requested_artifacts":"Provide a copy of the Firewall Ruleset (.xlsx).","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"03.c","item_number":34,"control_name":"Firewall and Proxy controls to block uploads, filesharing, email sites","requested_artifacts":"Provide a report or screen clips of the outbound web proxy configuration.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"03.d","item_number":35,"control_name":"Firewall and Proxy controls to block uploads, filesharing, email sites","requested_artifacts":"Provide a report or screen clips of the Proofpoint configuration that controls outgoing email w/ attachments.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"03.e","item_number":36,"control_name":"Firewall and Proxy controls to block uploads, filesharing, email sites","requested_artifacts":"Provide explanation of the PCI DSS controls implemented in our DLP solution as it relates to cardholder data.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"04.a","item_number":37,"control_name":"Mgmt of removable media - USB/CD/DVD  and access restrictions","requested_artifacts":"Provide policy and procedures on endpoint security controls and restrictions place of removable media.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"04.b","item_number":38,"control_name":"Mgmt of removable media - USB/CD/DVD  and access restrictions","requested_artifacts":"Provide screen clip of the end-point security app configurations that restricts removable media.  Explain if there are any exemptions or deviations in place.","delivery_status":"Delivered","number_of_files":5,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"05.a","item_number":39,"control_name":"Outbound email exfiltration (e.g. Proofpoint, ForcePoint)","requested_artifacts":"Provide copy of policies and procedures for data governance.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"05.b","item_number":40,"control_name":"Outbound email exfiltration (e.g. Proofpoint, ForcePoint)","requested_artifacts":"Provide report or screen snapshots of DLP application configuration restricting outbound email.","delivery_status":"Delivered","number_of_files":7,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"06.a","item_number":41,"control_name":"Disposal of Media","requested_artifacts":"Provide copy of media sanitation and disposal policies and procedures.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"06.b","item_number":42,"control_name":"Disposal of Media","requested_artifacts":"Provide a report or log showing all disposal / sanitation actions the past 12 months.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"07.a","item_number":43,"control_name":"Securing facilities and areas where sensitive information resides","requested_artifacts":"Provide copy of Physical Security Standards Manual.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":1,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"07.b","item_number":44,"control_name":"Securing facilities and areas where sensitive information resides","requested_artifacts":"Provide copy of procedure for management of video camera and recordings in sensitive data areas.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Data Loss Prevention","section_code":"DLP","section_id":"07.c","item_number":45,"control_name":"Securing facilities and areas where sensitive information resides","requested_artifacts":"Provide configuration screenshot showing network jack access restrictions for non-company computer devices.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"01","item_number":46,"control_name":"Patch Management Policy","requested_artifacts":"Provide a copy of the patch management policy","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"02.a","item_number":47,"control_name":"Patch Management Process","requested_artifacts":"Provide copy of patch management procedures and process flow diagrams.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"02.b","item_number":48,"control_name":"Patch Management Process","requested_artifacts":"Provide patch management test procedures and test results.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"02.c","item_number":49,"control_name":"Patch Management Process","requested_artifacts":"Provide a report or evidence patches are successfully applied.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"02.d","item_number":50,"control_name":"Patch Management Process","requested_artifacts":"Provide explanation how the patching process is aligned with the vulnerability management scanning that regularly takes place.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"03","item_number":51,"control_name":"Uninstalled Patches","requested_artifacts":"Provide of listing of uninstalled patches and a explanation what the plan is to remediate the risk.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":1,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"04","item_number":52,"control_name":"Inventory of assets patched","requested_artifacts":"Provide explanation how patching process handles non-windows machines such as  Linux servers/appliances, printers, VoIP phones, network switches/routers.  Are there different procedures followed?  If so, please provide a copy of them.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":1,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"05","item_number":53,"control_name":"3rd Party Service providers","requested_artifacts":"Provide explanation as to how we ensure 3rd party providers are reviewing, understanding, testing and deploying patches to their products.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"06.a","item_number":54,"control_name":"Patch Mgmt metrics","requested_artifacts":"Provide a sample copy of any metrics used to manage our patch management process.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Patch Management","section_code":"PM","section_id":"06.b","item_number":55,"control_name":"Patch Mgmt metrics","requested_artifacts":"Provide a sample report to management showing patch management effectivness","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"01","item_number":56,"control_name":"Vendor Listing","requested_artifacts":"Provide a vendor listing.  Include the vendor's initial contract date (to identify new vendors); description of the services they provide; Risk rating; and vendor owner.  Categorize by criticality.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"02","item_number":57,"control_name":"Vendor Management Program","requested_artifacts":"Provide copy of vendor management program and policies","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"03.a","item_number":58,"control_name":"Vendor Risk Assessments","requested_artifacts":"Provide copy of procedure(s) or explanation of vendor due diligence process.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"03.b","item_number":59,"control_name":"Vendor Risk Assessments","requested_artifacts":"Provide support for the due diligence (including contract review) conducted on the two most recently added critical vendors.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"03.c","item_number":60,"control_name":"Vendor Risk Assessments","requested_artifacts":"Provide support for the three (3) most recently conducted or updated vendor risk assessments","delivery_status":"Delivered","number_of_files":3,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"04","item_number":61,"control_name":"Vendor Exception Report","requested_artifacts":"Provide copy of any management reports indicating vendor exceptions/concerns.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":1,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"05","item_number":62,"control_name":"Vendor Survey and Review","requested_artifacts":"Provide listing of vendors of all IT products and services and version/release information.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"06","item_number":63,"control_name":"Vendor Contracts","requested_artifacts":"Provide copies of contracts for IT vendors with risk ratings of medium or above acquired the past 12 months.","delivery_status":"Delivered","number_of_files":5,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"07","item_number":64,"control_name":"Vendor Reviews","requested_artifacts":"Provide copy of procedure(s) for ensuring vendors comply with Service Level Agreements (SLA's) - critical or high risk vendors only.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":1,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"08.a","item_number":65,"control_name":"Cloud Vendors","requested_artifacts":"Provide listing of cloud vendors or vendors using cloud computing services.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":1,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Vendor Management","section_code":"VM","section_id":"08.b","item_number":66,"control_name":"Cloud Vendors","requested_artifacts":"Provide risk assessments for last 3 cloud vendors added the past 12 months.","delivery_status":"Delivered","number_of_files":3,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.a","item_number":67,"control_name":"Network Security Management","requested_artifacts":"Provide copy of Information Security Policy and Standards.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":1,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.b","item_number":68,"control_name":"Network Security Management","requested_artifacts":"Provide copy  of 2019 and 2020 IT Strategic Plans (MS project or Excel).","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.c","item_number":69,"control_name":"Network Security Management","requested_artifacts":"Provide copy  of 2019 and 2020 IT Project Plans (MS project or Excel).","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.d","item_number":70,"control_name":"Network Security Management","requested_artifacts":"Provide copy of LAN/WAN diagrams showing Firewalls, Routers or L3 switches, gateways, proxies, load balancers, DMZ's, IDS system, connections to 3rd party provider and cloud providers (e.g. Azure, AWS, Salesforce, ...), Internet connections and any security-minded network segments - Please provide V","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.e","item_number":71,"control_name":"Network Security Management","requested_artifacts":"Provide a list of new 3rd party application services and cloud providers within the past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"01.f","item_number":72,"control_name":"Network Security Management","requested_artifacts":"Provide a list of network related IT projects initiated the past 12 months including: business objectives, project requirements, any 3rd party agreements, SOW's and project deliverables, explain how security controls were impacted by the project and status.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"02","item_number":73,"control_name":"Network Internet Protocol addressing","requested_artifacts":"Provide a list of all internal and external IP addresses assigned and/or used at the credit union (all subnets and network segments).","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":0,"time_detective":1,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"03.a","item_number":74,"control_name":"Managed Firewall","requested_artifacts":"Provide a copy of policies and/or procedures for firewall mgmt.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":1,"time_preventative":1,"time_detective":1,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"03.b","item_number":75,"control_name":"Managed Firewall","requested_artifacts":"Provide evidence of last review of firewall rules.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"04.a","item_number":76,"control_name":"Change vendor-supplied defaults for system passwords and parms","requested_artifacts":"Provide a copy of policies and procedures for changing default passwords.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"04.b","item_number":77,"control_name":"Change vendor-supplied defaults for system passwords and parms","requested_artifacts":"Provide evidence we are tracking and reviewing this activity.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"05","item_number":78,"control_name":"Anti-Virus Management","requested_artifacts":"Provide AV policies and procedures, including screen shots of the AV product dashboard and server/workstation scanning and update schedules.","delivery_status":"Delivered","number_of_files":3,"ctrl_administrative":0,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":1,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"06.a","item_number":79,"control_name":"Cryptography","requested_artifacts":"Provide copy of policy and procedures on use of cryptographic controls.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"06.b","item_number":80,"control_name":"Cryptography","requested_artifacts":"Provide copy of or describe the Cryptographic architecture including:  Algorithm, protocols, key strength, expiration date and keys used to protect member information.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"06.c","item_number":81,"control_name":"Cryptography","requested_artifacts":"Provide list of devices or systems using cryptography.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"06.d","item_number":82,"control_name":"Cryptography","requested_artifacts":"Provide copy of policy and procedures for managing cryptographic keys.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"07.a","item_number":83,"control_name":"IDS/IPS","requested_artifacts":"Provide a description of the IDS/IPS system in place along with evidence of regular review of IDS/IPS Reporting.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":1,"time_preventative":0,"time_detective":1,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"07.b","item_number":84,"control_name":"IDS/IPS","requested_artifacts":"Provide a description of the alerting system of the DS/IPS system.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"07.c","item_number":85,"control_name":"IDS/IPS","requested_artifacts":"Provide sample IDS/IPS output from last Friday of each month in Q3 of last year.","delivery_status":"Delivered","number_of_files":9,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"08.a","item_number":86,"control_name":"Restrict physical access to network and sensitive areas","requested_artifacts":"Provide a copy of policies and procedures regarding physical access controls to data centers, data closets and other areas where sensitive information is located.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":1,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"08.b","item_number":87,"control_name":"Restrict physical access to network and sensitive areas","requested_artifacts":"Provide a copy of badge access and physical key procedures and video recording controls within the company Data Centers.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"08.c","item_number":88,"control_name":"Restrict physical access to network and sensitive areas","requested_artifacts":"Question:   Are network access controls (NAC) in place to prevent unrecognized/unauthorized devices from connecting to the network?  If so, explain the NAC solution in place and provide screen shots of its configuration.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"09.a","item_number":89,"control_name":"Remote Access","requested_artifacts":"Provide a copy of policies and procedures regarding remote access.","delivery_status":"Delivered","number_of_files":7,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"09.b","item_number":90,"control_name":"Remote Access","requested_artifacts":"Provide a list of users with remote access (VPN) privileges.  Include a description of remote access methods, including authentication methods for each access method.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"10.a","item_number":91,"control_name":"Wireless Access","requested_artifacts":"Provide an inventory of the wireless network assets.  Include vendor, model#, software/firmware versions.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"10.b","item_number":92,"control_name":"Wireless Access","requested_artifacts":"Provide a copy of wireless network diagram showing access points wireless access controllers.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"10.c","item_number":93,"control_name":"Wireless Access","requested_artifacts":"Provide a coverage map of main SJ corporate office location and one retail branch as evidence wireless radio wave signals are limited to company building only.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"11.a","item_number":94,"control_name":"Admin Privileges","requested_artifacts":"Provide policy and procedures for restricting and monitoring use of administrative privileges on the network.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"11.b","item_number":95,"control_name":"Admin Privileges","requested_artifacts":"Provide evidence this is being reviewed on a regular basis.","delivery_status":"Delivered","number_of_files":17,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"12.a","item_number":96,"control_name":"Active Directory settings","requested_artifacts":"Provide screenshots of all AD settings including, but not limited to: Any trust relationships Organizational Units Default Domain Policy Default Domain Controller(s) policy Screen Saver policy (or other method to lockout idle sessions) Group Policy Objects Built-in Administrator group members Two ke","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"13.a","item_number":97,"control_name":"Authorized Software","requested_artifacts":"Provide procedure for monitoring the network environment to validate that only authorized software is installed on the network and at workstations.  Include evidence this procedure is being followed.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"13.b","item_number":98,"control_name":"Authorized Software","requested_artifacts":"Provide evidence we are monitoring the network to validate only authorized software is installed.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"14","item_number":99,"control_name":"End-of-Life operating systems","requested_artifacts":"Provide a list of all \"end-of-life\" operating systems and their replacement schedule.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"15","item_number":100,"control_name":"DDoS","requested_artifacts":"Provide written strategy or explanation how the credit union is protected from a DDoS attack and sample report showing how this is monitored.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"16.a","item_number":101,"control_name":"SIEM and Log Management","requested_artifacts":"Provide policy and procedures governing log management.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":0,"time_detective":1,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"16.b","item_number":102,"control_name":"SIEM and Log Management","requested_artifacts":"Provide list of logging data sources to the SIEM (include for each the hostname, IP address, App/software, and events being logged).","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"16.c","item_number":103,"control_name":"SIEM and Log Management","requested_artifacts":"Provide a list of alerts configured on the SIEM and include who receives them.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"17","item_number":104,"control_name":"Password Management","requested_artifacts":"Provide the password parameters for core financial system, e-banking and wire transfer applications.  Include: length, complexity, expiration, session timeout (screensaver timeout), account lockout, password history, and security and event logging directly from the system (e.g. screen prints or repo","delivery_status":"Pending","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Network Security","section_code":"NS","section_id":"18","item_number":105,"control_name":"Configuration Standards","requested_artifacts":"Provide a copy of the server, network device, workstation and laptop configuration standards (including procedures and checklists).","delivery_status":"Delivered","number_of_files":13,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"01.a","item_number":106,"control_name":"Information Security Governance","requested_artifacts":"Provide copy of information security policy and standards.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"01.b","item_number":107,"control_name":"Information Security Governance","requested_artifacts":"Provide copy  of 2019 and 2020 IT Strategic Plans. (MS project or Excel)","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"01.c","item_number":108,"control_name":"Information Security Governance","requested_artifacts":"Provide copy  of 2019 and 2020 IT Project Plans. (MS project or Excel)","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"01.d","item_number":109,"control_name":"Information Security Governance","requested_artifacts":"Provide evidence of Information Security compliance with FFIEC, GLBA, PCI DSS, and GDPR or explain compliance progress/status.  If not planning to become compliant, provide a written statement explaining why?","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"01.e","item_number":110,"control_name":"Information Security Governance","requested_artifacts":"Provide copy of response program for unauthorized access to member information (Appendix A to Part 748).","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"02","item_number":111,"control_name":"BoD Reporting","requested_artifacts":"Provide reports and meeting minutes to the BoD (or Supervisory Committee) describing the overall status and compliance of the Information Security Program (Appendix A, III.F.) for the past 12 months.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"03","item_number":112,"control_name":"Security Awareness and Training (including Phishing)","requested_artifacts":"Provide copy of KnowBe4 Phishing testing activity and results.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":1,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"04.a","item_number":113,"control_name":"Asset Management","requested_artifacts":"Provide copy of policies and procedures for inventory and management of all Information System components (assets: data, software, systems, computers, network, devices,..).","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"04.b","item_number":114,"control_name":"Asset Management","requested_artifacts":"Provide copy of (or access to) the complete Information Systems component inventory including asset ownership.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"04.c","item_number":115,"control_name":"Asset Management","requested_artifacts":"Provide copy of procedure for identifying and classifying all inventory components by sensitivity and criticality.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"04.d","item_number":116,"control_name":"Asset Management","requested_artifacts":"Provide evidence inventory is maintained and up-to-date.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.a","item_number":117,"control_name":"Access Control","requested_artifacts":"Provide copy of access control policies and procedures.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.b","item_number":118,"control_name":"Access Control","requested_artifacts":"Provide user account management policy and procedures for employee on-boarding and terminations.","delivery_status":"Delivered","number_of_files":2,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.c","item_number":119,"control_name":"Access Control","requested_artifacts":"Provide list of all network user (e.g. Active Directory) accounts including service accounts.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.d","item_number":120,"control_name":"Access Control","requested_artifacts":"Provide list of all core financial system user accounts and permissions.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.e","item_number":121,"control_name":"Access Control","requested_artifacts":"Provide list of all accounts on all servers/workstations with local admin access (e.g. member of administrators group).  Identify by machine by account.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"05.f","item_number":122,"control_name":"Access Control","requested_artifacts":"Provide evidence that privileged accounts are reviewed regularly.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"06.a","item_number":123,"control_name":"Cryptography","requested_artifacts":"Provide a copy of policy and procedures on use of cryptographic controls.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"06.b","item_number":124,"control_name":"Cryptography","requested_artifacts":"Provide copy of or describe the Cryptographic architecture including:  Algorithm, protocols, key strength, expiration date and keys used to protect member information.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"06.c","item_number":125,"control_name":"Cryptography","requested_artifacts":"Provide list of devices or systems using cryptography.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"06.d","item_number":126,"control_name":"Cryptography","requested_artifacts":"Provide copy of policy and procedures for managing cryptographic keys.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"07","item_number":127,"control_name":"Cybersecurity","requested_artifacts":"Provide a copy of the FFIEC ACAT cybersecurity controls matrix and maturity details.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"08.a","item_number":128,"control_name":"Third Party interconnectivity","requested_artifacts":"Provide a copy of policies and procedures for management of 3rd party interfaces.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"08.b","item_number":129,"control_name":"Third Party interconnectivity","requested_artifacts":"Provide copy of network diagrams (LAN, WAN and DMZ) showing 3rd party interface details and related data flow diagrams.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"08.c","item_number":130,"control_name":"Third Party interconnectivity","requested_artifacts":"Provide copy of procedure for authorization and tracking of data exchanged with 3rd parties and evidence this is reviewed periodically.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"09","item_number":131,"control_name":"Physical and Environmental Security","requested_artifacts":"Provide copy of Physical Security policies and procedures. Provide copy of any physical security audits/reviews conducted the past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":1,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"10.a","item_number":132,"control_name":"Authentication","requested_artifacts":"Provide copy of remote access standards and procedures, including use of Multi-Factor Authentication.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"10.b","item_number":133,"control_name":"Authentication","requested_artifacts":"Provide copy of MFA configuration settings.","delivery_status":"Delivered","number_of_files":7,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"10.c","item_number":134,"control_name":"Authentication","requested_artifacts":"Provide the password parameters for core financial system, e-banking and wire transfer applications.  Include: length, complexity, expiration, session timeout (screensaver timeout), account lockout, password history, and security and event logging directly from the system (e.g. screen prints or repo","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"11.a","item_number":135,"control_name":"Information Security Resources","requested_artifacts":"Provide copy of IT org chart.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"11.b","item_number":136,"control_name":"Information Security Resources","requested_artifacts":"Provide copy of InfoSec team training/certification skills past 12 months.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"11.c","item_number":137,"control_name":"Information Security Resources","requested_artifacts":"Provide copy of IT budget 2019 and 2020 including staffing or 3rd party support plans.","delivery_status":"Pending","number_of_files":0,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Information Security Program","section_code":"ISP","section_id":"11.d","item_number":138,"control_name":"Information Security Resources","requested_artifacts":"Provide copy of IT project plans 2019 and 2020.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"01","item_number":139,"control_name":"Incident Response Plan","requested_artifacts":"Provide copy of the incident response plan and policy explaining purpose, scope, roles, responsibilities, mgmt. commitment, organizational coordination and compliance.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"02","item_number":140,"control_name":"Incident Response Training","requested_artifacts":"Provide a list of training activities or vendor engagements in past 12 months to prepare the IR team.  Include agenda's, deliverables and training materials.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"03","item_number":141,"control_name":"Incident Response Testing","requested_artifacts":"Provide copy of the results of IR testing in the past 12 months.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":1,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"04.a","item_number":142,"control_name":"Incident Response Handling","requested_artifacts":"Provide copy of IR procedures for handling a security incident and flow diagram of the process.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":1,"ctrl_physical":0,"time_preventative":0,"time_detective":1,"time_corrective":1,"area_people":0,"area_process":1,"area_technology":1,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"04.b","item_number":143,"control_name":"Incident Response Handling","requested_artifacts":"Provide configuration screen shots of any mechanisms to automate recovery actions to ensure business continuity.","delivery_status":"Pending","number_of_files":1,"ctrl_administrative":0,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":0,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":0,"area_technology":0,"map_ncua":0,"map_glba":0,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"05","item_number":144,"control_name":"Incident Response Monitoring","requested_artifacts":"Provide a list of all IT incidents, intrusions, or attacks (breach, ransomware, DDoS, lost data files, etc…) in the past 12 months.  Include post-incident reports and any risk assessments for incidents that occurred but did not require regulatory or member notification.","delivery_status":"Delivered","number_of_files":1,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
        {"doctype":"GRC ITGC Audit Item","control_domain":"Incident Response","section_code":"IR","section_id":"06.a","item_number":145,"control_name":"Incident Response Reporting","requested_artifacts":"Provide copy of IR policy and procedures related to personnel reporting of security incidents.","delivery_status":"Delivered","number_of_files":0,"ctrl_administrative":1,"ctrl_technical":0,"ctrl_physical":0,"time_preventative":1,"time_detective":0,"time_corrective":0,"area_people":0,"area_process":1,"area_technology":0,"map_ncua":0,"map_glba":1,"map_ffiec":0,"map_nist":0,"map_pci_dss":0,"map_iso":0,"map_cobit":0,"map_cis":0,"review_status":"Not Started","audit_year":year},
    ]
    for item in items:
        safe_insert(item, {"item_number": item["item_number"], "control_domain": item["control_domain"]})
    frappe.logger().info(f"AlphaX GRC: Seeded {len(items)} ITGC audit items")


# ===========================================================================
# v1.2.2 — Asset Inventory & NCA ECC rebuild from source XLS/PDF
# ===========================================================================

def seed_asset_inventory_v2():
    """
    Seed ISO 27001 Asset Register with real data from all 6 sheet types:
    Software, Network Devices, Servers, Laptops, Media, Desktops.
    Extracted from Asset_Inventory.xls by Tawhid / ISO27k Forum (CC licence).
    Each record has full CIA classification, NCA ECC-2:2024 linkage, PDPL flag.
    """
    if not frappe.db.exists("DocType", "GRC Asset Inventory"):
        return
    if frappe.db.count("GRC Asset Inventory") >= 15:
        return  # already seeded

    from frappe.utils import add_months, getdate
    today_date = frappe.utils.today()

    def d(asset):
        asset["doctype"] = "GRC Asset Inventory"
        return asset

    assets = [
        # ── SOFTWARE (List of Software sheet) ──────────────────────────
        d({"asset_name": "G Banker Core Banking System",
           "asset_type": "Software", "asset_id": "SW-001",
           "software_type": "Application",
           "version": "X.x.x", "sla": "Yes",
           "asset_location": "Head Office",
           "owner": "Administrator", "user_role": "GC User 1",
           "purpose_service_role": "Core banking and financial operations platform",
           "stored_information_assets": "Customer financial records, transaction data, accounts",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "data_classification": "Restricted",
           "contains_personal_data": 1,
           "backup_schedule": "Daily", "backup_location": "DR Site",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "Antivirus / EDR Endpoint Protection",
           "asset_type": "Software", "asset_id": "SW-002",
           "software_type": "Security Tool",
           "version": "Latest", "sla": "Yes",
           "asset_location": "Head Office",
           "purpose_service_role": "Endpoint detection, antivirus, malware protection across all workstations",
           "maintenance_status": "Active",
           "confidentiality": "Medium (M)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "High",
           "data_classification": "Confidential",
           "anti_virus_updated": "Yes",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "SIEM Platform — Security Monitoring",
           "asset_type": "Software", "asset_id": "SW-003",
           "software_type": "Security Tool",
           "sla": "Yes",
           "asset_location": "Data Centre",
           "purpose_service_role": "Real-time security event monitoring, threat detection, SOAR integration",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "data_classification": "Restricted",
           "nca_ecc_domain": "Resilience", "nca_control_number": "2.12",
           "pillar_ai_automation": 1, "pillar_cyber_resilience": 1,
           "last_reviewed": today_date}),

        # ── NETWORK DEVICES (List of Network Devices sheet) ─────────────
        d({"asset_name": "Core Network Switch — Head Office",
           "asset_type": "Network Device", "asset_id": "ND-001",
           "serial_number": "CISCO-SW-XYZ-001",
           "make_model": "Cisco Catalyst 9300",
           "vendor_name_text": "Cisco",
           "os_version": "IOS XE 17.x",
           "ip_address": "10.0.0.1",
           "hostname": "SWITCH-HO-01",
           "asset_location": "Head Office",
           "features": "Device Built-in Firewall, VLAN segmentation, QoS",
           "purpose_service_role": "Core LAN switching — G Banker application network backbone",
           "maintenance_status": "Active",
           "confidentiality": "Medium (M)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "High",
           "redundancy_required": "Yes",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.5",
           "last_reviewed": today_date}),

        d({"asset_name": "Next-Generation Firewall (NGFW) — Perimeter",
           "asset_type": "Network Device", "asset_id": "ND-002",
           "make_model": "Palo Alto PA-3440",
           "vendor_name_text": "Palo Alto Networks",
           "ip_address": "10.0.0.254",
           "hostname": "NGFW-PERIMETER-01",
           "asset_location": "Data Centre",
           "features": "Zero Trust Network Access, IPS, URL Filtering, SSL Inspection",
           "purpose_service_role": "Perimeter firewall, ZTNA enforcement, network segmentation, DDoS mitigation",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "redundancy_required": "Yes",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.5",
           "last_reviewed": today_date}),

        # ── SERVERS (List of Servers sheet) ─────────────────────────────
        d({"asset_name": "Application Server — GC_APP_01",
           "asset_type": "Server", "asset_id": "SRV-001",
           "serial_number": "GC_X_X",
           "os_version": "Windows Server 2019",
           "rack_number": "Rack-01",
           "ip_address": "192.168.1.10",
           "cpu": "Intel Xeon E5-2680 (Core i15)",
           "ram": "8 GB ECC",
           "storage": "1 TB SSD RAID-1",
           "vendor_name_text": "Dell",
           "asset_location": "Data Centre",
           "purpose_service_role": "Hosts G Banker application tier — primary production workload",
           "stored_information_assets": "Application binaries, runtime data, session state",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "backup_schedule": "Daily", "backup_location": "DR Site",
           "configuration_backup": "Yes", "redundancy_required": "Yes",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "Database Server — GC_DB_01",
           "asset_type": "Server", "asset_id": "SRV-002",
           "os_version": "Windows Server 2019",
           "rack_number": "Rack-02",
           "ip_address": "192.168.1.11",
           "cpu": "Intel Xeon Gold", "ram": "32 GB", "storage": "4 TB NVMe RAID-10",
           "vendor_name_text": "Dell",
           "asset_location": "Data Centre",
           "purpose_service_role": "Primary database server — G Banker MSSQL production database",
           "stored_information_assets": "Customer accounts, transactions, KYC data, financial history",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "contains_personal_data": 1,
           "backup_schedule": "Daily", "backup_location": "DR Site",
           "configuration_backup": "Yes", "redundancy_required": "Yes",
           "data_classification": "Restricted",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "Backup / DR Server — Off-Site",
           "asset_type": "Server", "asset_id": "SRV-003",
           "os_version": "Linux (RHEL 8)",
           "rack_number": "DR-Rack-01",
           "cpu": "Intel Xeon", "ram": "16 GB", "storage": "10 TB NAS",
           "vendor_name_text": "HPE",
           "asset_location": "Off-Site Storage",
           "purpose_service_role": "Immutable backup target and disaster recovery replica for G Banker",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "Medium (M)",
           "asset_criticality": "High",
           "backup_schedule": "Real-time", "configuration_backup": "Yes",
           "nca_ecc_domain": "Resilience", "nca_control_number": "2.9",
           "last_reviewed": today_date}),

        # ── LAPTOPS (List of Laptops sheet) ─────────────────────────────
        d({"asset_name": "Executive Laptop — Head of IT",
           "asset_type": "Laptop", "asset_id": "LPT-001",
           "serial_number": "DELL-LPT-001",
           "make_model": "Dell Latitude 7490",
           "vendor_name_text": "Dell",
           "ip_address": "DHCP",
           "cpu": "Intel Core i5", "ram": "8 GB", "storage": "1 TB SSD",
           "os_version": "Windows 11 Pro",
           "asset_location": "Head Office",
           "user_role": "Head of IT — Administrative & privileged access",
           "anti_virus_updated": "Yes",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "Medium (M)", "availability": "Medium (M)",
           "asset_criticality": "High",
           "data_classification": "Confidential",
           "contains_personal_data": 1,
           "backup_schedule": "Weekly",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "Staff Laptop — Finance Department",
           "asset_type": "Laptop", "asset_id": "LPT-002",
           "make_model": "Lenovo ThinkPad E14",
           "vendor_name_text": "Lenovo",
           "cpu": "Intel Core i5", "ram": "8 GB", "storage": "512 GB SSD",
           "os_version": "Windows 11 Pro",
           "asset_location": "Head Office",
           "user_role": "Finance user — read/write G Banker",
           "anti_virus_updated": "Yes",
           "maintenance_status": "Active",
           "confidentiality": "Medium (M)", "integrity": "Medium (M)", "availability": "Low (L)",
           "asset_criticality": "Medium",
           "data_classification": "Confidential",
           "backup_schedule": "Weekly",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        # ── MEDIA / PORTABLE DEVICES (List of Media sheet) ──────────────
        d({"asset_name": "External Backup Drive — Server Room",
           "asset_type": "Media / Portable Device", "asset_id": "MED-001",
           "serial_number": "TOSH-EXT-001",
           "make_model": "Toshiba Canvio 4TB",
           "vendor_name_text": "Toshiba",
           "capacity": "4 TB",
           "asset_location": "Data Centre",
           "stored_information_assets": "Server backup archives and software installation media",
           "maintenance_status": "Active",
           "confidentiality": "Low (L)", "integrity": "Low (L)", "availability": "Low (L)",
           "asset_criticality": "Low",
           "data_classification": "Internal Use Only",
           "nca_ecc_domain": "Resilience", "nca_control_number": "2.9",
           "last_reviewed": today_date}),

        d({"asset_name": "Encrypted USB Drive — Management",
           "asset_type": "Media / Portable Device", "asset_id": "MED-002",
           "make_model": "Kingston IronKey 32GB",
           "vendor_name_text": "Kingston",
           "capacity": "32 GB",
           "asset_location": "Head Office",
           "stored_information_assets": "Encrypted management documents, policy drafts",
           "maintenance_status": "Active",
           "confidentiality": "Medium (M)", "integrity": "Medium (M)", "availability": "Low (L)",
           "asset_criticality": "Medium",
           "data_classification": "Confidential",
           "contains_personal_data": 0,
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        # ── DESKTOPS (ISO-27001 PROJECT - List of Important Desktops) ────
        d({"asset_name": "Workstation 01 — Operations",
           "asset_type": "Desktop", "asset_id": "DSK-001",
           "serial_number": "DSK-SN-WS01",
           "make_model": "Dell OptiPlex 7080",
           "vendor_name_text": "Dell",
           "cpu": "Intel Core i5", "ram": "8 GB", "storage": "1 TB HDD",
           "os_version": "Windows 11 Pro",
           "ip_address": "192.168.1.101",
           "asset_location": "Head Office",
           "user_role": "GC Operations User — read-only G Banker",
           "anti_virus_updated": "Yes",
           "redundancy_required": "No",
           "maintenance_status": "Active",
           "confidentiality": "Medium (M)", "integrity": "Medium (M)", "availability": "Medium (M)",
           "asset_criticality": "Medium",
           "data_classification": "Internal Use Only",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        d({"asset_name": "Workstation 02 — IT Helpdesk",
           "asset_type": "Desktop", "asset_id": "DSK-002",
           "serial_number": "DSK-SN-WS02",
           "make_model": "HP EliteDesk 800 G6",
           "vendor_name_text": "HP",
           "cpu": "Intel Core i7", "ram": "16 GB", "storage": "512 GB SSD",
           "os_version": "Windows 11 Enterprise",
           "ip_address": "192.168.1.102",
           "asset_location": "Head Office",
           "user_role": "IT Helpdesk — admin access for support",
           "anti_virus_updated": "Yes",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "Medium (M)",
           "asset_criticality": "High",
           "data_classification": "Confidential",
           "nca_ecc_domain": "Defense", "nca_control_number": "2.3",
           "last_reviewed": today_date}),

        # ── CLOUD SERVICE ────────────────────────────────────────────────
        d({"asset_name": "Microsoft Azure — Cloud IaaS / PaaS",
           "asset_type": "Cloud Service", "asset_id": "CLD-001",
           "vendor_name_text": "Microsoft",
           "sla": "Yes",
           "asset_location": "Cloud",
           "purpose_service_role": "Cloud infrastructure, Azure AD, storage, and backup services",
           "stored_information_assets": "Application data replicas, archive logs, identity directory",
           "maintenance_status": "Active",
           "confidentiality": "High (H)", "integrity": "High (H)", "availability": "High (H)",
           "asset_criticality": "Critical",
           "data_classification": "Confidential",
           "contains_personal_data": 1,
           "backup_schedule": "Real-time",
           "nca_ecc_domain": "Technical Systems", "nca_control_number": "4.2",
           "last_reviewed": today_date}),
    ]

    for a in assets:
        safe_insert(a, {"asset_name": a["asset_name"]})

    frappe.logger().info(f"AlphaX GRC v1.2.2: Seeded {len(assets)} asset inventory records across 6 types")


def seed_nca_ecc_controls_full_v2():
    """
    Seed all 15 NCA ECC-2:2024 controls with technology mapping.
    Source: CYBERSECURITY_TECHNOLOGY_MAPPING.pdf (NCA ECC-2:2024).
    Includes 4 strategic pillars: Zero Trust, Cyber Resilience, PDPL, AI/SOAR.
    """
    if not frappe.db.exists("DocType", "GRC NCA ECC Control"):
        return
    if frappe.db.count("GRC NCA ECC Control") >= 14:
        return  # already seeded

    controls = [
        # ── GOVERNANCE ───────────────────────────────────────────────────
        {"main_domain": "Governance", "control_number": "1.3-1.5",
         "control_name": "Cybersecurity Policies & Risk Management",
         "control_description": (
             "Establish, approve, publish and regularly review cybersecurity policies, standards and procedures. "
             "Conduct periodic risk assessments and maintain a cybersecurity risk register aligned to organizational objectives."
         ),
         "required_technology_type": "GRC Solutions",
         "technology_solutions": "ServiceNow / Archer / CyberImtithal",
         "pillar_data_sovereignty": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Governance", "control_number": "1.10",
         "control_name": "Cybersecurity Awareness & Training Program",
         "control_description": (
             "Implement a formal cybersecurity awareness program including phishing simulations, "
             "mandatory annual training for all staff, and role-based training for privileged users."
         ),
         "required_technology_type": "Security Awareness Systems",
         "technology_solutions": "KnowBe4 / Proofpoint / PhishRod",
         "compliance_status": "Not Assessed"},

        # ── DEFENSE ──────────────────────────────────────────────────────
        {"main_domain": "Defense", "control_number": "2.1",
         "control_name": "Asset Management (ITAM / CAASM)",
         "control_description": (
             "Maintain a complete, accurate and up-to-date inventory of all information assets including hardware, software, "
             "data, network devices, cloud services and personnel. Classify assets by CIA rating."
         ),
         "required_technology_type": "ITAM / CAASM",
         "technology_solutions": "ServiceNow / Axonius / ManageEngine",
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.2",
         "control_name": "Identity & Access Management (IAM / PAM / IGA)",
         "control_description": (
             "Implement identity-based access controls enforcing least privilege, MFA, privileged access management, "
             "and identity governance aligned to Zero Trust Architecture principles."
         ),
         "required_technology_type": "IAM / PAM / IGA",
         "technology_solutions": "CyberArk / SailPoint / Okta / BeyondTrust",
         "pillar_zero_trust": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.3",
         "control_name": "Systems Protection — EDR / XDR",
         "control_description": (
             "Deploy endpoint detection and response across all endpoints and servers. "
             "XDR integration to correlate signals across endpoint, network, identity and cloud workloads."
         ),
         "required_technology_type": "EDR / XDR",
         "technology_solutions": "CrowdStrike / SentinelOne / Trend Micro",
         "pillar_cyber_resilience": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.3",
         "control_name": "Data Protection — DLP / DSPM",
         "control_description": (
             "Implement data loss prevention and data security posture management. "
             "Enforce PDPL and data classification policy through technical controls on endpoints, email, cloud and storage."
         ),
         "required_technology_type": "DLP / DSPM / Purview",
         "technology_solutions": "Forcepoint / Varonis / MS Purview",
         "pillar_data_sovereignty": 1, "pillar_cyber_resilience": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.4",
         "control_name": "Email Security — Cloud Email Security Gateway",
         "control_description": (
             "Deploy a cloud email security gateway (SEG) to block phishing, malware, BEC attacks, "
             "malicious URLs and spoofed domains. Enable DMARC, DKIM and SPF enforcement."
         ),
         "required_technology_type": "Cloud Email Security (SEG)",
         "technology_solutions": "Proofpoint / Mimecast / Ironscales",
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.5",
         "control_name": "Network Security — NGFW / NAC / ZTNA",
         "control_description": (
             "Implement next-generation firewalls, network access control (NAC) and zero trust network access (ZTNA). "
             "Enforce network segmentation, micro-segmentation, and deny-by-default policies."
         ),
         "required_technology_type": "NGFW / NAC / ZTNA",
         "technology_solutions": "Palo Alto / Fortinet / Cisco / Illumio",
         "pillar_zero_trust": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.5",
         "control_name": "Web & Application Security — WAF / WAAP / API Security",
         "control_description": (
             "Protect web applications and APIs using a WAF, WAAP and API security gateway. "
             "Block OWASP Top 10 attacks, bot traffic, DDoS and application-layer exploits."
         ),
         "required_technology_type": "WAF / WAAP / API Security",
         "technology_solutions": "F5 / Imperva / Akamai / Cloudflare",
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.10",
         "control_name": "Vulnerability Management — Risk-Based (RBVM)",
         "control_description": (
             "Continuously discover, scan, prioritize and remediate vulnerabilities across all assets. "
             "Risk-based approach prioritizes high-impact CVEs. Integrate with asset inventory and patch management."
         ),
         "required_technology_type": "RBVM / VM",
         "technology_solutions": "Tenable / Qualys / Rapid7",
         "compliance_status": "Not Assessed"},

        {"main_domain": "Defense", "control_number": "2.11",
         "control_name": "Penetration Testing & Breach Attack Simulation (BAS)",
         "control_description": (
             "Conduct regular authorized penetration testing and continuous breach-and-attack simulation. "
             "Identify exploitable weaknesses before adversaries. Align with red team exercises and threat intelligence."
         ),
         "required_technology_type": "BAS / Pentest Tools",
         "technology_solutions": "XM Cyber / Pentera / Metasploit",
         "compliance_status": "Not Assessed"},

        # ── RESILIENCE ───────────────────────────────────────────────────
        {"main_domain": "Resilience", "control_number": "2.9",
         "control_name": "Backup & Recovery — Immutable Backup / DR",
         "control_description": (
             "Implement immutable, air-gapped backup and tested disaster recovery. "
             "Define RTO/RPO, validate backups regularly, and ensure rapid restoration capability. "
             "Aligned with NCA cyber resilience pillar."
         ),
         "required_technology_type": "Immutable Backup / DR",
         "technology_solutions": "Veeam / Cohesity / Rubrik / Veritas",
         "pillar_cyber_resilience": 1,
         "compliance_status": "Not Assessed"},

        {"main_domain": "Resilience", "control_number": "2.12",
         "control_name": "Security Monitoring — Next-Gen SIEM / SOAR",
         "control_description": (
             "Deploy a next-generation SIEM with AI/ML-driven detection and SOAR for automated response. "
             "Reduces MTTR, enables threat hunting, supports regulatory incident reporting requirements."
         ),
         "required_technology_type": "Next-Gen SIEM / SOAR",
         "technology_solutions": "Splunk / MS Sentinel / IBM QRadar",
         "pillar_cyber_resilience": 1, "pillar_ai_automation": 1,
         "compliance_status": "Not Assessed"},

        # ── EXTERNAL PARTIES ─────────────────────────────────────────────
        {"main_domain": "External Parties", "control_number": "3.1",
         "control_name": "Supply Chain & Third-Party Security (TPRM / VRM)",
         "control_description": (
             "Assess and continuously monitor third-party and supply chain cybersecurity risk. "
             "Enforce security clauses in contracts. Conduct periodic vendor risk assessments aligned to PDPL data transfer obligations."
         ),
         "required_technology_type": "TPRM / VRM",
         "technology_solutions": "BitSight / SecurityScorecard",
         "pillar_data_sovereignty": 1,
         "compliance_status": "Not Assessed"},

        # ── TECHNICAL SYSTEMS ────────────────────────────────────────────
        {"main_domain": "Technical Systems", "control_number": "4.2",
         "control_name": "Cloud Security — CSPM / CWPP / CNAPP",
         "control_description": (
             "Implement cloud security posture management (CSPM), cloud workload protection (CWPP) and cloud-native application "
             "protection (CNAPP) across IaaS, PaaS and SaaS. Enforce data sovereignty, Zero Trust and cloud misconfiguration remediation."
         ),
         "required_technology_type": "CSPM / CWPP / CNAPP",
         "technology_solutions": "Wiz / Prisma Cloud / Orca Security",
         "pillar_zero_trust": 1, "pillar_cyber_resilience": 1,
         "compliance_status": "Not Assessed"},
    ]

    for c in controls:
        c["doctype"] = "GRC NCA ECC Control"
        safe_insert(c, {"control_name": c["control_name"], "main_domain": c["main_domain"]})

    frappe.logger().info(f"AlphaX GRC v1.2.2: Seeded {len(controls)} NCA ECC-2:2024 controls")


# ---------------------------------------------------------------------------
# Workspace and Report registration (v1.2.2)
# ---------------------------------------------------------------------------

def ensure_workspace():
    """
    The Workspace is auto-loaded from alphax_grc/workspace/ during bench migrate.
    In production (Frappe Cloud) direct insertion is not allowed.

    v1.2.5: Repair workspace on existing installs.

    The real root cause of `AttributeError: 'Workspace' object has no
    attribute 'onboarding_list'` (Frappe v15.106) is a NULL `content`
    field on the Workspace document. In frappe/desk/desktop.py, the
    `Workspace.__init__` only sets `self.onboarding_list` when
    `self.doc.content` is truthy. If content is NULL, the attribute is
    never assigned, then `get_onboardings()` references it and crashes.
    See https://github.com/frappe/erpnext/issues/43234

    Fix: ensure the Workspace row has a non-empty JSON-encoded content
    string. The shipped JSON already includes `content`; this code
    repairs installs whose DB row was created before content was added.
    """
    try:
        if not frappe.db.exists("Workspace", "AlphaX GRC"):
            return

        # Repair empty-string onboarding (defensive — kept from v1.2.4)
        cur_onb = frappe.db.get_value("Workspace", "AlphaX GRC", "onboarding")
        if cur_onb == "" or cur_onb is False:
            frappe.db.set_value("Workspace", "AlphaX GRC", "onboarding", None)

        # Repair NULL / empty content — the real fix
        cur_content = frappe.db.get_value("Workspace", "AlphaX GRC", "content")
        if not cur_content:
            default_content = (
                '[{"type":"header","data":{"text":"Welcome to AlphaX GRC","col":12,"level":4}},'
                '{"type":"shortcut","data":{"shortcut_name":"Command Centre","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Risk Dashboard","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Neo Hub","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"ITGC Programme","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Risk Register","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Audit Findings","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Asset Dashboard","col":3}},'
                '{"type":"shortcut","data":{"shortcut_name":"Incidents","col":3}},'
                '{"type":"spacer","data":{"col":12}},'
                '{"type":"header","data":{"text":"Modules","col":12,"level":4}},'
                '{"type":"card","data":{"card_name":"Dashboards & Pages","col":4}},'
                '{"type":"card","data":{"card_name":"Risk Management","col":4}},'
                '{"type":"card","data":{"card_name":"Compliance & Frameworks","col":4}},'
                '{"type":"card","data":{"card_name":"Audit & ITGC","col":4}},'
                '{"type":"card","data":{"card_name":"Assets & Inventory","col":4}},'
                '{"type":"card","data":{"card_name":"Vendor & Privacy","col":4}},'
                '{"type":"card","data":{"card_name":"Incidents & DR","col":4}},'
                '{"type":"card","data":{"card_name":"Reports","col":4}},'
                '{"type":"card","data":{"card_name":"Settings","col":4}}]'
            )
            frappe.db.set_value("Workspace", "AlphaX GRC", "content", default_content)
            try:
                frappe.logger().info(
                    "AlphaX GRC v1.2.5: Repaired Workspace.content "
                    "(NULL -> default layout) to fix Frappe core "
                    "onboarding_list AttributeError."
                )
            except Exception:
                pass

        # Always clear cache so the change is picked up immediately
        try:
            frappe.clear_cache()
        except Exception:
            pass
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC ensure_workspace repair failed")
        except Exception:
            pass
    return  # workspace records themselves are handled by Frappe's module sync


def ensure_reports():
    """
    Reports are auto-loaded from alphax_grc/report/ during bench migrate.
    In production (Frappe Cloud) direct insertion is not allowed.
    This is intentionally a no-op.
    """
    return  # handled by Frappe's module sync from report/ folder


# ===========================================================================
# v1.3.0 — Multi-tenant Client Profile + NCA ECC trackers + BIA + RCM
# ===========================================================================

DEFAULT_CLIENT_NAME = "DEMO"


def seed_default_client_profile():
    """Create one demo client so existing data has a home and the lifecycle
    dashboard has something to show on first install."""
    if not frappe.db.exists("DocType", "GRC Client Profile"):
        return
    if frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    safe_insert({
        "doctype": "GRC Client Profile",
        "client_code": DEFAULT_CLIENT_NAME,
        "client_name": "Demo Client (Saudi Arabia / Government)",
        "client_name_ar": "العميل التجريبي",
        "country": "Saudi Arabia",
        "sector": "Government",
        "is_active": 1,
        "engagement_type": "Retainer",
        "lead_consultant": "Administrator",
        "default_hourly_rate": 600,
        "billing_currency": "SAR",
        "scope_notes": ("This is a sample client created on install. "
                        "Create real Client Profiles via /app/grc-client-profile."),
    }, {"client_code": DEFAULT_CLIENT_NAME})


def backfill_client_on_existing_records():
    """For wipe-and-reseed installs: assign the demo client to any orphan
    record that was created without a client (existing seeded sample data
    from earlier versions)."""
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    # The 34 doctypes that got the client field in v1.3.0
    doctypes = [
        "GRC Action Plan", "GRC Aramco Incident Notification",
        "GRC Aramco Third Party Profile", "GRC Assessment",
        "GRC Assessment Run", "GRC Asset Inventory", "GRC Audit Finding",
        "GRC Audit Plan", "GRC Audit Workpaper", "GRC Board Report",
        "GRC Control", "GRC Data Subject Request", "GRC DR Plan",
        "GRC Evidence", "GRC Exception", "GRC Framework", "GRC Incident",
        "GRC ISMS Document Register", "GRC ISO27001 Document",
        "GRC IT Audit Program", "GRC ITGC Audit Item", "GRC KRI",
        "GRC Maturity Assessment", "GRC NCA ECC Control", "GRC Policy",
        "GRC Privacy Processing Activity", "GRC Problem Record",
        "GRC Regulatory Obligation", "GRC Remediation Action",
        "GRC Risk Acceptance", "GRC Risk Register", "GRC Technology Control",
        "GRC Vendor", "GRC Vendor Assessment",
    ]
    for dt in doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
        try:
            frappe.db.sql(f"""
                UPDATE `tab{dt}`
                SET client = %s
                WHERE client IS NULL OR client = ''
            """, (DEFAULT_CLIENT_NAME,))
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"AlphaX GRC client backfill failed for {dt}")
            except Exception:
                pass


# ---------------------------------------------------------------------------
# NCA ECC Documentation checklist (32 documents from Axidian guide)
# ---------------------------------------------------------------------------

NCA_ECC_DOCUMENTS = [
    ("1-1-1", "Cybersecurity Strategy",
     "استراتيجية الأمن السيبراني",
     "Defined, documented and approved by the Authorizing Official."),
    ("1-2-3", "Cybersecurity Steering Committee Charter",
     "ميثاق لجنة توجيه الأمن السيبراني",
     "Members, roles, responsibilities and governance framework."),
    ("1-3-1", "Cybersecurity Policies & Procedures",
     "سياسات وإجراءات الأمن السيبراني",
     "Defined, documented, approved and disseminated to relevant parties."),
    ("1-4-1", "Cybersecurity Organization Structure & Roles",
     "الهيكل التنظيمي للأمن السيبراني والأدوار",
     "Roles and responsibilities defined, documented and approved."),
    ("1-5-1", "Cybersecurity Risk Management Methodology",
     "منهجية إدارة مخاطر الأمن السيبراني",
     "Per CIA considerations of information and technology assets."),
    ("1-5-4", "Cybersecurity Risk Methodology Review Records",
     "سجلات مراجعة منهجية إدارة المخاطر",
     "Periodic review per planned intervals or on regulatory change."),
    ("1-6-1", "Cybersecurity in Project & Change Management",
     "الأمن السيبراني في إدارة المشاريع والتغيير",
     "Cybersecurity included in project and change management procedures."),
    ("1-8-3", "Audit & Review Results Documentation",
     "توثيق نتائج المراجعات والتدقيقات",
     "Scope, observations, recommendations, remediation plans."),
    ("1-9-1", "Personnel Cybersecurity Requirements",
     "متطلبات الأمن السيبراني للموظفين",
     "Prior to, during, and after employment / termination."),
    ("2-1-1", "Information & Technology Asset Management Requirements",
     "متطلبات إدارة أصول المعلومات والتقنية",
     "Identified, documented and approved."),
    ("2-1-3", "Acceptable Use Policy",
     "سياسة الاستخدام المقبول",
     "For information and technology assets."),
    ("2-2-1", "Identity & Access Management Requirements",
     "متطلبات إدارة الهويات والصلاحيات",
     "Defined, documented and approved."),
    ("2-3-1", "Information Systems Protection Requirements",
     "متطلبات حماية أنظمة المعلومات",
     "Information systems and processing facilities."),
    ("2-4-1", "Email Service Protection Requirements",
     "متطلبات حماية خدمة البريد الإلكتروني",
     "Defined, documented and approved."),
    ("2-5-1", "Network Security Management Requirements",
     "متطلبات إدارة أمن الشبكات",
     "Defined, documented and approved."),
    ("2-6-1", "Mobile Devices Security & BYOD Requirements",
     "متطلبات أمن الأجهزة المحمولة و BYOD",
     "Defined, documented and approved."),
    ("2-7-1", "Data & Information Protection Requirements",
     "متطلبات حماية البيانات والمعلومات",
     "Per related laws and regulations."),
    ("2-8-1", "Cryptography Requirements",
     "متطلبات التشفير",
     "Defined, documented and approved."),
    ("2-9-1", "Backup & Recovery Management Requirements",
     "متطلبات إدارة النسخ الاحتياطي والاسترداد",
     "Defined, documented and approved."),
    ("2-10-1", "Technical Vulnerabilities Management Requirements",
     "متطلبات إدارة الثغرات التقنية",
     "Defined, documented and approved."),
    ("2-11-1", "Penetration Testing Requirements",
     "متطلبات اختبار الاختراق",
     "Defined, documented and approved."),
    ("2-12-1", "Event Logs & Monitoring Requirements",
     "متطلبات سجلات الأحداث والمراقبة",
     "Defined, documented and approved."),
    ("2-13-1", "Cybersecurity Incidents & Threat Management",
     "إدارة الحوادث والتهديدات السيبرانية",
     "Defined, documented and approved."),
    ("2-14-1", "Physical Asset Protection Requirements",
     "متطلبات الحماية المادية للأصول",
     "Defined, documented and approved."),
    ("2-15-1", "External Web Applications Requirements",
     "متطلبات تطبيقات الويب الخارجية",
     "Defined, documented and approved."),
    ("3-1-1", "Business Continuity Management Requirements",
     "متطلبات إدارة استمرارية الأعمال",
     "Defined, documented and approved."),
    ("4-1-1", "Third-Party Contracts & Agreements Requirements",
     "متطلبات عقود واتفاقيات الأطراف الخارجية",
     "Identified, documented and approved."),
    ("4-2-1", "Hosting & Cloud Computing Requirements",
     "متطلبات الاستضافة والحوسبة السحابية",
     "Defined, documented and approved."),
]


def seed_nca_ecc_documents():
    """Pre-seed the 28 mandatory NCA ECC documents under the demo client."""
    if not frappe.db.exists("DocType", "GRC NCA ECC Document"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC NCA ECC Document",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    for ctrl, title, title_ar, desc in NCA_ECC_DOCUMENTS:
        safe_insert({
            "doctype": "GRC NCA ECC Document",
            "client": DEFAULT_CLIENT_NAME,
            "control_number": ctrl,
            "document_title": title,
            "document_title_ar": title_ar,
            "control_description": desc,
            "status": "To Do",
            "approval_authority": "Authorizing Official",
            "review_frequency": "Annually",
        }, {"client": DEFAULT_CLIENT_NAME, "control_number": ctrl})
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.3.0: Seeded {len(NCA_ECC_DOCUMENTS)} NCA ECC documents")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# NCA ECC Tool Mapping (controls that require/imply tooling)
# ---------------------------------------------------------------------------

NCA_ECC_TOOL_MAPPINGS = [
    ("1-3-3", "Technical security standards for policies",
     "GRC tools, Policy Management, IAM/PAM"),
    ("1-5-3", "Cybersecurity risk assessment procedures",
     "GRC tools, ERM, TPRM, IAM/PAM"),
    ("1-6-2", "Cybersecurity in change management",
     "Vulnerability assessment, configuration mgmt, patch mgmt"),
    ("1-6-3", "Cybersecurity in software/application projects",
     "SCA, DAST, API security testing"),
    ("1-9-4", "Personnel cybersecurity during employment",
     "Security awareness platform, IAM/PAM"),
    ("1-10-3", "Cybersecurity awareness program",
     "Security awareness & training platforms"),
    ("1-10-4", "Specialized cybersecurity training",
     "Security awareness & training platforms"),
    ("2-1-2", "Information & technology asset management",
     "ITAM, CMDB, EPP/EDR, Data Discovery & Classification"),
    ("2-1-4", "Acceptable use policy implementation",
     "DLP, User Activity Monitoring / PAM"),
    ("2-1-5", "Asset classification, labelling, handling",
     "Data Discovery & Classification, PAM/ITDR"),
    ("2-2-3", "Identity & access management",
     "IAM, PAM, MFA"),
    ("2-3-3", "Protect information systems",
     "Antivirus/EDR, DLP, Patch Management, NTP"),
    ("2-4-3", "Email service protection",
     "Email Security Gateway, IAM with MFA, Email Auth Mgmt"),
    ("2-5-3", "Network security management",
     "NGFW/NAC/SDN, SWG, WIDS/WIPS, IPS, DDoS, Haseen"),
    ("2-6-3", "Mobile devices & BYOD security",
     "MDM/EMM, MAM, Mobile DLP, MTD, awareness"),
    ("2-7-3", "Data & information protection",
     "DLP, Data Discovery & Classification, IAM, Backup"),
    ("2-8-3", "Cryptography",
     "KMS/CMS, PKI management, encryption (in-transit/rest/use)"),
    ("2-9-3", "Backup & recovery management",
     "Enterprise backup, DR orchestration, backup testing"),
    ("2-10-3", "Technical vulnerabilities management",
     "Vuln assessment, patch mgmt, threat intel, CVE feeds"),
    ("2-11-3", "Penetration testing",
     "Pentest platforms / managed pentest services"),
    ("2-12-3", "Event logs & monitoring",
     "Log mgmt / SIEM, UEBA, PAM"),
    ("2-13-3", "Incidents & threat management",
     "SOAR, SIEM with IR, Threat Intel Platform"),
    ("2-14-3", "Physical protection of assets",
     "PACS, VMS, SIEM+VMS storage, media destruction, IAM"),
    ("2-15-3", "External web applications",
     "WAF, Policy Management, IAM with MFA"),
    ("3-1-3", "Business continuity management",
     "IR tools, GRC platforms, BCM platforms, DR/Backup, IAM"),
    ("4-1-2", "Third-party contracts",
     "CLM, TPRM, GRC, PAM"),
    ("4-1-3", "IT outsourcing & managed services contracts",
     "TPRM, GRC"),
    ("4-2-3", "Hosting & cloud services",
     "DDC, DLP, CWPP"),
]


def seed_nca_ecc_tool_mappings():
    if not frappe.db.exists("DocType", "GRC NCA ECC Tool Mapping"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC NCA ECC Tool Mapping",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    for ctrl, summary, cats in NCA_ECC_TOOL_MAPPINGS:
        safe_insert({
            "doctype": "GRC NCA ECC Tool Mapping",
            "client": DEFAULT_CLIENT_NAME,
            "control_number": ctrl,
            "control_summary": summary,
            "recommended_categories": cats,
            "coverage_status": "Not Assessed",
            "tool_in_place": 0,
        }, {"client": DEFAULT_CLIENT_NAME, "control_number": ctrl})
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.3.0: Seeded {len(NCA_ECC_TOOL_MAPPINGS)} NCA ECC tool mappings")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# NCA ECC Review Calendar (controls requiring periodic review)
# ---------------------------------------------------------------------------

NCA_ECC_REVIEWS = [
    ("1-1-3", "Cybersecurity strategy review", "Yearly"),
    ("1-3-4", "Policies & procedures review", "Yearly"),
    ("1-4-2", "Roles & responsibilities review", "Yearly"),
    ("1-5-4", "Risk methodology review", "Yearly"),
    ("1-6-4", "Project management cybersecurity review", "Yearly"),
    ("1-8-1", "Periodic cybersecurity reviews", "6 Months"),
    ("1-9-6", "Personnel cybersecurity requirements review", "Yearly"),
    ("1-10-1", "Awareness program execution", "Yearly"),
    ("1-10-5", "Awareness program implementation review", "Yearly"),
    ("2-1-6", "Asset management requirements review", "Yearly"),
    ("2-2-3-5", "Periodic review of users' identities and access rights", "3 Months"),
    ("2-2-4", "IAM implementation review", "Yearly"),
    ("2-3-4", "Information systems protection review", "Yearly"),
    ("2-4-4", "Email service protection review", "Yearly"),
    ("2-5-4", "Network security review", "Yearly"),
    ("2-6-4", "Mobile/BYOD review", "Yearly"),
    ("2-7-4", "Data protection review", "Yearly"),
    ("2-8-4", "Cryptography requirements review", "Yearly"),
    ("2-9-4", "Backup & recovery review", "Yearly"),
    ("2-10-4", "Vulnerability management review", "Yearly"),
    ("2-11-3", "Conducting penetration tests", "Yearly"),
    ("2-11-4", "Penetration testing process review", "Yearly"),
    ("2-12-4", "Event logs & monitoring review", "Yearly"),
    ("2-13-4", "Incidents & threat management review", "Yearly"),
    ("2-14-4", "Physical protection review", "Yearly"),
    ("2-15-4", "External web applications review", "Yearly"),
    ("3-1-4", "Business continuity review", "Yearly"),
    ("4-1-4", "Third-party contracts review", "Yearly"),
    ("4-2-4", "Hosting & cloud review", "Yearly"),
]


def seed_nca_ecc_review_calendar():
    if not frappe.db.exists("DocType", "GRC NCA ECC Review Calendar"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC NCA ECC Review Calendar",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    from datetime import date, timedelta
    today = date.today()
    next_year = today + timedelta(days=365)
    for ctrl, subject, freq in NCA_ECC_REVIEWS:
        # Stagger schedules — quarterly reviews next 90 days, yearly next year
        if freq == "3 Months":
            sched = today + timedelta(days=90)
        elif freq == "6 Months":
            sched = today + timedelta(days=180)
        elif freq == "Monthly":
            sched = today + timedelta(days=30)
        else:
            sched = next_year
        safe_insert({
            "doctype": "GRC NCA ECC Review Calendar",
            "client": DEFAULT_CLIENT_NAME,
            "control_number": ctrl,
            "review_subject": subject,
            "frequency": freq,
            "next_scheduled": sched,
            "status": "Scheduled",
        }, {"client": DEFAULT_CLIENT_NAME, "control_number": ctrl})
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.3.0: Seeded {len(NCA_ECC_REVIEWS)} review calendar entries")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Sample BIA records (5 common critical activities)
# ---------------------------------------------------------------------------

BIA_SAMPLES = [
    {
        "activity_name": "Customer-facing online services",
        "activity_name_ar": "الخدمات الإلكترونية للعملاء",
        "description": "Public web portal and mobile app used by customers to access services.",
        "rto": 4, "rpo": 1, "mtpd": 24,
        "fin": 4, "ops": 5, "reg": 3, "rep": 5, "cust": 5,
        "deps": [
            ("Technology / Application", "Production web cluster", "Critical"),
            ("Technology / Application", "Identity provider (SSO)", "Critical"),
            ("Data & Information", "Customer database (primary)", "Critical"),
            ("Third-Party Provider", "CDN", "High"),
        ],
    },
    {
        "activity_name": "Financial close and reporting",
        "activity_name_ar": "الإقفال المالي والتقارير",
        "description": "Monthly and quarterly financial close, regulator submissions.",
        "rto": 24, "rpo": 24, "mtpd": 168,
        "fin": 5, "ops": 3, "reg": 5, "rep": 4, "cust": 2,
        "deps": [
            ("Technology / Application", "ERP general ledger", "Critical"),
            ("People & Skills", "Finance controller", "Critical"),
            ("Data & Information", "Sub-ledgers, fixed asset register", "High"),
        ],
    },
    {
        "activity_name": "Payroll processing",
        "activity_name_ar": "معالجة الرواتب",
        "description": "End-to-end monthly payroll for all employees.",
        "rto": 48, "rpo": 24, "mtpd": 96,
        "fin": 3, "ops": 4, "reg": 4, "rep": 4, "cust": 1,
        "deps": [
            ("Technology / Application", "HRMS / payroll system", "Critical"),
            ("Third-Party Provider", "Bank salary transfer file API", "Critical"),
            ("People & Skills", "Payroll officer", "Critical"),
        ],
    },
    {
        "activity_name": "IT operations & service desk",
        "activity_name_ar": "عمليات تقنية المعلومات ومكتب الخدمة",
        "description": "Internal IT support, incident response, change deployments.",
        "rto": 8, "rpo": 4, "mtpd": 48,
        "fin": 2, "ops": 5, "reg": 2, "rep": 3, "cust": 4,
        "deps": [
            ("Technology / Application", "ITSM ticketing system", "High"),
            ("Technology / Application", "Monitoring & alerting", "Critical"),
            ("People & Skills", "IT operations engineers", "Critical"),
        ],
    },
    {
        "activity_name": "Regulatory reporting (SAMA / NCA / PDPL)",
        "activity_name_ar": "التقارير التنظيمية",
        "description": "Periodic reports to regulators including SAMA, NCA and PDPL.",
        "rto": 24, "rpo": 8, "mtpd": 168,
        "fin": 3, "ops": 2, "reg": 5, "rep": 5, "cust": 2,
        "deps": [
            ("Data & Information", "Compliance evidence repository", "Critical"),
            ("People & Skills", "Compliance officer", "Critical"),
            ("Technology / Application", "GRC platform (this app)", "High"),
        ],
    },
]


def seed_sample_bia():
    if not frappe.db.exists("DocType", "GRC Business Impact Analysis"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC Business Impact Analysis",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    for sample in BIA_SAMPLES:
        deps = [{"dependency_type": d[0], "dependency_name": d[1],
                 "criticality": d[2]} for d in sample["deps"]]
        safe_insert({
            "doctype": "GRC Business Impact Analysis",
            "client": DEFAULT_CLIENT_NAME,
            "activity_name": sample["activity_name"],
            "activity_name_ar": sample["activity_name_ar"],
            "is_critical": 1,
            "activity_description": sample["description"],
            "rto_hours": sample["rto"],
            "rpo_hours": sample["rpo"],
            "mtpd_hours": sample["mtpd"],
            "financial_impact": sample["fin"],
            "operational_impact": sample["ops"],
            "regulatory_impact": sample["reg"],
            "reputational_impact": sample["rep"],
            "customer_impact": sample["cust"],
            "dependencies": deps,
        }, {"client": DEFAULT_CLIENT_NAME,
            "activity_name": sample["activity_name"]})
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.3.0: Seeded {len(BIA_SAMPLES)} sample BIA records")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Sample RCM (PMO Government from RCM_PMO_Government.docx)
# ---------------------------------------------------------------------------

RCM_PMO_LINES = [
    ("Strategic Alignment",
     "Approving projects not aligned to the strategy",
     "Financial waste and weak achievement of objectives",
     "Project approval committee with clear criteria",
     "Preventive", "PMO Director", "Per Project",
     "% of projects aligned to strategy"),
    ("Project Governance",
     "Project delays vs. baseline",
     "Delay of government objectives",
     "Weekly executive dashboards and tracking reports",
     "Detective", "Project Manager", "Weekly",
     "% schedule variance"),
    ("Budget & Financial Control",
     "Budget overrun beyond approved baseline",
     "Financial and operational impact",
     "Monthly financial review and multi-level approvals",
     "Preventive", "Finance Department", "Monthly",
     "% budget variance"),
    ("Risk Management",
     "Risks not identified early",
     "Project disruption",
     "Up-to-date risk register and periodic review meetings",
     "Preventive/Detective", "Risk Officer", "Monthly",
     "Number of critical risks"),
    ("Vendor & Contract",
     "Weak contractor performance",
     "Implementation delays",
     "SLA and contractual KPIs",
     "Detective", "Contracts Department", "Monthly",
     "% vendor compliance"),
    ("Performance Reporting",
     "Inaccurate reports to senior management",
     "Wrong decisions",
     "Data quality review before reports are issued",
     "Preventive", "PMO Analyst", "Monthly",
     "Reporting accuracy"),
]


def seed_sample_rcm():
    if not frappe.db.exists("DocType", "GRC Risk Control Matrix"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC Risk Control Matrix",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    lines = [{
        "domain": d, "risk_description": r, "impact_description": i,
        "control_description": c, "control_type": ct, "control_owner": o,
        "frequency": f, "kpi": k,
    } for (d, r, i, c, ct, o, f, k) in RCM_PMO_LINES]
    safe_insert({
        "doctype": "GRC Risk Control Matrix",
        "client": DEFAULT_CLIENT_NAME,
        "matrix_title": "PMO Risk Control Matrix — Government",
        "matrix_title_ar": "مصفوفة المخاطر والضوابط — مكتب إدارة المشاريع الحكومي",
        "scope": "PMO",
        "version": "1.0",
        "status": "Approved",
        "objective": ("Govern the PMO portfolio: ensure projects are "
                      "aligned, on-schedule, on-budget, and reported "
                      "accurately to senior management."),
        "lines": lines,
    }, {"client": DEFAULT_CLIENT_NAME,
        "matrix_title": "PMO Risk Control Matrix — Government"})
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.3.0: Seeded sample RCM with {len(RCM_PMO_LINES)} lines")
    except Exception:
        pass


# ===========================================================================
# v1.3.2 — Initial snapshot computation
# ===========================================================================

def seed_initial_snapshots():
    """Compute the first dashboard snapshot for every active client.
    Without this, dashboards would show 'Loading…' until the 15-minute cron
    fires for the first time."""
    if not frappe.db.exists("DocType", "GRC Dashboard Snapshot"):
        return
    if not frappe.db.exists("DocType", "GRC Client Profile"):
        return
    try:
        from alphax_grc.dashboards_live import refresh_all_snapshots
        result = refresh_all_snapshots()
        if result:
            try:
                frappe.logger().info(
                    f"AlphaX GRC v1.3.2: seeded {result.get('refreshed', 0)} "
                    f"of {result.get('total', 0)} initial dashboard snapshots."
                )
            except Exception:
                pass
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC seed_initial_snapshots failed")
        except Exception:
            pass


# ===========================================================================
# v1.4.0 — Threat Catalogue, Vulnerability, KPI, NCA template libraries
# ===========================================================================

NCA_STANDARD_THREATS = [
    ("T01", "Credential compromise", "اختراق بيانات الاعتماد", "Identity & Access",
     "Theft, brute-force, phishing, or reuse of authentication credentials."),
    ("T02", "Insider threats", "التهديدات الداخلية", "Insider",
     "Malicious or negligent actions by employees, contractors, or partners."),
    ("T03", "Asset compromise", "اختراق الأصول", "Asset",
     "Unauthorized control or modification of an information / technology asset."),
    ("T04", "Social engineering", "الهندسة الاجتماعية", "Social Engineering",
     "Manipulation of personnel into disclosing information or performing actions."),
    ("T05", "Data breach / leakage", "تسرب البيانات", "Data",
     "Unauthorized exfiltration or disclosure of sensitive data."),
    ("T06", "Loss of business continuity", "فقدان استمرارية الأعمال", "Business Continuity",
     "Disruption of critical business processes or services."),
    ("T07", "Data loss", "فقدان البيانات", "Data",
     "Permanent or temporary loss of data due to corruption, deletion, or hardware failure."),
    ("T08", "Mistaking compliance for protection", "الخلط بين الامتثال والحماية", "Compliance",
     "Belief that meeting compliance requirements is sufficient cybersecurity."),
    ("T09", "Regulatory fines", "الغرامات التنظيمية", "Compliance",
     "Financial penalties from regulators for non-compliance."),
    ("T10", "Outdated hardware", "أجهزة قديمة", "Technology",
     "Unsupported, end-of-life, or vulnerable hardware in production."),
    ("T11", "Vulnerable software", "برامج معرضة للخطر", "Technology",
     "Unpatched, deprecated, or insecurely configured software."),
    ("T12", "Cloud vulnerabilities", "ثغرات سحابية", "Technology",
     "Misconfiguration or inherent risks in cloud services."),
    ("T13", "Ransomware", "برامج الفدية", "Malware",
     "Malicious encryption of organisation data with extortion demand."),
    ("T14", "Malware", "البرامج الضارة", "Malware",
     "General-purpose malicious software (viruses, worms, trojans, spyware)."),
    ("T15", "Attacks on IoT devices", "هجمات على إنترنت الأشياء", "Technology",
     "Compromise of connected sensors, controllers, or smart devices."),
    ("T16", "Operational downtime", "تعطل تشغيلي", "Operational",
     "Unplanned outage of operational systems impacting service delivery."),
    ("T17", "DDoS", "الحرمان من الخدمة الموزع", "Operational",
     "Distributed denial-of-service attack overwhelming services."),
    ("T18", "Underestimation of risk occurrence probability", "تقدير منخفض لاحتمال حدوث المخاطر", "Process",
     "Under-rating likelihood, leading to inadequate controls."),
    ("T19", "Partial risk assessment", "تقييم جزئي للمخاطر", "Process",
     "Risk assessment scope or depth that misses material risks."),
    ("T20", "Improper risk management", "إدارة غير صحيحة للمخاطر", "Process",
     "Incorrect or absent treatment, monitoring, or escalation."),
    ("T21", "Improper incident response", "استجابة غير ملائمة للحوادث", "Process",
     "Slow, ineffective, or undocumented incident handling."),
    ("T22", "Third party exposure", "التعرض للأطراف الخارجية", "Third Party",
     "Risk introduced via vendors, suppliers, or service providers."),
]


def seed_threat_catalogue():
    """Seed NCA's 22 standard threats. Global / not client-scoped."""
    if not frappe.db.exists("DocType", "GRC Threat Catalogue"):
        return
    inserted = 0
    for code, name, name_ar, cat, desc in NCA_STANDARD_THREATS:
        if frappe.db.exists("GRC Threat Catalogue", code):
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "GRC Threat Catalogue",
                "threat_code": code,
                "threat_name": name,
                "threat_name_ar": name_ar,
                "category": cat,
                "description": desc,
                "is_nca_standard": 1,
            })
            doc.insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Threat seed failed: {code}")
            except Exception:
                pass
    if inserted:
        try:
            frappe.logger().info(
                f"AlphaX GRC v1.4.0: Seeded {inserted} NCA standard threats")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Sample vulnerabilities for the DEMO client
# ---------------------------------------------------------------------------

SAMPLE_VULNERABILITIES = [
    {
        "vulnerability_id": "VULN01",
        "title": "Netlogon Elevation of Privilege Vulnerability (Zerologon)",
        "title_ar": "ثغرة رفع الصلاحيات في Netlogon",
        "vulnerability_description": "Cryptographic authentication scheme in Netlogon can be exploited to take control of a Windows domain controller.",
        "vendor_link": "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2020-1472",
        "cve_number": "CVE-2020-1472",
        "cvss_score": 10.0,
        "affected_technology": "Microsoft Active Directory",
        "affected_assets": "All Domain Controllers",
        "threat_analysis": "Threat actor can compromise the entire Active Directory environment.",
        "threat_severity": 5, "risk_likelihood": 3, "risk_severity": 5,
        "owner_user": "Administrator",
        "status": "Resolved",
        "linked_threat": "T01",
    },
    {
        "vulnerability_id": "VULN02",
        "title": "Microsoft Exchange Server SSRF (ProxyLogon)",
        "title_ar": "ثغرة SSRF في Microsoft Exchange",
        "vulnerability_description": "SSRF vulnerability in Exchange enabling pre-authentication RCE.",
        "vendor_link": "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855",
        "cve_number": "CVE-2021-26855",
        "cvss_score": 9.1,
        "affected_technology": "Microsoft Exchange",
        "affected_assets": "Two on-prem Exchange servers",
        "threat_analysis": "Pre-auth RCE could lead to mailbox theft and further lateral movement.",
        "threat_severity": 5, "risk_likelihood": 1, "risk_severity": 1,
        "owner_user": "Administrator",
        "status": "In Progress",
        "linked_threat": "T11",
    },
    {
        "vulnerability_id": "VULN03",
        "title": "Apache Log4j RCE (Log4Shell)",
        "title_ar": "ثغرة Log4Shell",
        "vulnerability_description": "JNDI feature in log4j allows remote code execution via crafted log strings.",
        "vendor_link": "https://logging.apache.org/log4j/2.x/security.html",
        "cve_number": "CVE-2021-44228",
        "cvss_score": 10.0,
        "affected_technology": "Java applications using log4j 2.x",
        "affected_assets": "Web frontend cluster, backend services",
        "threat_analysis": "Trivially exploitable RCE; mass-scanned by adversaries within hours of disclosure.",
        "threat_severity": 5, "risk_likelihood": 4, "risk_severity": 5,
        "owner_user": "Administrator",
        "status": "Open",
        "linked_threat": "T11",
    },
    {
        "vulnerability_id": "VULN04",
        "title": "OpenSSL Heartbleed",
        "title_ar": "ثغرة هارت بليد",
        "vulnerability_description": "Memory disclosure in OpenSSL TLS heartbeat extension.",
        "vendor_link": "https://www.openssl.org/news/secadv/20140407.txt",
        "cve_number": "CVE-2014-0160",
        "cvss_score": 7.5,
        "affected_technology": "OpenSSL 1.0.1 to 1.0.1f",
        "affected_assets": "Legacy load balancer (decommission planned)",
        "threat_analysis": "Memory disclosure of session keys and credentials.",
        "threat_severity": 4, "risk_likelihood": 2, "risk_severity": 3,
        "owner_user": "Administrator",
        "status": "On Hold",
        "linked_threat": "T05",
    },
    {
        "vulnerability_id": "VULN05",
        "title": "MOVEit Transfer SQL Injection",
        "title_ar": "ثغرة حقن SQL في MOVEit",
        "vulnerability_description": "SQL injection in MOVEit Transfer leading to data exfiltration.",
        "vendor_link": "https://community.progress.com/s/article/MOVEit-Transfer-Critical-Vulnerability",
        "cve_number": "CVE-2023-34362",
        "cvss_score": 9.8,
        "affected_technology": "Progress MOVEit Transfer",
        "affected_assets": "External file-transfer gateway",
        "threat_analysis": "Mass-exploited by Cl0p ransomware; targets file-transfer services holding sensitive data.",
        "threat_severity": 5, "risk_likelihood": 3, "risk_severity": 5,
        "owner_user": "Administrator",
        "status": "Open",
        "linked_threat": "T05",
    },
]


def seed_sample_vulnerabilities():
    if not frappe.db.exists("DocType", "GRC Vulnerability"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC Vulnerability", {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    from datetime import date, timedelta
    today_d = date.today()
    for v in SAMPLE_VULNERABILITIES:
        try:
            data = dict(v)
            data["doctype"] = "GRC Vulnerability"
            data["client"] = DEFAULT_CLIENT_NAME
            data["first_observation_date"] = today_d - timedelta(days=60)
            data["due_date"] = today_d + timedelta(days=30)
            if data.get("status") == "Resolved":
                data["resolution_date"] = today_d - timedelta(days=15)
            # linked_threat may not exist if Threat Catalogue not seeded yet
            if data.get("linked_threat") and not frappe.db.exists(
                    "GRC Threat Catalogue", data["linked_threat"]):
                data.pop("linked_threat", None)
            frappe.get_doc(data).insert(ignore_permissions=True)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Vulnerability seed failed: {v.get('vulnerability_id')}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {len(SAMPLE_VULNERABILITIES)} sample vulnerabilities")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 10 NCA Cybersecurity Domain KPIs with quarterly target/actual
# ---------------------------------------------------------------------------

NCA_KPIS = [
    (1, "Asset Management",
     "Server and Endpoint anti-virus agent installation review",
     "% of anti-virus agent installation review on servers and endpoints",
     "Quarterly", "Devices / EDR"),
    (2, "Business Continuity",
     "Business continuity plan usage in case of critical incident",
     "% of critical incidents where BCP has been activated",
     "Weekly", "Incident management system"),
    (3, "Awareness",
     "Annual training including privacy and sensitive data protection",
     "% of employees completing annual cybersecurity training",
     "Annually", "LMS / HR"),
    (4, "Event Monitoring",
     "Continuous Monitoring — critical alerts not annotated",
     "% of critical anomalies/alerts not annotated and still open past deadline",
     "By-Weekly", "SIEM / SOC dashboard"),
    (5, "Cybersecurity Assurance & Compliance",
     "Compliance — Policy reviews",
     "% of annual policy reviews completed on time",
     "Quarterly", "GRC platform / policy register"),
    (6, "Identity and Access Management",
     "PAM — Privileged accounts not monitored",
     "% of privileged accounts not monitored on a monthly basis",
     "Weekly", "PAM solution / IAM logs"),
    (7, "Network Security",
     "Firewall configuration high-criticality action items overdue",
     "% of firewall configuration high-criticality action plan items open past deadline",
     "Annually", "Firewall management / change tickets"),
    (8, "Physical Security",
     "Network devices not on latest stable security update",
     "% of network devices not utilizing the latest stable security-related updates",
     "By-Weekly", "NMS / patch management"),
    (9, "Risk Management",
     "Network devices without standard documented configuration",
     "% of network devices without a documented standard security configuration",
     "Weekly", "Configuration management database"),
    (10, "Vulnerability Management",
     "Vulnerability scan false-positive review rate",
     "% of vulnerability alerts reviewed for false positives within SLA",
     "Monthly", "Vulnerability scanner / GRC"),
]


def seed_sample_kpis():
    if not frappe.db.exists("DocType", "GRC KPI"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC KPI", {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    import random, datetime
    year = datetime.date.today().year
    for kpi_id, domain, name, definition, freq, source in NCA_KPIS:
        try:
            # Sample quarterly data — random but deterministic per KPI
            random.seed(kpi_id * 7919)
            measurement = {
                "year": year,
                "prior_year_q4_actual": round(random.uniform(0.5, 0.95), 3),
                "q1_target": round(random.uniform(0.7, 0.95), 3),
                "q1_actual": round(random.uniform(0.5, 0.95), 3),
                "q1_notes": "—",
                "q2_target": round(random.uniform(0.7, 0.95), 3),
                "q2_actual": round(random.uniform(0.5, 0.95), 3),
                "q2_notes": "—",
                "q3_target": round(random.uniform(0.7, 0.95), 3),
                "q3_actual": round(random.uniform(0.5, 0.95), 3),
                "q3_notes": "—",
                "q4_target": round(random.uniform(0.7, 0.95), 3),
                "q4_actual": round(random.uniform(0.5, 0.95), 3),
                "q4_notes": "—",
            }
            doc = frappe.get_doc({
                "doctype": "GRC KPI",
                "client": DEFAULT_CLIENT_NAME,
                "kpi_id": kpi_id,
                "indicator_name": name,
                "cybersecurity_domain": domain,
                "kpi_type": "Percentage",
                "frequency": freq,
                "kpi_definition": definition,
                "data_source": source,
                "owner_user": "Administrator",
                "measurements": [measurement],
            })
            doc.insert(ignore_permissions=True)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"KPI seed failed: {kpi_id}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {len(NCA_KPIS)} NCA KPIs with quarterly data")
    except Exception:
        pass


# ===========================================================================
# NCA Cybersecurity Toolkit Library (official templates)
# Source: https://nca.gov.sa/en/regulatory-documents/guidelines-list/cybersecurity-toolkits/
# Last NCA update: 26 November 2025
# ===========================================================================

# Format: (template_code, template_name, category, ecc_controls, word_url, pdf_url)
NCA_POLICY_LIBRARY = [
    ("NCA-POL-ORGSTRUCT", "Cybersecurity Organizational Structure", "Governance", "1-4-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/75fe27c2-c644-4c66-ab72-f7fa5e734ae9_Cybersecurity_Organizational_Structure_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/d5934a06-7bd9-4dbb-b693-47701f025c57_Cybersecurity_Organizational_Structure_Template_en.pdf"),
    ("NCA-POL-ROLES", "Cybersecurity Roles and Responsibilities", "Governance", "1-4-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/d756e6ca-1da3-4dba-9bff-28c7cfa72c32_Cybersecurity_Roles_and_Responsibilities_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ff898cdc-4363-4070-93d3-042f987bc307_Cybersecurity_Roles_and_Responsibilities_Template_en.pdf"),
    ("NCA-POL-COMMITTEE", "Cybersecurity Steering Committee Regulating Document", "Governance", "1-2-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/b44179df-ae7f-4198-817c-f15b1303b2d6_Cybersecurity_Steering_Committee_Regulating_Document_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/6b746a5a-c354-47e2-8a13-a4fb9b417d0c_Cybersecurity_Steering_Committee_Regulating_Document_Template_en-.pdf"),
    ("NCA-POL-STRATEGY", "Cybersecurity Strategy and Roadmap", "Governance", "1-1-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/5253fb82-c56c-41dd-a404-5681bbcedc09_Cybersecurity_Strategy_and_Roadmap_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ef629c5f-d128-42e4-8b3b-8ed066c52a36_Cybersecurity_Strategy_and_Roadmap_Template_en-.pdf"),
    ("NCA-POL-MALWARE", "Malware Protection Policy", "Application", "2-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/de6fec28-6828-49c6-b62a-c6bbcc7b1d47_POLICY_anti-Malware_Protection-_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/74183fb2-9c35-4983-b244-92febdbb9456_POLICY_anti-Malware_Protection-_template_en-.pdf"),
    ("NCA-POL-AUP", "Asset Acceptable Use Policy", "Asset", "2-1-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/6e13a46e-c17f-457b-9bb6-28a01306df57_POLICY_Asset_Acceptable_Use_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2b464d42-bf29-4b69-94e6-e29a13af1be2_POLICY_Asset_Acceptable_Use_Template_en-.pdf"),
    ("NCA-POL-CLOUD", "Cloud Computing and Hosting Cybersecurity Policy", "Network", "4-2-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/3d163153-0792-41bc-8e7f-03558ffcf59e_POLICY_Cloud_Computing_and_Hosting_Cybersecurity_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/5f93305c-618b-4363-b6ea-0ed3316ffc27_POLICY_Cloud_Computing_and_Hosting_Cybersecurity_template_en.pdf"),
    ("NCA-POL-COMPLIANCE", "Compliance with Cybersecurity Legislation and Regulations", "Governance", "1-7-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/26cc6771-52bb-480f-a169-c4fdea901724_POLICY_Compliance_With_Cybersecurity_Legislation_And_Regulations_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2393260a-55e0-4d9d-941d-6818a3a714c6_POLICY_Compliance_With_Cybersecurity_Legislation_And_Regulations_Template_en-.pdf"),
    ("NCA-POL-CONFIG", "Configuration and Hardening Policy", "Application", "2-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/36577da9-e084-4975-b977-8212478e33f2_POLICY_Configuration_and_Hardening_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/63794984-f69a-4b86-907c-dc465b0a7c4f_POLICY_Configuration_and_Hardening_template_en-.pdf"),
    ("NCA-POL-CORPORATE", "Corporate Cybersecurity Policy", "Governance", "1-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/ed18e6a3-87c4-4cd9-ab59-a2ecb8c12097_POLICY_Corporate-Cybersecurity-Policy_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/6db9eb86-67ab-4d22-8afe-3db6855e3994_POLICY_Corporate-Cybersecurity-Policy_template_en-.pdf"),
    ("NCA-POL-CRYPTO", "Cryptography Policy", "Data", "2-8-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/63dd5bd4-315c-4ff8-bc3b-308e030d110a_POLICY_Cryptography_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/c0617414-8544-4111-a17e-377b31c8c7d5_POLICY_Cryptography_Template_en-.pdf"),
    ("NCA-POL-BCP", "Cybersecurity Business Continuity Policy", "Resilience", "3-1-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/b3c5db63-c3d1-4149-b815-b55486284b9a_POLICY_Cybersecurity_Business_Continuity_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/01013186-c6ed-4456-8531-858de55b6130_POLICY_Cybersecurity_Business_Continuity_Template_en-.pdf"),
    ("NCA-POL-LOGGING", "Cybersecurity Event Logs and Monitoring Management Policy", "Monitoring", "2-12-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/76b535cf-3370-452d-b2c7-3aeb7cd89cc9_POLICY_Cybersecurity_Event_Logs_and_Monitoring_Management_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/8fbcbe22-ce9b-4b32-8fe7-f66a2ddcf727_POLICY_Cybersecurity_Event_Logs_and_Monitoring_Management_Template-.pdf"),
    ("NCA-POL-INCIDENT", "Cybersecurity Incident and Threat Management Policy", "Incident", "2-13-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/935c89a7-b1cb-41a0-8a73-a5334c2c2ed4_POLICY_Cybersecurity_Incident_and_Threat_Management_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/6c15978a-f6a1-4024-87b3-c7bdc16f05d0_POLICY_Cybersecurity_Incident_and_Threat_Management_Template_en-.pdf"),
    ("NCA-POL-OT", "Cybersecurity Policy for Operational Technology", "Network", "2-15-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/17721af6-a9f5-4c44-b99d-fd66d008591f_POLICY_Cybersecurity_Industrial_Controls_Systems_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/4ae174c2-06e2-4e10-ba70-4e7547b8f984_POLICY_Cybersecurity_Industrial_Controls_Systems_template_en-.pdf"),
    ("NCA-POL-AUDIT", "Cybersecurity Review and Audit Policy", "Governance", "1-8-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/155e9a9f-3b2f-43f6-b8df-4f02cbe0c129_POLICY_Cybersecurity_Review_and_Audit_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/f90b3946-77fd-48fd-ae2f-532dc121013f_POLICY_Cybersecurity_Review_and_Audit_Template_en-.pdf"),
    ("NCA-POL-RISK", "Cybersecurity Risk Management Policy", "Governance", "1-5-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/e11c0438-c801-4891-ae77-4893a79e074d_POLICY_Cybersecurity_Risk_Management_Template_en---.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/fcf4c28b-a84f-4c11-a245-63e2964f0255_POLICY_Cybersecurity_Risk_Management_Template_en---.pdf"),
    ("NCA-POL-DB", "Database Security Policy", "Application", "2-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/48d89ff1-fbd9-416d-bcea-149bfe18b9cd_POLICY_Database_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2c1bace3-0e3d-4ff1-8a2e-6eb407f6b25d_POLICY_Database_Security_template_en-.pdf"),
    ("NCA-POL-EMAIL", "Email Security Policy", "Application", "2-4-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/e85b867d-52e7-4c86-9eab-edd095f17135_POLICY_Email_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/d5c56ebf-6d5d-493f-90f4-5fc854ec28b8_POLICY_Email_Security_template_en-.pdf"),
    ("NCA-POL-HR", "Human Resources Cybersecurity Policy", "Governance", "1-9-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/05f38b0c-2405-43de-b407-79ab026999aa_POLICY_Human_Resources_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2b360ab4-cb99-4e1c-b396-27e3c70c6567_POLICY_Human_Resources_Template_en-.pdf"),
    ("NCA-POL-IAM", "Identity and Access Management Policy", "Access", "2-2-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/6c46b246-6987-474c-9262-a34427ca6b2a_POLICY_Identity_and_Access_Management_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/d6f7c6e1-dfeb-4e70-b935-fd66912508f8_POLICY_Identity_and_Access_Management_template_en-.pdf"),
    ("NCA-POL-NETWORK", "Network Security Policy", "Network", "2-5-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/81e7bd80-688b-4847-a748-56308c790469_POLICY_Network_Security_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/d0503849-c66a-4477-9ad3-ceaab7f8215e_POLICY_Network_Security_Template_en-.pdf"),
    ("NCA-POL-PATCH", "Patch Management Policy", "Vulnerability", "2-10-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/dc949d9e-b35d-44c8-97b8-9db0e6036d43_POLICY_Patch_Management_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ba218b18-e7f1-4974-bbe1-1eeb592c810c_POLICY_Patch_Management_Template_en-.pdf"),
    ("NCA-POL-PENTEST", "Penetration Testing Policy", "Vulnerability", "2-11-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/8570cb5c-155a-4baf-b4ab-75a04d026a84_POLICY_Penetration_Testing_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/04156481-aa0b-4a6a-87d1-d789c0db92df_POLICY_Penetration_Testing_Template_en-.pdf"),
    ("NCA-POL-PHYSICAL", "Physical Security Policy", "Physical", "2-14-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/ad15d841-a531-4501-9008-5e174a4accf8_POLICY_Physical_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/a89027d8-e51d-46d7-a9f8-7f6349c38479_POLICY_Physical_Security_template_en-.pdf"),
    ("NCA-POL-SERVER", "Server Security Policy", "Application", "2-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/4f00d745-c846-4350-8a53-dd41a85d4b24_POLICY_Servers_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/8d9aeb1c-ec58-4317-8a3a-bbedc3313dd3_POLICY_Servers_Security_template_en-.pdf"),
    ("NCA-POL-3RDPARTY", "Third-Party Cybersecurity Policy", "Third Party", "4-1-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/7d3a52ae-e049-4ac5-9b76-fd8184656300_POLICY_Third_Party_Cybersecurity_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/e1304ba0-3d66-42b1-925a-5783bdfd8b44_POLICY_Third_Party_Cybersecurity_template_en-.pdf"),
    ("NCA-POL-VULN", "Vulnerabilities Management Policy", "Vulnerability", "2-10-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/71502b24-f8e5-41d0-9a93-e5e28bdfee0c_POLICY_Vulnerabilities_Management_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/10c64733-9de5-48c0-9d89-9387f3e51335_POLICY_Vulnerabilities_Management_Template_en-.pdf"),
    ("NCA-POL-WEB", "Web Application Protection Policy", "Application", "2-15-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/5af246a8-a4f7-46dc-8d5e-10aa492039b0_POLICY_Web_Applications_Protection_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/52d4bea6-795a-424f-ba01-dcea8091ca03_POLICY_Web_Applications_Protection_Template_en-.pdf"),
    ("NCA-POL-BYOD", "Workstations, Mobile Devices and BYOD Security Policy", "Asset", "2-6-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/9deeab88-2bec-4516-985b-7b5ddd0cfd8b_POLICY_Workstations_and_Mobile_Devices_and_BYOD_Security_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/339a82e3-a3d2-4cde-a7d9-6cb7ae1453b8_POLICY_Workstations_and_Mobile_Devices_and_BYOD_Security_Template_en---.pdf"),
    ("NCA-POL-ASSET", "Asset Management Policy", "Asset", "2-1-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/cec508e0-b58b-45ac-8812-d53629da9c95_POLICY_Asset_Management_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/b2de0067-b6c6-426b-b3e1-cc5a27515191_POLICY_Asset_Management_template_en.pdf"),
    ("NCA-POL-BACKUP", "Backup Policy", "Resilience", "2-9-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/4e01cb6c-6456-4722-9391-54af89e75ad8_POLICY_Backup_and_Recovery_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/18f485e9-9cee-4013-b789-a60191068944_POLICY_Backup_and_Recovery_template_en.pdf"),
    ("NCA-POL-DATA", "Data Cybersecurity Policy", "Data", "2-7-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/12401718-4338-4bd1-9abd-3dfc53cf0b0a_POLICY_Data_Cybersecurity_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/a8fc8779-e215-4ef8-a457-ae7882165c7f_POLICY_Data_Cybersecurity_template_en.pdf"),
    ("NCA-POL-SSDLC", "Secure Systems Development Life Cycle Policy", "Application", "1-6-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/87fec17d-8def-4b82-9f3e-73440aedc3be_Policy_SSDLC_Policy_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/5f87a811-756f-4a0d-bf05-9d001fc3c038_Policy_SSDLC_Policy_template_en-.pdf"),
    ("NCA-POL-STORAGE", "Storage Media Security Policy", "Data", "2-1-5",
     "https://cdn.nca.gov.sa/api/files/public/upload/8b02f6e8-7224-4a95-bcf0-98e3a92d52a1_POLICY_Storage_Media_Policy_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2d8f01ee-ec8f-4b95-9aa0-b7373fffbcfc_POLICY_Storage_Media_Policy_Template_en-.pdf"),
]


def seed_nca_policy_library():
    if not frappe.db.exists("DocType", "GRC NCA Policy Library"):
        return
    if frappe.db.count("GRC NCA Policy Library") > 0:
        return
    inserted = 0
    for code, name, cat, ecc, word_url, pdf_url in NCA_POLICY_LIBRARY:
        try:
            frappe.get_doc({
                "doctype": "GRC NCA Policy Library",
                "template_code": code,
                "template_name": name,
                "kind": "Policy",
                "category": cat,
                "ecc_controls": ecc,
                "official_word_url": word_url,
                "official_pdf_url": pdf_url,
                "is_active": 1,
                "version": "Latest (NCA)",
            }).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"NCA Policy seed failed: {code}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {inserted} NCA policy templates")
    except Exception:
        pass


NCA_STANDARD_LIBRARY = [
    ("NCA-STD-CRYPTO", "Cryptography Standard", "Cryptography", "2-8-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/9fa5e94f-debf-4baa-8a7a-997a12ddac59_STANDARD_Cryptography_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/e6e85d58-3ba7-4a71-93b2-438d08b737e2_STANDARD_Cryptography_Template_en--.pdf"),
    ("NCA-STD-LOGGING", "Cybersecurity Event Logs and Monitoring Management Standard", "Monitoring", "2-12-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/4855cc4d-c2bd-4e1b-8113-775bec6f28c2_STANDARD_Cybersecurity_Event_Logs_and_Monitoring_Management_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2882e50b-e185-4df0-ab36-4d3feadc23ee_STANDARD_Cybersecurity_Event_Logs_and_Monitoring_Management_Template_en-.pdf"),
    ("NCA-STD-DB", "Database Security Standard", "Database", "2-3-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/903fa416-c1e4-4259-a43a-f9d629c1a4ed_STANDARD_Database_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/95bf1aeb-2c06-4801-96f3-c23b355e2ec2_STANDARD_Database_Security_template_en-.pdf"),
    ("NCA-STD-EMAIL", "Email Protection Standard", "Email", "2-4-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/2ced0e86-0973-4d08-8dcf-979059cc22b2_STANDARD_Email_Protection_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/aebe48b6-6a6a-4d00-814d-7f41e1d39f9e_STANDARD_Email_Protection_template_en-.pdf"),
    ("NCA-STD-MALWARE", "Malware Protection Standard", "Malware", "2-3-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/14dfb3a3-903a-474c-ab02-ea6c80257558_STANDARD_Malware_Protection_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/14dfb3a3-903a-474c-ab02-ea6c80257558_STANDARD_Malware_Protection_template_en-.docx"),
    ("NCA-STD-MOBILE", "Mobile Devices Security Standard", "Mobile", "2-6-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/ff83bf1a-0838-462a-86b5-af40a22c8740_STANDARD_Mobile_Devices_Security_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/1861a422-d529-4e4c-bba3-a5255b98b500_STANDARD_Mobile_Devices_Security_Template_en.pdf"),
    ("NCA-STD-NETWORK", "Network Security Standard", "Network", "2-5-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/c22d675a-3083-4949-9e97-2d51e850541c_STANDARD_Network_Security_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/d5f821da-0d18-4b35-809f-2072f707cc6f_STANDARD_Network_Security_Template_en.pdf"),
    ("NCA-STD-PENTEST", "Penetration Testing Standard", "Penetration Testing", "2-11-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/edd01292-50a9-46a6-9cd8-6ebd6b160ae0_STANDARD_Penetration_Testing_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/3a098671-bd77-4d76-a24d-7518ae9ac953_STANDARD_Penetration_Testing_Template_en-.pdf"),
    ("NCA-STD-CODING", "Secure Coding Standard Controls", "Secure Coding", "1-6-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/a8dea67a-34ce-4c62-8070-5f810a5bcb29_Standard_Secure_Coding_standrd-controls_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ccea5a8c-a237-4fb8-be67-8e6e8d9dc12f_Standard_Secure_Coding_standrd-controls_Template_en-.pdf"),
    ("NCA-STD-SERVER", "Server Security Standard", "Server", "2-3-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/b3dab602-d426-4572-999b-99533958fdeb_STANDARD_Servers_Security_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ce6504dc-2d0e-41c4-aea4-eaf8d9adc6c3_STANDARD_Servers_Security_template_en-.pdf"),
    ("NCA-STD-VULN", "Vulnerabilities Management Standard", "Vulnerability", "2-10-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/4fed4b5a-2a1e-4298-843d-1b81455d5f10_STANDARD_Vulnerabilities_Management_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ec648325-97f2-41f0-aca6-c3a49a323af8_STANDARD_Vulnerabilities_Management_Template_en-.pdf"),
    ("NCA-STD-WIFI", "Wireless Network Security Standard", "Wireless", "2-5-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/9d806546-c42b-4f82-8806-1045c3719698_Standard_Wireless_Network_Security_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/eaafcc77-aff6-4663-a7cd-4f498138d68b_Standard_Wireless_Network_Security_Template_en-.pdf"),
    ("NCA-STD-WORKSTATION", "Workstation Security Standard", "Workstation", "2-6-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/706944d0-17c1-4589-9305-ea808ac25567_Standard_Workstations_Security_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/9fa10b76-7729-41bd-835c-b63f26f7ce53_Standard_Workstations_Security_Template_en-.pdf"),
    ("NCA-STD-APT", "Advanced Persistent Threats (APT) Standard", "APT", "2-13-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/1e7590d4-1bcf-424d-ad48-aa9861aa18f4_STANDARD_APT-Standard_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/bd3a0e0e-491f-475b-b62a-7dc8a305c011_STANDARD_APT-Standard_Template_en.pdf"),
    ("NCA-STD-ASSETCLASS", "Asset Classification Standard", "Asset", "2-1-5",
     "https://cdn.nca.gov.sa/api/files/public/upload/1bf71b5c-e8f4-4197-8113-fcef2eeadad5_STANDARD_Asset_Classification_template_en_.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/782a31b7-422d-40fc-a439-34cb8db88de3_STANDARD_Asset_Classification_template_en_-.pdf"),
    ("NCA-STD-ASSET", "Asset Management Standard", "Asset", "2-1-2",
     "https://cdn.nca.gov.sa/api/files/public/upload/24fe68ab-d0ec-4cd9-a073-e7a3cb0e03f0_STANDARD_Asset_Management_template_en_v0.3.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/37b3e9ee-350d-4565-a88c-5b0e6f3a96f6_STANDARD_Asset_Management_template_en_v0.3-.pdf"),
    ("NCA-STD-BACKUP", "Backup Standard", "Backup", "2-9-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/ff672df1-aba2-443d-9bf6-dbdca8f59b87_STANDARD_Backup_and_Recovery_template_en_v0.3-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/f9fb4ebd-9949-4888-8c1a-419786857fb5_STANDARD_Backup_and_Recovery_template_en_v0.3.pdf"),
    ("NCA-STD-DIODE", "Data Diode Standard", "Data Diode", "2-15-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/f31dde1a-02fc-4692-a602-baf3002b5818_Standard_Data-Diode-Standard_Template_en_.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/75692e52-f16b-4504-9c61-741ee3e969c0_Standard_Data-Diode-Standard_Template_en.pdf"),
    ("NCA-STD-DLP", "Data Loss Prevention Standard", "DLP", "2-7-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/6bb9b11d-2f0c-4671-8f98-074135e0e6cc_STANDARD_Data-Loss-Prevention_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/a40c292f-a88b-40df-bf59-388ac289684a_STANDARD_Data-Loss-Prevention_template_en-.pdf"),
    ("NCA-STD-DATA", "Data Cybersecurity Standard", "Data Cybersecurity", "2-7-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/112576bf-00f7-4785-9c0e-291c8a3b9a82_Standard_Data-Protection_template_en_-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/f99d5678-09dd-4a20-bf4f-c1269d6b2b96_Standard_Data-Protection_template_en_-.pdf"),
    ("NCA-STD-DDOS", "DDoS Protection Standard", "DDoS", "2-5-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/c4c3a94a-93a3-4ba3-bf0c-b846a2275eab_STANDARD_DDoS-Protection-Standard_Template_en_-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/172d3cb6-2297-48eb-a368-7b5560de2d39_STANDARD_DDoS-Protection-Standard_Template_en_.pdf"),
    ("NCA-STD-EDR", "Endpoint Detection and Response Standard", "EDR", "2-13-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/3f1d28cd-ecb5-4c15-994e-5d75f1a9c1eb_Standard_EDR_Template_en_-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/e0790c91-e283-4349-995b-eca0639bb989_Standard_EDR_Template_en_.pdf"),
    ("NCA-STD-IAM", "Identity and Access Management Standard", "IAM", "2-2-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/112e5725-39e6-4e54-b365-c60e4bccbabf_STANDARD_Identity-and-Access-Management_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/51974456-adb3-4450-bea7-419643e32442_STANDARD_Identity-and-Access-Management_template_en-.pdf"),
    ("NCA-STD-KMS", "Key Management Standard", "Key Management", "2-8-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/3106f4e0-8281-4077-b118-4fd0bb2eef36_Standard_Key-management-standard_template_en--.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/cb0be657-a82d-4eee-a93f-0c5f1eb380e2_Standard_Key-management-standard_template_en_-.pdf"),
    ("NCA-STD-NDR", "Network Detection and Response Standard", "NDR", "2-13-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/179f2255-b6cf-4624-99d8-ddf53882c475_Standard_NDR_Template_en_v0.9-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/a0a76969-c3a1-4c43-acd7-4e5d85194817_Standard_NDR_Template_en_v0.9-.pdf"),
    ("NCA-STD-OTICS", "OT/ICS Security Standard", "OT/ICS", "2-15-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/e69fe0ce-6068-49c9-b2ec-dce68f3b85db_Standard_OT-ICS-Security-Standard_Template_en--.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/6a87b8ae-2301-4094-87fe-da894c2853b6_Standard_OT-ICS-Security-Standard_Template_en--.pdf"),
    ("NCA-STD-PATCH", "Patch Management Standard", "Patch Management", "2-10-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/dbde1742-7ed7-40da-9be2-f24593475eeb_STANDARD_Patch_Management_Template_en_-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/6dbdd8f1-11e7-457b-8934-7fb9939cdaa7_STANDARD_Patch_Management_Template_en.pdf"),
    ("NCA-STD-PHYSICAL", "Physical Security Standard", "Physical", "2-14-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/17bfddb3-83e0-44d5-b6bb-247be6b22f75_STANDARD_Physical-Security_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/97c09b56-d650-45a3-adc7-49882ce5fc59_STANDARD_Physical-Security_template_en-.pdf"),
    ("NCA-STD-PAW", "Privileged Access Workstations Standard", "Privileged Access", "2-2-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/2e241035-7b5c-465c-a152-813d1a4cced4_Standard_Privileged-Access-Workstation_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/5e05d8ba-fb15-4819-af33-e953355d48ba_Standard_Privileged-Access-Workstation_Template_en_.pdf"),
    ("NCA-STD-PROXY", "Proxy Security Standard", "Proxy", "2-5-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/cc25ad41-4f5c-4460-9d1b-10d88e18e1e7_Standard_Proxy_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/906a8d4a-631f-457e-9cad-02e1178c13d1_Standard_Proxy_template_en-.pdf"),
    ("NCA-STD-CONFIG", "Secure Configuration and Hardening Standard", "Secure Configuration", "2-3-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/2b8b839f-e16c-4dac-a229-e2d02b3f4a73_STANDARD_Secure-Configuration-and-Hardening_template_en_v0.3-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/287a01f6-9d37-4331-9cde-99144a394ce8_STANDARD_Secure-Configuration-and-Hardening_template_en-.pdf"),
    ("NCA-STD-SOCIAL", "Social Media Security Standard", "Social Media", "1-9-4",
     "https://cdn.nca.gov.sa/api/files/public/upload/88a94095-7029-49c7-98db-edf3a7d3753d_STANDARD_Social-Media-Security-Standard_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/333b5368-ea76-4b93-a08d-43c7b9f0302d_STANDARD_Social-Media-Security-Standard_Template_en.pdf"),
    ("NCA-STD-VIRT", "Virtualization Security Standard", "Virtualization", "2-3-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/721ab35b-c6ed-46b7-a965-47edc1662a27_STANDARD_Virtualization_Security_Template_en_.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/8c17c1bc-5a28-40f5-bbd7-f3ef5e7519de_STANDARD_Virtualization_Security_Template_en_.pdf"),
    ("NCA-STD-WEB", "Web Application Security Standard", "Web Application", "2-15-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/3f135dd2-9295-4726-980a-80485931823a_Standard_Web_Applications_Protection_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/9cea9ea5-fa62-41ce-9e57-eec0342379a0_Standard_Web_Applications_Protection_Template_en-.pdf"),
]


def seed_nca_standard_library():
    if not frappe.db.exists("DocType", "GRC NCA Standard Library"):
        return
    if frappe.db.count("GRC NCA Standard Library") > 0:
        return
    inserted = 0
    for code, name, cat, ecc, word_url, pdf_url in NCA_STANDARD_LIBRARY:
        try:
            frappe.get_doc({
                "doctype": "GRC NCA Standard Library",
                "template_code": code,
                "template_name": name,
                "kind": "Standard",
                "category": cat,
                "ecc_controls": ecc,
                "official_word_url": word_url,
                "official_pdf_url": pdf_url,
                "is_active": 1,
                "version": "Latest (NCA)",
            }).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"NCA Standard seed failed: {code}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {inserted} NCA standard templates")
    except Exception:
        pass


NCA_PROCEDURE_LIBRARY = [
    ("NCA-PROC-VULN", "Vulnerability Assessment Procedure", "Vulnerability", "2-10-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/437554e4-c625-4191-bb3f-dd3dd3d92f95_PROCEDURE_Vulnerability-Management-Procedure_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/2460b86b-9ded-42f8-8615-773d13122c24_PROCEDURE_Vulnerability-Management-Procedure_Template_en.pdf"),
    ("NCA-PROC-AUDIT", "Cybersecurity Audit Procedure", "Audit", "1-8-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/a0f6d03e-4cd1-46ef-b42a-117937b7f83c_Procedure_Cybersecurity-Audit_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/f15885f7-fb9d-4dd9-8422-2461cdd46c58_Procedure_Cybersecurity-Audit_Template_en_.pdf"),
    ("NCA-PROC-DOCDEV", "Procedure for Development of Cybersecurity Documents", "Document Development", "1-3-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/038067bb-b4e8-4423-99ff-f1db183a007f_PROCEDURE_Cybersecurity-Document-Development-Procedure_Template.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/251fb354-37c7-49dc-82a9-6ba984bdc364_PROCEDURE_Cybersecurity-Document-Development-Procedure_Template_en.pdf"),
    ("NCA-PROC-RISK", "Cybersecurity Risk Management Procedure", "Risk Management", "1-5-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/36273a80-4b60-4cf0-8085-d198d79e4c4b_Procedure_Cybersecurity-risk-management_template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/b1d4e028-9d86-4d78-a498-e18e2a562e64_Procedure_Cybersecurity-risk-management_template_en_-.pdf"),
]


def seed_nca_procedure_library():
    if not frappe.db.exists("DocType", "GRC NCA Procedure Library"):
        return
    if frappe.db.count("GRC NCA Procedure Library") > 0:
        return
    for code, name, cat, ecc, word_url, pdf_url in NCA_PROCEDURE_LIBRARY:
        try:
            frappe.get_doc({
                "doctype": "GRC NCA Procedure Library",
                "template_code": code,
                "template_name": name,
                "kind": "Procedure",
                "category": cat,
                "ecc_controls": ecc,
                "official_word_url": word_url,
                "official_pdf_url": pdf_url,
                "is_active": 1,
                "version": "Latest (NCA)",
            }).insert(ignore_permissions=True)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"NCA Procedure seed failed: {code}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {len(NCA_PROCEDURE_LIBRARY)} NCA procedure templates")
    except Exception:
        pass


NCA_FORM_LIBRARY = [
    ("NCA-FORM-NDA", "Confidentiality Agreement", "Confidentiality Agreement", "1-9-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/3c45c898-6646-40a8-841c-7dbce0de489e_Form_Confidentiality-Agreement_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/b6ff8838-e5cc-4cb5-b094-d3d6d34e6e8c_Form_Confidentiality-Agreement_Template_en.pdf"),
    ("NCA-FORM-UNDERTAKING", "Cybersecurity Policies Undertaking Form", "Policy Undertaking", "1-9-4",
     "https://cdn.nca.gov.sa/api/files/public/upload/fe3555cd-4e27-492c-bd4f-47b25bfd08bc_Form_Policy-Undertaking_Template.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/cee056c6-f796-4c53-8293-fbd19d9e631e_Form_Policy-Undertaking_Template.pdf"),
    ("NCA-FORM-CHECKLIST-IT", "Cybersecurity Requirements Checklist for IT Projects and Change Management", "Checklist", "1-6-1",
     "https://cdn.nca.gov.sa/api/files/public/upload/ccd89457-ce3a-497f-96d3-2a1ce8bc09b7_Checklist_Cybersecurity-Requirements-in-IT-Projects-and-Change-Management_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/270d5330-ecea-4047-9458-b062189d3ec2_Checklist_Cybersecurity-Requirements-in-IT-Projects-and-Change-Management_template_en.pdf"),
    ("NCA-FORM-CHECKLIST-DEV", "Cybersecurity Requirements Checklist for Software Development", "Checklist", "1-6-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/1f713964-3cae-4269-8dd9-534a024c7195_Checklist_Cybersecurity-Requirements-in-Software-Development_template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/43c50545-de13-4fd9-a484-7cb81194d327_Checklist_Cybersecurity-Requirements-in-Software-Development_template_en-.pdf"),
    ("NCA-FORM-AWARENESS", "Cybersecurity Awareness Program", "Program", "1-10-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/c3ed1d6c-e985-4f59-8fbf-3a4f15a342ce_PROGRAM_Cybersecurity-Awareness-Program_Template_en.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/ba49811b-cdc0-4ff6-b4f2-535764de5988_PROGRAM_Cybersecurity-Awareness-Program_Template_en_.pdf"),
    ("NCA-FORM-AUDITREPORT", "Cybersecurity Audit Report", "Report Template", "1-8-3",
     "https://cdn.nca.gov.sa/api/files/public/upload/ec67b96f-b31b-427b-aeed-64090218a63c_Report_Cybersecurity-Audit_Template_en-.docx",
     "https://cdn.nca.gov.sa/api/files/public/upload/e35007c4-519d-4c61-bede-798c001f1971_Report_Cybersecurity-Audit_Template_en_-.pdf"),
]


def seed_nca_form_library():
    if not frappe.db.exists("DocType", "GRC NCA Form Library"):
        return
    if frappe.db.count("GRC NCA Form Library") > 0:
        return
    for code, name, cat, ecc, word_url, pdf_url in NCA_FORM_LIBRARY:
        try:
            frappe.get_doc({
                "doctype": "GRC NCA Form Library",
                "template_code": code,
                "template_name": name,
                "kind": "Form",
                "category": cat,
                "ecc_controls": ecc,
                "official_word_url": word_url,
                "official_pdf_url": pdf_url,
                "is_active": 1,
                "version": "Latest (NCA)",
            }).insert(ignore_permissions=True)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"NCA Form seed failed: {code}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.0: Seeded {len(NCA_FORM_LIBRARY)} NCA form/governance templates")
    except Exception:
        pass


# ===========================================================================
# v1.4.3 — Aramco CCC seeders
# ===========================================================================

# 14 SACS-002 domains × 2 placeholder controls each = 28 starter controls.
# Each is_placeholder=True so it's clear these need replacement with real
# SACS-002 text once you provide the licensed document.
SACS002_PLACEHOLDER_CONTROLS = [
    # Asset Management
    ("SACS-AM-01", "Information asset inventory", "Asset Management",
     "Inventory & Classification",
     "Maintain an inventory of all information assets in scope, classified by criticality."),
    ("SACS-AM-02", "Asset ownership assignment", "Asset Management",
     "Inventory & Classification",
     "Each asset must have an assigned owner accountable for security."),
    # Access Control
    ("SACS-AC-01", "User access provisioning", "Access Control",
     "Identity Lifecycle",
     "Formal user access provisioning process based on role and need-to-know."),
    ("SACS-AC-02", "Privileged access management", "Access Control",
     "Privileged Access",
     "Privileged accounts must use MFA, session recording, and just-in-time access where feasible."),
    # Cryptography
    ("SACS-CR-01", "Cryptographic key management", "Cryptography",
     "Key Management",
     "Documented key management procedures covering generation, storage, rotation, retirement."),
    ("SACS-CR-02", "Encryption in transit and at rest", "Cryptography",
     "Encryption",
     "Data classified Confidential and above must be encrypted in transit and at rest."),
    # Physical Security
    ("SACS-PS-01", "Physical access controls", "Physical Security",
     "Facility Security",
     "Physical access to facilities housing Aramco data must be controlled and logged."),
    ("SACS-PS-02", "Equipment disposal", "Physical Security",
     "Media Sanitization",
     "Equipment disposal must follow secure media sanitization procedures."),
    # Operations Security
    ("SACS-OS-01", "Operational change management", "Operations Security",
     "Change Management",
     "Formal change management process with approval gates and rollback procedures."),
    ("SACS-OS-02", "Patch management", "Operations Security",
     "Vulnerability Management",
     "Critical patches deployed within defined SLA based on CVSS score."),
    # Communications Security
    ("SACS-CM-01", "Network segmentation", "Communications Security",
     "Network Architecture",
     "Network segmentation between trust zones, with documented data flows."),
    ("SACS-CM-02", "Secure data transfer", "Communications Security",
     "Data Transfer",
     "All external data transfer with Aramco must use approved secure channels."),
    # System Acquisition Development
    ("SACS-SD-01", "Secure SDLC", "System Acquisition Development",
     "Secure Development",
     "Documented secure development lifecycle covering requirements, design, code, test, deploy."),
    ("SACS-SD-02", "Vulnerability testing", "System Acquisition Development",
     "Testing",
     "Pre-production vulnerability scans and remediation before deployment."),
    # Supplier Relationships (sub-suppliers)
    ("SACS-SR-01", "Sub-supplier risk assessment", "Supplier Relationships",
     "Sub-Supplier Management",
     "Risk-assess your own suppliers handling Aramco data; flow down CCC requirements."),
    ("SACS-SR-02", "Sub-supplier contract requirements", "Supplier Relationships",
     "Contracts",
     "Sub-supplier contracts must include cybersecurity, audit, and incident notification clauses."),
    # Incident Management
    ("SACS-IM-01", "Incident detection capability", "Incident Management",
     "Detection",
     "24x7 incident detection and triage capability covering Aramco-scope systems."),
    ("SACS-IM-02", "Aramco incident notification", "Incident Management",
     "Notification",
     "Aramco notified within 4 hours of confirmed incident affecting Aramco scope."),
    # Business Continuity
    ("SACS-BC-01", "Business continuity plan", "Business Continuity",
     "BCP",
     "Documented BCP covering Aramco services with defined RTO/RPO."),
    ("SACS-BC-02", "BCP testing", "Business Continuity",
     "Testing",
     "Annual BCP exercise documenting findings and improvements."),
    # Compliance
    ("SACS-CP-01", "Regulatory compliance register", "Compliance",
     "Regulatory",
     "Maintain register of all applicable cybersecurity laws and Aramco contractual requirements."),
    ("SACS-CP-02", "Internal cybersecurity audit", "Compliance",
     "Internal Audit",
     "Annual internal cybersecurity audit with findings reported to senior management."),
    # Human Resources Security
    ("SACS-HR-01", "Background screening", "Human Resources Security",
     "Pre-Employment",
     "Background screening for personnel with access to Aramco data, per local law."),
    ("SACS-HR-02", "Termination procedures", "Human Resources Security",
     "Off-boarding",
     "Documented procedures to revoke access immediately upon termination."),
    # Awareness & Training
    ("SACS-AT-01", "Cybersecurity awareness program", "Awareness & Training",
     "Awareness",
     "Annual cybersecurity awareness training for all personnel with Aramco data access."),
    ("SACS-AT-02", "Role-specific security training", "Awareness & Training",
     "Specialized Training",
     "Role-specific security training (developers, admins, executives)."),
    # Governance
    ("SACS-GV-01", "Cybersecurity governance committee", "Governance",
     "Oversight",
     "Senior governance body overseeing cybersecurity programme."),
    ("SACS-GV-02", "Cybersecurity policy framework", "Governance",
     "Policy",
     "Documented and approved cybersecurity policies aligned to SACS-002."),
]


def seed_aramco_sacs002_controls():
    """Seed SACS-002 placeholder control library — 28 controls across 14
    domains. Each marked is_placeholder=True so they can be batch-replaced
    once the licensed Aramco SACS-002 PDF is imported."""
    if not frappe.db.exists("DocType", "GRC Aramco SACS002 Control"):
        return
    if frappe.db.count("GRC Aramco SACS002 Control") > 0:
        return
    inserted = 0
    for code, title, domain, sub, req in SACS002_PLACEHOLDER_CONTROLS:
        try:
            frappe.get_doc({
                "doctype": "GRC Aramco SACS002 Control",
                "control_id": code,
                "control_title": title,
                "domain": domain,
                "sub_domain": sub,
                "applicability_tier": "All Tiers",
                "is_placeholder": 1,
                "requirement_text": req,
                "is_active": 1,
                "source_version": "Public summary (placeholder)",
            }).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"SACS-002 seed failed: {code}")
            except Exception:
                pass
    try:
        frappe.logger().info(
            f"AlphaX GRC v1.4.3: Seeded {inserted} SACS-002 placeholder controls "
            "(replace with verbatim text once licensed SACS-002 PDF is imported)")
    except Exception:
        pass


# Audit firm placeholders — VERIFY ACCREDITATION with Aramco SCM before use
AUDIT_FIRM_PLACEHOLDERS = [
    ("ACCFIRM-PLACEHOLDER-01",
     "(Add accredited firm here)",
     "Saudi Arabia",
     "Replace this placeholder with actual accredited firms from Aramco SCM list."),
]


def seed_aramco_audit_firms():
    if not frappe.db.exists("DocType", "GRC Aramco Audit Firm"):
        return
    if frappe.db.count("GRC Aramco Audit Firm") > 0:
        return
    for code, name, country, notes in AUDIT_FIRM_PLACEHOLDERS:
        try:
            frappe.get_doc({
                "doctype": "GRC Aramco Audit Firm",
                "firm_code": code,
                "firm_name": name,
                "country": country,
                "accreditation_status": "Unverified",
                "is_active": 1,
                "internal_notes": notes,
            }).insert(ignore_permissions=True)
        except Exception:
            pass
    try:
        frappe.logger().info("AlphaX GRC v1.4.3: Seeded Aramco audit firm placeholders")
    except Exception:
        pass


def seed_sample_aramco_certificate():
    """Demo certificate so the dashboard isn't empty on fresh install.
    Tied to DEMO client; expires in 60 days so it triggers the 90-day alert."""
    if not frappe.db.exists("DocType", "GRC Aramco Certificate"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC Aramco Certificate",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    from datetime import date, timedelta
    today_d = date.today()
    try:
        frappe.get_doc({
            "doctype": "GRC Aramco Certificate",
            "client": DEFAULT_CLIENT_NAME,
            "certificate_number": "DEMO-CCC-2025-001",
            "issue_date": today_d - timedelta(days=305),
            "expiry_date": today_d + timedelta(days=60),
            "service_class_tier": "High",
            "certified_scope": "Sample scope — certified for cybersecurity controls under SACS-002 covering "
                               "managed services to Aramco refinery operations.",
            "status": "Active",
        }).insert(ignore_permissions=True)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "seed_sample_aramco_certificate failed")
        except Exception:
            pass


def seed_sample_ccc_engagement():
    """Demo engagement so the dashboard has data on fresh install."""
    if not frappe.db.exists("DocType", "GRC Aramco CCC Engagement"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return
    if frappe.db.count("GRC Aramco CCC Engagement",
                       {"client": DEFAULT_CLIENT_NAME}) > 0:
        return
    from datetime import date, timedelta
    today_d = date.today()
    try:
        eng = frappe.get_doc({
            "doctype": "GRC Aramco CCC Engagement",
            "client": DEFAULT_CLIENT_NAME,
            "engagement_title": "Sample CCC Engagement — Managed Services Vendor",
            "engagement_status": "Self-Assessment",
            "service_class_tier": "High",
            "lead_consultant": "Administrator",
            "in_scope_services": "Network connectivity, Critical data processor, Customised software",
            "scope_summary": ("Sample engagement to demonstrate the CCC lifecycle. "
                              "Replace with real engagements via /app/grc-aramco-ccc-engagement/new."),
            "kickoff_date": today_d - timedelta(days=30),
            "self_assessment_due_date": today_d + timedelta(days=60),
        })
        eng.insert(ignore_permissions=True)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "seed_sample_ccc_engagement failed")
        except Exception:
            pass


# ===========================================================================
# v1.5.0 — ECC-2:2024 master catalog seeder
# ===========================================================================

def seed_ecc2_2024_catalog():
    """Seed the GRC NCA ECC2 Catalog from the bundled fixture file
    (data/ecc2_2024_catalog.json — 198 controls extracted from the official
    NCA GECC-2024 spreadsheet)."""
    if not frappe.db.exists("DocType", "GRC NCA ECC2 Catalog"):
        return
    if frappe.db.count("GRC NCA ECC2 Catalog") > 0:
        return  # idempotent

    import os, json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data", "ecc2_2024_catalog.json")
    if not os.path.exists(fixture_path):
        try:
            frappe.log_error(
                f"ECC-2:2024 fixture not found at {fixture_path}",
                "v1.5.0 seed_ecc2_2024_catalog"
            )
        except Exception:
            pass
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load ECC-2:2024 fixture")
        except Exception:
            pass
        return

    inserted = 0
    failed = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC NCA ECC2 Catalog"
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            failed += 1
            try:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"ECC-2:2024 catalog seed failed: {entry.get('control_code')}"
                )
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.5.0: Seeded ECC-2:2024 catalog — "
            f"{inserted} controls inserted, {failed} failed."
        )
    except Exception:
        pass


# ===========================================================================
# v1.7.0 — ISO 42001 catalog seeder
# ===========================================================================

def seed_iso42001_catalog():
    """Seed the GRC ISO42001 Catalog from the bundled fixture file (38 controls
    across 9 domains — A.2 through A.10)."""
    if not frappe.db.exists("DocType", "GRC ISO42001 Catalog"):
        return
    if frappe.db.count("GRC ISO42001 Catalog") > 0:
        return  # idempotent

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "iso42001_catalog.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load ISO 42001 fixture")
        except Exception:
            pass
        return

    inserted = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC ISO42001 Catalog"
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"ISO 42001 seed failed: "
                                 f"{entry.get('control_code')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.7.0: Seeded ISO 42001 catalog — "
            f"{inserted} of {len(entries)} controls.")
    except Exception:
        pass


# ===========================================================================
# v1.7.0 — Sample evidence rules (continuous control monitoring)
# ===========================================================================

SAMPLE_EVIDENCE_RULES = [
    {
        "rule_name": "HR Offboarding — Access Revoked Within 1 Day",
        "framework": "NCA ECC-2:2024",
        "control_reference": "1-9-3-1",
        "rule_priority": "High",
        "source_doctype": "Employee",
        "source_filters": '{"status": "Left"}',
        "evaluation_type": "Field Must Be Within Days",
        "field_to_check": "relieving_date",
        "tolerance_days": 1,
        "auto_create_finding": 1,
        "finding_severity": "High",
        "evaluate_on_save": 1,
        "evaluate_daily": 1,
        "description": "When an employee leaves, the relieving date must be set "
                       "within 1 day of separation. Maps to NCA ECC 1-9-3-1 "
                       "(HR offboarding cybersecurity).",
    },
    {
        "rule_name": "Vendor Master — Active Suppliers Have Cybersecurity Review",
        "framework": "NCA ECC-2:2024",
        "control_reference": "4-1-2",
        "rule_priority": "High",
        "source_doctype": "Supplier",
        "source_filters": '{"disabled": 0}',
        "evaluation_type": "Field Must Be Set",
        "field_to_check": "supplier_group",
        "auto_create_finding": 1,
        "finding_severity": "Medium",
        "evaluate_on_save": 1,
        "evaluate_daily": 1,
        "description": "All active suppliers must have a supplier_group set so "
                       "they can be filtered into the GRC vendor cybersecurity "
                       "review queue. Maps to NCA ECC 4-1-2 (third-party "
                       "cybersecurity review).",
    },
    {
        "rule_name": "Asset Register — All Assets Have Custodian Assigned",
        "framework": "NCA ECC-2:2024",
        "control_reference": "2-1-1",
        "rule_priority": "Medium",
        "source_doctype": "Asset",
        "source_filters": '{"status": "In Use"}',
        "evaluation_type": "Field Must Be Set",
        "field_to_check": "custodian",
        "auto_create_finding": 1,
        "finding_severity": "Medium",
        "evaluate_on_save": 1,
        "evaluate_daily": 1,
        "description": "Every in-use asset must have a custodian assigned. "
                       "Maps to NCA ECC 2-1-1 (asset management).",
    },
    {
        "rule_name": "Sales Invoice — Approval Workflow Status",
        "framework": "NCA ECC-2:2024",
        "control_reference": "1-3-1",
        "rule_priority": "Medium",
        "source_doctype": "Sales Invoice",
        "source_filters": '{"docstatus": 1}',
        "evaluation_type": "Field Must Be Set",
        "field_to_check": "owner",
        "auto_create_finding": 0,
        "finding_severity": "Low",
        "evaluate_on_save": 0,
        "evaluate_daily": 1,
        "description": "All submitted sales invoices must have an attributable "
                       "owner field for audit traceability. Demonstrative rule — "
                       "in production, replace with workflow-state checks.",
    },
    {
        "rule_name": "User Records — Disabled Users Have No Active Permissions",
        "framework": "NCA ECC-2:2024",
        "control_reference": "2-2-3",
        "rule_priority": "High",
        "source_doctype": "User",
        "source_filters": '{"enabled": 0}',
        "evaluation_type": "Field Must Equal Value",
        "field_to_check": "enabled",
        "expected_value": "0",
        "auto_create_finding": 1,
        "finding_severity": "Medium",
        "evaluate_on_save": 1,
        "evaluate_daily": 1,
        "description": "Disabled User records must remain disabled. Real-time "
                       "monitoring catches anyone re-enabling a disabled account "
                       "outside the formal access-grant procedure. Maps to NCA "
                       "ECC 2-2-3 (privileged-access management).",
    },
    {
        "rule_name": "ISO 42001 — AI Policy Document Must Exist",
        "framework": "ISO 42001",
        "control_reference": "A.2.2",
        "rule_priority": "High",
        "source_doctype": "GRC ISO42001 Control",
        "source_filters": '{"control_code": "A.2.2", "compliance_status": "Implemented"}',
        "evaluation_type": "Minimum Record Count",
        "min_required_count": 1,
        "auto_create_finding": 1,
        "finding_severity": "High",
        "evaluate_on_save": 1,
        "evaluate_daily": 1,
        "description": "Every client adopting ISO 42001 must have control A.2.2 "
                       "(AI Policy) marked Implemented before the AIMS audit. "
                       "Self-referential rule — checks that the GRC system "
                       "itself records implementation of the foundational AI "
                       "policy control.",
    },
]


def seed_sample_evidence_rules():
    """Seed 6 sample Evidence Rules covering common NCA + ISO 42001 controls
    that map to ERPNext data. Idempotent."""
    if not frappe.db.exists("DocType", "GRC Evidence Rule"):
        return
    if frappe.db.count("GRC Evidence Rule") > 0:
        return  # idempotent — admin may have already created their own rules

    inserted = 0
    for rule in SAMPLE_EVIDENCE_RULES:
        try:
            doc = dict(rule)
            doc["doctype"] = "GRC Evidence Rule"
            doc["is_active"] = 1
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Sample rule seed failed: {rule.get('rule_name')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.7.0: Seeded {inserted} sample Evidence Rules.")
    except Exception:
        pass


# ===========================================================================
# v1.7.0 — Branded print format seeder wrapper
# ===========================================================================

def seed_branded_print_formats():
    """Delegate to the print_format module seeder."""
    try:
        from alphax_grc.alphax_grc.print_format.grc_branded_seeder import (
            seed_branded_print_formats as _seed
        )
        _seed()
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC v1.7.0 print format seed wrapper failed")
        except Exception:
            pass


# ===========================================================================
# v1.8.0 — Engagement Phase Templates
# ===========================================================================

def seed_engagement_phase_templates():
    """Seed the engagement phase templates fixture (Standard NCA + Aramco CCC).
    Idempotent — only inserts missing templates."""
    if not frappe.db.exists("DocType", "GRC Engagement Phase Template"):
        return

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "engagement_phase_templates.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load engagement phase templates fixture")
        except Exception:
            pass
        return

    inserted, skipped = 0, 0
    for entry in entries:
        # Compute the auto-name to check existence
        eng_type = entry.get("engagement_type")
        phase_num = entry.get("phase_number")
        if not eng_type or not phase_num:
            continue
        # Frappe applies format:{engagement_type}-P{phase_number}
        # but we should check by composite key instead
        existing = frappe.db.exists("GRC Engagement Phase Template",
                                    {"engagement_type": eng_type,
                                     "phase_number": phase_num})
        if existing:
            skipped += 1
            continue
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC Engagement Phase Template"
            doc["is_active"] = 1
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Phase template seed failed: {eng_type} phase {phase_num}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.8.0: Seeded {inserted} engagement phase templates "
            f"({skipped} skipped/already exist).")
    except Exception:
        pass


# ===========================================================================
# v1.9.0 — GDPR catalog seeder
# ===========================================================================

def seed_gdpr_catalog():
    """Seed the GRC GDPR Catalog from the bundled fixture file (43 articles
    across 6 chapters)."""
    if not frappe.db.exists("DocType", "GRC GDPR Catalog"):
        return
    if frappe.db.count("GRC GDPR Catalog") > 0:
        return  # idempotent

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "gdpr_catalog.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load GDPR fixture")
        except Exception:
            pass
        return

    inserted = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC GDPR Catalog"
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"GDPR seed failed: "
                                 f"{entry.get('article_code')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.9.0: Seeded GDPR catalog — "
            f"{inserted} of {len(entries)} entries.")
    except Exception:
        pass


# ===========================================================================
# v1.9.1 — Workspace diagnostic + re-seeder
# ===========================================================================

@frappe.whitelist()
def workspace_diagnostic():
    """Report which tiles SHOULD exist vs which are present in the database.
    Run from bench: bench --site <name> execute alphax_grc.install.workspace_diagnostic
    Or from /app via frappe.call.
    """
    expected_links = [
        # v1.5+
        ("grc-ecc2-dashboard", "Page"),
        ("grc-aramco-ccc", "Page"),
        # v1.7
        ("grc-iso42001-dashboard", "Page"),
        ("grc-ccm-dashboard", "Page"),
        ("GRC Evidence Rule", "DocType"),
        # v1.8
        ("grc-consultant-inbox", "Page"),
        ("GRC Engagement", "DocType"),
        ("GRC Implementation Task", "DocType"),
        # v1.9
        ("grc-enterprise-risk-summary", "Page"),
        ("grc-gdpr-dashboard", "Page"),
    ]

    report = {"expected": len(expected_links), "found_in_workspace": 0,
              "missing": [], "doctypes_exist": [], "doctypes_missing": [],
              "pages_exist": [], "pages_missing": []}

    # Check what's actually in the workspace JSON record
    if frappe.db.exists("Workspace", "AlphaX GRC"):
        ws = frappe.get_doc("Workspace", "AlphaX GRC")
        ws_links = {(s.link_to, s.type) for s in (ws.shortcuts or [])}
    else:
        ws_links = set()
        report["error"] = "Workspace 'AlphaX GRC' not found"

    for link_to, link_type in expected_links:
        if (link_to, link_type) in ws_links:
            report["found_in_workspace"] += 1
        else:
            report["missing"].append(f"{link_type}: {link_to}")

        # Check if the underlying record exists at all
        if link_type == "Page":
            if frappe.db.exists("Page", link_to):
                report["pages_exist"].append(link_to)
            else:
                report["pages_missing"].append(link_to)
        elif link_type == "DocType":
            if frappe.db.exists("DocType", link_to):
                report["doctypes_exist"].append(link_to)
            else:
                report["doctypes_missing"].append(link_to)

    return report


@frappe.whitelist()
def reseed_workspace_shortcuts():
    """Re-import the AlphaX GRC workspace from the shipped JSON, so missing
    tiles from prior versions get added. Idempotent — skips tiles that
    already exist in the workspace.
    Run from bench:
      bench --site <name> execute alphax_grc.install.reseed_workspace_shortcuts
    """
    import os
    import json as _json

    app_path = frappe.get_app_path("alphax_grc")
    ws_json_path = os.path.join(
        app_path, "alphax_grc", "workspace", "alphax_grc", "alphax_grc.json")
    if not os.path.exists(ws_json_path):
        return {"ok": False, "error": "workspace JSON not found at " + ws_json_path}

    try:
        with open(ws_json_path, "r", encoding="utf-8") as f:
            ws_data = _json.load(f)
    except Exception as e:
        return {"ok": False, "error": f"could not parse workspace JSON: {e}"}

    expected_shortcuts = ws_data.get("shortcuts", [])

    if not frappe.db.exists("Workspace", "AlphaX GRC"):
        return {"ok": False,
                "error": "Workspace 'AlphaX GRC' does not exist on this site. "
                         "Reinstall the app or run bench migrate."}

    ws = frappe.get_doc("Workspace", "AlphaX GRC")
    existing_links = {(s.link_to, s.type) for s in (ws.shortcuts or [])}

    added = []
    for sc in expected_shortcuts:
        link_to = sc.get("link_to")
        link_type = sc.get("type", "DocType")
        if not link_to:
            continue
        if (link_to, link_type) in existing_links:
            continue
        try:
            ws.append("shortcuts", {
                "type": link_type,
                "link_to": link_to,
                "label": sc.get("label", link_to),
                "color": sc.get("color"),
                "icon": sc.get("icon"),
                "doc_view": sc.get("doc_view", ""),
                "stats_filter": sc.get("stats_filter", ""),
            })
            added.append(f"{link_type}: {link_to}")
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Re-seed failed for tile {link_to}")
            except Exception:
                pass

    if added:
        try:
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.clear_cache(doctype="Workspace")
        except Exception as e:
            return {"ok": False, "error": f"save failed: {e}",
                    "would_have_added": added}

    return {
        "ok": True,
        "added_count": len(added),
        "added": added,
        "total_shortcuts_now": len(ws.shortcuts),
    }


# ===========================================================================
# v1.9.4 — Comprehensive workspace + theme repair (auto-runs on every migrate)
# ===========================================================================

@frappe.whitelist()
def v194_force_repair():
    """v1.9.4 — force repair of workspace + theme.

    Called automatically from `before_migrate` hook. Also callable via API
    URL by System Manager.

    What this does:
    1. Force-overwrites the workspace 'AlphaX GRC' from the shipped JSON
       (preserves user customizations only if they chose 'Custom' theme)
    2. Applies Odoo Mauve theme if user is not on 'Custom'
    3. Clears workspace cache so next page load shows fresh state
    """
    import os
    import json as _json

    result = {"workspace_repaired": False, "theme_applied": False, "errors": []}

    # ----- Workspace repair -----
    try:
        if not frappe.db.exists("Workspace", "AlphaX GRC"):
            result["errors"].append("Workspace 'AlphaX GRC' does not exist")
        else:
            app_path = frappe.get_app_path("alphax_grc")
            ws_json = os.path.join(
                app_path, "alphax_grc", "workspace", "alphax_grc",
                "alphax_grc.json")
            if not os.path.exists(ws_json):
                result["errors"].append(f"Workspace JSON not found: {ws_json}")
            else:
                with open(ws_json, "r", encoding="utf-8") as f:
                    shipped = _json.load(f)

                ws = frappe.get_doc("Workspace", "AlphaX GRC")

                # Replace shortcuts (drop all, re-add from shipped)
                # v1.9.5: defensively skip shortcuts pointing at non-existent
                # doctypes or pages (same reasoning as links below).
                ws.shortcuts = []
                skipped_shortcuts = []
                for sc in shipped.get("shortcuts", []):
                    sc_type = sc.get("type", "DocType")
                    sc_target = sc.get("link_to") or ""

                    target_exists = True
                    if sc_target:
                        if sc_type == "DocType":
                            target_exists = bool(
                                frappe.db.exists("DocType", sc_target))
                        elif sc_type == "Page":
                            target_exists = bool(
                                frappe.db.exists("Page", sc_target))
                        elif sc_type == "Report":
                            target_exists = bool(
                                frappe.db.exists("Report", sc_target))

                    if not target_exists:
                        skipped_shortcuts.append(f"{sc_type}: {sc_target}")
                        continue

                    ws.append("shortcuts", {
                        "type": sc_type,
                        "link_to": sc_target,
                        "label": sc.get("label", sc_target),
                        "color": sc.get("color"),
                        "icon": sc.get("icon"),
                        "doc_view": sc.get("doc_view", ""),
                        "stats_filter": sc.get("stats_filter", ""),
                        "format": sc.get("format", ""),
                    })

                if skipped_shortcuts:
                    result["skipped_stale_shortcuts"] = skipped_shortcuts

                # Replace links (drop all, re-add from shipped)
                # v1.9.5: defensively skip any link pointing at a doctype
                # or page that doesn't exist on this site. Older shipped JSON
                # may carry stale references that have since been removed,
                # which would otherwise fail the entire save.
                ws.links = []
                skipped_links = []
                for link in shipped.get("links", []):
                    link_type = link.get("type", "Link")
                    link_target_type = link.get("link_type") or "DocType"
                    link_target = link.get("link_to") or ""

                    # Card Break entries don't reference a doctype, always include
                    if link_type == "Card Break":
                        ws.append("links", {
                            "type": "Card Break",
                            "label": link.get("label", ""),
                            "link_to": "",
                            "link_type": "DocType",
                            "description": link.get("description", "") or "",
                            "hidden": link.get("hidden", 0),
                            "is_query_report": link.get("is_query_report", 0),
                            "link_count": link.get("link_count", 0),
                            "onboard": link.get("onboard", 0),
                            "icon": link.get("icon", ""),
                        })
                        continue

                    # For Link entries, verify target exists
                    target_exists = True
                    if link_target:
                        if link_target_type == "DocType":
                            target_exists = bool(
                                frappe.db.exists("DocType", link_target))
                        elif link_target_type == "Page":
                            target_exists = bool(
                                frappe.db.exists("Page", link_target))
                        elif link_target_type == "Report":
                            target_exists = bool(
                                frappe.db.exists("Report", link_target))

                    if not target_exists:
                        skipped_links.append(
                            f"{link_target_type}: {link_target}")
                        continue

                    ws.append("links", {
                        "type": link_type,
                        "label": link.get("label", ""),
                        "link_to": link_target,
                        "link_type": link_target_type,
                        "description": link.get("description", "") or "",
                        "hidden": link.get("hidden", 0),
                        "is_query_report": link.get("is_query_report", 0),
                        "link_count": link.get("link_count", 0),
                        "onboard": link.get("onboard", 0),
                        "icon": link.get("icon", ""),
                    })

                # Drop empty Card Breaks (no subsequent Link before next break)
                cleaned = []
                for i, entry in enumerate(ws.links):
                    if entry.type != "Card Break":
                        cleaned.append(entry)
                        continue
                    # Look ahead
                    has_following_link = False
                    for j in range(i + 1, len(ws.links)):
                        if ws.links[j].type == "Card Break":
                            break
                        if ws.links[j].type == "Link":
                            has_following_link = True
                            break
                    if has_following_link:
                        cleaned.append(entry)
                ws.links = cleaned

                if skipped_links:
                    result["skipped_stale_links"] = skipped_links

                # Replace content (cards layout)
                ws.content = shipped.get("content", "")

                ws.save(ignore_permissions=True)
                frappe.db.commit()
                result["workspace_repaired"] = True
                result["shortcuts_count"] = len(ws.shortcuts)
                result["links_count"] = len(ws.links)
    except Exception:
        result["errors"].append(
            "workspace repair: " + frappe.get_traceback()[:300])

    # ----- Theme apply (only if not Custom) -----
    try:
        if frappe.db.exists("GRC Theme Settings", "GRC Theme Settings"):
            ts = frappe.get_doc("GRC Theme Settings", "GRC Theme Settings")
            if ts.theme_preset != "Custom":
                if ts.theme_preset != "Odoo Mauve":
                    ts.theme_preset = "Odoo Mauve"
                    ts.save(ignore_permissions=True)
                    frappe.db.commit()
                    result["theme_applied"] = True
                    result["theme_was"] = ts.theme_preset
                else:
                    result["theme_applied"] = True  # already mauve
                    result["theme_was"] = "Odoo Mauve (already)"
            else:
                result["theme_applied"] = False
                result["theme_was"] = "Custom (preserved)"
    except Exception:
        result["errors"].append(
            "theme apply: " + frappe.get_traceback()[:300])

    # ----- Clear caches so changes are visible -----
    try:
        frappe.clear_cache()
        frappe.clear_document_cache("Workspace", "AlphaX GRC")
    except Exception:
        pass

    try:
        frappe.logger().info(f"AlphaX GRC v1.9.4 force-repair: {result}")
    except Exception:
        pass

    return result


def v194_run_repair_on_migrate():
    """Auto-runner for `before_migrate` hook in hooks.py.
    Wraps v194_force_repair so any failure is logged but doesn't abort migrate.
    """
    try:
        v194_force_repair()
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC v1.9.4 migrate-repair failed")
        except Exception:
            pass


# ===========================================================================
# v1.9.6 — Doctype existence diagnostic
# ===========================================================================

@frappe.whitelist()
def v196_check_missing_doctypes():
    """v1.9.6 diagnostic — check which AlphaX GRC doctypes are referenced
    by Link fields but don't exist on this site.

    Run via API URL:
        /api/method/alphax_grc.install.v196_check_missing_doctypes

    This helps identify when migration partially failed and dependent
    doctypes weren't installed.
    """
    expected_doctypes = [
        # Aramco-related
        "GRC Aramco Third Party Profile",
        "GRC Aramco CCC Engagement",
        "GRC Aramco Certificate",
        "GRC Aramco Incident Notification",
        "GRC Aramco Audit Firm",
        # v1.7+
        "GRC Evidence Rule",
        "GRC Evidence Rule Evaluation",
        "GRC ISO42001 Catalog",
        "GRC ISO42001 Control",
        # v1.8+
        "GRC Engagement",
        "GRC Engagement Phase Template",
        "GRC Engagement Phase Log",
        "GRC Engagement Phase Checklist Item",
        "GRC Engagement Decision Log",
        "GRC Implementation Task",
        "GRC Document Publication",
        # v1.9+
        "GRC GDPR Catalog",
        "GRC GDPR Control",
        # v2.0+
        "GRC Detection Coverage",
        # v2.1+
        "GRC NIST CSF Catalog",
        "GRC NIST CSF Control",
        "GRC ISO22301 Catalog",
        "GRC ISO22301 Control",
        # v2.1.1+
        "GRC CRQ Scenario",
        # v2.2.0 — PDPL Privacy Pack
        "GRC PDPL Catalog",
        "GRC PDPL Control",
        "GRC DSAR Request",
        "GRC DPIA Record",
        "GRC ISO27001 SOA",
        # Core
        "GRC Client Profile",
        "GRC Risk Register",
        "GRC Audit Plan",
        "GRC Audit Finding",
        "GRC Audit Workpaper",
        "GRC IT Audit Program",
        "GRC IT Audit Control Item",
        "GRC Incident",
        "GRC Asset Inventory",
        "GRC ITGC Audit Item",
        "GRC Vendor",
        "GRC NCA ECC Control",
    ]

    present = []
    missing = []
    for dt in expected_doctypes:
        if frappe.db.exists("DocType", dt):
            present.append(dt)
        else:
            missing.append(dt)

    return {
        "expected": len(expected_doctypes),
        "present_count": len(present),
        "missing_count": len(missing),
        "present": present,
        "missing": missing,
        "advice": "If 'missing' is non-empty, run bench migrate (or click "
                  "Migrate in Frappe Cloud) to install them. If migration "
                  "still doesn't create them, it's a doctype-source issue.",
    }


# ===========================================================================
# v1.9.7 — Force-recreate missing doctypes
# ===========================================================================

def v197_recreate_missing_doctypes():
    """v1.9.7 — re-import any AlphaX GRC doctype JSON files whose
    DocType records are missing from the database.

    This handles the recovery scenario where a doctype existed in an earlier
    version, was deleted (manually or via cleanup), and now Frappe's normal
    migrate doesn't re-register it because there's no entry to compare against.

    Auto-runs from after_migrate. Wrapped to never abort migration.
    """
    import os
    from frappe.modules.import_file import import_file_by_path

    app_path = frappe.get_app_path("alphax_grc")
    doctype_dir = os.path.join(app_path, "alphax_grc", "doctype")
    if not os.path.isdir(doctype_dir):
        return {"ok": False, "error": f"doctype dir not found: {doctype_dir}"}

    recreated = []
    skipped_present = []
    failed = []

    for entry in sorted(os.listdir(doctype_dir)):
        sub = os.path.join(doctype_dir, entry)
        if not os.path.isdir(sub):
            continue
        json_path = os.path.join(sub, entry + ".json")
        if not os.path.isfile(json_path):
            continue

        # Read the JSON to find the doctype name (handles renames)
        try:
            import json as _json
            with open(json_path, "r", encoding="utf-8") as f:
                spec = _json.load(f)
            dt_name = spec.get("name")
            if not dt_name:
                continue
        except Exception:
            continue

        # If the doctype already exists, skip
        if frappe.db.exists("DocType", dt_name):
            skipped_present.append(dt_name)
            continue

        # Force-import it
        try:
            import_file_by_path(json_path, force=True, reset_permissions=True)
            recreated.append(dt_name)
        except Exception:
            failed.append(dt_name)
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"v197_recreate_missing_doctypes: "
                                 f"could not import {dt_name}")
            except Exception:
                pass

    if recreated:
        try:
            frappe.db.commit()
            frappe.clear_cache()
            frappe.logger().info(
                f"AlphaX GRC v1.9.7: re-created {len(recreated)} "
                f"missing doctypes: {recreated}")
        except Exception:
            pass

    return {
        "ok": True,
        "recreated_count": len(recreated),
        "recreated": recreated,
        "already_present": len(skipped_present),
        "failed_count": len(failed),
        "failed": failed,
    }


@frappe.whitelist()
def v197_force_recreate_missing_doctypes():
    """Whitelisted wrapper so admins can manually trigger the recreation
    via API URL:
        /api/method/alphax_grc.install.v197_force_recreate_missing_doctypes
    """
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw("System Manager role required.", frappe.PermissionError)
    return v197_recreate_missing_doctypes()


# ===========================================================================
# v2.0.0 — Standard CISO KPI seed pack (11 KPIs)
# ===========================================================================

# 11 KPIs with framework hints. The first 5 are wired to live data via the
# auto-compute hooks at the bottom of this module; the rest are manual-entry.
_STANDARD_CISO_KPIS = [
    {
        "kpi_id": 1,
        "indicator_name": "Asset Inventory Coverage",
        "indicator_name_ar": "تغطية مخزون الأصول",
        "cybersecurity_domain": "Asset Management",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of IT assets formally inventoried, classified, "
                           "and assigned an owner.",
        "kpi_definition": "Target: >95%. Source: GRC Asset Inventory records "
                          "with owner and classification populated, divided by total "
                          "GRC Asset Inventory records.",
        "data_source": "GRC Asset Inventory",
    },
    {
        "kpi_id": 2,
        "indicator_name": "Security Controls Coverage",
        "indicator_name_ar": "تغطية الضوابط الأمنية",
        "cybersecurity_domain": "Compliance",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of in-scope NCA ECC-2:2024 controls with "
                           "compliance_status of Implemented or Partially Implemented.",
        "kpi_definition": "Target: >90%. Source: GRC NCA ECC Control records.",
        "data_source": "GRC NCA ECC Control",
    },
    {
        "kpi_id": 3,
        "indicator_name": "Vulnerability Assessment Coverage",
        "indicator_name_ar": "تغطية تقييم الثغرات",
        "cybersecurity_domain": "Vulnerability Management",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of in-scope assets that have been "
                           "vulnerability-scanned in the last 90 days.",
        "kpi_definition": "Target: >85%. Source: GRC Asset Inventory records "
                          "with last_va_scan_date within 90 days.",
        "data_source": "GRC Asset Inventory + GRC Vulnerability",
    },
    {
        "kpi_id": 4,
        "indicator_name": "Mean Time To Remediate (MTTR)",
        "indicator_name_ar": "متوسط زمن المعالجة",
        "cybersecurity_domain": "Vulnerability Management",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Average days between vulnerability discovery and "
                           "remediation closure.",
        "kpi_definition": "Target: <100 days. Source: GRC Vulnerability records "
                          "with closed_date populated; average of "
                          "(closed_date - discovered_date).",
        "data_source": "GRC Vulnerability",
    },
    {
        "kpi_id": 5,
        "indicator_name": "Cyber Security Incidents Reported",
        "indicator_name_ar": "حوادث الأمن السيبراني المبلغ عنها",
        "cybersecurity_domain": "Incident Management",
        "kpi_type": "Trend",
        "frequency": "Quarterly",
        "kpi_description": "Number of cyber security incidents reported per quarter. "
                           "Increasing trend is desirable (better detection/reporting).",
        "kpi_definition": "Trend metric, no fixed threshold. Source: GRC Incident "
                          "records created in the quarter.",
        "data_source": "GRC Incident",
    },
    {
        "kpi_id": 6,
        "indicator_name": "Patch Compliance",
        "indicator_name_ar": "الامتثال للتحديثات الأمنية",
        "cybersecurity_domain": "Vulnerability Management",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of devices with the latest critical "
                           "security patches applied.",
        "kpi_definition": "Target: >90%. Manual entry until ERPNext Asset "
                          "patch-status integration is built.",
        "data_source": "Manual entry (patch management system feed)",
    },
    {
        "kpi_id": 7,
        "indicator_name": "Outdated OS / Software",
        "indicator_name_ar": "أنظمة التشغيل والبرامج القديمة",
        "cybersecurity_domain": "Vulnerability Management",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of devices running an unsupported OS or "
                           "out-of-date software.",
        "kpi_definition": "Target: <5%. Manual entry until OS-version asset "
                          "feed is built.",
        "data_source": "Manual entry (asset management system feed)",
    },
    {
        "kpi_id": 8,
        "indicator_name": "Phishing Email Open Rate",
        "indicator_name_ar": "معدل فتح رسائل التصيد",
        "cybersecurity_domain": "Awareness & Training",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of users who opened a simulated phishing "
                           "email during the quarterly campaign.",
        "kpi_definition": "Target: <3%. Manual entry from phishing simulation "
                          "platform results.",
        "data_source": "Manual entry (phishing platform results)",
    },
    {
        "kpi_id": 9,
        "indicator_name": "Phishing Campaign Failure Rate",
        "indicator_name_ar": "معدل فشل حملة التصيد",
        "cybersecurity_domain": "Awareness & Training",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of users who clicked a phishing link or "
                           "submitted credentials. RAG: Green ≤5%, Yellow 6-10%, "
                           "Red >10%.",
        "kpi_definition": "RAG thresholds. Manual entry from phishing platform.",
        "data_source": "Manual entry (phishing platform)",
    },
    {
        "kpi_id": 10,
        "indicator_name": "Administrative Access Count",
        "indicator_name_ar": "عدد حسابات الوصول الإداري",
        "cybersecurity_domain": "Access Control",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Total number of accounts with administrative privileges. "
                           "Tracked as count to drive least-privilege reviews.",
        "kpi_definition": "Manual entry. Compare quarter-on-quarter; declining "
                          "trend is desirable.",
        "data_source": "Manual entry (privileged access management feed)",
    },
    {
        "kpi_id": 11,
        "indicator_name": "Third-Party Risk Assessment Coverage",
        "indicator_name_ar": "تغطية تقييم مخاطر الأطراف الثالثة",
        "cybersecurity_domain": "Third-Party Risk",
        "kpi_type": "Performance",
        "frequency": "Quarterly",
        "kpi_description": "Percentage of active vendors that have a current "
                           "risk assessment on file.",
        "kpi_definition": "Target: 100%. Source: GRC Vendor records with "
                          "last_assessment_date in the last 12 months, divided "
                          "by total active vendors.",
        "data_source": "GRC Vendor",
    },
]


def seed_standard_ciso_kpis():
    """Seed 11 standard CISO KPIs as starter records linked to the
    DEFAULT_CLIENT_NAME. Idempotent — only inserts KPIs that don't already
    exist (matched by indicator_name + client)."""
    if not frappe.db.exists("DocType", "GRC KPI"):
        return
    if not frappe.db.exists("GRC Client Profile", DEFAULT_CLIENT_NAME):
        return

    inserted = 0
    skipped = 0
    failed = 0

    for kpi_data in _STANDARD_CISO_KPIS:
        # Idempotency: skip if a KPI with this indicator_name already exists
        # for the default client
        existing = frappe.db.exists("GRC KPI", {
            "client": DEFAULT_CLIENT_NAME,
            "indicator_name": kpi_data["indicator_name"],
        })
        if existing:
            skipped += 1
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "GRC KPI",
                "client": DEFAULT_CLIENT_NAME,
                **kpi_data,
            })
            doc.insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            failed += 1
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"CISO KPI seed failed: "
                                 f"{kpi_data['indicator_name']}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v2.0.0: seeded standard CISO KPIs — "
            f"{inserted} new, {skipped} skipped, {failed} failed.")
    except Exception:
        pass


# ===========================================================================
# v2.0.0 — Live KPI auto-compute (5 of 11 KPIs)
# ===========================================================================
# These functions compute the current value of each live-data KPI.
# They are exposed via whitelisted API URLs so a dashboard or scheduler
# can refresh KPI values on demand.

@frappe.whitelist()
def compute_live_ciso_kpis(client=None):
    """Compute current values for the 5 live-data CISO KPIs.

    Returns a dict mapping indicator_name → {value, target_threshold,
    rag_status, computed_at}.

    These are the 5 we can compute deterministically from data already
    in AlphaX GRC. The other 6 require external feeds (patch management,
    phishing platform, PAM, etc.) and stay in manual-entry mode.
    """
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)

    from frappe.utils import today, add_days, date_diff

    results = {}
    today_d = frappe.utils.getdate(today())
    ninety_days_ago = add_days(today(), -90)
    twelve_months_ago = add_days(today(), -365)

    # --- 1. Asset Inventory Coverage ---
    if frappe.db.exists("DocType", "GRC Asset Inventory"):
        try:
            filters = {}
            if client:
                filters["client"] = client
            total = frappe.db.count("GRC Asset Inventory", filters) or 0
            covered_filters = dict(filters)
            covered_filters["custodian"] = ["not in", ["", None]]
            covered = frappe.db.count("GRC Asset Inventory",
                                      covered_filters) or 0
            value = (covered / total * 100) if total > 0 else 0
            results["Asset Inventory Coverage"] = {
                "value": round(value, 1),
                "target": 95,
                "rag": "Green" if value >= 95 else
                       ("Yellow" if value >= 85 else "Red"),
                "total": total,
                "covered": covered,
            }
        except Exception:
            pass

    # --- 2. Security Controls Coverage ---
    if frappe.db.exists("DocType", "GRC NCA ECC Control"):
        try:
            filters = {}
            if client:
                filters["client"] = client
            total = frappe.db.count("GRC NCA ECC Control", filters) or 0
            implemented_filters = dict(filters)
            implemented_filters["compliance_status"] = [
                "in", ["Implemented", "Partially Implemented"]]
            implemented = frappe.db.count("GRC NCA ECC Control",
                                          implemented_filters) or 0
            value = (implemented / total * 100) if total > 0 else 0
            results["Security Controls Coverage"] = {
                "value": round(value, 1),
                "target": 90,
                "rag": "Green" if value >= 90 else
                       ("Yellow" if value >= 75 else "Red"),
                "total": total,
                "implemented": implemented,
            }
        except Exception:
            pass

    # --- 3. Vulnerability Assessment Coverage ---
    if frappe.db.exists("DocType", "GRC Asset Inventory"):
        try:
            filters = {}
            if client:
                filters["client"] = client
            total = frappe.db.count("GRC Asset Inventory", filters) or 0
            scanned_filters = dict(filters)
            scanned_filters["last_va_scan_date"] = [">=", ninety_days_ago]
            scanned = frappe.db.count("GRC Asset Inventory",
                                      scanned_filters) or 0
            value = (scanned / total * 100) if total > 0 else 0
            results["Vulnerability Assessment Coverage"] = {
                "value": round(value, 1),
                "target": 85,
                "rag": "Green" if value >= 85 else
                       ("Yellow" if value >= 70 else "Red"),
                "total": total,
                "scanned_in_90d": scanned,
            }
        except Exception:
            pass

    # --- 4. MTTR ---
    if frappe.db.exists("DocType", "GRC Vulnerability"):
        try:
            filters = {"closed_date": ["is", "set"]}
            if client:
                filters["client"] = client
            closed = frappe.get_all(
                "GRC Vulnerability", filters=filters,
                fields=["discovered_date", "closed_date"],
                limit_page_length=2000,
            )
            days = []
            for v in closed:
                if v.discovered_date and v.closed_date:
                    try:
                        days.append(date_diff(v.closed_date,
                                              v.discovered_date))
                    except Exception:
                        pass
            if days:
                mttr = sum(days) / len(days)
                results["Mean Time To Remediate (MTTR)"] = {
                    "value": round(mttr, 1),
                    "target": 100,
                    "rag": "Green" if mttr <= 100 else
                           ("Yellow" if mttr <= 180 else "Red"),
                    "sample_count": len(days),
                }
        except Exception:
            pass

    # --- 5. Cyber Security Incidents Reported (Quarter) ---
    if frappe.db.exists("DocType", "GRC Incident"):
        try:
            ninety = add_days(today(), -90)
            filters = {"creation": [">=", ninety]}
            if client:
                filters["client"] = client
            count = frappe.db.count("GRC Incident", filters) or 0
            # Trend-only metric — no fixed threshold
            results["Cyber Security Incidents Reported"] = {
                "value": count,
                "target": None,  # trend metric
                "rag": "Info",
                "period": "last 90 days",
            }
        except Exception:
            pass

    # --- 11. Third-Party Risk Assessment Coverage ---
    # (number 11 in the standard pack, computed live)
    if frappe.db.exists("DocType", "GRC Vendor"):
        try:
            filters = {}
            if client:
                filters["client"] = client
            total = frappe.db.count("GRC Vendor", filters) or 0
            assessed_filters = dict(filters)
            assessed_filters["last_assessment_date"] = [
                ">=", twelve_months_ago]
            assessed = frappe.db.count("GRC Vendor",
                                       assessed_filters) or 0
            value = (assessed / total * 100) if total > 0 else 0
            results["Third-Party Risk Assessment Coverage"] = {
                "value": round(value, 1),
                "target": 100,
                "rag": "Green" if value >= 100 else
                       ("Yellow" if value >= 80 else "Red"),
                "total": total,
                "assessed": assessed,
            }
        except Exception:
            pass

    # v2.1.1 — explicit skipped reporting (instead of silent failure)
    skipped = []
    if not frappe.db.exists("DocType", "GRC Asset Inventory"):
        skipped.append({
            "kpi": "Asset Inventory Coverage / Vulnerability Assessment Coverage",
            "reason": "GRC Asset Inventory doctype not present"})
    if not frappe.db.exists("DocType", "GRC NCA ECC Control"):
        skipped.append({
            "kpi": "Security Controls Coverage",
            "reason": "GRC NCA ECC Control doctype not present"})
    if not frappe.db.exists("DocType", "GRC Vulnerability"):
        skipped.append({
            "kpi": "Mean Time To Remediate (MTTR)",
            "reason": "GRC Vulnerability doctype not present in this app — "
                      "MTTR computation requires that doctype. Track manually "
                      "or add the doctype in a future release."})
    if not frappe.db.exists("DocType", "GRC Incident"):
        skipped.append({
            "kpi": "Cyber Security Incidents Reported",
            "reason": "GRC Incident doctype not present"})
    if not frappe.db.exists("DocType", "GRC Vendor"):
        skipped.append({
            "kpi": "Third-Party Risk Assessment Coverage",
            "reason": "GRC Vendor doctype not present"})

    if skipped:
        results["skipped_kpis"] = skipped

    results["computed_at"] = str(frappe.utils.now())
    return results


# ===========================================================================
# v2.1.0 — NIST CSF 2.0 catalog seeder
# ===========================================================================

def seed_nist_csf_catalog():
    """Seed the GRC NIST CSF Catalog from the bundled fixture file
    (106 subcategories across 6 functions: GV, ID, PR, DE, RS, RC)."""
    if not frappe.db.exists("DocType", "GRC NIST CSF Catalog"):
        return
    if frappe.db.count("GRC NIST CSF Catalog") > 0:
        return  # idempotent

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "nist_csf_catalog.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load NIST CSF fixture")
        except Exception:
            pass
        return

    function_label_map = {
        "GV": "Govern", "ID": "Identify", "PR": "Protect",
        "DE": "Detect", "RS": "Respond", "RC": "Recover",
    }

    inserted = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC NIST CSF Catalog"
            # Auto-fill function_label from function_code if not set
            if not doc.get("function_label"):
                doc["function_label"] = function_label_map.get(
                    doc.get("function_code", ""), "")
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"NIST CSF seed failed: "
                                 f"{entry.get('subcategory_code')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v2.1.0: Seeded NIST CSF 2.0 catalog — "
            f"{inserted} of {len(entries)} subcategories.")
    except Exception:
        pass


# ===========================================================================
# v2.1.0 — ISO 22301 BCMS catalog seeder
# ===========================================================================

def seed_iso22301_catalog():
    """Seed the GRC ISO22301 Catalog from the bundled fixture file
    (36 clauses across Sections 4-10).

    Original implementation guidance — NOT lifted from any commercial
    toolkit. Document codes use BCMS-XX-001 pattern parallel to AIMS-XX-001
    in ISO 42001.
    """
    if not frappe.db.exists("DocType", "GRC ISO22301 Catalog"):
        return
    if frappe.db.count("GRC ISO22301 Catalog") > 0:
        return  # idempotent

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "iso22301_catalog.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load ISO 22301 fixture")
        except Exception:
            pass
        return

    section_label_map = {
        "4 Context": "Context of the Organization",
        "5 Leadership": "Leadership",
        "6 Planning": "Planning",
        "7 Support": "Support",
        "8 Operation": "Operation",
        "9 Performance Evaluation": "Performance Evaluation",
        "10 Improvement": "Improvement",
    }

    inserted = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC ISO22301 Catalog"
            if not doc.get("section_label"):
                doc["section_label"] = section_label_map.get(
                    doc.get("section_number", ""), "")
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"ISO 22301 seed failed: "
                                 f"{entry.get('clause_code')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v2.1.0: Seeded ISO 22301 BCMS catalog — "
            f"{inserted} of {len(entries)} clauses.")
    except Exception:
        pass


# ===========================================================================
# v2.2.0 — PDPL catalog seeder
# ===========================================================================

def seed_pdpl_catalog():
    """Seed the GRC PDPL Catalog from the bundled fixture file
    (31 articles across PDPL Law, Implementing Regulation, Cross-Border
    Transfer Regulation, NDMO Guidance).

    Original implementation guidance written from the publicly-published
    SDAIA PDPL law text. NOT lifted from any commercial toolkit. Article
    references (PDPL-A1, IR-A4, CB-A1, NDMO-G1) follow our own naming
    convention parallel to BCMS-XX/AIMS-XX patterns elsewhere in the app.
    """
    if not frappe.db.exists("DocType", "GRC PDPL Catalog"):
        return
    if frappe.db.count("GRC PDPL Catalog") > 0:
        return  # idempotent

    import os
    import json as _json
    app_path = frappe.get_app_path("alphax_grc")
    fixture_path = os.path.join(app_path, "alphax_grc", "data",
                                "pdpl_catalog.json")
    if not os.path.exists(fixture_path):
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            entries = _json.load(f)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "Failed to load PDPL fixture")
        except Exception:
            pass
        return

    inserted = 0
    for entry in entries:
        try:
            doc = dict(entry)
            doc["doctype"] = "GRC PDPL Catalog"
            frappe.get_doc(doc).insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"PDPL seed failed: "
                                 f"{entry.get('article_code')}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v2.2.0: Seeded PDPL catalog — "
            f"{inserted} of {len(entries)} articles.")
    except Exception:
        pass
