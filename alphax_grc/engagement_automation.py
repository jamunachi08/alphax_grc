"""AlphaX GRC v2.0.0 — Engagement-driven automation.

Three engagement-level automations live here:

1. auto_create_per_client_controls(engagement_doc)
   When an Engagement's frameworks_in_scope changes, create per-client
   control records for each newly-adopted framework. Skips frameworks
   already populated for that client. Idempotent.

2. auto_generate_tasks_from_finding(finding_doc)
   When a Finding moves to Open or In Progress, generate 3-5 Implementation
   Task records pre-assigned to the right team based on finding_category.
   Skips if tasks already exist for this finding.

3. recommend_phase_advance(engagement_name)
   AI-assisted phase advancement advisor. Reviews engagement state +
   blocker status and produces a recommendation. Falls back gracefully
   if alphax_grc_ai is not installed.
"""

import frappe
from frappe.utils import today


# ===========================================================================
# 1. Auto-create per-client controls when an Engagement adopts a framework
# ===========================================================================

# Mapping: framework name -> (catalog_doctype, control_doctype, fields_to_copy)
# fields_to_copy maps catalog field name -> per-client tracking field name
_FRAMEWORK_MAP = {
    "ISO 42001": {
        "catalog": "GRC ISO42001 Catalog",
        "tracking": "GRC ISO42001 Control",
        "fields": {
            "control_code": "control_code",
            "control_title": "control_title",
            "annex_section": "annex_section",
        },
    },
    "GDPR": {
        "catalog": "GRC GDPR Catalog",
        "tracking": "GRC GDPR Control",
        "fields": {
            "name": "catalog_ref",  # GDPR uses catalog_ref Link, not direct copy
        },
    },
    "NCA ECC-2:2024": {
        "catalog": "GRC NCA ECC Catalog",
        "tracking": "GRC NCA ECC Control",
        "fields": {
            "control_code": "control_code",
            "control_title": "control_title",
            "subdomain": "subdomain",
        },
    },
    # v2.1.0 — framework expansion
    "NIST CSF 2.0": {
        "catalog": "GRC NIST CSF Catalog",
        "tracking": "GRC NIST CSF Control",
        "fields": {
            "name": "catalog_ref",  # uses catalog_ref Link to fetch fields
        },
    },
    "ISO 22301": {
        "catalog": "GRC ISO22301 Catalog",
        "tracking": "GRC ISO22301 Control",
        "fields": {
            "name": "catalog_ref",  # uses catalog_ref Link to fetch fields
        },
    },
    # v2.2.0 — PDPL privacy pack
    "PDPL": {
        "catalog": "GRC PDPL Catalog",
        "tracking": "GRC PDPL Control",
        "fields": {
            "name": "catalog_ref",  # uses catalog_ref Link to fetch fields
        },
    },
}


def auto_create_per_client_controls(engagement_doc):
    """Called from GRC Engagement validate() when frameworks_in_scope changes.
    For each new framework, create per-client control records linked to the
    engagement's client. Idempotent — skips frameworks already populated.

    Returns a dict {framework: count_created}.
    """
    if not engagement_doc:
        return {}
    if not engagement_doc.client:
        return {}
    if not engagement_doc.frameworks_in_scope:
        return {}

    # Parse frameworks_in_scope (comma-separated string)
    frameworks = [
        f.strip()
        for f in (engagement_doc.frameworks_in_scope or "").split(",")
        if f.strip()
    ]
    if not frameworks:
        return {}

    # Avoid recursion if validate triggers a save
    if frappe.flags.get("alphax_grc_engagement_adopting"):
        return {}
    frappe.flags.alphax_grc_engagement_adopting = True

    results = {}
    try:
        for fw in frameworks:
            mapping = _FRAMEWORK_MAP.get(fw)
            if not mapping:
                # Framework not in our mapping yet (e.g. NIST CSF in v2.1)
                continue
            catalog_dt = mapping["catalog"]
            tracking_dt = mapping["tracking"]

            # Skip if catalog or tracking doctype doesn't exist on this site
            if not frappe.db.exists("DocType", catalog_dt):
                continue
            if not frappe.db.exists("DocType", tracking_dt):
                continue

            # Skip if this client already has any tracking records for this fw
            try:
                existing = frappe.db.count(
                    tracking_dt, {"client": engagement_doc.client}) or 0
            except Exception:
                existing = 0
            if existing > 0:
                results[fw] = f"skipped ({existing} already exist)"
                continue

            # Read all active catalog records
            try:
                if "is_active" in [f.fieldname for f in
                                   frappe.get_meta(catalog_dt).fields]:
                    catalog_rows = frappe.get_all(
                        catalog_dt, filters={"is_active": 1},
                        fields=["name"] + list(mapping["fields"].keys()),
                    )
                else:
                    catalog_rows = frappe.get_all(
                        catalog_dt,
                        fields=["name"] + list(mapping["fields"].keys()),
                    )
            except Exception:
                catalog_rows = []

            created = 0
            for row in catalog_rows:
                try:
                    # Build new tracking doc
                    new_doc = {
                        "doctype": tracking_dt,
                        "client": engagement_doc.client,
                        "engagement": engagement_doc.name,
                        "compliance_status": "Not Started",
                        "compliance_score": 0,
                    }
                    # Copy mapped fields from catalog
                    for src, tgt in mapping["fields"].items():
                        if src == "name":
                            new_doc[tgt] = row["name"]
                        else:
                            new_doc[tgt] = row.get(src) or ""

                    frappe.get_doc(new_doc).insert(ignore_permissions=True)
                    created += 1
                except Exception:
                    try:
                        frappe.log_error(
                            frappe.get_traceback(),
                            f"Auto-create per-client control failed: "
                            f"{tracking_dt} for {row.get('name')}")
                    except Exception:
                        pass

            results[fw] = f"{created} created"
            try:
                frappe.db.commit()
            except Exception:
                pass
    finally:
        frappe.flags.alphax_grc_engagement_adopting = False

    return results


