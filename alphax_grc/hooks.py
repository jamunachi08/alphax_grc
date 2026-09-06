app_name = "alphax_grc"
app_title = "AlphaX GRC"
app_publisher = "IRSAA Business Solutions"
app_description = "Saudi-first Governance, Risk and Compliance app for Frappe"
app_email = "support@irsaa.com"
app_license = "MIT"
app_version = "2.11.0"

required_apps = []

before_install = "alphax_grc.install.before_install"
before_migrate = "alphax_grc.install.before_migrate"
after_install = "alphax_grc.install.after_install"

# v1.9.6 — repair runs AFTER migrate so doctype installations complete first
# (was before_migrate in v1.9.4-v1.9.5; that ordering could abort migration if
# repair crashed before doctypes were installed/upgraded).
after_migrate = "alphax_grc.install.after_migrate"

app_include_css = [
    "/assets/alphax_grc/css/grc_global_theme.css",
    "/assets/alphax_grc/css/grc_command_center.css",
    "/assets/alphax_grc/css/grc_reports.css",
    "/assets/alphax_grc/css/grc_neo_hub.css",
]

# v1.3.2 — shared liveness module (auto-refresh + realtime + indicator).
# Loaded on every desk page so dashboards can call frappe.alphaxGRC.live().
# v1.7.0 — theme loader runs first on every page to apply branding.
app_include_js = [
    "/assets/alphax_grc/js/grc_theme_loader.js",
    "/assets/alphax_grc/js/grc_visual_feast.js",
    "/assets/alphax_grc/js/grc_dashboard_live.js",
]

# ---------------------------------------------------------------------------
# GRC Evidence Automation module (merged from alphax_grc_evidence_automation
# in v2.3.0 — see CHANGELOG). Form scripts and scheduled jobs for the pathway,
# policy library, and evidence fetchers.
# ---------------------------------------------------------------------------
doctype_js = {
    "GRC Evidence Fetcher": "public/js/grc_evidence_fetcher.js",
    "GRC Project Plan": "public/js/grc_project_plan.js",
    "GRC Plan Template": "public/js/grc_project_plan.js",
}

doctype_list_js = {
    "GRC Global Policy": "public/js/grc_global_policy_list.js",
}

fixtures = []  # Cloud-hardened: an EMPTY grc_pages.json is shipped in fixtures/
               # to overwrite any stale legacy file on disk that contained
               # standard=Yes Page records (which require Developer Mode).

# ---------------------------------------------------------------------------
# Scheduled jobs
# ---------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "alphax_grc.notifications.send_overdue_remediation_alerts",
        "alphax_grc.notifications.send_expiring_exception_alerts",
        "alphax_grc.notifications.send_vendor_review_reminders",
        "alphax_grc.notifications.send_policy_review_reminders",
        "alphax_grc.notifications.send_overdue_dsr_alerts",
        "alphax_grc.notifications.check_kri_breaches",
        # v1.4.3 — Aramco CCC
        "alphax_grc.notifications.check_aramco_certificate_renewals",
        "alphax_grc.notifications.check_aramco_incident_escalation",
        # v1.7.0 — Continuous Control Monitoring: re-evaluate every active rule daily
        "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.evaluate_all_active_rules",
    ],
    # v1.3.2 — refresh dashboard snapshots every 15 minutes so even
    # without realtime invalidation, dashboards never lag more than 15m.
    "hourly_long": [
        "alphax_grc.grc_evidence_automation.tasks.run_due_evidence_fetchers",
    ],
    "daily_long": [
        "alphax_grc.grc_evidence_automation.tasks.run_due_daily_evidence_fetchers",
    ],
    "weekly_long": [
        "alphax_grc.grc_evidence_automation.tasks.run_due_weekly_evidence_fetchers",
    ],
    "monthly_long": [
        "alphax_grc.grc_evidence_automation.tasks.run_due_monthly_evidence_fetchers",
    ],
    "cron": {
        "*/15 * * * *": [
            "alphax_grc.dashboards_live.refresh_all_snapshots",
        ],
    },
}

# ---------------------------------------------------------------------------
# Doc-level hooks (wire up cross-doc logic on save/submit)
# ---------------------------------------------------------------------------
doc_events = {
    # v2.10.0 — snapshot an immutable, hash-chained version whenever a
    # policy is published, so what was published on a given date can be
    # proven later even if the live record is edited afterwards.
    "GRC Policy": {
        "on_update": "alphax_grc.policy_versioning.snapshot_if_published",
    },
    "GRC KRI": {
        "on_update": [
            "alphax_grc.notifications.kri_on_update",
            "alphax_grc.dashboards_live.invalidate_dashboards",
        ],
    },
    "GRC Audit Finding": {
        "on_update": [
            "alphax_grc.notifications.finding_on_update",
            "alphax_grc.dashboards_live.invalidate_dashboards",
            # v2.0.0 — auto-generate Implementation Tasks when finding opens
            "alphax_grc.engagement_automation.on_finding_created_or_updated",
        ],
        "after_insert": [
            # v2.0.0 — also fire on creation so newly-created Open findings
            # immediately get their task list
            "alphax_grc.engagement_automation.on_finding_created_or_updated",
        ],
    },
    "GRC Incident": {
        "on_update": [
            "alphax_grc.notifications.incident_on_update",
            "alphax_grc.dashboards_live.invalidate_dashboards",
        ],
    },
    # v1.3.2 — broadcast realtime invalidation when other tenant-scoped
    # records change, so dashboards never go stale.
    "GRC Risk Register":     {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Assessment":        {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Assessment Run":    {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Control":           {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Asset Inventory":   {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Remediation Action":{"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Framework":         {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Exception":         {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Risk Acceptance":   {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Maturity Assessment":{"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Vendor":            {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Vendor Assessment": {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Consultant Timesheet":{"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    # v1.4.0 — new tenant-scoped doctypes
    "GRC Vulnerability":     {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC KPI":               {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    # v1.4.3 — Aramco CCC dashboards
    "GRC Aramco CCC Engagement": {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Aramco Certificate":    {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Aramco Incident Notification": {
        "on_update": [
            "alphax_grc.notifications.aramco_incident_on_update",
            "alphax_grc.dashboards_live.invalidate_dashboards",
        ],
    },

    # v1.7.0 — ERPNext audit hooks: every save on these doctypes triggers
    # any active GRC Evidence Rules whose source_doctype matches.
    # The trigger function NEVER raises — it logs errors and returns silently
    # so it can't block legitimate ERPNext operations.
    # Add doctypes here as new Evidence Rules cover them.
    "Employee":            {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Employee Separation": {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Sales Invoice":       {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Purchase Invoice":    {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Asset":               {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Supplier":            {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "User":                {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "User Permission":     {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Stock Entry":         {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Issue":               {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Project":             {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},
    "Activity Log":        {"on_update": "alphax_grc.alphax_grc.doctype.grc_evidence_rule.grc_evidence_rule.trigger_realtime_evaluation"},

    # v1.7.0 — ISO 42001 dashboard refresh
    "GRC ISO42001 Control":{"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC ISO42001 Catalog":{"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
    "GRC Evidence Rule":   {"on_update": "alphax_grc.dashboards_live.invalidate_dashboards"},
}


# Theme API whitelist (additional entry point)
# alphax_grc.alphax_grc.doctype.grc_theme_settings.grc_theme_settings.get_theme
# is already whitelisted via @frappe.whitelist() decorator
