# AlphaX GRC — Engagement Lifecycle Phases

This document describes the **engagement lifecycle** that drives the AlphaX GRC application: how a consultant moves from "client signs SOW" to "engagement complete", phase by phase. The lifecycle is enforced by the platform — not just suggested.

The phase definitions live as data in the doctype `GRC Engagement Phase Template`, which means they can be edited via the UI (or by exporting/re-importing the fixture) **without code changes**. New engagement types can be added by creating a new set of phase templates with that engagement type label.

## Where phases live

| Location | What it contains |
| --- | --- |
| `alphax_grc/alphax_grc/data/engagement_phase_templates.json` | The seeded source-of-truth for all default phases. Edit this file and re-seed to apply changes. |
| Doctype `GRC Engagement Phase Template` | The active database records loaded from the fixture. Editable via `/app/grc-engagement-phase-template`. |
| Doctype `GRC Engagement` (field `phase_log`) | A snapshot of phases for a single engagement. Created when the engagement is first saved. |
| Doctype `GRC Engagement Decision Log` | Append-only audit trail of every phase transition and decision. |

## The three engagement types shipped

### Standard NCA Engagement — 7 phases

The default lifecycle for any KSA cybersecurity engagement.

| # | Code | Phase | Expected | Purpose |
| - | ---- | ----- | -------- | ------- |
| 1 | DISCOVERY | Discovery | 14 days | Understand the client. Identify stakeholders, scope boundaries, business context, existing certifications, audit-driven deadlines. |
| 2 | SCOPING | Framework Scoping | 7 days | Decide which compliance frameworks apply, with documented reasoning. |
| 3 | ASSESSMENT | Current-State Assessment | 28 days | Run interviews, request evidence, walk through every applicable control. |
| 4 | RISK_ANALYSIS | Risk Analysis | 14 days | Build the risk register. Map gaps to threats, rate likelihood and impact. |
| 5 | TREATMENT | Treatment Planning | 14 days | Choose treatment per risk. Generate Implementation Task backlog. |
| 6 | EXECUTION | Execution Oversight | 180 days | Tasks executed by client teams; we chase, escalate, and re-test. |
| 7 | AUDIT_READY | Audit Readiness | 30 days | Final audit pack assembled. Inspector visit supported. |

### Aramco CCC Pursuit — 8 phases

The lifecycle for a vendor pursuing Aramco Cybersecurity Compliance Certificate.

| # | Code | Phase | Expected |
| - | ---- | ----- | -------- |
| 1 | ARAMCO_SCOPING | CCC Scoping | 10 days |
| 2 | ARAMCO_SELF_ASSESS | Self-Assessment | 30 days |
| 3 | ARAMCO_AUDIT_SCHEDULED | Audit Scheduled | 14 days |
| 4 | ARAMCO_AUDIT_FIELDWORK | Audit In Progress | 14 days |
| 5 | ARAMCO_FINDINGS | Findings Reviewed | 7 days |
| 6 | ARAMCO_REMEDIATION | Remediation | 60 days |
| 7 | ARAMCO_CERTIFIED | Certified | 30 days |
| 8 | ARAMCO_RENEWAL | Renewal Cycle | 365 days |

### GDPR Compliance — 6 phases (added in v1.9.0)

For Saudi entities with EU presence, or pure GDPR readiness engagements.

| # | Code | Phase | Expected |
| - | ---- | ----- | -------- |
| 1 | GDPR_DISCOVERY | Data Discovery | 21 days |
| 2 | GDPR_LAWFUL_BASIS | Lawful Basis & DPIA | 14 days |
| 3 | GDPR_RIGHTS | Data Subject Rights | 21 days |
| 4 | GDPR_SECURITY | Security & Breach Response | 28 days |
| 5 | GDPR_VENDOR | Vendor & Transfer Compliance | 30 days |
| 6 | GDPR_OPERATIONS | Continuous Operations | 365 days |

## Anatomy of a phase

Each phase template carries:

- **Phase number** — execution order (1, 2, 3 ...)
- **Phase code** — short identifier (DISCOVERY, SCOPING ...)
- **Phase label** — human-readable name shown on the timeline
- **Icon** — emoji shown on the timeline dot
- **Purpose summary** — what the phase is for, shown at the top of the engagement form
- **Expected duration (days)** — used to compute `is_overdue`
- **Entry criteria** — text describing what must be true to enter
- **Completion criteria** — text describing what must be true to leave
- **Auto-advance when complete** — if checked, the engagement moves to the next phase automatically
- **Default checklist items** — child rows describing tasks (manual / auto-check / auto-complete / approval gate)
- **On-phase-start method** — optional Python dotted path called when the phase begins
- **On-phase-complete method** — optional Python dotted path called when the phase ends

## Anatomy of a checklist item

