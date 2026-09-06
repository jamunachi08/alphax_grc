# AlphaX GRC v2.11.0 — Report Studio

Prompted by a Power BI data-governance dashboard (Arabic, PDPL-flavoured):
maturity score, DSAR response time, % policies approved, incidents past the
notification deadline, current-vs-target by domain, unclassified assets. The
underlying data for nearly every tile already lived in the app — DSRs with due
dates, incidents with SLA and SAMA-notification fields, policies with
publication status, SAMA assessment lines, the asset register. What was
missing was the reporting layer: 5 fixed script reports and no way to make
another without code.

## Added — GRC Report Studio (`/app/grc-report-studio`)

A reports page and a **front-end report builder**. Left rail lists saved
reports grouped by category; the pane shows a themed chart (bar with one or
two series, donut, single number, or table only) over a drill-down table with
clickable record links and one-click **CSV export**.

**New Report** builds a report without code: pick any AlphaX GRC doctype,
choose a group-by field and an aggregate (Count / Sum / Average over a numeric
field), optionally add a Frappe filter list, pick a chart. The definition is
validated and executed once at save, so a broken report fails in the dialog,
not on first view.

## How it stays safe

- Builder reports execute through `frappe.get_list`, so **desk permissions
  apply**: a row the viewer cannot open is excluded from both the aggregate
  and the drill-down. Tested explicitly.
- Only AlphaX GRC module doctypes can be reported on — the builder refuses
  User, File, or anything else core.
- Bad definitions are rejected with reasons: unknown group-by field, Sum
  without a numeric field, filter JSON that isn't a list.
- Creating definitions from the front end requires System Manager, GRC Admin,
  GRC Executive or Compliance Officer.

## `GRC Report Definition`

Declarative doctype behind the studio — Builder definitions carry doctype /
filters / group-by / aggregate / chart; **Built-in** definitions cover what a
single group-by cannot express, keyed to implementations in
`pathway/reports.py`:

| Seeded report | Kind | Mirrors |
|---|---|---|
| Maturity by Domain — Current vs Target | Built-in | the two-series domain bar, with per-domain gap |
| DSR Ageing by Request Type | Built-in | DSAR response-time tile; drill-down lists overdue requests |
| Incidents Past SAMA Notification | Built-in | "incidents late past notification deadline" |
| Policy Publication % | Built-in | "% policies approved" |
| Risks Above Appetite by Category | Built-in | risk/gap map |
| Unclassified Assets by Type | Built-in | "unclassified assets" |
| Incidents by Severity | Builder | — |
| Open Risks by Category | Builder | — |
| SAMA Deliverables by Status | Builder | — |
| Project Plans — % Complete | Builder | — |

Ten reports out of the box; every one is also an editable example of how to
make more. Entry points: workspace **Reports** section and the console menu.

## Tests

`tests/test_reports.py`, 23 checks: field discovery (and refusal of non-GRC
doctypes), count and average aggregation, filter narrowing, rejection of bad
definitions, **permission exclusion proven**, the two-series maturity built-in
with per-domain gaps, publication %, and every seeded definition validated
against its implementation. 297 checks across seven suites.

# AlphaX GRC v2.10.0 — tamper-evident evidence, versioned policies, earned value

Merges the three features from the externally produced "v2.10.0-enhanced"
build onto the v2.9.0 base, with the defects that would have stopped it
installing fixed.

## What was wrong with the enhanced build, and what changed

| Issue | Effect | Fix |
|---|---|---|
| `policy_versioning.py` and `integrity.py` placed under `alphax_grc/alphax_grc/` but registered as `alphax_grc.policy_versioning` | `ModuleNotFoundError` on every GRC Policy save from the `on_update` hook | Moved to the app root, where the import path says they are |
| `pyproject.toml`, `setup.py` deleted | Wheel build fails on Frappe Cloud before any hook runs | Restored |
| `verify_tree.py` and all five test suites deleted | Nothing to catch any of the above | Restored, and extended (below) |
| `__init__.py` 2.9.0 vs `hooks.py` 2.10.0 | Version drift | Aligned at 2.10.0 |
| Planned % complete computed on calendar days while the docstring claimed working days | SPI overstated on every Fri/Sat and holiday | Uses `Calendar.count_working_days` from the scheduler |

## Added — from the enhanced build, kept as designed

**Hash-chained, immutable evidence evaluations.** `GRC Evidence Rule
Evaluation` carries `prev_hash` / `snapshot_hash`; creation is the only
operation allowed, and `verify_rule_chain` re-walks a rule's history and
names the first broken link. `alphax_grc.integrity` holds the shared
primitives.

**Immutable policy versions.** When `GRC Policy.publication_status` becomes
Published, `snapshot_if_published` writes a hash-chained `GRC Policy Version`.
No role has create permission on that doctype — the hook is the only way in —
and edits and deletes are refused. Re-saving the same published version does
not duplicate; a new `version_no` chains from the previous snapshot's hash.

