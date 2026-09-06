# AlphaX GRC — Consultant Questionnaire Library
## v0.8.0 | IRSAA Business Solutions

9 seeded templates, 15 questions each (135 total), all bilingual (EN/AR).

| Code | Area | Framework | Questions | Scope |
|------|------|-----------|-----------|-------|
| GOV_DISCOVERY | Governance | ISO 27001 | 15 | Global |
| IAM_REVIEW | IAM | ISO 27001, NCA ECC | 15 | Global |
| BCP_DRP | BCP/DR | ISO 22301, NCA ECC | 15 | Global |
| PRIVACY_PDPL | Privacy | PDPL, GDPR-aligned | 15 | Saudi Arabia |
| OT_ICS_CSCC | OT/ICS | NCA ECC, IEC 62443 | 15 | Saudi Energy/Utilities |
| AI_GOV_42001 | AI Governance | ISO 42001, SDAIA | 15 | Global |
| INTG_COMPLIANCE | Compliance | NCA ECC, SAMA CSF | 15 | Saudi Arabia |
| VENDOR_RISK | Vendor Risk | ISO 27001, Aramco TP | 15 | Global/Saudi |
| AUDIT_READY | Audit Readiness | ISO 27001, IIA | 15 | Global |

## Maturity Scale
| Score | Label | Action |
|-------|-------|--------|
| 0-19% | Initial | Immediate programme establishment |
| 20-39% | Developing | Formalise and document controls |
| 40-59% | Defined | Close evidence gaps |
| 60-79% | Managed | Automate and measure |
| 80-100% | Optimised | Maintain and prepare for external audit |

Use `alphax_grc.api.start_assessment_run(template_name, customer_name)` to launch a run.
Print the GRC Assessment Run Report print format for client deliverables.