# ===========================================================================
# 2. Auto-generate Implementation Tasks from new Findings
# ===========================================================================

# Default task templates per finding category. Each tuple is:
#   (task_title, responsible_team, default_offset_days, priority)
# When a Finding is created/opened, these become Implementation Tasks linked
# to the same engagement+control.
_TASK_TEMPLATES_BY_CATEGORY = {
    "Policy": [
        ("Draft policy document", "GRC Team", 7, "High"),
        ("Review with stakeholders", "GRC Team", 14, "Medium"),
        ("Get management approval", "Top Management", 21, "High"),
        ("Communicate to staff", "HR Administration", 28, "Medium"),
        ("Schedule annual review", "GRC Team", 30, "Low"),
    ],
    "Procedure": [
        ("Document the procedure", "GRC Team", 7, "High"),
        ("Process owner review", "GRC Team", 14, "Medium"),
        ("Pilot with one team", "IT Team", 21, "Medium"),
        ("Roll out broadly", "GRC Team", 30, "Medium"),
    ],
    "Standard/Guideline": [
        ("Author the standard", "GRC Team", 10, "Medium"),
        ("Technical review", "Cyber Security Team", 17, "Medium"),
        ("Approve and publish", "Top Management", 25, "Medium"),
    ],
    "Document Creating": [
        ("Identify document scope and template", "GRC Team", 5, "Medium"),
        ("Draft document", "GRC Team", 14, "Medium"),
        ("Stakeholder review", "GRC Team", 21, "Medium"),
        ("Finalize and publish", "GRC Team", 28, "Medium"),
    ],
    "Setup/Structure": [
        ("Design the structure", "GRC Team", 7, "High"),
        ("Implement the change", "IT Team", 14, "High"),
        ("Validate and document", "GRC Team", 21, "Medium"),
    ],
    "Configuration/System Check": [
        ("Identify current configuration", "IT Team", 3, "High"),
        ("Test proposed change in sandbox", "IT Team", 10, "High"),
        ("Apply configuration", "IT Team", 14, "Critical"),
        ("Verify and document", "Cyber Security Team", 18, "High"),
    ],
    "Revision": [
        ("Identify what needs revising", "GRC Team", 3, "Medium"),
        ("Draft revised version", "GRC Team", 10, "Medium"),
        ("Approve revision", "Top Management", 17, "Medium"),
        ("Publish revised version", "GRC Team", 21, "Medium"),
    ],
    "Training and Development": [
        ("Develop training content", "HR Administration", 14, "Medium"),
        ("Schedule training sessions", "HR Administration", 21, "Medium"),
        ("Deliver training", "HR Administration", 35, "Medium"),
        ("Track attendance and competency", "HR Administration", 42, "Low"),
    ],
    "Human Resource": [
        ("Define HR action required", "HR Administration", 5, "Medium"),
        ("Execute HR action", "HR Administration", 14, "High"),
        ("Document and close", "HR Administration", 21, "Low"),
    ],
    "Assessment": [
        ("Plan assessment scope", "GRC Team", 5, "Medium"),
        ("Conduct assessment", "GRC Team", 14, "High"),
        ("Document findings and remediation", "GRC Team", 21, "High"),
    ],
    "Recruitment and Onboarding": [
        ("Define role/profile", "HR Administration", 7, "Medium"),
        ("Recruit candidate", "HR Administration", 30, "High"),
        ("Onboard with security awareness", "HR Administration", 45, "Medium"),
    ],
}