**Earned value on GRC Project Plan.** Budget at Completion, Actual Cost
(summed from billable `GRC Consultant Timesheet` entries linked to the plan),
CPI, SPI, EAC. Activates only when a budget is set.

**Resilience in the pathway.** BIA and DR Plan had no presence in the console.
Now a "Business continuity" stage gated on BIA approval, a Resilience pillar,
and KRI/KPI surfaced under Risk.

## Guard

`verify_tree.py` gains `check_hook_targets_importable`: every hook and
doc_event target is resolved with `importlib.util.find_spec`, not just matched
to a file somewhere in the tree. Run against the enhanced build it reports
exactly the bug that would have shipped:

```
FAIL  hooks.py target 'alphax_grc.policy_versioning.snapshot_if_published':
      module 'alphax_grc.policy_versioning' is not importable
```

## Tests

`tests/test_integrity.py`, 29 checks: hash determinism and sensitivity, an
intact chain verifying, altered content and re-linked records both caught with
the broken link named, immutability of evaluations and policy versions, no
create permission on policy versions, snapshot only on publish, no duplicate
on re-save, new version chaining, and planned % proven to count working days
and to differ from the calendar-day figure the enhanced build produced. 274
checks across six suites.

# AlphaX GRC v2.9.0 — visual redesign of the pathway surfaces

The console worked but read as a column of grey cards. This release borrows
the design language of the better GRC infographics — a hero band with one big
number, numbered coloured tiles, and pillar framing — without changing any
behaviour underneath.

## Pathway Console

**Hero band.** A gradient banner (drawn from the active theme's palette) with
the completion percentage as a 46px headline, "next up", a white progress
rail, and five glass tiles: done / in progress / ready / blocked / need
attention. The last tile flips to solid white with red text when non-zero,
so the number that needs a person is the one that stands out.

**Pillar strip.** Below the hero, four chips reframe the ten stages as the
functions a GRC lead thinks in — Governance (direct and oversee), Risk
(anticipate threats), Compliance (enforce the rules), Audit (validate
controls) — each with its own colour, completion %, and record count.

**Journey grid.** Stages are now numbered coloured tiles in a responsive grid
rather than a vertical spine: a 6px colour bar across the top, a numbered
badge with a soft shadow, an icon, the count in the stage colour at 26px,
attention badges, and a hover lift with a tinted shadow. Done tiles get a
faint wash of their colour; blocked tiles grey out. Arrows link tiles on
wide screens.

**SAMA tab.** The three headline numbers are now SVG gauge rings —
maturity out of 5 (green at target, amber within one level, red below), %
of sub-domains at level 3+, and deliverables filed. Un-notified reportable
incidents keep their warning card.

## Workspace board

Card colour moved from a left rule to a gradient top bar, counts take the
stage colour, numbered badges get a shadow, and an "Open console" gradient
CTA sits in the header so the two surfaces feel like one product.

## Themes

Everything above is driven by the seven existing themes. Monochrome and High
Contrast drop the gradients, shadows and arrows and stay flat, so the
no-colour option is still genuinely no-colour.

No API, doctype or scheduling changes. All 245 checks pass unchanged.

# AlphaX GRC v2.8.0 — residual risk vs appetite

## Why

Auditing the app against the five questions every GRC programme has to
answer — what are we protecting, what could go wrong, how likely, what
controls, **is the remaining risk acceptable to the business** — four were
covered and the fifth had a hole. Appetite was defined per category on the
client profile and residual risk was computed on the register, but nothing
compared them. A risk could sit above the client's stated appetite for ever
with no flag anywhere.

## Added — appetite check on GRC Risk Register

On every save, the risk's `residual_rating` is compared against the client's
appetite for that risk category:

| Client appetite | Highest residual accepted |
|---|---|
| None | Very Low |
| Low | Low |
| Moderate | Medium |
| High | High |

Three read-only fields record the verdict: `appetite_ceiling`,
`within_appetite`, and `appetite_status` — one of *Within appetite*,
*Above appetite — needs treatment or acceptance*, or *Above appetite —
formally accepted* (response = Accept **and** an acceptance reference is
recorded; "Accept" on its own is not acceptance). No appetite set for the
category gives no verdict rather than a false breach.

All ten risk categories map to an appetite field on the client profile
(Legal → Compliance appetite, Environmental → Operational appetite).

`appetite_status` is a list-view column and standard filter, so "show me
everything above appetite" is one click.

## Dashboard

- New number card **Risks above appetite** — counts breaches without a
  formal acceptance — placed beside Open risks on the workspace.
- The Pathway Console risk stage's attention badge changes from "still open"
  to **"above appetite"**, which is the number a risk owner has to act on.

## Tests

`tests/test_nfcrm.py` grows to 26: every risk category maps to a real
appetite field on the client profile (read from both schemas), within /
equal / above verdicts, acceptance recognised only with a reference,
undefined appetite gives no verdict, unscored residual gives no verdict, and
the verdict is stamped by validate(). 245 checks in total.

# AlphaX GRC v2.7.1 — form and template-matching fixes

## Fixed — "Cb Head" and "Cb Sched" showing on forms

Every doctype I generated in v2.3.0-v2.7.0 gave its **column breaks** a label,
auto-derived from the fieldname. Frappe renders a labelled column break as a
heading, so forms showed stray text like `Cb Head`, `Cb Sched`, `Cb Score` —
and one waiver field was literally labelled `Column Break`.

Fourteen labels removed across GRC Project Plan, GRC Plan Template, GRC SAMA
Assessment / Deliverable / Waiver / Subdomain, GRC Global Policy and GRC
Pathway Settings. Section breaks keep their labels, which is correct.

`verify_tree.py` now fails on any labelled column break in the new module and
warns on auto-derived-looking section labels. Verified against the broken JSON:

```
FAIL  doctype 'GRC Project Plan': column break 'cb_head' has a label ('Cb Head')
      — it will render as stray text on the form
```

## Fixed — plan templates didn't line up with engagement types

An engagement of type **Standard NCA Engagement** was being planned with an
**Aramco SACS-002** template, because the two lists never agreed. Template
`engagement_type` was free text carrying values like "NCA ECC Compliance" and
"PCI DSS Assessment"; `GRC Engagement.engagement_type` is a Select offering
seven fixed options. Nothing could ever match.

- Template `engagement_type` is now the **same Select** as the engagement
  doctype, and all 15 templates are re-tagged to real options.
- The Plan Template field on GRC Project Plan is **filtered by the selected
  engagement's type** — pick ENG-1185 and only templates for a Standard NCA
  Engagement are offered.
- With exactly one match and no template chosen, it fills itself in and says
  what it did: "Template set to NCA ECC-2:2024 Implementation (30 tasks, ~205
  working days)". With several, a headline says how many match. With none, it
  says so and leaves the full list available rather than blocking.