| Field | Meaning |
| --- | --- |
| Task description | Free text — what needs to happen |
| Task type | `Manual` (consultant action), `Auto-check` (system computes a yes/no), `Auto-complete` (system performs the action), `Approval Gate` (requires sign-off) |
| Responsible team | One of: GRC Team, IT Team, Cyber Security Team, IT Audit Team, HR Administration, Top Management, Purchase Team, Client Side, Lead Consultant |
| Is blocker | If checked, phase cannot complete until this item is done |
| Auto-check method | For Auto-check items — Python dotted path that returns True/False |
| Default offset days | Default due date offset from phase start |

## Blocker enforcement

When a consultant clicks "Advance Phase" on an engagement, the system checks:

1. **Built-in phase blockers** (hard-coded in `grc_engagement.py:get_blockers`):
   - Phase 1: executive sponsor set, scope summary written
   - Phase 2: at least one framework adopted
   - Phase 3: at least 50% of in-scope controls assessed
   - Phase 4: every Open finding has a corresponding Risk
   - Phase 5: every High/Critical risk has a treatment strategy
2. **Checklist blockers** (data-defined in phase templates): items marked `is_blocker=1` that are not yet `Completed`

If any blockers exist, the system **refuses to advance** and shows a modal listing what's blocking. A System Manager can override using "Force Advance" — this is logged in the Decision Log so the audit trail is preserved.

## How to modify phases

### Edit one phase

Open `/app/grc-engagement-phase-template`, click the phase you want to change, edit the fields, save. Existing engagements that are already in that phase are unaffected (they have their own snapshot in `phase_log`). New engagements pick up the change.

### Add a new engagement type

Three steps:

1. Add the new type as an option to the `engagement_type` Select field on `GRC Engagement Phase Template` and `GRC Engagement` (via Customize Form).
2. Create one Phase Template record per phase for the new type.
3. New engagements of the new type pick up the new phases automatically.

To bake a new type into the install bundle: add the phase entries to `engagement_phase_templates.json`, then re-deploy.

### Re-seed from the fixture

```bash
bench --site <your-site> execute alphax_grc.install.seed_engagement_phase_templates
```

Idempotent: only inserts templates that don't already exist. Use this after editing the fixture file.

## How phases drive the consultant

When a consultant opens an engagement form they see, above the standard fields:

- A **gradient hero banner** with the engagement title, client, current phase, status chip
- A **horizontal timeline** showing every phase as a dot — completed (green check), current (gold, highlighted), locked (gray)
- The **purpose summary** of the current phase
- A **health strip** with: open findings, high/critical risks, pending tasks, overdue tasks, evidence-rule failures, days in current phase
- Buttons for **🚀 Kickoff** (if Draft) or **▶ Advance Phase** (if Active)

When a consultant logs into the platform they land on the **Consultant Cockpit** at `/app/grc-consultant-inbox` which shows:

- Hero stats: total engagements, overdue phases, overdue tasks, due-this-week, open findings, rule failures (last 7 days)
- Active engagement cards — each card shows phase, days in phase, and health metrics
- Overdue tasks table — sorted by priority
- Due-this-week tasks table
- Recent control monitoring failures (last 7 days)

## Decision Log

Every phase transition writes a record to `GRC Engagement Decision Log` capturing:

- Engagement, client, timestamp, user
- Decision type (e.g. "Phase Transition", "Risk Acceptance", "Scope Change")
- Phase at decision
- Decision summary
- Rationale (why this decision was made)
- Linked record (optional)

This is the audit trail that proves to a regulator: "we made decisions consciously, documented our reasoning, and didn't skip steps."

## What the phases unlock for the consultant

| Behaviour | Where it comes from |
| --- | --- |
| Can't accidentally jump from Discovery to Treatment | `advance_phase()` enforces sequence |
| Can't advance if assessment isn't 50% done | `get_blockers()` for Phase 3 |
| Engagement marked overdue if days_in_phase exceeds expected duration | Computed in `validate()` from `expected_duration_days` |
| Health metrics auto-refresh on every save | `_refresh_health_metrics()` hooks |
| Visual timeline shows progress at a glance | Form script `grc_engagement.js` |
| Inbox lists all active engagements sorted by urgency | `get_inbox()` server-side, JS renders |
| Branded print formats include phase context | v1.7.0 branded print formats include all standard fields |

## Roadmap (post-v1.8.0)

- **v1.9.0**: Auto-create per-client controls when frameworks are adopted on the engagement (currently auto-adopt happens on Client Profile save). Engagement-driven attestation queue. Engagement-driven Inspection Pack generator.
- **v2.0.0**: AI-assisted phase advancement — when entering Phase 3, the AI extension (alphax_grc_ai) can pre-fill assessor opinions for controls based on uploaded evidence documents. When entering Phase 5, the AI extension proposes treatment strategies per risk.

## Editing this document

This file lives at `alphax_grc/PHASES.md` in the app root. Update it whenever the phase model changes. The Frappe site can serve it via `/app/grc-help` if linked, or simply read it from the filesystem as part of onboarding documentation.
