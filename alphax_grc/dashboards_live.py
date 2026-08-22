"""AlphaX GRC v1.3.2 — Live dashboards layer.

This module provides three things:

1. `refresh_all_snapshots()` and `refresh_snapshot(client)` — recompute the
   GRC Dashboard Snapshot row(s). Called by the scheduler every 15 minutes
   and on-demand by `invalidate_dashboards()` after a watched record changes.

2. `invalidate_dashboards(doc, method=None)` — doc_event hook. When a Risk,
   Finding, KRI, Assessment, Control, Asset, Incident, or Remediation
   record is saved, this triggers a snapshot rebuild for the affected
   client and broadcasts a `grc.dashboard.refresh` realtime event so any
   open dashboard re-fetches immediately.

3. `get_live_dashboard(client=None)` — whitelisted endpoint that dashboards
   call. Reads from the snapshot table (fast, pre-aggregated). If the
   snapshot is stale (>900s) or missing, it triggers a refresh inline.
"""

import json
import frappe
from frappe.utils import now_datetime, get_datetime, add_to_date, today, flt


# ===========================================================================
# Doctypes whose changes invalidate the dashboard.
# Used both by the doc_event hook and by realtime invalidation.
# ===========================================================================

WATCHED_DOCTYPES = {
    "GRC Risk Register", "GRC Audit Finding", "GRC KRI",
    "GRC Assessment", "GRC Assessment Run", "GRC Control",
    "GRC Asset Inventory", "GRC Incident", "GRC Remediation Action",
    "GRC Framework", "GRC Exception", "GRC Risk Acceptance",
    "GRC Maturity Assessment", "GRC Vendor", "GRC Vendor Assessment",
    "GRC Consultant Timesheet",
    # v1.4.0 — new tenant-scoped doctypes
    "GRC Vulnerability", "GRC KPI",
    # v1.4.3 — Aramco CCC
    "GRC Aramco CCC Engagement", "GRC Aramco Certificate",
    "GRC Aramco Incident Notification",
    # v1.5.0 — ECC-2:2024 catalog (mostly read-only, but admin edits trigger refresh)
    "GRC NCA ECC2 Catalog",
}

SNAPSHOT_STALE_SECONDS = 900  # 15 minutes


# ===========================================================================
# Permission check (kept here so this module is self-contained).
# ===========================================================================

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


# ===========================================================================
# Snapshot computation
# ===========================================================================

def _safe_count(doctype, filters=None):
    if not frappe.db.exists("DocType", doctype):
        return 0
    try:
        return frappe.db.count(doctype, filters or {}) or 0
    except Exception:
        return 0


def _safe_avg(doctype, fieldname, filters=None):
    """Average of a numeric column. Safe if the doctype/field doesn't exist."""
    if not frappe.db.exists("DocType", doctype):
        return 0.0
    try:
        rows = frappe.get_all(doctype, filters=filters or {}, pluck=fieldname)
    except Exception:
        return 0.0
    nums = [float(v) for v in rows if v not in (None, "")]
    return round(sum(nums) / len(nums), 2) if nums else 0.0


def _scoped(client, extra_filters=None):
    """Build a filters dict that includes the client scope when given."""
    f = dict(extra_filters or {})
    if client:
        f["client"] = client
    return f


