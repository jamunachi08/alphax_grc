import frappe


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _settings():
    cache_key = "_alphax_grc_settings"
    cached = frappe.local.flags.get(cache_key)
    if cached:
        return cached
    if frappe.db.exists("DocType", "AlphaX GRC Settings") and frappe.db.exists(
        "AlphaX GRC Settings", "AlphaX GRC Settings"
    ):
        s = frappe.get_doc("AlphaX GRC Settings", "AlphaX GRC Settings").as_dict()
    else:
        s = {}
    frappe.local.flags[cache_key] = s
    return s


def _module_enabled(flag):
    s = _settings()
    val = s.get(flag)
    return val in (None, 1, True)


def _count(doctype, filters=None):
    if not frappe.db.exists("DocType", doctype):
        return 0
    return frappe.db.count(doctype, filters=filters or {})


def _avg(doctype, fieldname, filters=None):
    if not frappe.db.exists("DocType", doctype):
        return 0
    values = frappe.get_all(doctype, filters=filters or {}, pluck=fieldname)
    numbers = [float(v) for v in values if v not in (None, "")]
    return round(sum(numbers) / len(numbers), 2) if numbers else 0


def _group_count(doctype, fieldname, filters=None, limit=10):
    if not frappe.db.exists("DocType", doctype):
        return []
    rows = frappe.get_all(
        doctype,
        filters=filters or {},
        fields=[fieldname + " as label", "count(name) as value"],
        group_by=fieldname,
        order_by="value desc",
        limit=limit,
    )
    return [r for r in rows if r.get("label")]


# ---------------------------------------------------------------------------
# Authorization helper
# ---------------------------------------------------------------------------

# Roles allowed to read aggregated GRC dashboards.
GRC_DASHBOARD_ROLES = {
    "System Manager",
    "GRC Admin",
    "GRC Executive",
    "Compliance Officer",
    "GRC Assessor",
    "GRC Auditor",
    "Risk Owner",
    "Privacy Officer",
    "Aramco Compliance Owner",
}


