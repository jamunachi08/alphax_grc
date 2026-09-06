# AlphaX GRC v2.2.0 — PDPL Privacy Pack

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v2.2.0

KSA-first privacy release. Six new doctypes, one new dashboard, one
new engagement phase template. All content built fresh from public
KSA government sources — SDAIA-published PDPL law, Implementing
Regulations, Cross-Border Transfer Regulation, NDMO programme
guidance.

### 1. PDPL Catalog and per-client tracking

`GRC PDPL Catalog` doctype seeded with **31 articles** organized by
section:

- **PDPL Law** (19 articles) — A1 Definitions, A2 Scope,
  A4 Principles, A5 Data subject rights, A6 Right to be informed,
  A7 Lawful basis, A8 Sensitive data, A9 Children's data,
  A10 Consent management, A11 Direct marketing, A12 Accuracy,
  A13 Erasure, A14 DPO, A15 DPIA, A16 RoPA, A17 Security,
  A18 Breach notification, A19 Cross-border transfers,
  A20 Processor obligations
- **Implementing Regulation** (6 articles) — Privacy notice content,
  Consent detail, DSAR procedures, DPIA threshold, Breach procedure,
  DPO appointment criteria
- **Cross-Border Transfer Regulation** (2 articles) — Lawful bases,
  Risk assessment
- **NDMO Guidance** (4 entries) — Inventory & classification,
  Privacy by design, Awareness & training, Compliance monitoring

Each article carries article code (using our PDPL-AX/IR-AX/CB-AX/NDMO-GX
naming convention parallel to BCMS-XX-001 for ISO 22301 and AIMS-XX-001
for ISO 42001), section, title, intent statement, **original
implementation guidance**, typical evidence, and cross-references to
GDPR, NCA ECC, and NIST Privacy Framework where applicable.

`GRC PDPL Control` doctype — per-client tracker with compliance status
(Not Started / In Progress / Implemented / Partially Implemented / Not
Applicable), compliance score, owner, target date, last assessed.

### 2. PDPL Dashboard `/app/grc-pdpl-dashboard`

Four section cards (PDPL Law / Implementing Regulation /
Cross-Border / NDMO Guidance) with compliance status breakdown and
average scores. Plus integrated DSAR backlog tracker and DPIA risk
mix viewer in the same dashboard. Click-through to filtered list views.

### 3. DSAR Request workflow `GRC DSAR Request`

Tracks Data Subject Access Requests through the PDPL workflow with
**automated 30-day SLA enforcement**:

- 8 request types per PDPL: Access / Rectification / Erasure /
  Withdraw Consent / Object to Processing / Data Portability /
  Automated Decision Review / Complaint
- Identity verification (Iqama / Passport / Account-based)
- 11-status workflow: Received → Identity Verification → Scope
  Assessment → In Progress → Legal Review → Ready to Respond →
  Responded → Closed/Declined/Withdrawn
- **Auto-set due_date** = received_date + 30 days
  (per PDPL Implementing Regulation Article 8)
- **Auto-flag overdue** when due_date past and status not yet
  terminal
- **Auto-compute days_to_respond** when responded_date set
- Extension tracking with reason
- Outcome capture (Fulfilled / Partially Fulfilled / Declined /
  Referred to SDAIA / Withdrawn)
- Cross-references to PDPL articles and audit findings

### 4. DPIA Record `GRC DPIA Record`

Data Protection Impact Assessment record per PDPL Implementing
Regulation Article 11. Structured with:

- 9 trigger reasons (new system, sensitive data processing, large-
  scale monitoring, automated decisions, new technology, cross-border,
  periodic review, material change)
- Processing description with data categories, data subject categories,
  lawful basis, retention, data volume tier
- Necessity and proportionality assessment
- Risk to individuals with **likelihood × impact → auto-classified
  inherent risk level** using the same NIST 800-30 5×5 matrix as the
  CRQ doctype (consistency across the app)
- Mitigations and residual risk
- Consultation tracking (DPO, stakeholders, data subjects)
- Decision (Proceed / Proceed with Conditions / Do Not Proceed /
  Defer Pending Information) with rationale
- **Auto-mark high_risk** when inherent risk is High or Very High
- **Auto-set next_review_due** = dpia_date + 12 months when status
  flips to Approved

### 5. ISO 27001:2022 Statement of Applicability `GRC ISO27001 SOA`