- `api.suggest_templates(engagement, client)` backs it, falling back to the
  frameworks in the client's control set when the engagement type has no
  tagged template.

## Tests

Three new checks assert the template engagement types are drawn from the
options `GRC Engagement` actually ships, read from its schema rather than
hardcoded — so if the base app adds or renames a type, the test fails instead
of the matching silently breaking. 48 scheduler checks, 233 in total.

# AlphaX GRC v2.7.0 — global plan template library

## Added — 12 more templates (15 total, 314 tasks)

A plan now exists for every framework the app assesses against, plus the
engagement types that recur regardless of framework.

| Template | Framework | Tasks | Working days |
|---|---|---|---|
| SAMA CSF Implementation and Maturity Uplift | SAMA CSF | 47 | 305 |
| NCA ECC-2:2024 Implementation | NCA ECC-2:2024 | 30 | 205 |
| PCI DSS v4.0 Compliance | PCI DSS | 20 | 147 |
| SDAIA PDPL Privacy Programme | SDAIA PDPL | 24 | 141 |
| NIST CSF 2.0 Programme | NIST CSF 2.0 | 20 | 136 |
| ISO 22301 Business Continuity (BCMS) | ISO 22301 | 22 | 119 |
| ISO 27001:2022 ISMS Implementation | ISO 27001:2022 | 24 | 111 |
| ISO 42001 AI Management System | ISO 42001 | 18 | 100 |
| Aramco SACS-002 Third Party Certification | Aramco SACS-002 | 15 | 93 |
| Third Party Risk Management Programme | General | 15 | 86 |
| Cybersecurity Policy Framework Development | General | 17 | 71 |
| Incident Response Readiness | General | 17 | 66 |
| Certification Surveillance and Recertification | General | 13 | 53 |
| Internal Audit Engagement | General | 16 | 50 |
| Cybersecurity Gap Assessment (Short Engagement) | General | 16 | 38 |

Every plan follows the same five-stage spine — mobilise, assess, build,
implement, assure — so two programmes running at once stay comparable. Each
carries a `source_reference` naming the clauses or standard it follows.

## Added — defaults

**On the template:** `default_working_days` (Sun-Thu KSA), and read-only
`task_count`, `phase_count`, `indicative_duration_days` computed on save, so
the list view shows the shape of each plan without opening it.

**On the plan:** start date defaults to today; working week is inherited from
the template; plan title is derived as "Template — Client" when left blank.
None of these are mandatory to type any more.

**Create Project Plan** button on the template form: pick client, engagement
and start date, and it creates the plan, loads the tasks, dates them, and
opens it. The dialog shows the task count and indicative length first.

## Added — template validation