def _compute_snapshot_payload(client=None):
    """Compute every metric needed by the dashboards for one client (or
    firm-wide if client is None). Returns a dict ready to write to the
    snapshot row."""

    payload = {
        "compliance_score": 0.0,
        "maturity_score": 0.0,
        "critical_risks": 0,
        "open_risks": 0,
        "open_findings": 0,
        "overdue_actions": 0,
        "active_exceptions": 0,
        "accepted_risks": 0,
        "kris_breached": 0,
        "controls_implemented": 0,
        "controls_total": 0,
        "total_risks": 0,
        "total_findings": 0,
        "total_assessments": 0,
        "total_assets": 0,
        "total_kris": 0,
        "total_frameworks": 0,
        "billable_hours_30d": 0.0,
        "billable_amount_30d": 0.0,
        "consultants_active_30d": 0,
        "vulnerabilities_open": 0,
        "vulnerabilities_critical": 0,
        "vulnerabilities_overdue": 0,
        "vulnerabilities_total": 0,
        "kpis_total": 0,
        "kpis_on_target": 0,
        "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        "by_rating":   {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        "by_framework": [],
        "heatmap": [[0]*5 for _ in range(5)],
        "top_risks": [],
        "recent_findings": [],
        "kris": [],
    }

    # --- Risks ---
    if frappe.db.exists("DocType", "GRC Risk Register"):
        risks = frappe.get_all(
            "GRC Risk Register",
            filters=_scoped(client),
            fields=["name", "risk_title", "impact", "likelihood",
                    "inherent_score", "residual_score", "risk_rating",
                    "status", "risk_owner"],
            limit_page_length=0,
        )
        payload["total_risks"] = len(risks)
        for r in risks:
            if (r.status or "Open") != "Closed":
                payload["open_risks"] += 1
            if r.risk_rating == "Critical":
                payload["critical_risks"] += 1
            if r.risk_rating in payload["by_rating"]:
                payload["by_rating"][r.risk_rating] += 1
            try:
                imp = max(1, min(5, int(r.impact or 0)))
                lik = max(1, min(5, int(r.likelihood or 0)))
                payload["heatmap"][lik - 1][imp - 1] += 1
            except (ValueError, TypeError):
                pass
        # Top 8 open risks by inherent score
        open_risks = [r for r in risks if (r.status or "Open") != "Closed"]
        open_risks.sort(key=lambda x: int(x.inherent_score or 0), reverse=True)
        payload["top_risks"] = [{
            "name": r.name, "title": r.risk_title or "",
            "score": int(r.inherent_score or 0),
            "rating": r.risk_rating or "Low",
            "status": r.status or "Open",
            "owner": r.risk_owner or "",
        } for r in open_risks[:8]]

    # --- Findings ---
    if frappe.db.exists("DocType", "GRC Audit Finding"):
        findings = frappe.get_all(
            "GRC Audit Finding",
            filters=_scoped(client),
            fields=["name", "finding_title", "severity", "status",
                    "due_date", "owner", "modified"],
            limit_page_length=0,
        )
        payload["total_findings"] = len(findings)
        for f in findings:
            if f.status not in ("Closed", "Verified"):
                payload["open_findings"] += 1
                sev = f.severity or "Low"
                if sev in payload["by_severity"]:
                    payload["by_severity"][sev] += 1
        # Recent open
        open_findings = [f for f in findings if f.status not in ("Closed", "Verified")]
        open_findings.sort(key=lambda x: x.modified or "", reverse=True)
        payload["recent_findings"] = [{
            "name": f.name, "title": f.finding_title or "",
            "severity": f.severity or "Low",
            "due_date": str(f.due_date) if f.due_date else "",
            "owner": f.owner or "",
        } for f in open_findings[:6]]

    # --- Remediation overdue ---
    if frappe.db.exists("DocType", "GRC Remediation Action"):
        payload["overdue_actions"] = _safe_count(
            "GRC Remediation Action",
            _scoped(client, {"status": ["not in", ["Closed", "Verified"]],
                             "due_date": ["<", today()]}))

    # --- Exceptions / Risk Acceptance ---
    if frappe.db.exists("DocType", "GRC Exception"):
        payload["active_exceptions"] = _safe_count(
            "GRC Exception",
            _scoped(client, {"status": ["in", ["Approved", "Active"]]}))
    if frappe.db.exists("DocType", "GRC Risk Acceptance"):
        payload["accepted_risks"] = _safe_count(
            "GRC Risk Acceptance",
            _scoped(client, {"status": "Accepted"}))

    # --- KRIs ---
    if frappe.db.exists("DocType", "GRC KRI"):
        kris = frappe.get_all(
            "GRC KRI",
            filters=_scoped(client),
            fields=["indicator_name", "current_value", "threshold_value",
                    "status", "category"],
            limit_page_length=0,
        )
        payload["total_kris"] = len(kris)
        payload["kris_breached"] = sum(
            1 for k in kris if k.status == "Breach"
        )
        # Latest 8 for the dashboard list
        payload["kris"] = [{
            "name": k.indicator_name or "",
            "current": k.current_value, "threshold": k.threshold_value,
            "status": k.status or "OK",
            "category": k.category or "",
        } for k in kris[:8]]

    # --- Controls ---
    if frappe.db.exists("DocType", "GRC Control"):
        payload["controls_total"] = _safe_count("GRC Control", _scoped(client))
        payload["controls_implemented"] = _safe_count(
            "GRC Control",
            _scoped(client, {"implementation_status": "Implemented"}))

    # --- Assets ---
    if frappe.db.exists("DocType", "GRC Asset Inventory"):
        payload["total_assets"] = _safe_count("GRC Asset Inventory", _scoped(client))

    # --- Frameworks: derived compliance score per framework ---
    if frappe.db.exists("DocType", "GRC Framework"):
        fws = frappe.get_all(
            "GRC Framework",
            filters=_scoped(client),
            fields=["name", "framework_name"],
        )
        payload["total_frameworks"] = len(fws)
        framework_scores = []
        for fw in fws:
            score = 0
            if frappe.db.exists("DocType", "GRC Assessment"):
                rows = frappe.db.sql(
                    """SELECT AVG(compliance_score) AS s
                       FROM `tabGRC Assessment`
                       WHERE framework = %s
                         AND (%s IS NULL OR client = %s)""",
                    (fw.name, client, client),
                    as_dict=True,
                )
                if rows and rows[0].s is not None:
                    score = float(rows[0].s)
            payload["by_framework"].append({
                "name": fw.framework_name or fw.name,
                "score": round(score, 1),
            })
            framework_scores.append(score)
        if framework_scores:
            payload["compliance_score"] = round(
                sum(framework_scores) / len(framework_scores), 1
            )

    # --- Maturity ---
    if frappe.db.exists("DocType", "GRC Maturity Assessment"):
        payload["maturity_score"] = round(
            _safe_avg("GRC Maturity Assessment", "maturity_level",
                      _scoped(client)) * 20, 1
        )

    # --- Assessments total ---
    if frappe.db.exists("DocType", "GRC Assessment"):
        payload["total_assessments"] = _safe_count("GRC Assessment", _scoped(client))

    # --- Vulnerabilities (NCA Vulnerability Register) ---
    if frappe.db.exists("DocType", "GRC Vulnerability"):
        payload["vulnerabilities_total"] = _safe_count("GRC Vulnerability",
                                                        _scoped(client))
        payload["vulnerabilities_open"] = _safe_count(
            "GRC Vulnerability",
            _scoped(client, {"status": ["not in", ["Resolved"]]}))
        payload["vulnerabilities_critical"] = _safe_count(
            "GRC Vulnerability",
            _scoped(client, {"risk_level": "Critical",
                             "status": ["not in", ["Resolved"]]}))
        payload["vulnerabilities_overdue"] = _safe_count(
            "GRC Vulnerability",
            _scoped(client, {"status": ["not in", ["Resolved"]],
                             "due_date": ["<", today()]}))

    # --- KPIs (NCA KPI Report) ---
    if frappe.db.exists("DocType", "GRC KPI"):
        payload["kpis_total"] = _safe_count("GRC KPI", _scoped(client))
        # On-target = at least one quarter where actual >= target
        try:
            kpi_names = [k.name for k in frappe.get_all("GRC KPI",
                filters=_scoped(client), fields=["name"])]
            if kpi_names:
                on_target = 0
                for kn in kpi_names:
                    rows = frappe.db.sql("""
                        SELECT q1_target, q1_actual, q2_target, q2_actual,
                               q3_target, q3_actual, q4_target, q4_actual
                        FROM `tabGRC KPI Quarterly Measurement`
                        WHERE parent = %s
                        ORDER BY year DESC LIMIT 1
                    """, (kn,), as_dict=True)
                    if rows:
                        r = rows[0]
                        for q in ("q1", "q2", "q3", "q4"):
                            t = r.get(f"{q}_target")
                            a = r.get(f"{q}_actual")
                            if t is not None and a is not None and float(a) >= float(t):
                                on_target += 1
                                break
                payload["kpis_on_target"] = on_target
        except Exception:
            pass

    # --- Engagement metrics (last 30 days, requires client) ---
    if client and frappe.db.exists("DocType", "GRC Consultant Timesheet"):
        thirty_days_ago = add_to_date(today(), days=-30)
        ts_rows = frappe.get_all(
            "GRC Consultant Timesheet",
            filters={"client": client, "date": [">=", thirty_days_ago]},
            fields=["consultant", "hours", "amount", "billable"],
        )
        billable_hours = sum(flt(r.hours) for r in ts_rows if r.billable)
        billable_amount = sum(flt(r.amount) for r in ts_rows if r.billable)
        consultants = {r.consultant for r in ts_rows if r.consultant}
        payload["billable_hours_30d"] = round(billable_hours, 2)
        payload["billable_amount_30d"] = round(billable_amount, 2)
        payload["consultants_active_30d"] = len(consultants)

    return payload