Per-client SOA tracker for ISO 27001:2022 Annex A controls. **Catalog
side intentionally not seeded** — the verbatim Annex A control text is
ISO/IEC copyrighted material that we do not bundle. Consultants
populate `control_code` (e.g. 5.1) and `control_title` (e.g. "Policies
for information security") from the client's own certified copy of
the standard.

Captures: applicable Y/N/Under Review, implemented Y/N/Partial/In
Progress/Not Applicable, justification for inclusion or exclusion,
implementation remarks, evidence document reference, owner, target
date, last assessed, implementation %.

Auto-behavior: when `applicable=No`, forces `implemented=Not Applicable`.
Auto-stamps `last_assessed` on status changes.

### 6. PDPL Implementation engagement phase template

10-phase NDMO-aligned lifecycle baked into `GRC Engagement Phase
Template`:

1. Data Discovery & Mapping (14 days)
2. Initial PDPL Assessment (10 days)
3. Build RoPA (21 days)
4. Gap Analysis (14 days)
5. Develop Required Policies (21 days)
6. Implement Data Classification Policy (14 days)
7. Build DSAR Process (14 days)
8. Define KPIs/KCIs/KRIs (7 days)
9. Awareness Sessions (21 days)
10. Third-Party Management & Breach Response Plan (21 days)

Each phase has entry criteria, completion criteria, and 3-6 default
checklist items with responsible team and offset days. Total expected
timeline: ~157 days for a full PDPL implementation.

When a consultant creates a `GRC Engagement` and selects engagement
type "PDPL Implementation", these 10 phases are pre-populated. Driver-
less-car principle: the consultant doesn't construct the lifecycle.

### 7. Engagement automation extended

The `auto_create_per_client_controls` flow now supports PDPL. When you
add `PDPL` to a `GRC Engagement.frameworks_in_scope` field, the system
creates 31 per-client tracking records automatically. Idempotent.

### 8. Diagnostic updated

`v196_check_missing_doctypes` now expects **41 doctypes** (was 36 in
v2.1.1), adding:

- GRC PDPL Catalog
- GRC PDPL Control
- GRC DSAR Request
- GRC DPIA Record
- GRC ISO27001 SOA

### 9. Workspace updates

- 2 new shortcut tiles: PDPL (Pink), DSAR (Yellow)
- 5 new links in AI Governance & Data Protection group
  (PDPL Catalog, PDPL Per-Client, DSAR, DPIA, PDPL Dashboard)
- 1 new link in Compliance & Frameworks group (ISO 27001:2022 SOA)
- 1 new link in Dashboards & Pages (PDPL Dashboard)

Workspace now has 32 shortcuts and 104 links.

## What's NOT in v2.2.0

Per scope discipline — these are deliberately deferred:

- **NIST Privacy Framework 1.0 catalog** → v2.2.1 (~100 subcategories
  parallel to NIST CSF architecture, fresh build from public NIST
  publication)
- **ISO 27701 PIMS catalog** → v2.3 (fresh build NOT from CertiKit)
- **Risk Register field additions** → cancelled. The existing
  `risk_cause` and `risk_analysis_consequences` fields on
  `GRC Risk Register` already cover the ground that
  `root_causes` and `downstream_implications` would have covered.
  Adding duplicates would have confused consultants. Honest call.

## IP boundaries honored

This release sticks rigorously to the IP discipline you set:

- **PDPL law content** — drawn from SDAIA's publicly-published PDPL
  law text (link `#1` in the PDPL Compliance Toolkit's References
  sheet), Implementing Regulations (`#2`), Cross-Border Transfer
  Regulation (`#3`), NDMO programme structure. Implementation
  guidance is original — written from the law, not paraphrased
  from any commercial toolkit.
- **Article naming convention** — `PDPL-AX`, `IR-AX`, `CB-AX`,
  `NDMO-GX` is our own naming convention parallel to BCMS-XX-001
  (ISO 22301) and AIMS-XX-001 (ISO 42001).
- **NDMO 10-phase engagement template** — the structural framing
  (Data Discovery → Initial Assessment → ... → Breach Response Plan)
  is publicly published by NDMO. Phase descriptions, entry/completion
  criteria, and checklist items are original.
- **No CertiKit content** — explicitly refused the CertiKit
  ISO 27701 Toolkit V1 upload. Will refuse all future CertiKit
  toolkits.
- **No verbatim ISO 27001:2022 Annex A text** — explicitly refused
  the ISO 27001 SOA upload. ISO 27001 SOA doctype is structurally
  ready but consultant populates control text from client's own
  certified copy of the standard.

## Upgrade path

```bash
# Upload alphax_grc_v2_2_0.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate
```

After migrate completes:

1. **Run doctype diagnostic:**
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```
   Expected: `present_count: 41, missing: []`. Should now include all
   v2.2.0 doctypes.

2. **Verify PDPL catalog seeded:**
   - Open `/app/grc-pdpl-catalog` — should show 31 articles
   - Open `/app/grc-pdpl-dashboard` — should show 4 section cards with
     totals (PDPL Law: 19, Implementing Regulation: 6, Cross-Border: 2,
     NDMO Guidance: 4)

3. **Test framework auto-create:**
   - Open any GRC Engagement
   - Add `PDPL` to `frameworks_in_scope` (comma-separated)
   - Save — should auto-create 31 per-client tracking records

4. **Test DSAR workflow:**
   - Create new DSAR Request
   - Set received_date = today
   - Save — verify due_date auto-set to today + 30 days
   - Set responded_date = received_date + 5
   - Save — verify days_to_respond = 5

5. **Test DPIA risk classification:**
   - Create new DPIA Record
   - Set likelihood=High, impact=High
   - Save — verify inherent_risk_level auto-set to "High",
     is_high_risk auto-set to 1

6. **Verify engagement phase template:**
   - Create new GRC Engagement
   - Select engagement_type = "PDPL Implementation"
   - 10 phases should be pre-populated with checklist items

7. **Verify workspace tiles:**
   - Should see PDPL (Pink) and DSAR (Yellow) shortcuts
   - "AI Governance & Data Protection" card should now have ~10 links

---

# AlphaX GRC v2.1.1 — Cyber Risk Quantification + KPI Cleanup

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v2.1.1

Two items, both built on public methodology only — no proprietary
datasets, no commercial benchmarks.

### 1. Cyber Risk Quantification (CRQ) — `GRC CRQ Scenario` doctype

Implements **FAIR** (Factor Analysis of Information Risk, published by
The Open Group as the O-RA Risk Analysis open standard) and
**NIST SP 800-30** (US federal Guide for Conducting Risk Assessments,
public domain) in a single quantitative scenario record.

**Inputs (user-provided):**

- **Threat side**: threat event name, threat actor type
  (Nation State / Organized Crime / Cybercriminal / Hacktivist /
  Insider — Malicious / Insider — Negligent / Competitor / Physical /
  Natural / Other), threat capability (Very Low → Very High), contact
  frequency per year
- **Vulnerability side**: vulnerability summary, control strength
  (Very Low → Very High)
- **Loss magnitude (3-point estimate)**: minimum, most likely, maximum
- **Loss categories**: Productivity / Response / Replacement / Fines &
  Judgements / Reputation / Competitive Advantage

**Auto-computed (FAIR formulas):**

- **Threat Event Frequency** = Contact Frequency × threat capability factor
- **Vulnerability** % = function of (threat capability − control strength)
- **Loss Event Frequency** = TEF × Vulnerability
- **Single Loss Expectancy** = PERT-beta of (min, most_likely, max)
  using `(min + 4*ml + max) / 6`
- **Annual Loss Expectancy** = LEF × SLE

**Auto-classified (NIST SP 800-30 5×5 matrix):**

- **Likelihood band** mapped from Loss Event Frequency
- **Impact band** mapped from Single Loss Expectancy
  (SAR-denominated thresholds for KSA-first context)
- **Inherent Risk Rating** (Low / Moderate / High / Very High)
  per the published 800-30 matrix
- **Residual Risk Rating** — defaults to inherent, override after
  applying additional treatments

**Treatment recommendation** field captures the chosen response
(Mitigate / Transfer / Avoid / Accept) with notes.

### 2. CRQ Dashboard page `/app/grc-crq-dashboard`

Three components:

- **Hero stats**: total scenarios, total ALE per year, max single-event
  loss, client scope
- **Top scenarios table** sorted by Annual Loss Expectancy with risk
  rating pills, LEF, SLE, ALE — click any row to open the scenario
- **Inherent risk mix** (stacked bar across Low / Moderate / High /
  Very High)
- **Loss curve** SVG visualization — each scenario as a bar height-
  scaled to its ALE, color-coded by inherent risk rating

### 3. `compute_live_ciso_kpis` — explicit skipped reporting

Previously the live KPI compute function silently swallowed errors when
a source doctype was missing (e.g. `GRC Vulnerability` is referenced by
the MTTR KPI but isn't an installed doctype in this app). v2.1.1 adds
explicit reporting:

```json
{
  "Asset Inventory Coverage": { "value": 0.0, "target": 95, ... },
  "skipped_kpis": [
    {
      "kpi": "Mean Time To Remediate (MTTR)",
      "reason": "GRC Vulnerability doctype not present in this app — MTTR
                 computation requires that doctype. Track manually or
                 add the doctype in a future release."
    }
  ],
  "computed_at": "..."
}
```

This makes it obvious which KPIs are limited by data availability vs.
genuinely 0%.

### 4. v196 diagnostic updated

`v196_check_missing_doctypes` now expects 36 doctypes (was 35 in
v2.1.0), adding `GRC CRQ Scenario`.

### 5. Workspace updates

- 1 new shortcut tile: CRQ (Red)
- 2 new links: CRQ Scenarios (Risk Management group), CRQ Dashboard
  (Dashboards & Pages + Risk Management groups)

Workspace now has 30 shortcuts and 98 links.

## IP boundaries honored

- FAIR is published as an open standard by The Open Group. Math
  formulas are public.
- NIST SP 800-30 is a US federal publication, public domain.
- The qualitative-to-quantitative factor mappings (`_CAPABILITY_FACTOR`)
  follow common industry practice for FAIR implementations and are not
  copied from any specific vendor's tool.
- No proprietary loss datasets, no benchmark imports. Inputs are 100%
  user-provided based on the consultant's own threat modeling.

## Upgrade path

```bash
# Upload alphax_grc_v2_1_1.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate
```

After migrate completes:

1. **Run doctype diagnostic:**
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```
   Expected: `present_count: 36, missing: []`

2. **Run live KPI compute:**
   ```
   /api/method/alphax_grc.install.compute_live_ciso_kpis
   ```
   Should now include `skipped_kpis` field if any source doctypes are
   missing on your site.

3. **Open `/app/grc-crq-dashboard`** — should render with empty-state
   message inviting you to create the first scenario.

4. **Create a CRQ Scenario** to test the math:
   - Set threat capability High, control strength Medium
   - Contact frequency 12 per year
   - Loss min 100,000, most likely 500,000, max 2,000,000
   - Save — observe TEF, vulnerability %, LEF, SLE, ALE auto-compute.

---

# AlphaX GRC v2.1.0 — Framework Expansion

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v2.1.0

Two major framework additions, both built fresh from public-domain
sources. No content lifted from any commercial toolkit.

### 1. NIST CSF 2.0 catalog

`GRC NIST CSF Catalog` doctype seeded with **106 subcategories** across
the 6 NIST CSF 2.0 functions:

- **GV** Govern (31 subcategories — new in 2.0)
- **ID** Identify (21)
- **PR** Protect (22)
- **DE** Detect (11)
- **RS** Respond (13)
- **RC** Recover (8)

Each catalog row carries: subcategory code, function/category codes,
title, outcome statement, **original implementation guidance written
in our own words**, typical evidence artifacts, ISO 27001 cross-
references where applicable. NIST CSF 2.0 is a U.S. federal publication
(NIST), public domain.

`GRC NIST CSF Control` doctype tracks per-client implementation:
implementation tier (Tier 1: Partial through Tier 4: Adaptive),
compliance score, owner, target date, evidence document link, linked
audit findings.

New page `/app/grc-nist-csf-dashboard` shows 6 function cards (color-
coded), each with tier breakdown stacked bar, average implementation %,
click-through to subcategory list filtered by function.

### 2. ISO 22301 BCMS catalog

`GRC ISO22301 Catalog` doctype seeded with **36 clauses** covering all
7 sections of ISO 22301:2019:

- **4** Context of the Organization (4 clauses)
- **5** Leadership (3)
- **6** Planning (3)
- **7** Support (5)
- **8** Operation (16, including 8.2 BIA, 8.3 strategies, 8.4 plans, 8.5 exercises)
- **9** Performance Evaluation (3)
- **10** Improvement (2)

Each clause carries: clause code, section, title, intent statement,
**original implementation guidance** (NOT lifted from CertiKit or any
other commercial toolkit), document-to-prepare codes using
`BCMS-XX-001` pattern parallel to AIMS-XX-001 in ISO 42001.
Cross-references to existing GRC BIA and GRC DR Plan doctypes where
relevant.

`GRC ISO22301 Control` per-client tracker with compliance status,
score, owner, target date, last assessed.

New page `/app/grc-iso22301-dashboard` shows 7 section cards
(color-coded), each with compliance status breakdown, average score,
click-through.

### 3. Framework auto-creation extended

The v2.0.0 engagement-driven auto-create flow (`auto_create_per_client_controls`)
now supports two more frameworks. When you add `NIST CSF 2.0` or
`ISO 22301` to a `GRC Engagement.frameworks_in_scope` field, the
system creates per-client tracking records automatically. Idempotent.

### 4. Framework Select options updated

`GRC Audit Finding`, `GRC Evidence Rule`, `GRC Implementation Task`,
and `GRC Detection Coverage` now have `NIST CSF 2.0` and `ISO 22301`
in their framework Select fields. Existing records preserved.

### 5. Workspace updates

- 2 new shortcut tiles: NIST CSF (Yellow), ISO 22301 BCMS (Green)
- 6 new links in the AI Governance & Data Protection card group
- 2 new links in the Dashboards & Pages card group

Workspace now has 29 shortcuts and 96 links.

### 6. Diagnostic updated

`v196_check_missing_doctypes` now expects:

- 4 new doctypes: NIST CSF Catalog/Control, ISO 22301 Catalog/Control
- 1 v2.0 doctype: GRC Detection Coverage
- Total expected: 35 (was 30 in v1.9.7)

## What's NOT in v2.1.0

Per scope discipline — these are deliberately deferred:

- **Cyber Risk Quantification (CRQ)** — v2.1.1 (FAIR + NIST 800-30,
  Loss Curve dashboard, in-house math)
- **CISO KPI compute cleanup** — v2.1.1 (handle missing GRC Vulnerability
  doctype gracefully, report skipped KPIs)
- **Operational risk module** — v2.2+ (when client demand surfaces)
- **SOX / Financial GRC** — v2.2+ (when public-company engagement
  materializes)

## IP boundaries honored

This release sticks to the IP discipline you set:

- NIST CSF 2.0 content drawn from NIST's public-domain framework
  (clause codes, titles, structure). Implementation guidance is
  original.
- ISO 22301:2019 — clause structure (Sections 4-10, the Annex SL
  high-level structure) is published in marketing material and
  consultancy training. Implementation guidance is original — NOT
  derived from CertiKit's commercial toolkit.
- Document-to-prepare codes use **our** naming convention
  (BCMS-XX-001), not anyone else's.

## Upgrade path

```bash
# Upload alphax_grc_v2_1_0.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate
```

After migrate completes:

1. **Run doctype diagnostic:**
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```
   Expected: `present_count: 35, missing: []`. Should now include all
   v2.1 doctypes.

2. **Verify catalog seeded:**
   - Open `/app/grc-nist-csf-dashboard` — should show 6 function cards
     with totals (GV: 31, ID: 21, PR: 22, DE: 11, RS: 13, RC: 8)
   - Open `/app/grc-iso22301-dashboard` — should show 7 section cards
     with totals matching the 36 clauses

3. **Test framework auto-create:**
   - Open any GRC Engagement
   - Add `NIST CSF 2.0` to `frameworks_in_scope` (comma-separated)
   - Save — should auto-create 106 per-client tracking records

4. **Verify workspace tiles:**
   - Should see NIST CSF (Yellow) and ISO 22301 BCMS (Green) shortcuts
   - "AI Governance & Data Protection" card should now have 10 links
     (was 4)

---

# AlphaX GRC v2.0.0 — Platform Proactivity

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v2.0.0

The first major release in the 2.x series. Theme: **make the platform
do work the consultant used to do manually**. Six items.

### 1. Auto-create per-client controls when an Engagement adopts a framework

Previously: per-client framework controls were created when a Client
Profile was saved, decoupled from any specific consulting engagement.

Now: when a `frameworks_in_scope` value changes on a `GRC Engagement`,
the system automatically creates per-client tracking records for that
client + framework combination. Idempotent — skips frameworks that
are already populated for the client. Confirmation message displayed
after save: "Per-client controls auto-created — ISO 42001: 38 created;
GDPR: 43 created".

Wired in `GRC Engagement.on_update()` via the new module
`alphax_grc.engagement_automation`. Three frameworks supported in v2.0:
ISO 42001, GDPR, NCA ECC-2:2024. NIST CSF and ISO 22301 added in v2.1.

### 2. Auto-generate Implementation Tasks from new Findings

When a `GRC Audit Finding` is created with status `Open` or transitions
to `In Progress`, the system auto-creates 3-5 `GRC Implementation Task`
records based on the finding's category. Tasks are pre-assigned to the
appropriate team (one of the 9 teams from the v1.8.0 taxonomy), with
priority and due-date offsets that match a typical remediation
workflow.

11 category-specific task templates shipped:

- **Policy** → Draft / Review / Approve / Communicate / Schedule review
- **Procedure** → Document / Owner review / Pilot / Roll out
- **Configuration/System Check** → Identify / Test in sandbox / Apply / Verify
- **Training and Development** → Develop content / Schedule / Deliver / Track
- (plus 7 more, each with its own task template)

Tasks link back to the source finding via `linked_finding`. Idempotent —
won't double-create tasks if they already exist for that finding.
Wired via `doc_events` on GRC Audit Finding (after_insert + on_update).

### 3. AI-assisted phase advancement advisor

New "🤖 Ask Advisor" button on the GRC Engagement form (next to
"▶ Advance Phase"). Click it to get a structured recommendation:

- **Recommendation**: ADVANCE / REVIEW / HOLD (color-coded)
- **Confidence** percentage
- **Reasoning** explaining the call
- **Blockers** list if any
- **AI badge** showing whether alphax_grc_ai contributed analysis,
  or RULE-BASED if running the deterministic fallback alone

The function `alphax_grc.engagement_automation.recommend_phase_advance`
is whitelisted and falls back gracefully if `alphax_grc_ai` is not
installed. The fallback uses the same blocker-detection logic the
core advance_phase method already implements, so the recommendation
is always actionable.

### 4. Detection Coverage doctype

New `GRC Detection Coverage` doctype tracking which controls have
detection rules in place. Per-client. Fields: detection name,
client, framework, control reference, detection type (SIEM Rule /
EDR Rule / DLP Rule / Cloud Guardrail / Network IDS-IPS / Application
Logging / Manual Review), implementation status (Not Implemented /
Planned / In Tuning / Live / Retired), source/tool, SOC use-case
reference (becomes a Link when alphax_soc ships), evidence link,
last-validated date, next-validation due (auto-set 6 months out
when last_validated changes), owner, team, false-positive rate.

Allows a consultant to answer "show me detection coverage for
NCA ECC-2:2024 control 2-12-3" with a list of active detections.

### 5. Annual Audit Calendar with auto-roll-forward

New page `/app/grc-annual-audit-calendar`. Year-at-a-glance + tabular
planner. Three components on one page:

- **Hero stats**: total audits, completed, in progress, planned,
  overdue, recurring templates
- **Year-picker + client-picker** to filter the view
- **12-month calendar strip**: each month shows a count and up to 4
  audit chips colored by status; click any chip to open the audit
- **All-audits table** below: sortable rows with start date, title,
  client, auditor, frequency, status

Plus the **Roll Forward function** (admin-only): a menu action that
clones every recurring-template audit from the source year into the
target year, dated 12 months ahead. Idempotent — won't duplicate
audits already rolled. New API: `roll_forward_recurring`.

The `GRC Audit Plan` doctype gets three new fields:
`frequency` (One-time / Monthly / Quarterly / Semi-Annual / Annual /
Ad-hoc), `is_recurring_template` (check), `parent_audit_plan` (link
to the template if this audit was rolled forward).

### 6. Standard CISO KPI seed pack

11 KPIs auto-seeded on install for the demo client:

| # | KPI | Target | Live Data? |
| - | --- | --- | --- |
| 1 | Asset Inventory Coverage | >95% | ✓ |
| 2 | Security Controls Coverage | >90% | ✓ |
| 3 | Vulnerability Assessment Coverage | >85% | ✓ |
| 4 | Mean Time To Remediate (MTTR) | <100d | ✓ |
| 5 | Cyber Security Incidents Reported | trend | ✓ |
| 6 | Patch Compliance | >90% | manual |
| 7 | Outdated OS / Software | <5% | manual |
| 8 | Phishing Email Open Rate | <3% | manual |
| 9 | Phishing Campaign Failure Rate | RAG | manual |
| 10 | Administrative Access Count | trend | manual |
| 11 | Third-Party Risk Assessment Coverage | 100% | ✓ |

Six of the 11 are wired to live data (✓) — they auto-compute from
existing GRC doctypes (Asset Inventory, NCA ECC Control,
Vulnerability, Incident, Vendor). The remaining 5 require external
feeds (patch management system, phishing platform, PAM) and stay
in manual-entry mode until those integrations are built.

New whitelisted helper:
```
/api/method/alphax_grc.install.compute_live_ciso_kpis
```
Returns current values for all 6 live-data KPIs as JSON, with
target threshold and RAG status.

## Workspace updates

The workspace gains 2 new shortcut tiles (Audit Calendar — Orange,
Detection Coverage — Cyan) and 2 new card body links. Total now:
27 shortcuts, 90 links. The v1.9.4 force-repair on every migrate
ensures these propagate cleanly on upgrade.

## Honest scope notes

What's NOT in v2.0.0 (deliberately deferred):

- **NIST CSF, ISO 22301 catalogs** — v2.1 fresh-build, parallel to ISO
  42001 architecture. ISO 22301 will not be lifted from CertiKit's
  toolkit; original implementation guidance.
- **Cyber Risk Quantification (FAIR / NIST 800-30)** — v2.1.
- **Operational risk module** — v2.2+, when client demand surfaces.
- **SOX / Financial GRC** — v2.2+, when a public-company engagement
  materializes.

## Upgrade path

```bash
# Upload alphax_grc_v2_0_0.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate
```

After migrate completes:

1. Run the doctype diagnostic (carryover from v1.9.6):
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```
   Should show new doctype `GRC Detection Coverage` in the present list.

2. Compute live CISO KPIs (carryover for verification):
   ```
   /api/method/alphax_grc.install.compute_live_ciso_kpis
   ```
   Returns current values for the 6 live KPIs.

3. Open `/app/grc-annual-audit-calendar` and confirm the calendar renders.

4. Open any existing GRC Engagement and confirm the "🤖 Ask Advisor"
   button appears next to "Advance Phase".

5. Mark a GRC Audit Plan as `is_recurring_template = 1`, set its
   frequency to Annual, then test the "Roll recurring audits forward"
   menu action on the calendar page.

---

# AlphaX GRC v1.9.7 — Hotfix: Doctype recovery + phantom reference

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What v1.9.7 fixes

**Bug 1:** Two doctypes (`GRC Aramco Third Party Profile` and `GRC
Aramco Incident Notification`) had been deleted from the database in
some prior version, and Frappe's automatic migration does not
re-register doctypes that were once removed. Result: opening an Aramco
CCC Engagement form raised "Field third_party_profile is referring to
non-existing doctype GRC Aramco Third Party Profile."

**Bug 2:** v1.9.6's diagnostic helper `v196_check_missing_doctypes`
listed `GRC Audit Engagement` in its expected list, but no such
doctype exists in the source. Phantom reference left over from an
earlier draft. The branded print format seeder also referenced it.
Result: diagnostic always showed it as missing even when the site
was healthy.

## Three fixes in v1.9.7

**Fix 1: Auto-recreate missing doctypes during after_migrate.**

A new function `v197_recreate_missing_doctypes` runs at the start of
`after_migrate` (BEFORE workspace repair, since workspace links
reference doctypes that need to exist). It walks every doctype folder
in the source, reads the JSON, checks if the DocType row exists in the
database, and force-imports it if not. Uses Frappe's
`import_file_by_path` API which is the standard pattern for
recovering deleted doctypes.

The function is non-fatal (wrapped in try/except). If recovery fails,
migration still completes and an error is logged.

**Fix 2: Removed phantom `GRC Audit Engagement` reference.**

Cleaned out of:
- `v196_check_missing_doctypes` expected list
- `BRANDED_PRINT_DOCTYPES` in print format seeder

**Fix 3: New whitelisted recovery URL.**

```
/api/method/alphax_grc.install.v197_force_recreate_missing_doctypes
```

System-Manager-only. Returns a JSON report:
```json
{
  "ok": true,
  "recreated_count": 2,
  "recreated": ["GRC Aramco Third Party Profile",
                "GRC Aramco Incident Notification"],
  "already_present": 82,
  "failed_count": 0,
  "failed": []
}
```

## "Value missing for GRC Audit Finding: Finding Title" error

This second error in the user's screenshot is most likely a cascading
symptom of the missing-doctype error. When Frappe fails to load
`third_party_profile` link target, the form rendering may fall through
to a different code path that triggers Audit Finding validation. After
v1.9.7 fixes the missing doctypes, the Finding Title error should
also disappear.

If the Audit Finding error persists after v1.9.7 install, please share
the exact page/action that triggers it so it can be diagnosed
independently.

## Upgrade path

```bash
# Upload alphax_grc_v1_9_7.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate
```

After migrate, verify with the diagnostic:
```
/api/method/alphax_grc.install.v196_check_missing_doctypes
```

Expected: `"missing": []` and `"present_count": 30`.

If any doctypes are still missing, manually trigger recreation:
```
/api/method/alphax_grc.install.v197_force_recreate_missing_doctypes
```

---

# AlphaX GRC v1.9.6 — Hotfix: Migration sequencing

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What v1.9.6 fixes

**Bug:** Users on v1.9.4 / v1.9.5 reported the error:
"Field third_party_profile is referring to non-existing doctype
GRC Aramco Third Party Profile" when loading some Aramco-related forms.
Root cause was a sequencing issue introduced in v1.9.4.

**Root cause:** v1.9.4 added a `before_migrate` hook that ran the
workspace + theme repair function. `before_migrate` runs BEFORE Frappe's
doctype migration phase. If the repair raised any exception, it could
abort the entire migration cycle — leaving the site with stale
half-migrated state where some doctypes exist (records reference them)
but the DocType meta records weren't installed.

**Fix — three changes:**

1. **Moved repair from `before_migrate` to `after_migrate`.** Doctypes
   are now installed/upgraded by Frappe's normal migration path FIRST,
   then the workspace + theme repair runs. If repair fails, doctypes
   are still in good state.

2. **Wrapped `v194_run_repair_on_migrate` in defensive try/except** at
   the call site. If repair raises any exception, it logs the trace
   but does NOT propagate. Migration always completes cleanly.

3. **Added `v196_check_missing_doctypes` whitelisted helper** for
   diagnosing when migration partially failed:
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```
   Returns a list of expected AlphaX GRC doctypes vs what's actually
   present in the database, so you can see what failed to install.

## What this hotfix does NOT do

It does NOT auto-create missing doctypes. If your site is already
half-migrated from a v1.9.4 / v1.9.5 install, you'll need to:

1. Upload v1.9.6 zip
2. Click Migrate in Frappe Cloud (or `bench migrate`)
3. Migration completes cleanly (no early abort)
4. Run the diagnostic to confirm all doctypes are present:
   ```
   /api/method/alphax_grc.install.v196_check_missing_doctypes
   ```

If `missing` is empty, the site is healthy.
If `missing` has entries, share the list with support — those doctypes
need a clean re-register, which Frappe's normal migration should
handle on the next run.

## Upgrade path

```bash
# Upload alphax_grc_v1_9_6.zip via Frappe Cloud → Apps → Update from .zip
# Click Migrate. Migration runs cleanly.
# After migrate, the v194 force-repair runs and re-applies workspace + theme.
```

Diagnostic URLs unchanged from v1.9.5:
```
# What's missing from the workspace
/api/method/alphax_grc.install.workspace_diagnostic

# What's missing from doctype list (NEW in v1.9.6)
/api/method/alphax_grc.install.v196_check_missing_doctypes

# Force-trigger workspace + theme repair (manual, for ad-hoc fix)
/api/method/alphax_grc.install.v194_force_repair
```

---

# AlphaX GRC v1.9.5 — Hotfix: Stale doctype references

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's fixed in v1.9.5

**Bug:** v1.9.4's `v194_force_repair` failed with this error on real
sites: "Could not find Row #N: Link To: GRC NCA Policy Library, Row #N:
Link To: GRC NCA Standard Library, ..." — 11 stale doctype references
in the shipped workspace JSON pointed at doctypes that don't exist on
the user's installation. The save aborted on the first invalid row,
leaving the workspace links field unchanged.

**Root cause:** The shipped workspace JSON had accumulated 80 link
entries across v1.4–v1.9 releases, including 11 references to doctypes
that were either renamed, consolidated, or removed in earlier minor
releases. v1.9.4's force-overwrite logic didn't validate targets before
appending them — Frappe's `save()` then rejected the entire workspace
record on the first invalid row.

**Fix — two parts:**

**1. Cleaned workspace JSON.** Removed the 11 stale link references
from the shipped `alphax_grc.json`. Workspace now has 88 links (was 99
in v1.9.4) and the same 12 card-break sections. The 11 removed entries:
- GRC NCA Policy Library
- GRC NCA Standard Library
- GRC NCA Procedure Library
- GRC NCA Form Library
- GRC Regulatory Obligation
- GRC ISO27001 Document
- GRC Privacy Processing Activity
- GRC Data Subject Request
- GRC Aramco Third Party Profile
- GRC Board Report
- GRC Aramco Incident Notification

If any of these doctypes return in a future release, they'll be re-added
to the workspace at that point.

**2. Defensive validation in `v194_force_repair`.** Both the shortcuts
and links replacement now check `frappe.db.exists()` for each target
before appending. Non-existent targets are skipped silently and reported
in the JSON response under `skipped_stale_shortcuts` / `skipped_stale_links`.
This means future shipped JSON with stale references won't break the
repair function — it'll just skip them and log what was skipped.

Plus: empty Card Break entries (no subsequent Link before next Card
Break) are dropped automatically so the body doesn't show empty
section headers.

## What you should see after v1.9.5

Run the repair via API URL again:
```
https://neo15.k.frappe.cloud/api/method/alphax_grc.install.v194_force_repair
```

Expected response:
```json
{
  "workspace_repaired": true,
  "theme_applied": true,
  "shortcuts_count": 25,
  "links_count": 88
}
```

If `skipped_stale_links` or `skipped_stale_shortcuts` are present in the
response, those entries existed in the shipped JSON but not on your site
— they're now silently dropped and the rest of the workspace updates
correctly.

## Upgrade path

```bash
# Upload alphax_grc_v1_9_5.zip via Frappe Cloud → Apps → Update from .zip
```

The `before_migrate` hook from v1.9.4 fires automatically on the next
migrate, calls the now-defensive repair function, and the workspace
links persist correctly. Then hard-refresh the browser to see the
updated body cards.

---

# AlphaX GRC v1.9.4 — Workspace + Theme Repair Release

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What v1.9.4 fixes

A repair release. v1.7.0 through v1.9.3 added many new doctypes, pages,
and shortcuts — but the workspace `links` (the cards-section body) and
the `content` layout were never updated to match. Result: workspaces on
upgraded sites looked like v1.5-era even when running v1.9.3.

This release ships four concrete fixes:

### 1. Workspace cards/body now reflect v1.7-1.9 additions

The workspace `links` array grew from 80 to 99 entries. New entries:
- 5 v1.7+ pages added to the existing "Dashboards & Pages" card
  (Consultant Cockpit, ISO 42001 Dashboard, Continuous Monitoring,
  Enterprise Risk Summary, GDPR Dashboard)
- 3 new card-break groups appended:
  - **Engagement Lifecycle** (5 links: Engagements, Implementation Tasks,
    Document Publication, Phase Templates, Decision Log)
  - **Continuous Monitoring** (2 links: Evidence Rules, Rule Evaluations)
  - **AI Governance & Data Protection** (4 links: ISO 42001 Catalog
    + per-client tracking, GDPR Catalog + per-client tracking)

The workspace `content` (cards layout JSON) was extended with three
matching card references plus a section spacer/header.

### 2. Auto-run repair on every `bench migrate`

A new `before_migrate` hook (`alphax_grc.install.v194_run_repair_on_migrate`)
fires on every `bench migrate` and runs `v194_force_repair`:

- **Force-overwrites** the workspace shortcuts/links/content from the
  shipped JSON (no idempotent check — repair-style, always applies)
- **Auto-applies Odoo Mauve theme** — only if user is not on "Custom"
- **Clears caches** — workspace + document cache so changes are visible

This means future workspace structure changes will propagate
automatically on `migrate`, no API URL or manual intervention needed.

### 3. Fixed `{total_count}` literal placeholder bug

5 shortcut tiles (Clients, Risk Register, Audit Findings, Incidents,
ITGC Controls) had `format='{total_count}'` set but no `stats_filter`.
Frappe's render engine substitutes `{total_count}` only when
`stats_filter` is non-empty. Fixed by setting `stats_filter='{}'`
(empty filter — counts all records of that doctype).

### 4. Fixed Evidence Rule shortcut wrong-type

The Evidence Rule shortcut was registered with `type='Page'` but
`GRC Evidence Rule` is a DocType. Diagnostic in v1.9.1 reported it as
missing because the (link_to, type) tuple didn't match. Fixed.

## What v1.9.4 does NOT fix

The 403 on `/api/method/alphax_grc.install.seed_v191_apply_odoo_mauve`
is now moot — the theme is auto-applied via `before_migrate` instead
of needing to be triggered via API URL. The whitelisted function still
exists for diagnostic purposes but you no longer need to call it.

## Upgrade path

```bash
# Upload alphax_grc_v1_9_4.zip via Bench → Apps → Update from .zip
# Frappe Cloud Standard tier: just click "Update" in the Apps panel
```

The `before_migrate` hook fires automatically. Within seconds of the
update completing:
- Workspace shortcuts are force-replaced from shipped JSON
- Workspace links + content layout are force-replaced
- Theme switches to Odoo Mauve (unless user selected "Custom")
- Caches cleared

After the update completes, **hard-refresh your browser**
(Ctrl+Shift+Delete → Cached images and files → All time → Clear; then
reload `/app/alphax-grc`). The new layout should appear.

## What you should see after v1.9.4

- 25 colored shortcut tiles at the top, including 5 with count badges
  (Clients, Risk Register, Audit Findings, Incidents, ITGC Controls)
  showing actual numbers instead of `{total_count}`
- 12 card-break sections in the workspace body (was 9), with new
  groups for Engagement Lifecycle, Continuous Monitoring, and
  AI Governance & Data Protection
- Mauve color theme applied throughout (`#714B67` primary)

If any of these are still missing after a hard browser refresh, run
the diagnostic via API URL:

```
https://<your-site>/api/method/alphax_grc.install.workspace_diagnostic
```

---

# AlphaX GRC v1.9.3 — Cockpit Orientation Rail

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v1.9.3

A small, focused UX addition. No new doctypes. No schema changes. One
new component on the Consultant Cockpit page.

### "How AlphaX GRC Works" orientation rail

Inserted between the hero banner and the toolbar on `/app/grc-consultant-inbox`.
Four numbered steps connected by a horizontal line, in the same visual
style as a marketing landing page but pointing at internal pages:

1. **Onboard the client** — Capture profile, sector, scope, risk appetite
   → Routes to `GRC Client Profile` list (or `+ New` if no clients exist yet)
2. **Run the engagement** — Lifecycle phases drive every step
   → Routes to `GRC Engagement` list (or `+ New` if none exist)
3. **Track posture live** — Continuous control monitoring
   → Routes to `/app/grc-ccm-dashboard`
4. **Deliver to the board** — Enterprise risk summary + audit pack
   → Routes to `/app/grc-enterprise-risk-summary`

Each step is clickable. Hover lifts the circle into the primary mauve
color and underlines the title. Live count badges appear on each step
when there's something to act on (active engagements, rule failures,
open findings, clients onboarded).