Saving a template now refuses a broken WBS rather than letting it produce a
broken schedule downstream: duplicate WBS numbers, a `depends_on` that names a
task not in the template, a task depending on itself, and negative durations
are all rejected. Zero-day tasks are normalised to milestones and milestones
are forced to zero days, so the two can't disagree.

## Fixed — closing milestones pushed the end date out

A milestone marks the completion of what precedes it, so it now lands **on**
that day rather than the working day after. Previously a plan ending with
"Engagement closed" reported an end date one day later than its last real task.
Phase headers and closing milestones now add no working days and no calendar
time to a plan.

## Tests

`tests/test_scheduler.py` grows to 45 checks: all 15 templates are scheduled
end to end and checked for duplicate WBS, unresolvable or self-referencing
dependencies, unknown responsible roles, missing phases, missing source
references, and plausible length; framework coverage is asserted against the
list the app assesses; and headers are proven to add neither days nor calendar
time. 230 checks across all suites.

# AlphaX GRC v2.6.0 — SAMA CSF compliance

Answering the earlier audit: SAMA was a framework name and a hardcoded
coverage score. It is now a working module.

## What was missing, and what closes it

| SAMA CSF requirement | Before | Now |
|---|---|---|
| Control catalogue (4 domains, 36 sub-domains) | absent | `GRC SAMA Subdomain`, seeded, with control-consideration counts |
| Maturity model 0-5, target level 3 (2.4) | absent — controls only had Planned/Implemented | `GRC SAMA Assessment` with the six SAMA level definitions |
| Non-bank exclusions (1.4) | absent | 3.2.3, 3.3.12, 3.3.13 auto-excluded by entity type |
| Waiver request (Appendix D/E) | absent | `GRC SAMA Waiver`, approval chain enforced |
| Framework update request (Appendix B/C) | absent | same doctype, `request_type = Framework Update` |
| Incident reporting to SAMA (3.3.15.5-7) | absent | 12 fields incl. the full formal-report set |
| CISO Saudi nationality + SAMA NOL (3.1.1.9) | absent | on GRC Client Profile |
| 108-item evidence deliverable register | absent | `GRC SAMA Deliverable`, seeded and mapped |

### Maturity scoring

Overall maturity is the mean across **applicable** sub-domains, with per-domain
averages and the weakest domain surfaced. An insurance company assessed on the
same data as a bank scores differently, because 3.2.3, 3.3.12 and 3.3.13 drop
out rather than dragging the average down with zeros — excluded lines are
flagged not-applicable, never deleted, so the working remains auditable.

### Waiver chain

Validation refuses to skip steps: a waiver without compensating controls is
rejected (Appendix E), an update request without a proposal is rejected
(Appendix C), committee approval requires the CISO first, submission to SAMA
requires the committee, and marking a request Approved requires the SAMA
reference. The framework stays applicable while a waiver is pending — the
expiry field makes a lapsed waiver visible.

### Deliverable register

All 108 items from the SAMA deliverable workbook are seeded as master register
entries, each mapped to its sub-domain: 32 under Governance, 16 under Risk and
Compliance, 53 under Operations and Technology, 7 under Third Party. Mapping is
keyword-derived from the deliverable text and worth a review pass — the
sub-domain link is editable on every row.

## Dashboard

The Pathway Console gains a **SAMA CSF** tab: overall maturity against the
level-3 target, % of sub-domains at target, deliverables filed, and a count of
reportable incidents **not yet notified to SAMA** — the one number that carries
a regulatory deadline. Below it, maturity bars per domain with a target marker
at level 3, and the sub-domains furthest below target with their recorded gaps.
Quick actions start an assessment or open any SAMA register, scoped to the
selected client.

The workspace gains a SAMA section with two number cards (deliverables
outstanding, open waivers) and four shortcuts.

## Tests

`tests/test_sama.py`, 35 checks: the catalogue is compared code by code against
the sub-domains SAMA CSF v1.0 actually defines (no missing, none invented),
the 1.4 exclusions match the document, all 108 deliverables map to real
sub-domains, maturity scoring and the bank/non-bank divergence, division-by-zero
on an empty assessment, every step of the waiver chain, and the formal incident
report field set. Total across all suites: 223 checks.

# AlphaX GRC v2.5.0 — delivery plans and Gantt

## Added — plan templates, schedules, Gantt

**`GRC Plan Template`** + child task rows: WBS, task, working-day duration,
responsible role, phase, optional `depends_on`, optional `start_offset_days`,
deliverable, control reference. Duration `0` = milestone.

**`GRC Project Plan`** + child task rows: client, engagement, template, start
date, working week, holiday list. Load the template, then edit anything.

**Scheduling** (`pathway/scheduler.py`) dates every task from the start date:

- Working week is selectable — **Sun-Thu (KSA)** by default, plus Mon-Fri,
  Sat-Thu, and all-days. Non-working days are skipped inside durations, not
  just at the edges.