def refresh_snapshot(client):
    """Recompute and persist the snapshot row for one client.
    Returns the snapshot doc dict on success, None on failure."""
    if not client:
        return None
    if not frappe.db.exists("DocType", "GRC Dashboard Snapshot"):
        return None
    if not frappe.db.exists("GRC Client Profile", client):
        return None

    try:
        payload = _compute_snapshot_payload(client)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             f"AlphaX GRC snapshot compute failed: {client}")
        except Exception:
            pass
        return None

    snapshot_data = {
        "doctype": "GRC Dashboard Snapshot",
        "client": client,
        "snapshot_time": now_datetime(),
        "snapshot_age_seconds": 0,
        # Headline scalars
        "compliance_score": payload["compliance_score"],
        "maturity_score": payload["maturity_score"],
        "critical_risks": payload["critical_risks"],
        "open_risks": payload["open_risks"],
        "open_findings": payload["open_findings"],
        "overdue_actions": payload["overdue_actions"],
        "active_exceptions": payload["active_exceptions"],
        "accepted_risks": payload["accepted_risks"],
        "kris_breached": payload["kris_breached"],
        "vulnerabilities_open": payload["vulnerabilities_open"],
        "vulnerabilities_critical": payload["vulnerabilities_critical"],
        "vulnerabilities_overdue": payload["vulnerabilities_overdue"],
        "vulnerabilities_total": payload["vulnerabilities_total"],
        "kpis_total": payload["kpis_total"],
        "kpis_on_target": payload["kpis_on_target"],
        "controls_implemented": payload["controls_implemented"],
        "controls_total": payload["controls_total"],
        "total_risks": payload["total_risks"],
        "total_findings": payload["total_findings"],
        "total_assessments": payload["total_assessments"],
        "total_assets": payload["total_assets"],
        "total_kris": payload["total_kris"],
        "total_frameworks": payload["total_frameworks"],
        "billable_hours_30d": payload["billable_hours_30d"],
        "billable_amount_30d": payload["billable_amount_30d"],
        "consultants_active_30d": payload["consultants_active_30d"],
        # JSON blobs
        "by_severity_json": json.dumps(payload["by_severity"]),
        "by_rating_json":   json.dumps(payload["by_rating"]),
        "by_framework_json":json.dumps(payload["by_framework"]),
        "heatmap_json":     json.dumps(payload["heatmap"]),
        "top_risks_json":   json.dumps(payload["top_risks"]),
        "recent_findings_json": json.dumps(payload["recent_findings"]),
        "kris_json":        json.dumps(payload["kris"]),
    }

    try:
        if frappe.db.exists("GRC Dashboard Snapshot", client):
            doc = frappe.get_doc("GRC Dashboard Snapshot", client)
            for k, v in snapshot_data.items():
                if k != "doctype":
                    doc.set(k, v)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc(snapshot_data)
            doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return snapshot_data
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             f"AlphaX GRC snapshot save failed: {client}")
        except Exception:
            pass
        return None


