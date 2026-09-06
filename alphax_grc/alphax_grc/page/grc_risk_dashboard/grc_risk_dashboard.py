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


@frappe.whitelist()
def get_risk_dashboard_data():
    """Return live data for the interactive Risk Dashboard.
    Aggregates risks, findings, KRIs, frameworks and compliance score."""
    _check_auth()

    data = {
        "kpis": {"critical_risks": 0, "open_findings": 0,
                 "compliance_score": 0, "overdue_actions": 0},
        "heatmap": [[0] * 5 for _ in range(5)],
        "top_risks": [],
        "frameworks": [],
        "kris": [],
        "severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
    }

    # --- Risks ---
    if frappe.db.exists("DocType", "GRC Risk Register"):
        risks = frappe.get_all(
            "GRC Risk Register",
            fields=["name", "risk_title", "impact", "likelihood",
                    "inherent_score", "risk_rating", "status"],
        )
        for r in risks:
            if r.risk_rating == "Critical":
                data["kpis"]["critical_risks"] += 1
            imp = max(1, min(5, int(r.impact or 1)))
            lik = max(1, min(5, int(r.likelihood or 1)))
            data["heatmap"][lik - 1][imp - 1] += 1
        top = sorted(
            [r for r in risks if (r.status or "Open") != "Closed"],
            key=lambda x: (x.inherent_score or 0),
            reverse=True,
        )[:8]
        data["top_risks"] = [
            {"name": r.name, "title": r.risk_title,
             "score": r.inherent_score or 0,
             "rating": r.risk_rating or "Low",
             "status": r.status or "Open"}
            for r in top
        ]

    # --- Findings ---
    if frappe.db.exists("DocType", "GRC Audit Finding"):
        findings = frappe.get_all(
            "GRC Audit Finding",
            filters=[["status", "not in", ["Closed", "Verified"]]],
            fields=["severity", "status"],
        )
        data["kpis"]["open_findings"] = len(findings)
        for f in findings:
            sev = f.severity or "Low"
            if sev in data["severity"]:
                data["severity"][sev] += 1

    # --- Overdue Remediation ---
    if frappe.db.exists("DocType", "GRC Remediation Action"):
        today = frappe.utils.today()
        overdue = frappe.get_all(
            "GRC Remediation Action",
            filters=[["due_date", "<", today], ["status", "!=", "Completed"]],
        )
        data["kpis"]["overdue_actions"] = len(overdue)

    # --- Frameworks ---
    # NOTE: GRC Framework has no compliance_score column. We derive it by
    # averaging the compliance_score of GRC Assessment records linked to
    # each framework (the same approach as api.py).
    if frappe.db.exists("DocType", "GRC Framework"):
        fws = frappe.get_all(
            "GRC Framework",
            fields=["name", "framework_name"],
        )
        framework_scores = []
        for f in fws:
            score = 0
            if frappe.db.exists("DocType", "GRC Assessment"):
                rows = frappe.db.sql(
                    """SELECT AVG(compliance_score) AS s
                       FROM `tabGRC Assessment`
                       WHERE framework = %s""",
                    (f.name,),
                    as_dict=True,
                )
                if rows and rows[0].s is not None:
                    score = int(rows[0].s)
            data["frameworks"].append({
                "name": f.framework_name or f.name,
                "score": score,
            })
            framework_scores.append(score)
        if framework_scores:
            data["kpis"]["compliance_score"] = int(
                sum(framework_scores) / len(framework_scores)
            )

    # --- KRIs ---
    if frappe.db.exists("DocType", "GRC KRI"):
        kris = frappe.get_all(
            "GRC KRI",
            fields=["indicator_name", "current_value",
                    "threshold_value", "status"],
            limit=8,
        )
        data["kris"] = [
            {"name": k.indicator_name,
             "current": k.current_value,
             "threshold": k.threshold_value,
             "status": k.status or "OK"}
            for k in kris
        ]

    return data


@frappe.whitelist()
def save_user_theme(theme_json):
    """Persist a user's colour theme as a User default."""
    _check_auth()
    import json
    # Validate it parses as JSON; reject anything else
    try:
        parsed = json.loads(theme_json) if isinstance(theme_json, str) else theme_json
        if not isinstance(parsed, dict):
            raise ValueError("Theme must be a JSON object")
    except Exception:
        frappe.throw("Invalid theme payload.")
    frappe.defaults.set_user_default(
        "grc_risk_dashboard_theme",
        json.dumps(parsed),
        frappe.session.user,
    )
    return {"ok": True}


@frappe.whitelist()
def load_user_theme():
    """Return the saved theme for the current user, or empty dict."""
    _check_auth()
    import json
    raw = frappe.defaults.get_user_default(
        "grc_risk_dashboard_theme", frappe.session.user
    )
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}