def _require_grc_role(allowed=None):
    """Block access to GRC API endpoints unless the caller has at least one
    of the allowed roles. Defaults to GRC_DASHBOARD_ROLES.
    Guests are always rejected."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    roles = set(frappe.get_roles(frappe.session.user) or [])
    needed = set(allowed) if allowed else GRC_DASHBOARD_ROLES
    if not (roles & needed):
        frappe.throw("You are not permitted to access this GRC resource.",
                     frappe.PermissionError)



@frappe.whitelist()
def get_command_center_data():
    _require_grc_role()
    result = {
        "headline": {},
        "by_domain": [],
        "framework_coverage": [],
        "heatmap": [],
        "recent_findings": [],
        "active_audits": [],
        "kri_rows": [],
        "module_flags": {
            "incident": _module_enabled("enable_incident_management"),
            "vendor": _module_enabled("enable_vendor_risk"),
            "audit": _module_enabled("enable_audit_management"),
            "policy": _module_enabled("enable_policy_management"),
            "control_library": _module_enabled("enable_control_library"),
        },
    }
    result["headline"]["compliance_score"] = _avg("GRC Assessment", "compliance_score")
    result["headline"]["maturity_score"] = _avg("GRC Maturity Assessment", "maturity_level") * 20
    result["headline"]["critical_risks"] = _count("GRC Risk Register", {"inherent_score": [">=", 15], "status": ["not in", ["Closed"]]})
    result["headline"]["exceptions_active"] = _count("GRC Exception", {"status": ["in", ["Approved", "Active"]]})
    result["headline"]["accepted_risks"] = _count("GRC Risk Acceptance", {"status": "Accepted"})

    if _module_enabled("enable_audit_management"):
        result["headline"]["open_findings"] = _count("GRC Audit Finding", {"status": ["not in", ["Closed"]]})
        result["headline"]["overdue_actions"] = _count("GRC Remediation Action", {"status": ["not in", ["Closed", "Verified"]], "due_date": ["<", frappe.utils.today()]})
        result["recent_findings"] = frappe.get_all("GRC Audit Finding", filters={"status": ["not in", ["Closed"]]}, fields=["name", "finding_title", "severity", "due_date", "owner"], order_by="modified desc", limit=5) if frappe.db.exists("DocType", "GRC Audit Finding") else []
        result["active_audits"] = frappe.get_all("GRC Audit Plan", filters={"status": ["in", ["Planned", "In Progress"]]}, fields=["name", "audit_title", "status", "planned_end_date", "audit_owner"], order_by="planned_end_date asc", limit=5) if frappe.db.exists("DocType", "GRC Audit Plan") else []

    if _module_enabled("enable_control_library"):
        result["headline"]["controls_tested"] = _count("GRC Control Library", {"status": "Active"})
        result["by_domain"] = _group_count("GRC Control Library", "domain", {"status": "Active"}, limit=8)

    if frappe.db.exists("DocType", "GRC Framework"):
        for row in frappe.get_all("GRC Framework", fields=["name", "framework_name"], order_by="framework_name asc"):
            score = _avg("GRC Assessment", "compliance_score", {"framework": row.name})
            maturity = _avg("GRC Maturity Assessment", "maturity_level", {"framework": row.name}) * 20
            result["framework_coverage"].append({"label": row.framework_name or row.name, "value": max(score, maturity)})

    if frappe.db.exists("DocType", "GRC Risk Register"):
        risks = frappe.get_all("GRC Risk Register", filters={"status": ["not in", ["Closed"]]}, fields=["impact", "likelihood"], limit=500)
        matrix = {(i, j): 0 for i in range(1, 6) for j in range(1, 6)}
        for risk in risks:
            try:
                i, j = int(risk.get("impact") or 0), int(risk.get("likelihood") or 0)
            except Exception:
                continue
            if 1 <= i <= 5 and 1 <= j <= 5:
                matrix[(i, j)] += 1
        result["heatmap"] = [{"impact": i, "likelihood": j, "count": matrix[(i, j)]} for i in range(5, 0, -1) for j in range(1, 6)]

    if _module_enabled("enable_incident_management"):
        result["kri_rows"] = frappe.get_all("GRC KRI", fields=["indicator_name", "current_value", "threshold_value", "status"], order_by="modified desc", limit=6) if frappe.db.exists("DocType", "GRC KRI") else []

    return result


@frappe.whitelist()
def get_board_report_data():
    _require_grc_role({"System Manager", "GRC Admin", "GRC Executive", "Compliance Officer"})
    top_risks = frappe.get_all("GRC Risk Register", fields=["name", "risk_title", "inherent_score", "residual_score", "status", "risk_owner", "risk_rating"], order_by="inherent_score desc", limit=10) if frappe.db.exists("DocType", "GRC Risk Register") else []
    findings = frappe.get_all("GRC Audit Finding", fields=["name", "finding_title", "severity", "status", "due_date"], order_by="modified desc", limit=10) if frappe.db.exists("DocType", "GRC Audit Finding") else []
    decisions_required = [{"type": "Finding", "title": f.get("finding_title"), "severity": f.get("severity")} for f in findings if f.get("severity") in {"Critical", "High"} and f.get("status") not in {"Verified", "Closed"}]
    return {
        "summary": {"compliance_score": _avg("GRC Assessment", "compliance_score"), "maturity_score": _avg("GRC Maturity Assessment", "maturity_level") * 20, "open_findings": _count("GRC Audit Finding", {"status": ["not in", ["Closed"]]}), "overdue_actions": _count("GRC Remediation Action", {"status": ["not in", ["Closed", "Verified"]], "due_date": ["<", frappe.utils.today()]})},
        "top_risks": top_risks,
        "findings": findings,
        "decisions_required": decisions_required,
    }


@frappe.whitelist()
def get_audit_report_data(audit_plan=None):
    _require_grc_role({"System Manager", "GRC Admin", "GRC Auditor", "Compliance Officer", "GRC Executive"})
    filters = {"audit_plan": audit_plan} if audit_plan else {}
    plan = frappe.get_doc("GRC Audit Plan", audit_plan).as_dict() if audit_plan and frappe.db.exists("GRC Audit Plan", audit_plan) else None
    findings = frappe.get_all("GRC Audit Finding", filters=filters, fields=["finding_title", "severity", "resolution_type", "status", "observation", "recommendation", "management_response"], order_by="severity asc, modified desc", limit=200) if frappe.db.exists("DocType", "GRC Audit Finding") else []
    summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for row in findings:
        sev = row.get("severity") or "Low"
        summary[sev] = summary.get(sev, 0) + 1
    return {"audit_plan": plan, "severity_summary": summary, "findings": findings}


@frappe.whitelist()
def get_compliance_status_report():
    _require_grc_role()
    rows = []
    if frappe.db.exists("DocType", "GRC Framework"):
        for fw in frappe.get_all("GRC Framework", fields=["name", "framework_name"], order_by="framework_name asc"):
            rows.append({"framework": fw.framework_name or fw.name, "controls": _count("GRC Control Library", {"primary_framework": fw.name}) + _count("GRC Control", {"framework": fw.name}), "assessments": _count("GRC Assessment", {"framework": fw.name}), "compliance_score": _avg("GRC Assessment", "compliance_score", {"framework": fw.name}), "maturity_score": _avg("GRC Maturity Assessment", "maturity_level", {"framework": fw.name}) * 20})
    return rows


@frappe.whitelist()
def get_neo_hub_data():
    _require_grc_role()
    base = get_command_center_data()
    vendor_reviews_due = 0
    open_privacy_requests = 0
    if _module_enabled("enable_vendor_risk") and frappe.db.exists("DocType", "GRC Vendor"):
        from frappe.utils import add_days, today
        cutoff = str(add_days(today(), 30))
        vendor_reviews_due = _count("GRC Vendor", {"status": ["in", ["Active", "Under Review"]], "next_review_date": ["between", [today(), cutoff]]})
    if frappe.db.exists("DocType", "GRC Data Subject Request"):
        open_privacy_requests = _count("GRC Data Subject Request", {"status": ["not in", ["Closed", "Rejected"]]})
    framework_packs = frappe.get_all("GRC Framework Pack", fields=["pack_name", "pack_name_ar", "coverage_score", "mandatory_controls"], order_by="coverage_score desc", limit=8) if frappe.db.exists("DocType", "GRC Framework Pack") else []
    obligations = frappe.get_all("GRC Regulatory Obligation", fields=["obligation_title", "obligation_title_ar", "owner_user", "status"], order_by="modified desc", limit=8) if frappe.db.exists("DocType", "GRC Regulatory Obligation") else []
    privacy_rows = frappe.get_all("GRC Privacy Processing Activity", fields=["activity_name", "activity_name_ar", "purpose", "status"], order_by="modified desc", limit=8) if frappe.db.exists("DocType", "GRC Privacy Processing Activity") else []
    board_rows = frappe.get_all("GRC Board Report", fields=["report_title", "report_title_ar", "decision_type", "status", "board_review_date"], order_by="modified desc", limit=8) if frappe.db.exists("DocType", "GRC Board Report") else []
    aramco_rows = frappe.get_all("GRC Aramco Third Party Profile", fields=["third_party_name", "third_party_name_ar", "network_connectivity", "status"], order_by="modified desc", limit=8) if frappe.db.exists("DocType", "GRC Aramco Third Party Profile") else []
    base["headline"].update({"vendor_reviews_due": vendor_reviews_due, "open_privacy_requests": open_privacy_requests})
    base.update({"framework_packs": framework_packs, "obligations": obligations, "privacy_rows": privacy_rows, "board_rows": board_rows, "aramco_rows": aramco_rows})
    return base


@frappe.whitelist()
def start_assessment_run(template_name, customer_name=None, customer_country=None):
    _require_grc_role({"System Manager", "GRC Admin", "Compliance Officer", "GRC Assessor"})
    if not frappe.has_permission("GRC Assessment Run", "create"):
        frappe.throw("You are not permitted to create GRC Assessment Runs.",
                     frappe.PermissionError)
    if not frappe.db.exists("GRC Assessment Template", template_name):
        frappe.throw("Assessment Template not found")
    template = frappe.get_doc("GRC Assessment Template", template_name)
    doc = frappe.get_doc({
        "doctype": "GRC Assessment Run",
        "assessment_title": f"{template.template_name} — {customer_name or 'New Assessment'}",
        "assessment_title_ar": template.template_name_ar,
        "assessment_template": template.name,
        "customer_name": customer_name,
        "customer_country": customer_country,
        "lead_consultant": frappe.session.user,
        "status": "Draft",
        "assessment_date": frappe.utils.today(),
    })
    for q in template.questions or []:
        doc.append("responses", {"section": q.section, "question_code": q.question_code, "question_text": q.question_text, "question_text_ar": q.question_text_ar, "framework_reference": q.framework_reference, "response_type": q.response_type, "weight": q.weight, "recommendation": q.expected_evidence, "max_score": 5})
    doc.insert()
    return {"name": doc.name, "route": f"/app/grc-assessment-run/{doc.name}"}


@frappe.whitelist()
def get_assessment_summary(assessment_run):
    _require_grc_role()
    if not frappe.has_permission("GRC Assessment Run", "read", doc=assessment_run):
        frappe.throw("You are not permitted to read this Assessment Run.",
                     frappe.PermissionError)
    if not frappe.db.exists("GRC Assessment Run", assessment_run):
        frappe.throw("Assessment Run not found")
    doc = frappe.get_doc("GRC Assessment Run", assessment_run)
    sections = {}
    for row in doc.responses or []:
        sec = row.section or "General"
        sections.setdefault(sec, {"yes": 0, "partial": 0, "no": 0, "total": 0, "earned": 0.0, "max": 0.0})
        s = sections[sec]
        s["total"] += 1
        w = float(row.weight or 1)
        s["max"] += w * 5
        ans = (row.answer_option or "").strip()
        if ans in ("Yes", "Fully Implemented"):
            s["yes"] += 1; s["earned"] += w * 5
        elif ans in ("Partial", "Partially Implemented"):
            s["partial"] += 1; s["earned"] += w * 3
        elif ans != "Not Applicable":
            s["no"] += 1
    section_scores = [{"section": sec, "score_pct": round((v["earned"] / v["max"]) * 100, 1) if v["max"] else 0, **v} for sec, v in sections.items()]
    return {"name": doc.name, "assessment_title": doc.assessment_title, "customer_name": doc.customer_name, "maturity_score": doc.maturity_score, "maturity_label": doc.maturity_label, "yes_score": doc.yes_score, "partial_score": doc.partial_score, "no_score": doc.no_score, "total_questions": len(doc.responses or []), "section_scores": section_scores, "status": doc.status}


@frappe.whitelist()
def get_itgc_dashboard():
    """Return ITGC summary for the command centre integration."""
    _require_grc_role()
    from alphax_grc.alphax_grc.page.grc_itgc_program.grc_itgc_program import get_itgc_summary
    return get_itgc_summary()


@frappe.whitelist()
def get_asset_inventory_summary():
    """Return asset inventory statistics."""
    _require_grc_role()
    if not frappe.db.exists("DocType", "GRC Asset Inventory"):
        return {}
    total = frappe.db.count("GRC Asset Inventory")
    critical = frappe.db.count("GRC Asset Inventory", {"asset_criticality": "Critical"})
    high = frappe.db.count("GRC Asset Inventory", {"asset_criticality": "High"})
    personal_data = frappe.db.count("GRC Asset Inventory", {"contains_personal_data": 1})
    by_type = frappe.db.sql("""
        SELECT asset_type, COUNT(*) as total FROM `tabGRC Asset Inventory`
        GROUP BY asset_type ORDER BY total DESC
    """, as_dict=True)
    return {"total": total, "critical": critical, "high": high,
            "personal_data": personal_data, "by_type": by_type}


@frappe.whitelist()
def get_nca_ecc_compliance():
    """Return NCA ECC-2:2024 compliance status summary."""
    _require_grc_role()
    if not frappe.db.exists("DocType", "GRC NCA ECC Control"):
        return {}
    total = frappe.db.count("GRC NCA ECC Control")
    compliant = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Compliant"})
    partial = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Partially Compliant"})
    non_compliant = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Non-Compliant"})
    not_assessed = frappe.db.count("GRC NCA ECC Control", {"compliance_status": "Not Assessed"})
    by_domain = frappe.db.sql("""
        SELECT main_domain, COUNT(*) as total,
               SUM(CASE WHEN compliance_status='Compliant' THEN 1 ELSE 0 END) as compliant
        FROM `tabGRC NCA ECC Control` GROUP BY main_domain
    """, as_dict=True)
    score = round(compliant / total * 100, 1) if total else 0
    return {"total": total, "compliant": compliant, "partial": partial,
            "non_compliant": non_compliant, "not_assessed": not_assessed,
            "score": score, "by_domain": by_domain}
