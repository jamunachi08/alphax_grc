import frappe

_GRC_DASHBOARD_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive", "Compliance Officer",
    "GRC Assessor", "GRC Auditor", "Risk Owner", "Privacy Officer",
    "Aramco Compliance Owner",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_DASHBOARD_ROLES):
        frappe.throw("You are not permitted to access this GRC resource.",
                     frappe.PermissionError)


def _client_filter(client):
    """Build a filters dict that includes the client scope when given."""
    return {"client": client} if client else {}


@frappe.whitelist()
def get_lifecycle_data(client=None):
    """Return per-stage progress for the lifecycle wheel.

    Eight stages: Setup → Register → Assess → Control → Audit → Remediate
    → Report → Review. Each returns {total, complete, in_progress, status}.
    Status: 'green' (>=80% complete), 'amber' (40-80%), 'red' (<40%).
    """
    _check_auth()
    cf = _client_filter(client)

    def _safe_count(doctype, filters=None):
        if not frappe.db.exists("DocType", doctype):
            return 0
        f = dict(cf or {})
        if filters:
            f.update(filters)
        return frappe.db.count(doctype, f) or 0

    def _stage_status(complete, total):
        if total == 0:
            return {"total": 0, "complete": 0, "pct": 0, "status": "empty"}
        pct = (complete / total) * 100
        if pct >= 80:
            status = "green"
        elif pct >= 40:
            status = "amber"
        else:
            status = "red"
        return {"total": total, "complete": complete,
                "pct": round(pct, 1), "status": status}

    # Stage 1 — Setup: client profile complete? Frameworks loaded?
    setup_total = 0
    setup_complete = 0
    if client:
        cp = frappe.db.get_value(
            "GRC Client Profile", client,
            ["country", "sector", "applicable_frameworks", "lead_consultant"],
            as_dict=True,
        )
        if cp:
            checks = [bool(cp.country), bool(cp.sector),
                      bool(cp.applicable_frameworks), bool(cp.lead_consultant)]
            setup_total = len(checks)
            setup_complete = sum(checks)
    else:
        # Firm-wide view: count all active clients as setup-complete
        setup_total = _safe_count("GRC Client Profile") or 0
        setup_complete = _safe_count("GRC Client Profile", {"is_active": 1}) or 0

    # Stage 2 — Register: risks & assets registered
    risks_total = _safe_count("GRC Risk Register")
    risks_with_owner = 0
    if risks_total and frappe.db.exists("DocType", "GRC Risk Register"):
        f = dict(cf or {})
        f["risk_owner"] = ["is", "set"]
        risks_with_owner = _safe_count("GRC Risk Register", {"risk_owner": ["is", "set"]})
    assets_total = _safe_count("GRC Asset Inventory")
    register_total = risks_total + assets_total
    register_complete = risks_with_owner + assets_total  # assets are 'done' once registered

    # Stage 3 — Assess: assessment runs
    assess_total = _safe_count("GRC Assessment Run")
    assess_complete = _safe_count("GRC Assessment Run", {"status": "Completed"})

    # Stage 4 — Control: controls implemented
    control_total = _safe_count("GRC Control")
    control_complete = _safe_count("GRC Control", {"implementation_status": "Implemented"})

    # Stage 5 — Audit: audit plans + findings raised
    audit_total = _safe_count("GRC Audit Plan")
    audit_complete = _safe_count("GRC Audit Plan", {"status": "Completed"})

    # Stage 6 — Remediate: findings vs remediation actions closed
    findings_open = _safe_count("GRC Audit Finding",
                                 {"status": ["not in", ["Closed", "Verified"]]})
    findings_total = _safe_count("GRC Audit Finding")
    remediate_complete = max(findings_total - findings_open, 0)

    # Stage 7 — Report: board reports produced
    report_total = _safe_count("GRC Board Report")
    report_complete = _safe_count("GRC Board Report", {"status": "Published"})

    # Stage 8 — Review: KRIs in normal status as proxy for review health
    kri_total = _safe_count("GRC KRI")
    kri_ok = _safe_count("GRC KRI", {"status": "Normal"})

    return {
        "client": client,
        "stages": [
            {"id": 1, "name": "Setup",     **_stage_status(setup_complete, setup_total),
             "route": "/app/grc-client-profile" + (f"/{client}" if client else "")},
            {"id": 2, "name": "Register",  **_stage_status(register_complete, register_total),
             "route": "/app/grc-risk-register"},
            {"id": 3, "name": "Assess",    **_stage_status(assess_complete, assess_total),
             "route": "/app/grc-assessment-run"},
            {"id": 4, "name": "Control",   **_stage_status(control_complete, control_total),
             "route": "/app/grc-control"},
            {"id": 5, "name": "Audit",     **_stage_status(audit_complete, audit_total),
             "route": "/app/grc-audit-plan"},
            {"id": 6, "name": "Remediate", **_stage_status(remediate_complete, findings_total),
             "route": "/app/grc-audit-finding"},
            {"id": 7, "name": "Report",    **_stage_status(report_complete, report_total),
             "route": "/app/grc-board-report"},
            {"id": 8, "name": "Review",    **_stage_status(kri_ok, kri_total),
             "route": "/app/grc-kri"},
        ],
    }


@frappe.whitelist()
def get_firm_overview():
    """Firm-wide cross-client roll-up. For partners only."""
    _check_auth()
    if not frappe.db.exists("DocType", "GRC Client Profile"):
        return {"clients": [], "totals": {}}

    clients = frappe.get_all(
        "GRC Client Profile",
        filters={"is_active": 1},
        fields=["name", "client_name", "country", "sector",
                "compliance_score", "open_risks", "open_findings",
                "lead_consultant", "engagement_type"],
        order_by="modified desc",
    )

    totals = {
        "active_clients": len(clients),
        "total_open_risks": sum(int(c.open_risks or 0) for c in clients),
        "total_open_findings": sum(int(c.open_findings or 0) for c in clients),
        "avg_compliance": (
            round(sum(int(c.compliance_score or 0) for c in clients) / len(clients), 1)
            if clients else 0
        ),
        "by_country": {},
        "by_sector": {},
    }
    for c in clients:
        totals["by_country"][c.country] = totals["by_country"].get(c.country, 0) + 1
        totals["by_sector"][c.sector]   = totals["by_sector"].get(c.sector, 0) + 1

    return {"clients": clients, "totals": totals}