# Default fallback if finding has no recognized category
_DEFAULT_TASK_TEMPLATES = [
    ("Investigate root cause", "GRC Team", 5, "High"),
    ("Define remediation plan", "GRC Team", 10, "High"),
    ("Implement remediation", "GRC Team", 21, "Medium"),
    ("Verify closure", "GRC Team", 28, "Medium"),
]


def auto_generate_tasks_from_finding(finding_doc):
    """Called from GRC Audit Finding's after_insert / on_update hook.
    When status flips to Open or In Progress, generate Implementation Tasks
    based on finding_category (or the default template if no category).

    Idempotent — skips if any tasks already exist linked to this finding.
    Returns the number of tasks created.
    """
    if not finding_doc:
        return 0
    if not frappe.db.exists("DocType", "GRC Implementation Task"):
        return 0

    # Don't generate while the doc is being inserted from auto-creation flow
    if frappe.flags.get("alphax_grc_finding_generating_tasks"):
        return 0

    # Only generate when status is Open or In Progress
    if (finding_doc.status or "").strip() not in ("Open", "In Progress"):
        return 0

    # Skip if tasks already exist
    try:
        existing = frappe.db.count("GRC Implementation Task",
                                   {"linked_finding": finding_doc.name}) or 0
    except Exception:
        existing = 0
    if existing > 0:
        return 0

    # Resolve template list — use category if known, else default
    category = (getattr(finding_doc, "finding_category", "") or "").strip()
    templates = _TASK_TEMPLATES_BY_CATEGORY.get(category, _DEFAULT_TASK_TEMPLATES)

    frappe.flags.alphax_grc_finding_generating_tasks = True
    created = 0
    try:
        for title, team, offset, priority in templates:
            try:
                task = frappe.get_doc({
                    "doctype": "GRC Implementation Task",
                    "task_title": title,
                    "engagement": getattr(finding_doc, "engagement", None),
                    "client": getattr(finding_doc, "client", None),
                    "control_reference": getattr(
                        finding_doc, "control_reference", "") or "",
                    "framework": getattr(finding_doc, "framework", "") or "",
                    "category": _category_to_task_category(category),
                    "responsible_team": team,
                    "priority": priority,
                    "status": "Pending",
                    "due_date": frappe.utils.add_days(today(), offset),
                    "task_description": (
                        f"Auto-generated from finding '{finding_doc.name}' "
                        f"to address: "
                        f"{getattr(finding_doc, 'finding_title', '') or ''}"),
                    "linked_finding": finding_doc.name,
                })
                task.insert(ignore_permissions=True)
                created += 1
            except Exception:
                try:
                    frappe.log_error(
                        frappe.get_traceback(),
                        f"Task auto-generate failed for finding "
                        f"{finding_doc.name}: '{title}'")
                except Exception:
                    pass
        try:
            frappe.db.commit()
        except Exception:
            pass
    finally:
        frappe.flags.alphax_grc_finding_generating_tasks = False

    return created


def _category_to_task_category(finding_category):
    """Map finding category to Implementation Task category Select option.
    These don't always line up 1:1 because they're separately maintained
    Select option lists; this helper normalizes the mapping."""
    return finding_category or "Document Creating"


# Hook entry point for finding events
def on_finding_created_or_updated(doc, method=None):
    """doc_events hook for GRC Audit Finding."""
    try:
        auto_generate_tasks_from_finding(doc)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "on_finding_created_or_updated failed")
        except Exception:
            pass


# ===========================================================================
# 3. AI-assisted phase advancement
# ===========================================================================