### Why this exists

Per user feedback: "user should not go here and there — that's all my
concern." The orientation rail is the welcome mat that tells a new
consultant the four-step flow of the app and gets them to the right
document level in one click. Smart routing means a consultant who has
no clients yet jumps straight to "+ New Client Profile"; one with
clients goes to the list view.

### Backend change

Added `total_clients` to the inbox `summary` payload so step 1 can route
intelligently between list view and new-doc form. Defensive: wrapped in
try/except so missing client doctype doesn't break the inbox.

### Scope discipline

This widget is internal-only — consultant-facing. AlphaX GRC remains
an exclusive GRC platform for IRSAA's consulting practice. No public
self-service quizzes, no marketing widgets, no scope creep into adjacent
domains. If a future need surfaces for a public lead-gen compliance
self-assessment, that is a separate IRSAA website project, not an
AlphaX GRC feature.

## Upgrade path

```bash
# Upload alphax_grc_v1_9_3.zip via Bench → Apps → Update from .zip
bench --site <site> migrate
# Hard-refresh browser to pick up the updated cockpit JS
```

No data migration. No new doctypes. Pure additive UI.

---

# AlphaX GRC v1.9.2 — Hotfix: GRC Audit Finding framework field

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's fixed in v1.9.2

**Bug fixed:** v1.9.0 introduced a corruption in the `framework` field on the
`GRC Audit Finding` doctype. The field was a Link pointing to the legacy
`GRC Framework` doctype, and v1.9.0's GDPR-rollout script accidentally
appended `\nGDPR` to its options string — turning a valid Link target into
the malformed value `GRC Framework\nGDPR`. On install, this surfaced as:

```
DocType GRC Framework GDPR not found
```

**Root cause:** Field-type confusion. The script that added GDPR to framework
fields treated all of them as Select fields (where `\n` is the option
separator). The Audit Finding `framework` was actually a Link field
(where `options` is a single doctype name). The script corrupted just
that one field; all other framework Selects (Evidence Rule, Implementation
Task) were correctly handled.

**Fix:** Converted the Audit Finding `framework` field from Link →
Select with the same option set as Evidence Rule and Implementation Task:

```
NCA ECC-2:2024
ISO 27001
ISO 42001
Aramco SACS-002
PDPL
GDPR
Custom
```

**Data preservation:** Existing values in the database column are
preserved across the Link → Select conversion. Frappe stores both
fieldtypes as VARCHAR. Any value that's still in the new option list
(e.g. "ISO 27001", "NCA ECC-2:2024") will display correctly. The only
edge case: if a record had `framework = "GRC Framework"` (the literal
broken Link reference), that string is not in the new Select options
and will display as blank — re-select the correct value manually.

**No schema migration required** beyond Frappe's built-in `bench migrate`.

## Upgrade path from v1.9.0 / v1.9.1

```bash
# Upload alphax_grc_v1_9_2.zip via Bench → Apps → Update from .zip
bench --site <site> migrate
```

Frappe will detect the field-type change and apply it automatically.

---

# AlphaX GRC v1.9.1 — Odoo Mauve Theme + Workspace Diagnostic

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v1.9.1

A small theme + diagnostic release. No new doctypes, no schema changes.

### 1. New "Odoo Mauve" theme preset

A 6th theme preset using the palette `#714B67 / #875A7B / #DBCED9 / #EAE5E9`.
Available in `/app/grc-theme-settings` from the Theme Preset dropdown alongside
the existing AlphaX Navy, Saudi Green, Corporate Blue, Dark Mode, and Sand &
Gold options.

**Default for new installs.** Odoo Mauve is now the default preset for
fresh installs (was AlphaX Navy in v1.9.0 and earlier).

**One-time migration for existing v1.9.0 installs.** A new bootstrap step
`seed_v191_apply_odoo_mauve` switches the active theme to Odoo Mauve on
upgrade — but ONLY if the user has not deliberately set theme_preset to
"Custom". Idempotent (uses a default-flag to avoid re-running). To revert,
simply pick a different preset from the dropdown.

**Risk colors are deliberately unchanged.** Critical / High / Medium / Low
remain `#DC2626 / #D97706 / #F59E0B / #16A34A` because risk-rating colors
should not follow brand palette — accessibility and audit-fairness require
red-means-red regardless of theme.

### 2. Workspace diagnostic + re-seeder

Some users on v1.7.0 / v1.8.0 / v1.9.0 reported that new tiles
(Continuous Monitoring, ISO 42001, Consultant Cockpit, Engagements,
Tasks, Enterprise Risk Summary, GDPR) did not appear in the workspace
even though the underlying pages and doctypes installed correctly.
This is a known Frappe quirk where the workspace JSON record is
sometimes not refreshed when an app's workspace fixture changes.

Two new whitelisted helpers in `install.py`:

```bash
# Report what tiles SHOULD exist vs what's in the workspace
bench --site <site-name> execute alphax_grc.install.workspace_diagnostic

# Re-seed missing tiles from the shipped workspace JSON
bench --site <site-name> execute alphax_grc.install.reseed_workspace_shortcuts
```

Both are idempotent. The re-seeder only adds missing tiles; it never
removes existing ones, so user customizations are preserved.

### Usage

After upgrading to v1.9.1:

1. Open `/app/alphax-grc` and verify you see all 25 tiles. If not:
2. Run `bench --site <site> execute alphax_grc.install.workspace_diagnostic`
   to see what's missing.
3. Run `bench --site <site> execute alphax_grc.install.reseed_workspace_shortcuts`
   to fix it.
4. Open `/app/grc-theme-settings` and verify the Theme Preset dropdown
   has "Odoo Mauve" selected. Hard-refresh your browser (Ctrl+Shift+R) to
   pick up the new CSS variables.

---

# AlphaX GRC v1.7.0 — ISO 42001 + Continuous Control Monitoring + Visual Feast UI

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v1.7.0

This release introduces three substantial capability additions:

### 1. ISO 42001:2023 — AI Management System framework

Now AlphaX GRC supports the third major framework alongside NCA ECC-2:2024
and ISO 27001. Important for any KSA organization using AI or planning to.

- **New doctype `GRC ISO42001 Catalog`** — 38 controls across 9 domains
  (A.2 AI Policies → A.10 Third Party Relationships). Each control carries
  implementation guidance and a document-to-prepare code in the standard
  AIMS-XXX-001 naming convention (e.g. AIMS-POL-001 for AI Policy Document).
  Cross-references to related ISO standards (ISO 23894, ISO 5259, ISO 22989,
  etc.) where applicable.

- **New doctype `GRC ISO42001 Control`** — per-client tracking. When a Client
  Profile adopts ISO 42001, 38 records are auto-created. Each carries
  compliance status, score, owner, target date, and AI-system-scope field
  for documenting which AI systems the control applies to.

- **New page `/app/grc-iso42001-dashboard`** — branded dashboard with
  hero stats, 9 domain cards (each with unique gradient color), domain
  implementation progress bars, drilldown table per domain showing control
  code, title, implementation guidance preview, AIMS doc code pill, and
  status chip.

### 2. Continuous Control Monitoring (CCM) + ERPNext integration

The strategic capability — a one-time-defined Evidence Rule maps a compliance
control to ERPNext data. Once defined, the system continuously monitors
evidence on every save and updates compliance posture automatically. Auto-
creates Audit Findings when rules fail.

- **New doctype `GRC Evidence Rule`** — the rule definition. Specifies
  source ERPNext doctype, filters, evaluation logic (5 types), failure
  actions (auto-create Finding with severity + assignee), and schedule
  (real-time on save + daily scheduler).

- **5 evaluation types**: Field Must Be Set, Field Must Equal Value,
  Field Must Be Within Days, Minimum Record Count, No Records Allowed.
  More can be added without code changes by extending the `_evaluate_record`
  method.

- **New doctype `GRC Evidence Rule Evaluation`** — every evaluation is
  logged with pass/fail counts, failed record IDs, trigger type, and
  link to any auto-created Finding. Provides a complete audit trail of
  continuous monitoring activity.

- **6 sample rules seeded on install** — covering NCA ECC controls
  1-9-3-1 (HR offboarding access revocation), 4-1-2 (vendor cybersecurity
  review), 2-1-1 (asset custodian assignment), 1-3-1 (sales invoice
  ownership), 2-2-3 (disabled user permissions), and ISO 42001 A.2.2 (AI
  policy implementation). All map to standard ERPNext doctypes (Employee,
  Supplier, Asset, User, Sales Invoice).