- Optional **Holiday List** link; holidays push end dates the same way.
- Positioning, in order: `start_offset_days` pins a task N working days from
  the plan start; `depends_on` starts it after that WBS finishes; otherwise it
  follows the row above.
- Milestones and summary rows (`1.0`) take a single day and do **not** advance
  the chain, so the task after a phase header starts where the last real piece
  of work ended.

**Editing without losing edits.** Change the plan start date and every task
reschedules on save. Any task marked **Locked** keeps its dates, and the chain
behind it picks up from where that task actually ends — so a date a client
fixed survives every later regeneration. Editing a bar in the Gantt locks it
by default.

**Gantt page** at `/app/grc-project-gantt`: month ruler, today line, bars
coloured by phase, progress fill from % complete, milestone diamonds, WBS
indent by depth, lock markers, zoom, and all seven themes. Click a bar to edit
start, duration, and % complete inline; the plan re-dates and the chart
redraws. A **Gantt Chart** button on the plan form opens it on that plan.

### Seeded templates

| Template | Tasks | From a 6 Sep 2026 start |
|---|---|---|
| ISO 27001:2022 ISMS Implementation | 24 | 111 working days, ends 4 Feb 2027 |
| SAMA CSF Implementation and Maturity Uplift | 47 | 305 working days, ends 7 Nov 2027 |
| NCA ECC-2:2024 Implementation | 30 | 205 working days, ends 20 Jun 2027 |

Durations for the ISO plan come from a delivered ISMS project. The SAMA plan
follows domains 3.1-3.4 of SAMA CSF v1.0 and targets maturity level 3.
Templates seed once — local durations are never overwritten on re-seed.

## Tests

`tests/test_scheduler.py`, 38 checks: KSA weekend handling, durations spanning
weekends, chain sequencing, `depends_on` overriding the chain, milestones
consuming no calendar, offsets, whole-plan reschedule, **locked tasks
surviving a reschedule with the chain resuming from their real end**, holiday
skipping, duration-weighted rollup, and every shipped template scheduling end
to end with unique WBS codes and resolvable dependencies.

# AlphaX GRC v2.4.0 — NFCRM-1:2025 alignment

## Fixed — risk ratings did not match the national framework

`_score_to_rating()` used bands of its own invention:

| | app v2.3.4 | NFCRM-1:2025 Figure 3 |
|---|---|---|
| Critical | 15+ | 20-25 |
| High | 10-14 | 15-19 |
| Medium | 5-9 | 8-14 |
| Low | below 5 | 3-7 |
| Very Low | never produced | 1-2 |

**14 of the 25 matrix cells were rated differently from the NCA framework.**
A score of 16 was reported as Critical where NFCRM says High; 12 as High where
NFCRM says Medium; 6 as Medium where NFCRM says Low. `Very Low` was an option
on the field that the code could never produce.

This is not cosmetic. NFCRM 5.5 requires entities to report Critical (5) and
High (4) risks to the NCA **immediately on identification**, so mis-banding
drives both over-reporting and under-reporting to the regulator.

Bands are now the NFCRM ones, applied to residual risk as well, and a score of
zero returns N/A rather than falling into the bottom band.

## Added — NFCRM structures

- **CIA-derived impact** (Figure 4). `impact_confidentiality`,
  `impact_integrity`, `impact_availability` on GRC Risk Register; overall
  impact is the highest of the three, since a breach of any one element sets
  the level. Matches the C/I/A columns in the client's working register.
- **`residual_rating`** — residual score was computed but never banded.
- **Likelihood basis** (Figure 5) — Time Frame or Exploitability, plus a
  rationale field, so an assessor records *why* a likelihood was chosen.
- **NCA reporting section** (NFCRM 5.5) — `nca_reportable` set automatically
  for Critical and High (respecting a manual override), plus
  `nca_reported_on`, `haseen_reference`, and `treatment_plan_submitted_on`.

## Tests

`tests/test_nfcrm.py` transcribes Figure 2 cell by cell and asserts all 25,
plus every band boundary (1, 2, 3, 7, 8, 14, 15, 19, 20, 25), CIA derivation,
and the reporting flag. 14 checks.

# AlphaX GRC v2.3.4

## Fixed — my bug, introduced in v2.3.1

```
An error occurred while installing alphax_grc: module_app
  installer.py:316  add_module_defs(name, ignore_if_duplicate=force)
  __init__.py:1183  frappe.new_doc("Module Def")
  modules/utils.py:299  app = frappe.local.module_app.get(scrub(module))
  werkzeug/local.py:88  raise AttributeError(name)   # name = 'module_app'
AttributeError: module_app
```

`retire_legacy_module_defs()` — the v2.3.1 "fix" — ended with:

```python
for key in ("module_app", "app_modules"):
    frappe.cache.delete_value(key)
    delattr(frappe.local, key)          # <-- this
```

`frappe.local` is a **werkzeug Local**. `delattr` on it does not reset the
attribute to a default; it removes it, and every later read raises
`AttributeError`. `frappe.local.module_app` is populated once by
`setup_module_map()` during `frappe.init()`, and nothing re-populates it
lazily. So the next `frappe.new_doc()` — three lines later, inside
`add_module_defs` — resolved a controller, reached for `local.module_app`, and
died.

The install now fails *earlier* than before, at line 316 instead of during
doctype sync, which is why the diagnostics from v2.3.3 never got to run.

The cache manipulation was pointless anyway: module -> app resolution reads
`modules.txt` on disk, not the Module Def rows that function repairs. There was
nothing to invalidate. `retire_legacy_module_defs()` now sets the values,
commits, and calls `frappe.clear_cache()` — leaving `frappe.local` untouched.

### Guard

`verify_tree.py` fails on any `delattr(frappe.local, ...)` or
`setattr(frappe.local, ...)` in app code, and `tests/test_offline.py` asserts
`frappe.local.module_app` still exists after the reclaim runs. Verified against
the buggy source:

```
FAIL  alphax_grc/install.py:479 delattr(frappe.local, ...) — frappe.local is a
      werkzeug Local; mutating it this way makes later reads raise
      AttributeError for the rest of the process
```

118 offline checks, 16 diagnostics checks, verify_tree clean.

# AlphaX GRC v2.3.3 — self-diagnosis

## Audit of the shipped package

Static scan across both modules, 102 doctypes: **no install blockers left.**
Every Link and Table field points at a doctype that ships here or is core.
Every report `ref_doctype`, workspace link, and shortcut resolves. No duplicate
fieldnames, no required Select without options, no autoname pointing at a
missing field.

Two non-fatal findings, both pre-existing:

**Four doctypes have a field literally named `owner`** — GRC Asset Inventory,
GRC Remediation Action, GRC Audit Finding, GRC Action Plan (all `Link` to
User, labelled "Owner" / "Asset Owner"). `owner` is a framework column on
every table, so the DocField and the framework column are the same column:
setting the business owner silently overwrites who created the record. That
breaks `if_owner` permission rules and the audit trail. It does not block
install — `validate_field_name_conflicts()` only runs on update, and `owner`
is not a controller method or property, so nothing throws. Renaming the fields
needs a data migration, so it is flagged, not changed.

**Thirteen doctypes have a truncated `field_order`** (e.g. GRC Action Plan
lists 1 of 17 fields). Frappe appends the unlisted fields after the ordered
ones, so the only effect is `client` hoisted to the top of the form. Cosmetic.

`verify_tree.py` now fails on framework-column collisions in the new module and
warns on them elsewhere, and warns on partial `field_order`.

## Added — alphax_grc/diagnostics.py

Eight checks against the live site, ordered by how early they bite, so the
first blocker is the one to fix. Each reports BLOCKER / WARNING / OK and
carries its own fix text.

```
bench --site <site> execute alphax_grc.diagnostics.preflight
```

```
========================================================================
AlphaX GRC preflight  —  site: testneo.frappe.cloud
========================================================================
[X] module ownership: 'GRC Evidence Automation' resolves to app
    'alphax_grc_evidence_automation', not alphax_grc
      Another app on this bench declares the same module in its
      modules.txt. Remove it from the bench group and deploy again.
[X] app registration: alphax_grc is NOT in installed_apps, but 102 of
    its DocTypes are in the database
      A previous install died inside sync_for...
------------------------------------------------------------------------
2 blocker(s), 3 warning(s).

STOPPER: 'GRC Evidence Automation' resolves to app ...
```

The checks:

1. **Module ownership** — resolves each of our modules through
   `frappe.get_module_app` and names the app that stole it. This is what
   actually stopped both installs.
2. **App registration** — catches the half-state: doctypes synced, app never
   added to `installed_apps` because `sync_for` died before
   `add_to_installed_apps`. Counts the stranded doctypes.
3. **Module Def records** — stale rows still owned by a retired app.
4. **Controllers** — imports every shipped controller for real and checks the
   class name `get_controller` will look for. The bug that broke two installs,
   now detectable in one command.
5. **Orphan doctypes** — DocType rows in the database with no file behind them.
6. **Roles** — DocPerms referencing a Role that does not exist.
7. **Seed data** — whether the policy library, NCA templates, frameworks and
   roles actually seeded, with a pointer to the Error Log entry for whichever
   seeder failed silently inside `bootstrap_grc()`.
8. **Scheduler** — enabled, and how many fetchers are live.

Also available from the desk when bench console is not, as **Run Diagnostics**
in the GRC Pathway Console menu, or
`/api/method/alphax_grc.diagnostics.run_diagnostics` (System Manager only).