def refresh_all_snapshots():
    """Scheduler entry: refresh every active client's snapshot.
    Hooked from hooks.py:scheduler_events.cron (every 15 minutes)."""
    if not frappe.db.exists("DocType", "GRC Client Profile"):
        return
    clients = frappe.get_all(
        "GRC Client Profile",
        filters={"is_active": 1},
        fields=["name"],
    )
    refreshed = 0
    for c in clients:
        if refresh_snapshot(c.name):
            refreshed += 1
    try:
        frappe.logger().info(
            f"AlphaX GRC snapshot scheduler: refreshed {refreshed} of "
            f"{len(clients)} client snapshots."
        )
    except Exception:
        pass
    return {"refreshed": refreshed, "total": len(clients)}


# ===========================================================================
# Realtime invalidation (doc_events hook)
# ===========================================================================

def invalidate_dashboards(doc, method=None):
    """Doc-event hook: when a watched record is saved, refresh its client's
    snapshot inline and broadcast a realtime event to any open dashboards.

    This is registered via hooks.py:doc_events with `*` for the doctype
    set, so it's called on every save. We filter by WATCHED_DOCTYPES here
    instead of registering each hook individually."""
    try:
        dt = doc.get("doctype") if hasattr(doc, "get") else None
        if dt not in WATCHED_DOCTYPES:
            return
        client = doc.get("client") if hasattr(doc, "get") else None
        if not client:
            return
        # Refresh just this client (cheap — one client, one snapshot)
        refresh_snapshot(client)
        # Broadcast realtime so any open dashboard re-fetches
        try:
            frappe.publish_realtime(
                event="grc.dashboard.refresh",
                message={"client": client, "doctype": dt,
                         "name": doc.get("name") if hasattr(doc, "get") else None},
                after_commit=True,
            )
        except Exception:
            pass
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "AlphaX GRC invalidate_dashboards failed")
        except Exception:
            pass