- **ERPNext doc_events hooks** — Employee, Employee Separation, Sales
  Invoice, Purchase Invoice, Asset, Supplier, User, User Permission, Stock
  Entry, Issue, Project, Activity Log all trigger real-time evaluation
  on save. The trigger function NEVER raises (catches all exceptions) so
  it cannot block legitimate ERPNext operations.

- **Daily scheduler** — re-evaluates every active rule with `evaluate_daily=1`
  every day. Catches drift even for doctypes not in the realtime hook list.

- **New page `/app/grc-ccm-dashboard`** — Continuous Control Monitoring
  dashboard. Hero stats (total rules, failing, perfect-score, never-evaluated,
  avg pass rate). Framework breakdown cards with pass/fail/untested visual
  bars. Recent failures section with red left-border alert cards. Full
  rules table with priority chip, pass-rate visualization, and a "Run"
  button per row for manual re-evaluation.

### 3. Visual Feast UI — comprehensive cross-cutting polish

The most visible change. Every GRC page in the app now has a consistent,
branded visual style.

- **Global theme CSS** (`/assets/alphax_grc/css/grc_global_theme.css`)
  loaded on every page. Defines :root CSS variables and standardized
  classes (`.grc-chip-*`, `.grc-hero`, `.grc-section`, `.grc-card-grid`,
  `.grc-card`, `.grc-progress`).

- **Theme loader JS** (`grc_theme_loader.js`) reads `GRC Theme Settings`
  via the `get_theme` API and injects CSS variables on `:root` at runtime.
  Change the theme via the UI and every page re-themes instantly without
  recompile.

- **Visual feast engine** (`grc_visual_feast.js`) detects the current view
  and applies enhancements — branded chips on list views, animated tile
  hover transitions, branded print headers, form section icons.

- **List views** — all GRC- prefixed doctypes get hover translateX,
  branded header (3px navy top border), branded title color, brand-
  colored checkbox accents, indicator pills replaced with grc-chip
  classes.

- **Form views** — all GRC- prefixed doctypes get card-like layout-main
  with shadow, navy 3px page-head bottom border, branded section heads
  (uppercase + 2px secondary underline + ::before icons by section name),
  branded primary buttons with hover lift + shadow, gradient form
  dashboards.

- **Branded print formats** — generic Jinja template (in
  `print_format/grc_branded_seeder.py`) auto-creates "GRC Branded
  <Doctype>" print formats for 19 transactional doctypes on install.
  Navy/gold gradient header, branded section heads, severity chips,
  confidentiality footer.

- **5 theme presets** (existing, retained from earlier versions): AlphaX
  Navy (Default), Saudi Green, Corporate Blue, Dark Mode, Sand & Gold.
  Switch via `/app/grc-theme-settings`; instantly re-themes every page.

### Honest scope notes

This v1.7.0 release ships the **theme infrastructure and applies it to
the highest-visibility surfaces** — list views, forms, dashboards, and
print formats. There is more visual work that could come in subsequent
releases:

- Some legacy pages (Command Center, Neo Hub) still use their own CSS
  rather than the global theme classes. They render fine but don't
  re-theme dynamically.
- Login screen and Frappe desk chrome (top bar, sidebar) remain
  default Frappe styling. A "custom Frappe theme" via Settings → Theme
  is on the v1.8 roadmap.
- Workspace tile iconography is light — most tiles use Frappe's default
  icon set rather than custom GRC iconography.

These are deliberate scope decisions, not oversights. The v1.7.0 release
prioritizes the cross-cutting impact of the theme system over per-page
polish.

---

# AlphaX GRC v1.5.0 — NCA ECC-2:2024 Upgrade

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's new in v1.5.0

**The major credibility upgrade: NCA ECC-2:2024.** Prior versions of
AlphaX GRC referenced ECC-1:2018 vintage. ECC-2:2024 is the current
Saudi National Cybersecurity Authority standard and what NCA assesses
against in 2026. This release upgrades the framework support
end-to-end.

### What's in the upgrade

- **New doctype `GRC NCA ECC2 Catalog`** — the master ECC-2:2024
  control library. 198 controls across 4 domains and 31 subdomains.
  Bilingual (Arabic + English). Each control carries the official NCA
  GECC-2024 implementation method, related tools, and expected output
  text verbatim from the NCA spreadsheet. Read-mostly catalog (admins
  can edit; consultants/auditors read-only).

- **Per-client tracking enhanced** — the existing
  `GRC NCA ECC Control` doctype gains 14 new fields matching the
  official GECC-2024 14-column compliance workflow: sub-control
  compliance status (with the official Arabic/English options),
  compliance classification, related tools used, implementation method
  used, expected output / evidence produced, responsible department,
  corrective actions, department notes, cybersecurity department
  notes, last review date, plus a Link to the ECC2 Catalog so per-
  client records reference the master library.

- **New page `/app/grc-ecc2-dashboard`** — branded ECC-2:2024
  dashboard. Tri-colour gradient hero (governance blue, defense red,
  resilience green). Stat cards for total controls, main controls,
  sub-controls, domains. Four colour-coded domain cards (one per
  domain — click to filter subdomains). Subdomain grid showing 31
  subdomains as cards with control counts; if a client is selected,
  each card shows a per-subdomain implementation progress bar
  (Implemented / Partial / Not Implemented / N/A / Untracked) with
  legend. Click any subdomain to drill into its controls in a table
  showing code, control text, implementation method, and status —
  with EN⇄AR language toggle that switches the entire view.

### Data sourcing — honest notes

**The catalog content is sourced from two official NCA documents:**
1. The official NCA GECC-2024 Excel spreadsheet (control codes,
   bilingual control text, implementation method, related tools,
   expected output) — verbatim Arabic, with English where the
   spreadsheet provides it.
2. The NCA ECC-2:2024 Training Content guide (English implementation
   narrative for ~61 of the 198 controls — the ones the training doc
   discusses by name).

The remaining ~137 controls have full Arabic content (verbatim NCA)
but only partial or no English narrative. This is honest: NCA's
authoritative text is Arabic. Where English exists in the source, we
ship it. Where it doesn't, the field is blank rather than fabricated.

If you need English implementation guidance for the controls without
narrative, you can:
- Add it manually via the catalog form (we'll never overwrite admin
  edits)
- Use the `alphax_grc_ai` PoC app (v0.1.0 in your library) to
  generate draft English text from the Arabic source, with human
  review

### Domain structure (matches official NCA ECC-2:2024)

- **Domain 1 — Cybersecurity Governance** (10 subdomains): Strategy,
  Management, Policies & Procedures, Roles & Responsibilities, Risk
  Management, IT Project Management, Compliance with Standards,
  Periodical Review & Audit, HR Cybersecurity, Awareness & Training
- **Domain 2 — Cybersecurity Defense** (15 subdomains): Asset
  Management, IAM, Information Systems Protection, Email Protection,
  Networks Security, Mobile Devices, Data & Information Protection,
  Cryptography, Backup & Recovery, Vulnerabilities Management, Pen
  Testing, Event Logs & Monitoring, Incident & Threat Management,
  Physical Security, Web Application Security
- **Domain 3 — Cybersecurity Resilience** (varies): BCM aspects of
  cybersecurity, continuity testing, recovery procedures, disaster
  recovery
- **Domain 4 — Third-Party & Cloud** (2 subdomains): Third-Party
  Cybersecurity, Cloud Computing & Hosting Cybersecurity

### Sample data on install

198 ECC-2:2024 catalog records seeded automatically. The DEMO Client
Profile is created as before; per-client tracking starts empty so you
can demonstrate the onboarding flow.

### Wiring

- New page `grc-ecc2-dashboard` registered.
- `GRC NCA ECC2 Catalog` added to `WATCHED_DOCTYPES` so dashboard
  snapshots refresh on catalog edits.
- Workspace gains a "NCA ECC-2:2024" shortcut tile at the top.
- Bootstrap step `seed_ecc2_2024_catalog` runs on install/migrate.
  Idempotent — re-running won't duplicate.

## Install / Upgrade

For sites already running v1.4.4 with clean data:

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade:
1. Open `/app/grc-ecc2-dashboard` to see the catalog and domain cards
2. Pick a client from the dropdown to layer in implementation status
3. Click any domain card → focuses subdomains
4. Click any subdomain card → drills into its controls
5. Toggle العربية ⇄ English to switch language

## What's coming next (separate releases)

- **v1.6.0** — ISO 42001:2023 AI Management System framework support
  (38 controls across 9 domains, public-domain implementation
  guidance from the implementation guide PDF you provided)
- **v1.7.0** — Regulator Inspection Mode: one-click NCA evidence pack
  generation (controls list + evidence document for each + compliance
  scoring + audit history → PDF)
- **alphax_soc v0.1.0** — separate sister app for SOC operations
  (alert ingestion, incident triage, SIEM integration)
- **UI polish pass** — the "eye-feast" cross-cutting visual refresh

## What's fixed in v1.4.4

**Hotfix for v1.4.3 install crash.** The doctype `GRC Aramco SACS-002
Control` failed to install because Frappe's module-name autoresolver
expects a hyphen in a doctype name to map to an underscore in the
folder path. The shipped folder was `grc_aramco_sacs002_control` (no
underscore between `sacs` and `002`), but Frappe was looking for
`grc_aramco_sacs_002_control` (with the underscore). Result: install
crashed at step 55 of 88 with `ImportError: No module named
'alphax_grc.alphax_grc.doctype.grc_aramco_sacs_002_control'`.

Fix: renamed the doctype itself from `GRC Aramco SACS-002 Control` to
`GRC Aramco SACS002 Control` (no hyphen). The folder name is now
correct as-is. Avoids any future special-character resolution issues
with this doctype.

User-facing labels still display "SACS-002" in menu items, error
messages, and READMEs — the rename only affects the internal doctype
identifier. The framework being assessed is still SACS-002.

## What's in this build

Everything from v1.4.3 — Aramco CCC complete process automation —
remains intact:

- 5 Aramco doctypes (Engagement, Certificate, SACS002 Control,
  Control Assessment, Audit Firm)
- 28 placeholder SACS-002 controls across 14 domains
- Renewal automation (180/90/30/0-day alerts) with per-cert send tracking
- Incident automation (4-hour initial + 72-hour final reports)
- Aramco CCC dashboard at `/app/grc-aramco-ccc` with the clickable
  8-stage process wheel and stage drilldown
- All v1.4.x NCA toolkit, multi-tenant, lifecycle features

## Install / Upgrade

If your v1.4.3 install crashed mid-sync (as the user's
`neoterminal.k.frappe.cloud` did), the database is in a partial state.
Recommended: uninstall and reinstall.

```bash
# Clean the partial v1.4.3 install:
bench --site neoterminal.k.frappe.cloud uninstall-app alphax_grc --force

# Get the v1.4.4 zip:
bench get-app alphax_grc <url-of-this-zip>

# Install fresh:
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
bench restart
```

If you're upgrading from a clean v1.4.1 or v1.4.2 (before v1.4.3's
crash), a normal migrate works:

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

## What's new in v1.4.3

This release builds out the **Saudi Aramco Cybersecurity Compliance
Certificate (CCC)** lifecycle: scoping, SACS-002 self-assessment, audit,
findings, remediation, certification, and renewal — all with email
automation and a dedicated dashboard.

### Honest scoping note

The full SACS-002 control catalog is not freely downloadable (it's a
licensed Aramco document). v1.4.3 ships **28 placeholder controls across
all 14 SACS-002 domains**, each marked `is_placeholder=True`. Once you
provide the licensed SACS-002 PDF/Excel, an admin action can replace the
placeholders with verbatim control text. The framework structure,
workflow, dashboard, and notification automation work fully today; only
the control text is placeholder.

Audit firm directory is also placeholder — populate from your knowledge
of Aramco-accredited firms.

### New doctypes

- **GRC Aramco CCC Engagement** — umbrella record per vendor per
  certification cycle. Status workflow: Scoping → Self-Assessment →
  Audit Scheduled → Audit In Progress → Findings → Remediation →
  Certified → Renewal Due → Lapsed. Auto-status transitions based on
  dates. Auto-computed compliance % from control assessments. Includes
  `populate_controls_from_library()` action that bulk-loads applicable
  SACS-002 controls based on the engagement's tier (Critical / High /
  Medium / Low).

- **GRC Aramco SACS-002 Control** — global control library scaffolded
  with 28 placeholder controls organised by 14 SACS-002 domains
  (Asset Management, Access Control, Cryptography, Physical Security,
  Operations, Communications, System Acquisition Development, Supplier
  Relationships, Incident Management, Business Continuity, Compliance,
  HR Security, Awareness & Training, Governance). Tier applicability,
  cross-mapping to NCA ECC and ISO 27001.