`tests/test_diagnostics.py` runs the shipped module against simulated broken
sites — module conflict, half-install, orphan doctype — and asserts it names
the right stopper. Check 4 imports all 102 real controllers, so it is a genuine
regression test for the class-naming bug.

# AlphaX GRC v2.3.2

## The actual cause: the retired app is still on the bench

My v2.3.1 diagnosis was wrong. Module ownership does not come from
`tabModule Def`. Confirmed against frappe/version-15:

```python
# frappe/modules/utils.py
def get_module_app(module: str) -> str:
    app = frappe.local.module_app.get(scrub(module))

# frappe/__init__.py — setup_module_map()
apps = get_all_apps(with_internal_apps=True)   # sites/apps.txt: EVERY app on the bench
for app in apps:
    for module in get_module_list(app):        # that app's modules.txt, on disk
        local.app_modules[app].append(module)
...
for app, modules in local.app_modules.items():
    for module in modules:
        if module in local.module_app:
            warnings.warn(f"WARNING: module `{module}` found in apps `...` and `{app}`")
        local.module_app[module] = app         # last app on the bench wins
```

`alphax_grc_evidence_automation` is still on the bench. It is not installed on
the site — your traceback's `installed_apps` proves that — but it doesn't need
to be. It only has to be in `sites/apps.txt`, because `get_all_apps` reads the
bench, not the site. Its `modules.txt` still claims **GRC Evidence
Automation**, it sorts after `alphax_grc`, and last app wins.

So doctype sync reaches our child table and imports it from
`alphax_grc_evidence_automation` — the v0.3.0 copy on that bench, which is the
exact build missing `grc_global_policy_mapping.py`. Same error, same line,
because it is literally the same broken file being imported.

Frappe notices the collision and emits `warnings.warn()`, which goes nowhere
visible.

### Fix

**Remove `alphax_grc_evidence_automation` from the bench group and deploy.**

No uninstall needed — it was never successfully installed on the site. No code
change can work around this: the module map is built before any app code runs.

### What v2.3.2 adds

`assert_module_ownership()`, called from `before_install` and `before_migrate`.
It compares this app's `modules.txt` against `frappe.get_module_app()` for each
module and aborts immediately with:

```
AlphaX GRC cannot install while another app on this bench declares
the same module(s):

  - 'GRC Evidence Automation' is claimed by app 'alphax_grc_evidence_automation'

Remove alphax_grc_evidence_automation from the bench group and deploy again.
```

A readable failure at 0% instead of an ImportError at 95%. The v2.3.1 Module
Def repair stays — it keeps desk metadata consistent — but it was never going
to fix this on its own, and the changelog entry below overstates it.

# AlphaX GRC v2.3.1

## Fixed — install aborted at 95% with the old app's name in the traceback

```
Module import failed for GRC Global Policy Mapping
No module named 'alphax_grc_evidence_automation.grc_evidence_automation...'
```

The files had moved into `alphax_grc`, but the **site** still believed that
module belonged to the retired app.

Frappe resolves module -> app at runtime from `tabModule Def`.app_name (cached
as `frappe.local.module_app`), not from where the files sit on disk. The failed
install of the standalone add-on created:

```
Module Def: name = "GRC Evidence Automation"
            app_name = "alphax_grc_evidence_automation"
```

and that row outlived it. The install aborted before the app was ever
registered in `installed_apps` — the traceback confirms it, listing only
`frappe, erpnext, neotec_recurring, hrms` — so there was nothing to uninstall
and nothing cleaned it up. When `alphax_grc` then synced its own doctype in
that module, Frappe asked Module Def who owns it, got the retired app, and
tried to import a package that is no longer on the bench.

`retire_legacy_module_defs()` now repoints any Module Def owned by a retired
app back to `alphax_grc`, commits, and clears the `module_app` cache so the
running install picks up the change rather than re-reading the stale value.

It runs from `before_install` (which executes ahead of `sync_for`) and again as
a **pre_model_sync** patch, since doctype sync is the thing that breaks and
post-sync would be too late. Repointing rather than deleting: DocType rows
already reference the module by name, so a delete would have to cascade
through them.

Nothing to do by hand — deploy and install. If you would rather unblock the
current bench immediately, this is the same fix in `bench console`:

```python
frappe.db.set_value("Module Def", "GRC Evidence Automation", "app_name", "alphax_grc")
frappe.db.commit()
frappe.clear_cache()
```

# AlphaX GRC v2.3.0 — merged release

`alphax_grc_evidence_automation` no longer exists as a separate app. Its
contents ship inside `alphax_grc` as a second module, **GRC Evidence
Automation**. One repo, one App Source, one deploy, one version number.

## Fixed — 14 doctypes that could never be opened

