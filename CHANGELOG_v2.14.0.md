# AlphaX GRC v2.14.0 — Governance & Bilingual release

## Added — approval workflows (closing the governance gap)
- **GRC Risk Acceptance Workflow**: Draft → Pending Approval → Accepted /
  Rejected, with Expired / Revoked states. Approval requires an approver and
  an expiry date (mirrors the Exception workflow's condition convention).
- **GRC SAMA Waiver Workflow**: mirrors the doctype's own ladder — Draft →
  CISO Approval → Committee Approval → Submitted to SAMA → Approved /
  Rejected, plus Withdraw at any pre-submission stage. CISO and Committee
  transitions require the respective approver fields to be set.
- **GRC DPIA Workflow**: Draft → In Review → Approved / Needs Revision /
  Rejected → Retired. **Approval is conditional on `dpo_consulted`** — a DPIA
  cannot be approved without DPO consultation.
- Workflows ship as JSON in the existing `workflow/` folder and install via
  the existing `install_workflows()` (skips existing — idempotent).
  Patch `v2_14_0_governance` installs them on already-deployed sites.

## Changed — DSAR consolidation
- **GRC Data Subject Request is deprecated** in favour of GRC DSAR Request
  (identity verification, statutory clocks, fulfilment tracking).
  New legacy records are blocked server-side with guidance; existing records
  stay readable. The v2_14_0 patch migrates legacy records into DSAR Request
  idempotently (traceable `migrated-from:` marker; status not auto-mapped
  because option sets differ). PDPL framework map now links DSAR Request only.

## Added — bilingual (Arabic)
- `translations/ar.csv` with 223 entries: both process-map pages, all lane
  labels, step titles, decision diamonds, edge labels, workflow states and
  actions for the three new workflows, framework names/taglines, and the
  deprecation message. Map pages now wrap node strings in `__()` so they
  translate when the user's language is العربية.

## Added — tests
- `tests/test_v2_14_governance.py`: workflows installed + idempotent,
  legacy DSR insert blocked, DSR migration idempotent.

## Audit notes
- Vendor Assessment and Maturity Assessment scoring verified as already
  enforced server-side; remaining pass-only controllers are catalogs/masters.

## Deploy
`bench migrate` (runs the patch) → `bench build --app alphax_grc` →
hard refresh. Arabic: user menu → My Settings → Language → العربية.