- **GRC Aramco Control Assessment** — child table of CCC Engagement.
  Per-control status (Not Started / In Progress / Compliant /
  Partially Compliant / Non-Compliant / N/A), score, evidence
  attachment, remediation plan, link to GRC Remediation Action.

- **GRC Aramco Certificate** — issued certificate record with
  certificate number, issue/expiry dates, certified scope, audit firm,
  certificate PDF attachment. Auto-computed days_to_expiry,
  renewal_kickoff_date (180 days before expiry), and status
  (Active / Expiring Soon / Pending Renewal / Expired / Revoked).
  Notification tracking fields prevent duplicate emails.

- **GRC Aramco Audit Firm** — accredited assessor directory with
  contact details, accreditation status, accreditation number/dates,
  service classes covered. Default status "Unverified" with a flag to
  verify with Aramco SCM before engaging.

### Renewal automation

Daily scheduler runs `notifications.check_aramco_certificate_renewals()`:

- **180 days before expiry** → "Renewal kickoff" advisory email to lead
  consultant + GRC Admin/Aramco Compliance Owner role users
- **90 days** → "Renewal must now be in progress" attention email
- **30 days** → "URGENT — confirm renewal status" escalation
- **0 days** → "EXPIRED" alert with non-compliance warning

Each tier's email tracks the send date on the certificate
(`last_180day_alert_sent` etc.) so the same alert never fires twice.

### Incident notification automation

- **On create**: `aramco_incident_on_update` doc-event sends an
  immediate "New Aramco-scope incident" email to the lead consultant
  + Aramco Compliance Owners. Marks `initial_notification_sent_on` so
  the 4-hour SLA timer can start.
- **Daily check**: `check_aramco_incident_escalation()` reviews open
  incidents. If 4-hour initial notification not sent, escalates. If
  72-hour final business and technical reports not on file, escalates
  again.

All 4-hour, 24-hour, and 72-hour Aramco SLAs from the CCC programme
are now enforced automatically.

### Aramco CCC dashboard — `/app/grc-aramco-ccc`

Branded dashboard (gradient hero in Aramco colours) showing:
- Hero stats: Engagements / Certificates / Active / Expiring 30 days /
  Expiring 90 days / Expired
- Engagements-by-stage grid (9 status buckets with colour coding)
- **Interactive 8-stage CCC lifecycle wheel** (Scoping → Self-Assessment
  → Audit Scheduled → Audit In Progress → Findings → Remediation →
  Certified → Renewal Due) with live engagement counts per stage,
  red/amber/green status colouring based on engagement distribution,
  and **clickable drilldown** — click any stage in the wheel (or the
  matching row in the side list) to navigate to a filtered list view
  of engagements in that stage, scoped to the active client picker.
- Hover any stage to read what it covers in the side detail panel
- Active engagements table with compliance %, open findings, lead
- Certificates table sorted by expiry, with colour-coded days-to-expiry

Client picker scopes to one engagement or shows firm-wide.

### Wiring

- `GRC Aramco CCC Engagement` and `GRC Aramco Certificate` added to
  `WATCHED_DOCTYPES` so dashboard snapshots refresh on save (live
  system from v1.3.2).
- `GRC Aramco Incident Notification` doc_events wire both notification
  email and dashboard invalidation.
- New page `grc-aramco-ccc` registered in PAGES.
- Workspace gains "Aramco CCC" shortcut tile and 5 new link entries.

### Sample data seeded for DEMO client

- 28 SACS-002 placeholder controls (across 14 domains)
- 1 sample CCC engagement (tier: High, status: Self-Assessment)
- 1 sample certificate (expires in 60 days — triggers the 90-day alert)
- 1 audit firm placeholder

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade:
1. Open `/app/grc-aramco-ccc` to see the dashboard with the sample
   certificate expiring in 60 days.
2. Open the sample engagement; on the form, click the **Populate
   Controls from Library** action (server method) to see all
   applicable SACS-002 controls loaded as assessment rows.
3. The renewal scheduler runs daily — to test it manually:
   `bench --site <site> execute alphax_grc.notifications.check_aramco_certificate_renewals`

## Email configuration

The renewal/incident emails use Frappe's `frappe.sendmail`. Make sure
SMTP / Mailgun / SES is configured at the site level
(/app/email-domain). Without email config, the functions queue silently
and log to `Error Log`.

## Roadmap (v1.5+)

- Replace SACS-002 placeholder controls with verbatim text once
  licensed PDF is provided
- NCA-conformant Excel print formats (Risk Register, Audit Plan,
  Vulnerability Register, KPI Report)
- Bulk replacement action for CCC controls (CSV / Excel import)
- Snapshot trend history for CCC compliance %

## What's new in v1.4.2

The NCA Templates page (`/app/grc-nca-templates`) is fully redesigned.
Same data, better UX.

**Hero stats strip** — gradient header with live counts: total templates,
breakdown by kind, and (when a client is selected) how many are adopted
by that client.

**Sticky toolbar** — search, client picker, and grid/list view toggle
that stays at the top as you scroll.

**Category chips with icons** — replaces the old dropdown filter.
Horizontally scrollable strip of clickable categories: Governance ⚖️,
Access 🔒, Asset 📦, Network 🌐, Application 🧩, Data 💾, Physical 🏛,
Third Party 🤝, Resilience 🛡️, Incident 🚨, Monitoring 📡,
Vulnerability 🐛, Cryptography 🔐. Active category highlights blue,
shows count badge.

**Card redesign** — bigger cards, category-coloured icon, ECC controls
shown as compact monospace chips (first 4 + "+N" indicator), bilingual
title (EN with AR underneath), hover-lift effect, primary action button
prominent.

**Adoption badges** — when a client is selected, cards already adopted
by that client show a green "✓ Adopted" badge in the top-right and a
green left border. The Adopt button for those cards becomes "✓ Adopted"
disabled. Saves the consultant from accidentally creating duplicates.

**"For this client" side panel** — pinned to the right (collapses below
on mobile). Shows the client name, country, sector, overall NCA library
coverage percentage with progress bar, per-kind breakdown (Policies
12/35, Standards 5/34, etc.), and a "Coverage gap analysis" button.

**Bulk action bar** — slides up from the bottom when you tick checkboxes.
Shows the count, plus "Adopt for client" and "Clear" buttons. Drops the
35-click onboarding into 35-checkboxes-and-one-button.

**Grid / list view toggle** — grid view shows responsive cards, list view
shows full-width rows. Useful when you want to scan many templates fast.

**Bilingual EN ⇄ AR toggle** — menu item that switches the page direction
to RTL and shows Arabic labels everywhere (category names, kind names,
hero text). Template names already had Arabic from v1.4.0; v1.4.2 makes
the chrome around them switch too.

**Mobile-responsive** — under ~900px the side panel moves to the top.
Cards reflow to a single column. The previous layout broke at narrow
widths; this one doesn't.

**Theme-aware** — uses Frappe's CSS variables (`--bg-color`,
`--text-color`, `--text-muted`, `--border-color`, `--card-bg`) so it
follows whatever theme the user has set. Hero gradient stays consistent
because it's intentionally branded.

## Backend additions

One new whitelisted endpoint:

- `alphax_grc...grc_nca_templates.get_client_adoption_status(client)` —
  returns the set of NCA template_codes already adopted by the given
  client. Used by the UI to show ✓ badges on cards and progress in the
  side panel. Best-effort name match between adopted Policy/ISMS records
  and library template_name.

All endpoints from v1.4.1 carry through unchanged: `get_template_library`
(self-healing), `force_seed_libraries`, `bulk_adopt_for_client`,
`get_client_policy_coverage`, `adopt_template_for_client`.

## Compatibility

- All 79 NCA templates from v1.4.0 still seeded (35 policies + 34
  standards + 4 procedures + 6 forms).
- Auto-adopt-on-Client-Profile-save from v1.4.1 still works.
- Self-heal on page load from v1.4.1 still works.
- All v1.3.x live dashboards, multi-tenant, lifecycle, etc. unchanged.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade, navigate to `/app/grc-nca-templates`. You should see the
new gradient hero, category chips, and reorganised cards. Pick a client
in the toolbar dropdown to see adoption badges and the side panel
populate.

## What's new in v1.4.1

This release fixes the v1.4.0 "empty NCA library on upgrade" issue and
adds three productivity features for managing multiple policies per client.

**The fix: self-healing NCA Templates page**

In v1.4.0, when upgrading from v1.3.x via `bench migrate`, the new NCA
library doctypes were sometimes synced *after* the bootstrap seeders ran,
causing the seeders to bail (no doctype = no seed) and the NCA Templates
page to show 0/0/0/0 across all four tabs.

v1.4.1 fixes this three ways:
1. When an admin (System Manager / GRC Admin) opens
   `/app/grc-nca-templates`, the page server-side checks whether each
   library is empty and, if so, calls the seeder inline before rendering.
2. A new menu item **"Re-seed NCA library (admin)"** lets admins force a
   re-seed at any time. Idempotent — safe to run repeatedly.
3. A new whitelisted endpoint
   `alphax_grc...grc_nca_templates.force_seed_libraries` exposes the same
   action programmatically.

**New: Bulk adopt selected templates**

Each template card on the NCA Templates page now has a checkbox in the
top-right corner. Tick multiple templates, pick a client in the picker,
then **Menu → "Adopt selected for client…"** creates them all in one
server call. Drops the time to onboard a new client from ~35 clicks to
two checkboxes plus one menu item.

**New: Auto-adopt NCA library on Client Profile save (opt-in)**

`GRC Client Profile` gains 3 new checkboxes in a collapsible
**NCA Library Auto-Adopt** section:
- *Auto-adopt all NCA Policies on save* — creates 35 GRC Policy records
  in Draft status, one per NCA policy template
- *Auto-adopt all NCA Procedures on save* — creates 4 ISMS Document
  Register records for NCA procedures
- *Auto-adopt all NCA Forms on save* — creates 6 ISMS Document Register
  records for NCA forms

Tick the relevant box, save the client, and the system auto-creates
draft records pre-populated from the NCA library. Each checkbox auto-clears
after first use so subsequent saves don't re-trigger. An adoption_status
field shows the result (e.g. "Policy: 35 adopted | Procedure: 4 adopted").

Defaults to **opt-in** (off by default) so consultants stay in control —
turn on for a single client at creation time, leave off for clients
that need a custom subset.

**New: Coverage gap analysis per client**

Menu → **"Coverage gap analysis…"** on the NCA Templates page shows:
- Number of policies adopted for the selected client
- Number of NCA-mapped ECC controls covered
- Number of NCA-mapped ECC controls *not* covered (the gaps)
- Coverage percentage
- Expandable lists of covered and gap controls

Lets the consultant answer the regulator's question *"which ECC controls
do you have a written policy for?"* in one click.

**Confirms: multiple policies per client (this was already supported)**

Just to make this visible in the docs: `GRC Policy` autoname is
`POL-00001`, `POL-00002` and so on. There is no uniqueness constraint
on (client + policy_title) — a single client can have unlimited policies.
The v1.4.1 bulk-adopt and auto-adopt flows make creating many policies
per client effortless.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# Or upgrading from v1.4.0:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade: open `/app/grc-nca-templates`. If the tabs show 0/0/0/0,
the self-heal will trigger automatically on first load. If for any reason
it doesn't, click Menu → **Re-seed NCA library (admin)**.

## What's new in v1.4.0

This is a major content release. The app now ships with the **complete
NCA Cybersecurity Toolkit** (~80 official Saudi NCA templates) pre-loaded
as a browsable, adoptable library, plus three new domain modules
(Vulnerability Register, KPI Reporting, Threat Catalogue) and significant
NCA-conformance enhancements to existing Risk Register and Audit Plan.

### NCA Cybersecurity Toolkit — full library, browsable & adoptable

Source: https://nca.gov.sa/en/regulatory-documents/guidelines-list/cybersecurity-toolkits/
Last NCA update: 26 November 2025

Four new catalogue doctypes seeded with every official template:
- **GRC NCA Policy Library** — 35 NCA Policy templates (Anti-Malware,
  Cloud, Cryptography, Email, IAM, Network, Patch, Penetration Testing,
  Physical, Risk Management, Vulnerabilities, Web Application, etc.)
- **GRC NCA Standard Library** — 34 NCA Standard templates (Cryptography,
  DLP, EDR, IAM, NDR, OT/ICS, Patch, Privileged Access Workstations,
  Web Application, Wireless, etc.)