`get_controller` derives a controller class name as
`doctype.replace(" ", "").replace("-", "")`. Fourteen controllers were named in
`GrcXxx` style instead of `GRCXxx`, so every one of them raised
`ImportError` the moment a record was instantiated:

| DocType | was | now |
|---|---|---|
| GRC NCA Policy Library | `GrcNcaPolicyLibrary` | `GRCNCAPolicyLibrary` |
| GRC NCA Standard Library | `GrcNcaStandardLibrary` | `GRCNCAStandardLibrary` |
| GRC NCA Procedure Library | `GrcNcaProcedureLibrary` | `GRCNCAProcedureLibrary` |
| GRC NCA Form Library | `GrcNcaFormLibrary` | `GRCNCAFormLibrary` |
| GRC Data Subject Request | `GrcDataSubjectRequest` | `GRCDataSubjectRequest` |
| GRC Regulatory Obligation | `GrcRegulatoryObligation` | `GRCRegulatoryObligation` |
| GRC Privacy Processing Activity | `GrcPrivacyProcessingActivity` | `GRCPrivacyProcessingActivity` |
| GRC Framework Pack | `GrcFrameworkPack` | `GRCFrameworkPack` |
| GRC Pack Framework Item | `GrcPackFrameworkItem` | `GRCPackFrameworkItem` |
| GRC Board Report | `GrcBoardReport` | `GRCBoardReport` |
| GRC ISO27001 Document | `GRCISo27001Document` | `GRCISO27001Document` |
| GRC Aramco Incident Notification | `GrcAramcoIncidentNotification` | `GRCAramcoIncidentNotification` |
| GRC Aramco Third Party Profile | `GrcAramcoThirdPartyProfile` | `GRCAramcoThirdPartyProfile` |
| GRC Vendor Question Item | `GrcVendorQuestionItem` | `GRCVendorQuestionItem` |

This is why the policy list looked missing. `seed_nca_policy_library()` calls
`frappe.get_doc({...}).insert()`, which resolves the controller and threw
before inserting a single row. `bootstrap_grc()` catches and swallows any
failing step, so all four NCA libraries silently stayed empty on every install,
and opening one from the desk would have errored too.

## Merged — GRC Evidence Automation module

Everything from the add-on, now native:

- 7 doctypes: `GRC Evidence Connector`, `GRC Evidence Fetcher`,
  `GRC Evidence Run`, `GRC Global Policy` (+ mapping child),
  `GRC Risk Treatment Action`, `GRC Pathway Settings`
- **GRC Pathway Console** page at `/app/grc-pathway-console`
- **GRC Pathway** workspace with the graphical themed board
- 53-policy global library with client adoption
- Evidence fetcher engine and its four scheduled jobs

Python lives in `alphax_grc/pathway/` (`setup`, `policies`, `board`, `api`,
`console`); doctypes, page, and workspace live in
`alphax_grc/grc_evidence_automation/`.

## Changed by the merge

- **`GRC Risk Register.treatment_actions` is now a native DocField**, inserted
  after `treatment_plan`. It used to be a Custom Field applied by a second app
  — one less moving part, and it appears in the doctype JSON where it belongs.
- **`required_apps` and the install-order dependency are gone.**
- Pathway seeding runs from `run_pathway_setup()`, called by `after_install`
  and `after_migrate` **outside `bootstrap_grc()`** — deliberately, so a
  failure is logged under its own title instead of being swallowed by the
  resilient bootstrap that hid the NCA library problem.
- Scheduler gains `hourly_long` / `daily_long` / `weekly_long` /
  `monthly_long` for evidence fetchers, alongside the existing jobs.

## verify_tree.py now covers the whole app

Run `python3 verify_tree.py` before every push. Guards that would have caught
this release's bugs: controller module exists, controller class named the way
`get_controller` expects, child tables declare no permissions, DocPerms name no
role that doesn't exist yet, Table fields point at real child tables, page
folder/name/module alignment, workspace blocks resolve to declared shortcuts
and cards, and `frappe.log_error` discipline.

Failures are scoped to the new module; the same findings in pre-existing code
are warnings so the guard is adoptable without a 97-doctype rewrite. Current
backlog, all non-blocking:

| Warnings | What |
|---|---|
| 392 | DocPerms naming GRC roles — works because `before_install` creates them first, but it's load-bearing |
| 71 | `frappe.log_error(traceback, "title")` positional — the traceback lands in the 140-char title field, the real title in the message |
| 23 | Pages shipped `standard = No` — `bench migrate` won't sync them from disk, hence `ensure_pages_exist()` |
| 15 | DocTypes with no `autoname` — falling back to hash names |

## Migration

`bench --site <site> migrate` after deploying. The v2.3.0 patch re-runs pathway
setup idempotently. If the standalone app was ever installed on a site,
uninstall it **after** this deploy; nothing needs to be moved by hand, since
table names follow the doctype, not the module.