# ===========================================================================
# Read API — what dashboards call
# ===========================================================================

@frappe.whitelist()
def get_live_dashboard(client=None):
    """Return live dashboard data for one client (or firm-wide aggregation
    if client is None). Reads from the snapshot table; if the snapshot is
    stale (>15 min) or missing, refreshes inline before returning.

    Output schema is flat and stable so dashboards can rely on it:
    {
        "client": "ACME" or null,
        "scope": "client" or "firm",
        "snapshot_time": "2026-04-25 10:30:00",
        "snapshot_age_seconds": 142,
        "headline": { compliance_score, maturity_score, critical_risks,
                      open_risks, open_findings, overdue_actions, ... },
        "by_severity": {Critical, High, Medium, Low},
        "by_rating":   {Critical, High, Medium, Low},
        "by_framework": [{name, score}, ...],
        "heatmap": [[0..0], ... 5x5],
        "top_risks": [{name, title, score, rating, status, owner}, ...],
        "recent_findings": [...],
        "kris": [...],
        "engagement": {billable_hours_30d, billable_amount_30d, consultants_active_30d}
    }
    """
    _check_auth()

    if not frappe.db.exists("DocType", "GRC Dashboard Snapshot"):
        # If the snapshot doctype isn't installed yet, compute live (slow path).
        return _format_live_payload(client, _compute_snapshot_payload(client),
                                    snapshot_time=None, age=0)

    if client:
        return _read_one(client)

    # Firm-wide: aggregate every active client's snapshot
    return _read_firm_wide()


def _format_live_payload(client, payload, snapshot_time, age):
    return {
        "client": client,
        "scope": "client" if client else "firm",
        "snapshot_time": str(snapshot_time) if snapshot_time else None,
        "snapshot_age_seconds": age,
        "headline": {
            "compliance_score": payload.get("compliance_score", 0),
            "maturity_score": payload.get("maturity_score", 0),
            "critical_risks": payload.get("critical_risks", 0),
            "open_risks": payload.get("open_risks", 0),
            "open_findings": payload.get("open_findings", 0),
            "overdue_actions": payload.get("overdue_actions", 0),
            "active_exceptions": payload.get("active_exceptions", 0),
            "accepted_risks": payload.get("accepted_risks", 0),
            "kris_breached": payload.get("kris_breached", 0),
            "vulnerabilities_open": payload.get("vulnerabilities_open", 0),
            "vulnerabilities_critical": payload.get("vulnerabilities_critical", 0),
            "vulnerabilities_overdue": payload.get("vulnerabilities_overdue", 0),
            "vulnerabilities_total": payload.get("vulnerabilities_total", 0),
            "kpis_total": payload.get("kpis_total", 0),
            "kpis_on_target": payload.get("kpis_on_target", 0),
            "controls_implemented": payload.get("controls_implemented", 0),
            "controls_total": payload.get("controls_total", 0),
            "total_risks": payload.get("total_risks", 0),
            "total_findings": payload.get("total_findings", 0),
            "total_assessments": payload.get("total_assessments", 0),
            "total_assets": payload.get("total_assets", 0),
            "total_kris": payload.get("total_kris", 0),
            "total_frameworks": payload.get("total_frameworks", 0),
        },
        "by_severity": payload.get("by_severity", {}),
        "by_rating":   payload.get("by_rating", {}),
        "by_framework": payload.get("by_framework", []),
        "heatmap": payload.get("heatmap", [[0]*5]*5),
        "top_risks": payload.get("top_risks", []),
        "recent_findings": payload.get("recent_findings", []),
        "kris": payload.get("kris", []),
        "engagement": {
            "billable_hours_30d": payload.get("billable_hours_30d", 0),
            "billable_amount_30d": payload.get("billable_amount_30d", 0),
            "consultants_active_30d": payload.get("consultants_active_30d", 0),
        },
    }