- **GRC NCA Procedure Library** — 4 NCA Procedure templates
  (Vulnerability Assessment, Cybersecurity Audit, Document Development,
  Risk Management)
- **GRC NCA Form Library** — 6 NCA Forms / Programs / Reports
  (Confidentiality Agreement, Policy Undertaking, IT Project Checklist,
  Software Development Checklist, Awareness Program, Audit Report)

Every entry carries the official NCA Word + PDF download URLs, mapped
ECC controls, and category. Total: **79 official NCA templates** in
the library.

### NCA Templates Library page — `/app/grc-nca-templates`

Tabbed catalogue browser (Policy / Standard / Procedure / Form). Search
by name, ECC control, or category. Each card shows official Word + PDF
download links plus a one-click **Adopt for client** button: pick a
client, click Adopt, and the app creates a draft `GRC Policy` (or
`GRC ISMS Document Register` for non-policy types) pre-populated from
the NCA template.

This means: when a Saudi regulator asks your client *"show me your IAM
policy / your network security standard / your vulnerability assessment
procedure"*, you can produce one based on the official NCA template
within seconds rather than starting from a blank page.

### GRC Vulnerability — NCA Vulnerability Register

New doctype matching NCA's official Vulnerability Register Excel
template. Fields: vulnerability_id, title (EN+AR), CVE number, CVSS
score, vendor link, affected technology, affected assets, threat
analysis, threat severity (1-5), risk likelihood (1-5), risk severity
(1-5), auto-computed risk_level (Critical/High/Medium/Low/Very Low),
owner, status (Open/In Progress/On Hold/Resolved), first observation
date, due date, resolution date, linked_threat (to Threat Catalogue),
linked asset, linked remediation action.

Risk level auto-computes from severity × likelihood, falls back to
CVSS-based mapping when scores aren't entered. Resolution date
auto-fills when status flips to Resolved.

Five sample vulnerabilities seeded for the DEMO client: Zerologon,
ProxyLogon, Log4Shell, Heartbleed, MOVEit SQL injection — each with
correct CVE, CVSS, and threat-catalogue linkage.

### GRC KPI + Quarterly Measurement — NCA KPI Report

New doctype matching NCA's KPI Report Excel template. Parent fields:
kpi_id, indicator_name (EN+AR), cybersecurity_domain (15 NCA domains),
type, frequency, definition, data_source, owner. Child table for
quarterly measurements: year, Q1-Q4 target/actual/notes plus prior
year Q4 actual.

10 NCA cybersecurity domain KPIs seeded (Asset Management, Business
Continuity, Awareness, Event Monitoring, Compliance, IAM, Network
Security, Physical Security, Risk Management, Vulnerability
Management) each with a year of quarterly target/actual data.

### KPI Dashboard page — `/app/grc-kpi-dashboard`

Quarterly target-vs-actual visualisation per KPI. Cards show domain,
indicator, latest year's quarterly bars (actual fill, target marker,
green when meeting target, amber when below), and full numeric
breakdown. Client picker scopes to one engagement or shows firm-wide.

### GRC Threat Catalogue

Global reference doctype seeded with **all 22 NCA standard threats**:
Credential compromise, Insider threats, Asset compromise, Social
engineering, Data breach, Loss of business continuity, Data loss,
Mistaking compliance for protection, Regulatory fines, Outdated
hardware, Vulnerable software, Cloud vulnerabilities, Ransomware,
Malware, IoT attacks, Operational downtime, DDoS, Underestimation of
risk probability, Partial risk assessment, Improper risk management,
Improper incident response, Third party exposure.

Each threat has EN + AR name, category, description, and is_nca_standard
flag. Risk Register and Vulnerability records can link to threats from
this catalogue.

### Enhanced GRC Risk Register (NCA Risk Register conformance)

Added 9 new fields matching NCA's Risk Register Excel template:
- `risk_cause` — description of the inherent risk's cause
- `threat` — Link to GRC Threat Catalogue
- `risk_analysis_consequences` — possible consequences and timescale
- `date_of_risk_identification`
- `date_of_risk_analysis`
- `last_evaluation_date`
- `inherent_rating_accepted` — risk owner acceptance flow (Yes/No)
- `inherent_rating_override_reason` — text shown when accepted=No
- `manual_rating_override` — rating override when accepted=No

Risk rating options extended from 4 levels to NCA's 6 levels:
Critical, High, Medium, Low, **Very Low**, **N/A**.

### Enhanced GRC Audit Plan (NCA Audit Plan conformance)

Added 11 new fields matching NCA's Audit Plan Excel template:
- `audit_id` — A001/A002 for audits, R001/R002 for reviews
- `audit_or_review` — Audit / Review type
- `lead_auditor` — separate from `audit_owner` (sponsor)
- `team_responsible` — Cybersecurity Org / Internal Audit / Third Party
- `audit_methods` — Inquiry, Inspection, Re-performance
- `criteria` — reference framework / control list
- `sampling` — sampling approach
- `evidence_needed`
- `duration_estimate`
- `schedule_notes`
- `cost`

### Live dashboards extended

`GRC Dashboard Snapshot` gains 6 new fields:
`vulnerabilities_open`, `vulnerabilities_critical`, `vulnerabilities_overdue`,
`vulnerabilities_total`, `kpis_total`, `kpis_on_target`.

`dashboards_live.py` updated to compute these on every snapshot
refresh. The 15-minute cron, the realtime-on-save invalidation, and
the 30s client auto-refresh from v1.3.2 all carry through to the new
fields. Vulnerability and KPI saves trigger snapshot rebuilds via
`doc_events`.

### Workspace refresh

New top-row shortcut tiles: **NCA Templates**, **KPI Dashboard**,
**Vulnerabilities**. New links section entries for all 8 new doctypes
and 2 new pages.

### Migration & data safety

Per the **wipe-and-reseed cleanly** decision:
- Existing data on `neoterminal.k.frappe.cloud` is preserved by the
  Frappe migration (not wiped) but new fields default to NULL.
- All v1.4.0 seed data lands under the **DEMO** client.
- 79 NCA template library entries are global (not client-scoped) and
  read-only for non-admin roles.

If you want a true clean wipe, drop the alphax_grc tables and
reinstall — the `bootstrap_grc` 38 step list is fully resilient and
will re-create everything.

### Compatibility

All v1.3.0–v1.3.2 features carry through unchanged: multi-tenant
Client Profile, lifecycle dashboard, consultant timesheet, NCA ECC
trackers (Document Register, Tool Mapping, Review Calendar), BIA, RCM,
Live Snapshot system.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# Or upgrading from v1.3.x:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After install:
1. Open `/app/grc-nca-templates` to browse the 79-template NCA library.
2. Open `/app/grc-kpi-dashboard` to see quarterly KPI charts.
3. Open `/app/grc-vulnerability` (List view) — 5 sample vulnerabilities pre-loaded.
4. Live dashboards now include vulnerability counts in the snapshot.

## Roadmap (v1.5+)

- NCA-conformant Excel print formats (export Risk Register, Audit Plan,
  Vulnerability Register, KPI Report in NCA's exact Excel layouts).
- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail).
- Bahrain, Qatar, Kuwait, Oman framework controls.
- Snapshot trend history (compliance score over 90 days).

## What's new in v1.3.2

Dashboards are now **always live** — no more snapshot-until-reload.
Three layers of liveness, all working together:

**Layer 1 — Materialized snapshot table** (`GRC Dashboard Snapshot`)
A scheduler job runs every 15 minutes and pre-computes 16 KPIs plus 7
JSON detail blobs (heatmap, top risks, frameworks, KRIs, severities,
findings, ratings) for every active client. Dashboards read from this
single row instead of running 12+ aggregation queries per page load.
A firm-wide read merges the snapshots across clients in Python.
- Source: `alphax_grc/dashboards_live.py:refresh_all_snapshots`
- Cron: `*/15 * * * *` via `hooks.py:scheduler_events`

**Layer 2 — Realtime push on data changes** (Frappe WebSocket bus)
When a Risk, Finding, KRI, Assessment, Control, Asset, Incident,
Remediation, Framework, Exception, Risk Acceptance, Maturity Assessment,
Vendor, Vendor Assessment, or Consultant Timesheet record is saved,
`invalidate_dashboards()` immediately:
1. Recomputes the snapshot for that client (cheap — one client only).
2. Broadcasts `grc.dashboard.refresh` over `frappe.realtime`.
Every open dashboard for that client (or firm-wide) re-fetches within
~1 second of the save. No polling needed for typical interactive use.

**Layer 3 — 30-second auto-refresh** (client-side timer, fallback)
Every dashboard page wires up `frappe.alphaxGRC.live({...})` which polls
every 30 seconds — but pauses when the browser tab is hidden, so we
don't burn server cycles for tabs no one's looking at. Also doubles as
the heartbeat that keeps the "Live · updated Xs ago" indicator fresh.

**Live status indicator**
Every dashboard now shows a small pill in the page header:
`● Live · updated 14s ago` (green when fresh, amber after 60s, red on
error). Tooltip shows the exact snapshot timestamp. There's also a
manual "Refresh now" button for impatient users.

**Cleanup**
- Removed hardcoded fallback constants from `grc_command_center.js`
  (`'68%'` compliance, `'4'` critical, `'7'` findings, `'3'` overdue,
  fake heatmap pattern). When the database returns nothing, dashboards
  now show `0` or `—` instead of fake numbers.
- Risk Dashboard's framework section now derives compliance score
  correctly (carried over from v1.3.1).

**Schema**
One new doctype:
- `GRC Dashboard Snapshot` — one row per client, autoname = client code.
  Read-only to non-admin roles. Auto-created on first install for the
  DEMO client; refreshed every 15 minutes thereafter.

**API surface (whitelisted)**
- `alphax_grc.dashboards_live.get_live_dashboard(client=None)` — main
  read endpoint; returns the snapshot or computes inline if missing.
- `alphax_grc.dashboards_live.force_refresh(client=None)` — manual
  recompute, bypasses staleness check.

**Compatibility**
- All v1.3.0 doctypes (Client Profile, Consultant Timesheet, NCA ECC
  trackers, BIA, RCM) carry through unchanged.
- All v1.3.1 fixes (compliance_score derivation) carry through.
- Multi-tenant model unchanged.
- Existing dashboards (Command Centre, Risk Dashboard, Lifecycle) all
  rewired to the live system; existing endpoints still work but are now
  routed through the snapshot layer where applicable.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# OR upgrade from v1.3.x:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