@frappe.whitelist()
def recommend_phase_advance(engagement_name):
    """AI-assisted advisor for phase advancement.

    Returns a structured recommendation:
      {
        "engagement": "ENG-####",
        "current_phase": int,
        "current_phase_label": "...",
        "next_phase": int or None,
        "recommendation": "advance" | "hold" | "review",
        "confidence": float (0-1),
        "reasoning": "...",
        "blockers": [list of strings],
        "ai_used": bool,
      }

    If alphax_grc_ai is installed and configured, asks the AI for a richer
    recommendation. Otherwise falls back to a deterministic rule-based
    recommendation using the same blockers logic the engagement.advance_phase
    method already implements.
    """
    if not engagement_name:
        frappe.throw("engagement_name required")
    if not frappe.db.exists("GRC Engagement", engagement_name):
        frappe.throw(f"Engagement {engagement_name} not found")

    eng = frappe.get_doc("GRC Engagement", engagement_name)
    blockers = eng.get_blockers()

    base = {
        "engagement": engagement_name,
        "current_phase": eng.current_phase_number or 0,
        "current_phase_label": eng.current_phase_label or "",
        "next_phase": (eng.current_phase_number or 0) + 1,
        "blockers": blockers,
        "ai_used": False,
    }

    # Deterministic rule-based recommendation as the floor
    if blockers:
        base["recommendation"] = "hold"
        base["confidence"] = 0.95
        base["reasoning"] = (
            f"{len(blockers)} blocker(s) prevent phase advance. "
            f"Resolve them before requesting advance: "
            + "; ".join(blockers[:3])
            + ("..." if len(blockers) > 3 else ""))
    elif eng.is_overdue:
        base["recommendation"] = "review"
        base["confidence"] = 0.7
        base["reasoning"] = (
            f"Phase has been active {eng.days_in_current_phase} days, "
            f"longer than expected duration. Review whether scope drift "
            f"or external blockers are slowing progress before advancing.")
    else:
        base["recommendation"] = "advance"
        base["confidence"] = 0.85
        base["reasoning"] = (
            "No blockers detected and phase duration is on schedule. "
            "Safe to advance.")

    # If alphax_grc_ai is available, layer on richer AI reasoning
    try:
        if "alphax_grc_ai" in frappe.get_installed_apps():
            ai_result = _ask_ai_for_advance_opinion(eng, blockers)
            if ai_result:
                base.update(ai_result)
                base["ai_used"] = True
    except Exception:
        # AI is best-effort; rule-based answer always available
        try:
            frappe.log_error(frappe.get_traceback(),
                             "alphax_grc_ai phase-advance call failed")
        except Exception:
            pass

    return base


def _ask_ai_for_advance_opinion(engagement_doc, blockers):
    """Ask alphax_grc_ai for an advance recommendation. Returns a dict
    with at least 'reasoning' and 'confidence' keys, or None if the AI
    extension can't be reached."""
    try:
        from alphax_grc_ai.api import get_phase_advance_recommendation
    except ImportError:
        return None

    try:
        return get_phase_advance_recommendation({
            "engagement_name": engagement_doc.name,
            "client": engagement_doc.client,
            "engagement_type": engagement_doc.engagement_type,
            "current_phase_number": engagement_doc.current_phase_number,
            "current_phase_label": engagement_doc.current_phase_label,
            "days_in_phase": engagement_doc.days_in_current_phase,
            "is_overdue": engagement_doc.is_overdue,
            "open_findings": engagement_doc.open_findings_count or 0,
            "high_risks": engagement_doc.high_risks_count or 0,
            "tasks_pending": engagement_doc.tasks_pending_count or 0,
            "tasks_overdue": engagement_doc.tasks_overdue_count or 0,
            "evidence_rule_failures": engagement_doc.evidence_rule_failures or 0,
            "blockers": blockers,
        })
    except Exception:
        return None


# ===========================================================================
# Hook helpers — used by Phase Templates' on_phase_start_method etc.
# ===========================================================================

def check_all_controls_assessed(engagement_doc):
    """Phase 3 (Assessment) auto-check: returns True if all in-scope controls
    have been assessed (compliance_status not 'Not Started' or blank)."""
    if not engagement_doc or not engagement_doc.client:
        return False
    return engagement_doc._assessment_threshold_met(1.0)


def check_critical_findings_closed(engagement_doc):
    """Phase 6 (Execution) auto-check: returns True if all Critical findings
    for this client/engagement are closed."""
    if not engagement_doc or not engagement_doc.client:
        return False
    if not frappe.db.exists("DocType", "GRC Audit Finding"):
        return True
    open_critical = frappe.db.count(
        "GRC Audit Finding", {
            "client": engagement_doc.client,
            "severity": "Critical",
            "status": ["in", ["Open", "In Progress"]],
        }) or 0
    return open_critical == 0