def _read_one(client):
    """Read a single client's snapshot, refresh if stale."""
    if not frappe.db.exists("GRC Client Profile", client):
        frappe.throw(f"Client {client} not found.")

    snap = None
    if frappe.db.exists("GRC Dashboard Snapshot", client):
        snap = frappe.get_doc("GRC Dashboard Snapshot", client)
        age = (now_datetime() - get_datetime(snap.snapshot_time)).total_seconds()
    else:
        age = 999999

    if not snap or age > SNAPSHOT_STALE_SECONDS:
        # Stale or missing — recompute inline
        refresh_snapshot(client)
        if frappe.db.exists("GRC Dashboard Snapshot", client):
            snap = frappe.get_doc("GRC Dashboard Snapshot", client)
            age = (now_datetime() - get_datetime(snap.snapshot_time)).total_seconds()

    if not snap:
        # Could not produce a snapshot — fall back to live compute
        return _format_live_payload(
            client, _compute_snapshot_payload(client),
            snapshot_time=now_datetime(), age=0,
        )

    payload = {
        "compliance_score": snap.compliance_score or 0,
        "maturity_score": snap.maturity_score or 0,
        "critical_risks": snap.critical_risks or 0,
        "open_risks": snap.open_risks or 0,
        "open_findings": snap.open_findings or 0,
        "overdue_actions": snap.overdue_actions or 0,
        "active_exceptions": snap.active_exceptions or 0,
        "accepted_risks": snap.accepted_risks or 0,
        "kris_breached": snap.kris_breached or 0,
        "vulnerabilities_open": snap.vulnerabilities_open or 0,
        "vulnerabilities_critical": snap.vulnerabilities_critical or 0,
        "vulnerabilities_overdue": snap.vulnerabilities_overdue or 0,
        "vulnerabilities_total": snap.vulnerabilities_total or 0,
        "kpis_total": snap.kpis_total or 0,
        "kpis_on_target": snap.kpis_on_target or 0,
        "controls_implemented": snap.controls_implemented or 0,
        "controls_total": snap.controls_total or 0,
        "total_risks": snap.total_risks or 0,
        "total_findings": snap.total_findings or 0,
        "total_assessments": snap.total_assessments or 0,
        "total_assets": snap.total_assets or 0,
        "total_kris": snap.total_kris or 0,
        "total_frameworks": snap.total_frameworks or 0,
        "billable_hours_30d": snap.billable_hours_30d or 0,
        "billable_amount_30d": snap.billable_amount_30d or 0,
        "consultants_active_30d": snap.consultants_active_30d or 0,
        "by_severity": _safe_load(snap.by_severity_json, {}),
        "by_rating":   _safe_load(snap.by_rating_json, {}),
        "by_framework":_safe_load(snap.by_framework_json, []),
        "heatmap":     _safe_load(snap.heatmap_json, [[0]*5]*5),
        "top_risks":   _safe_load(snap.top_risks_json, []),
        "recent_findings": _safe_load(snap.recent_findings_json, []),
        "kris":        _safe_load(snap.kris_json, []),
    }
    return _format_live_payload(client, payload, snap.snapshot_time, int(age))