```

After install, the bootstrap will:
1. Create the `GRC Dashboard Snapshot` doctype.
2. Compute the first snapshot for every active client (DEMO + any you've
   created), so dashboards show data immediately.
3. The 15-minute cron schedule activates automatically.

## How to verify it's working

1. Open `/app/grc-lifecycle` or `/app/grc-risk-dashboard`. You should
   see a "● Live · updated Xs ago" pill in the page header.
2. Open `/app/grc-risk-register`, create a new risk, save.
3. Switch back to the dashboard tab — it should refresh within ~1 second
   without you clicking anything. The new risk should appear in the
   counts and heatmap.
4. If realtime isn't working (rare — usually a websocket config issue),
   the 30-second timer takes over as fallback.

## Roadmap (v1.4+)

- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail)
- Bahrain, Qatar, Kuwait, Oman framework controls
- Snapshot history table for trending ("compliance score over 90 days")
- Engagement profitability dashboard

## What's new in v1.3.1

**Bug fix: Risk Dashboard crash with `Unknown column 'compliance_score'`**

The Risk Dashboard's `get_risk_dashboard_data` endpoint and the Client
Profile's `_refresh_summary` method were querying `compliance_score` from
`GRC Framework`, but that column never existed on the Framework doctype.
The code was inherited from v1.2.3 and went unnoticed because the path
was only hit when a user opened the Risk Dashboard with at least one
GRC Framework record present.

`compliance_score` actually lives on `GRC Assessment`, not `GRC Framework`
(also on `GRC Board Report`, `GRC NCA ECC Control`, `GRC Vendor Assessment`,
and `GRC Client Profile` — all correctly).

Fix: both endpoints now derive a framework's compliance score by averaging
the `compliance_score` of GRC Assessment records linked to each framework
— the same approach `api.py:get_command_center_data` already uses.

A schema-mismatch sweep was also run across `api.py`, `notifications.py`,
and all page Python files; no other field references are misaligned with
their target doctype schemas.

No other changes from v1.3.0. Multi-tenant Client Profile, Lifecycle
dashboard, Consultant Timesheet, NCA ECC trackers, BIA, RCM all carry
through unchanged.

## What's new in v1.3.0

This is a major release. The app moves from single-tenant to **multi-client
consulting platform**: every record is now scoped to a client engagement,
country and sector intelligence drives framework selection, and the new
Lifecycle dashboard is the central UI.

**Multi-tenant architecture**
- New `GRC Client Profile` doctype — central tenant record. Holds the
  client name (EN+AR), country, sector, engagement type and dates, lead
  consultant, applicable frameworks, default hourly rate.
- Country + sector → applicable frameworks intelligence: KSA Government
  loads NCA ECC, NCA CSCC, PDPL, NCA Data Cybersecurity, SDAIA AI Ethics;
  KSA Banking loads SAMA CSF, SAMA CTI, PDPL; Aramco supply chain loads
  TPCSP and SACS-002; etc. Picking country and sector on a new Client
  Profile auto-suggests the right framework set.
- 34 existing doctypes plumbed with a `client` Link field: Risk Register,
  Audit Finding, Control, KRI, Framework, Asset Inventory, Incident,
  Vendor, etc. Every record is now scoped to a client engagement.
- Country coverage in v1.3.0:
  - 🇸🇦 **Saudi Arabia** — fully built (Government, Banking, Aramco
    Supply Chain, Healthcare, Energy & Utilities, Telecom, Education,
    General Private)
  - 🇦🇪 **UAE** — scaffolded (Government/TDRA, Banking/DIFC/ADGM/DFSA,
    Healthcare/DHA/DoH)
  - 🇧🇭 🇶🇦 🇰🇼 🇴🇲 🇪🇬 🇯🇴 — framework names listed; deeper content
    planned for v1.4

**Lifecycle dashboard** — `/app/grc-lifecycle`
- 8-stage process cycle visualisation: Setup → Register → Assess →
  Control → Audit → Remediate → Report → Review (loops back to setup)
- Client picker at the top; pick a client to scope the wheel to that
  engagement. Pick "Firm-wide overview" to see roll-ups across all clients
- Each stage shows live progress percentage and red/amber/green status
  based on completion vs total
- Clickable stages deep-link into the relevant module
- KPI tiles, framework pills, sortable stage list

**Consultant time-tracking**
- New `GRC Consultant Timesheet` doctype: client + consultant + date +
  hours + billable + activity type + linked module + reference document
  + auto-computed amount from client hourly rate
- 14 activity types: Risk Assessment, Framework Assessment, Audit
  Fieldwork, Finding Review, Remediation Support, Document Review,
  Policy Drafting, Workshop / Training, Client Meeting, Report Writing,
  Project Management, Research, Travel, Other
- API endpoints: `get_client_hours_summary` (per-client roll-up),
  `get_my_timesheet_summary` (current user's weekly view)

**NCA ECC compliance trackers** (from Axidian NCA ECC Compliance Guide)
- `GRC NCA ECC Document` — 28 mandatory documents (1-1-1 Cybersecurity
  Strategy, 1-2-3 Steering Committee Charter, etc.). Status workflow:
  To Do / In Progress / Awaiting Approval / Approved / Needs Review.
  EN + AR titles. Evidence attachment, approval authority, review cycle.
- `GRC NCA ECC Tool Mapping` — 28 tooling-required ECC controls mapped
  to recommended solution categories (GRC, IAM, PAM, DLP, SIEM, MDM,
  NGFW, MFA, etc.). Coverage status per control.
- `GRC NCA ECC Review Calendar` — 29 periodic review cycles with
  frequency, next-scheduled date, last-review results, evidence
  attachment. Auto-flags overdue.

**Business Impact Analysis** (BIA infographic methodology)
- `GRC Business Impact Analysis` doctype with full BIA dimensions:
  RTO, RPO, MTPD, dependencies child table (5 dependency types),
  5 impact dimensions (Financial, Operational, Regulatory, Reputational,
  Customer) on a 1-5 severity scale
- 5 sample BIA records seeded: Customer-facing online services,
  Financial close & reporting, Payroll processing, IT operations &
  service desk, Regulatory reporting

**Risk Control Matrix** (PMO-Government template)
- `GRC Risk Control Matrix` doctype with `GRC RCM Line` child rows:
  domain, risk, impact, control, control type
  (Preventive/Detective/Corrective), owner, frequency, KPI
- 11 RCM domains: Strategic Alignment, Project Governance, Portfolio
  Management, Budget & Financial Control, Risk Management, Compliance
  & Regulatory, Vendor & Contract, Performance Reporting, Change
  Management, Benefits Realization
- Sample PMO-Government RCM seeded with 6 lines

**Migration & data safety**
- Per the "wipe-and-reseed cleanly" decision: this release auto-creates
  a **DEMO** client on first install, then backfills `client = DEMO`
  on any existing seeded data so nothing is orphaned. Real engagement
  data should be created under fresh Client Profile records.
- All existing v1.2.x fixes carry through: workspace `content` populated,
  empty `grc_pages.json` shipped, resilient `bootstrap_grc`, all 17
  whitelisted endpoints permission-gated.

**Workspace refresh**
- New shortcuts: Lifecycle, Clients, Timesheets
- New links section: GRC Client Profile, Consultant Timesheet, all 5
  new NCA ECC / BIA / RCM doctypes
- Updated `content` layout puts Lifecycle as the primary entry point

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# OR for upgrade from v1.2.5:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
```

After install, navigate to `/app/grc-lifecycle` to see the new dashboard.
The DEMO client comes pre-loaded with sample NCA ECC documents, tool
mappings, review calendar, BIA records and the PMO-Government RCM.

To create a real engagement, click "+ New Client" from the Lifecycle
dashboard, pick country and sector, and the app will suggest the right
framework bundle automatically.

## Roadmap (v1.4+)

- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail)
- Bahrain, Qatar, Kuwait, Oman framework controls
- Cross-client benchmark dashboards (compare your KSA Banking clients
  against each other)
- Engagement profitability dashboard (timesheet hours × rate vs fixed-fee
  contract value)
- Rename `owner` field on `GRC Audit Finding` (collides with Frappe's
  reserved column) — held because it's a destructive migration

## What was claimed for v1.2.x (kept for history)

**Actual fix for the workspace `onboarding_list` crash on Frappe v15.106+**

v1.2.4 attempted to fix this by changing the `onboarding` field, but that
field was unrelated. The real cause is a NULL `content` field on the
Workspace document.

In `frappe/desk/desktop.py` (Frappe v15), `Workspace.__init__` only assigns
`self.onboarding_list = [...]` inside an `if self.doc.content:` branch.
If `content` is NULL, the attribute is never created — and the later
`if self.onboarding_list:` in `get_onboardings()` raises
`AttributeError: 'Workspace' object has no attribute 'onboarding_list'`.

Two-part fix:
- The shipped workspace JSON now includes a populated `content` field with
  a default layout (welcome header, 8 shortcut tiles, 9 module cards).
- `ensure_workspace()` self-heals existing installs whose DB row was
  created without `content` — on `bench migrate` it injects the default
  layout if the field is NULL or empty.

If you previously installed v1.2.3 or v1.2.4, upgrading to v1.2.5 and
running `bench migrate` will repair the workspace automatically and the
crash will stop on next page load.

No other changes. Risk Dashboard, theme presets, permission gates, report
fixes, KRI breach-direction, resilient `bootstrap_grc`, all carry over.

## What was claimed for v1.2.4 (incorrect — kept for history)

**Frappe v15.106+ workspace fix**
Fixes `AttributeError: 'Workspace' object has no attribute 'onboarding_list'`
that prevented the AlphaX GRC workspace from loading on Frappe v15.106 and
later. Root cause is a Frappe core bug where an empty-string `onboarding`
field on a Workspace document skips initialization of `onboarding_list`,
which `get_onboardings()` then references.
See https://github.com/frappe/erpnext/issues/43234

Two-part fix:
- Workspace JSON now ships with `"onboarding": null` instead of `""` so
  fresh installs avoid the broken Frappe code branch entirely.
- `ensure_workspace()` now self-heals existing installs: on `bench migrate`
  it detects an empty-string `onboarding` value in the Workspace row and
  rewrites it to NULL.

No other changes — Risk Dashboard, permission gates, report fixes, KRI
breach-direction, and all v1.2.3 features carry over unchanged.

## What's new in v1.2.3

**New page: GRC Risk Dashboard** (`/app/grc-risk-dashboard`)
A live, theme-able risk dashboard with:
- 4 KPI tiles (critical risks, open findings, avg compliance score, overdue actions)
- 5×5 risk heatmap driven by `GRC Risk Register.impact` × `likelihood`
- Top open risks table with deep-link to each risk
- Framework compliance progress bars (reads `GRC Framework.compliance_score`)
- KRI status panel (reads `GRC KRI` with live status badges)
- Findings-by-severity breakdown (reads `GRC Audit Finding`)
- Interactive theme panel: 5 presets (AlphaX Navy / Saudi Green / Corporate Blue / Dark Mode / Sand & Gold) + individual colour pickers for global, risk-level and heatmap-cell colours
- **Per-user theme persistence** via `frappe.defaults` — each user keeps their own colour preferences
- Bilingual (EN/AR) labels via Frappe's `__()`
- All text content passed through `frappe.utils.escape_html` (no XSS risk from risk titles, KRI names, framework names, etc.)

Workspace includes a new "Risk Dashboard" shortcut tile (red) and a link in the "Dashboards & Pages" group.

Access is gated via the existing role list (System Manager / GRC Admin / GRC Executive / Compliance Officer / GRC Assessor / GRC Auditor / Risk Owner / Privacy Officer).

## What's new in v1.2.2

**Install reliability**
- Ships an empty `fixtures/grc_pages.json` to overwrite any legacy
  `standard:Yes` Page records that triggered "Not in Developer Mode"
  on Frappe Cloud during `bench install-app`.
- `before_install` runs a defensive `neutralize_legacy_page_fixtures()` pass
  that rewrites stale fixture files to `[]` for re-install / migrate scenarios.

**Bug fixes (script reports)**
- `grc_risk_summary` rewritten to use the actual schema fields
  (`inherent_score`, `residual_score`, `risk_rating`, `linked_framework`,
  `next_review_date`).
- `grc_audit_findings_report` rewritten with correct columns
  (`owner`, `due_date`, `root_cause`) plus a computed `days_open`.
- `grc_compliance_status` rewritten with a real `JOIN` against
  `tabGRC Framework` for friendly framework names.

**Security hardening**
- New role-based gate `_require_grc_role()` covering all 17 whitelisted
  endpoints in `api.py`, the page controllers, and the ITGC seeder method.
- `start_assessment_run` no longer uses `ignore_permissions=True`; it now
  calls `frappe.has_permission("GRC Assessment Run", "create")`.
- `get_assessment_summary` checks per-document read permission.
- KRI alert email HTML is now `frappe.utils.escape_html`-escaped.

**Data model**
- `GRC KRI` gains a `breach_direction` field (`Above` / `Below`) so KRIs like
  patch-SLA-met-% breach when the value falls below the threshold instead of
  above it. Default `Above` preserves existing behaviour.
- `risk_rating` added to `GRC Risk Register.field_order` so it actually
  renders in the form.

**Notifications**
- `_admin_emails()` no longer returns the literal string `"Administrator"`
  when no GRC Admin role users exist; falls back to the real Administrator
  user email or `[]`.
- `check_kri_breaches()` honours `breach_direction` and reports it in the
  alert table.

**Cleanup**
- Removed ~380 lines of dead v1 seeder code
  (`seed_nca_ecc_controls`, `seed_asset_inventory`, `seed_nca_ecc_controls_full`).
  Bootstrap calls only the `_v2` versions.
- Version stamps unified to 1.2.2 across `__init__.py`, `hooks.py`, install logs.

## Install

```bash
bench get-app alphax_grc <git-or-zip-url>
bench --site <your-site> install-app alphax_grc
```

If a previous install partially completed and left a stale
`apps/alphax_grc/alphax_grc/fixtures/grc_pages.json` on disk, this version
will overwrite it during `bench update`. If you're stuck on a different
app version and can't update yet, the manual one-liner is:

```bash
echo '[]' > apps/alphax_grc/alphax_grc/fixtures/grc_pages.json
bench --site <your-site> install-app alphax_grc
```

## What's still on the roadmap

- Rename the `owner` field on `GRC Audit Finding` (collides with Frappe's
  reserved `owner` system column). Requires a migration patch on existing
  sites — held for v1.3.
- Flesh out the stub manuals under `manuals/`.

Licence: MIT