def _read_firm_wide():
    """Sum/average snapshots across all active clients."""
    snaps = frappe.get_all(
        "GRC Dashboard Snapshot",
        fields=["*"],
    )

    if not snaps:
        return _format_live_payload(None, _compute_snapshot_payload(None),
                                    snapshot_time=now_datetime(), age=0)

    # Sum scalars
    summed_keys = ["critical_risks", "open_risks", "open_findings",
                   "overdue_actions", "active_exceptions", "accepted_risks",
                   "kris_breached", "controls_implemented", "controls_total",
                   "total_risks", "total_findings", "total_assessments",
                   "total_assets", "total_kris", "total_frameworks",
                   "consultants_active_30d",
                   "vulnerabilities_open", "vulnerabilities_critical",
                   "vulnerabilities_overdue", "vulnerabilities_total",
                   "kpis_total", "kpis_on_target"]
    money_keys = ["billable_hours_30d", "billable_amount_30d"]
    avg_keys = ["compliance_score", "maturity_score"]

    payload = {k: 0 for k in summed_keys}
    payload.update({k: 0.0 for k in money_keys})
    payload.update({k: 0.0 for k in avg_keys})

    for s in snaps:
        for k in summed_keys:
            payload[k] += int(s.get(k) or 0)
        for k in money_keys:
            payload[k] += float(s.get(k) or 0)
    for k in avg_keys:
        vals = [float(s.get(k) or 0) for s in snaps]
        payload[k] = round(sum(vals) / len(vals), 1) if vals else 0.0
    payload["billable_hours_30d"]  = round(payload["billable_hours_30d"], 2)
    payload["billable_amount_30d"] = round(payload["billable_amount_30d"], 2)

    # Aggregate by_severity, by_rating, heatmap across clients
    agg_sev = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    agg_rat = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    agg_heat = [[0]*5 for _ in range(5)]
    for s in snaps:
        for k, v in _safe_load(s.get("by_severity_json"), {}).items():
            if k in agg_sev:
                agg_sev[k] += int(v or 0)
        for k, v in _safe_load(s.get("by_rating_json"), {}).items():
            if k in agg_rat:
                agg_rat[k] += int(v or 0)
        h = _safe_load(s.get("heatmap_json"), [[0]*5]*5)
        for i in range(5):
            for j in range(5):
                try:
                    agg_heat[i][j] += int(h[i][j])
                except (IndexError, TypeError, ValueError):
                    pass
    payload["by_severity"] = agg_sev
    payload["by_rating"] = agg_rat
    payload["heatmap"] = agg_heat

    # Take top 8 risks across all clients
    all_top = []
    for s in snaps:
        for r in _safe_load(s.get("top_risks_json"), []):
            r["client"] = s.get("client")
            all_top.append(r)
    all_top.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    payload["top_risks"] = all_top[:8]

    # Same for recent findings
    all_recent = []
    for s in snaps:
        for f in _safe_load(s.get("recent_findings_json"), []):
            f["client"] = s.get("client")
            all_recent.append(f)
    payload["recent_findings"] = all_recent[:8]

    # KRIs
    all_kris = []
    for s in snaps:
        for k in _safe_load(s.get("kris_json"), []):
            k["client"] = s.get("client")
            all_kris.append(k)
    payload["kris"] = all_kris[:8]

    # Compliance by framework — group by framework name across snapshots
    fw_agg = {}
    for s in snaps:
        for f in _safe_load(s.get("by_framework_json"), []):
            n = f.get("name")
            if n:
                fw_agg.setdefault(n, []).append(float(f.get("score") or 0))
    payload["by_framework"] = [
        {"name": n, "score": round(sum(v) / len(v), 1)}
        for n, v in sorted(fw_agg.items())
    ]

    # Use the freshest snapshot time as the firm-wide timestamp
    latest_time = max((s.get("snapshot_time") for s in snaps if s.get("snapshot_time")),
                      default=now_datetime())
    age = int((now_datetime() - get_datetime(latest_time)).total_seconds())
    return _format_live_payload(None, payload, latest_time, age)


def _safe_load(s, default):
    if not s:
        return default
    try:
        return json.loads(s) if isinstance(s, str) else (s or default)
    except Exception:
        return default


# ===========================================================================
# On-demand refresh (whitelisted, used by manual refresh button)
# ===========================================================================

@frappe.whitelist()
def force_refresh(client=None):
    """User-triggered hard refresh, bypasses staleness check."""
    _check_auth()
    if client:
        return refresh_snapshot(client) or {}
    return refresh_all_snapshots()
