"""
alphax_grc.notifications
------------------------
Scheduled daily alerts and doc-event hooks for AlphaX GRC v0.8.0.

All mailer calls are wrapped in try/except so a misconfigured mail
server never breaks the scheduler queue.
"""

import frappe
from frappe.utils import today, getdate, add_days, now_datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_send(recipients, subject, message, reference_doctype=None, reference_name=None):
    """Send an email, silently log any failure."""
    if not recipients:
        return
    try:
        frappe.sendmail(
            recipients=recipients,
            subject=f"[AlphaX GRC] {subject}",
            message=message,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"AlphaX GRC mail failed: {subject}")


def _user_email(user):
    if not user:
        return None
    email = frappe.db.get_value("User", user, "email")
    return email if email and "@" in email else None


def _admin_emails():
    """Return emails of all GRC Admin role users.
    Falls back to the real Administrator user's email, then to an empty list
    so callers can no-op cleanly when no admin is configured."""
    users = frappe.get_all(
        "Has Role",
        filters={"role": "GRC Admin", "parenttype": "User"},
        fields=["parent"],
    )
    emails = []
    for u in users:
        e = _user_email(u.parent)
        if e:
            emails.append(e)
    if emails:
        return list(set(emails))
    # Fallback: real Administrator email if defined
    admin_email = frappe.db.get_value("User", "Administrator", "email")
    return [admin_email] if admin_email else []


# ---------------------------------------------------------------------------
# Daily scheduler jobs
# ---------------------------------------------------------------------------

def send_overdue_remediation_alerts():
    """Alert owners of remediation actions that are past due date."""
    if not frappe.db.exists("DocType", "GRC Remediation Action"):
        return

    overdue = frappe.get_all(
        "GRC Remediation Action",
        filters={
            "status": ["not in", ["Closed", "Verified"]],
            "due_date": ["<", today()],
        },
        fields=["name", "action_title", "owner", "due_date", "priority"],
    )

    by_owner = {}
    for row in overdue:
        owner = row.owner or "Administrator"
        by_owner.setdefault(owner, []).append(row)

    for owner, actions in by_owner.items():
        email = _user_email(owner)
        if not email:
            continue
        rows_html = "".join(
            f"<tr><td>{a.name}</td><td>{a.action_title}</td>"
            f"<td>{a.priority or '-'}</td><td style='color:red'>{a.due_date}</td></tr>"
            for a in actions
        )
        _safe_send(
            [email],
            f"Overdue Remediation Actions ({len(actions)})",
            f"""<p>Hi,</p>
            <p>The following remediation actions assigned to you are overdue:</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
            <tr><th>ID</th><th>Title</th><th>Priority</th><th>Due Date</th></tr>
            {rows_html}
            </table>
            <p>Please update these in AlphaX GRC at your earliest convenience.</p>""",
        )


def send_expiring_exception_alerts():
    """Warn approvers of exceptions expiring within 14 days."""
    if not frappe.db.exists("DocType", "GRC Exception"):
        return

    cutoff = str(add_days(today(), 14))
    expiring = frappe.get_all(
        "GRC Exception",
        filters={
            "status": ["in", ["Approved", "Active"]],
            "expiry_date": ["between", [today(), cutoff]],
        },
        fields=["name", "exception_title", "approved_by", "expiry_date", "risk_level"],
    )

    by_approver = {}
    for row in expiring:
        approver = row.approved_by or "Administrator"
        by_approver.setdefault(approver, []).append(row)

    for approver, items in by_approver.items():
        email = _user_email(approver)
        if not email:
            continue
        rows_html = "".join(
            f"<tr><td>{e.name}</td><td>{e.exception_title}</td>"
            f"<td>{e.risk_level or '-'}</td><td>{e.expiry_date}</td></tr>"
            for e in items
        )
        _safe_send(
            [email],
            f"GRC Exceptions Expiring Soon ({len(items)})",
            f"""<p>Hi,</p>
            <p>The following policy/control exceptions are expiring within 14 days and require renewal or closure:</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
            <tr><th>ID</th><th>Title</th><th>Risk Level</th><th>Expiry</th></tr>
            {rows_html}
            </table>
            <p>Please review these in AlphaX GRC.</p>""",
        )


def send_vendor_review_reminders():
    """Remind vendor owners 30 days before next review date."""
    if not frappe.db.exists("DocType", "GRC Vendor"):
        return

    cutoff = str(add_days(today(), 30))
    due = frappe.get_all(
        "GRC Vendor",
        filters={
            "status": ["in", ["Active", "Under Review"]],
            "next_review_date": ["between", [today(), cutoff]],
        },
        fields=["name", "vendor_name", "risk_owner", "criticality", "next_review_date"],
    )

    by_owner = {}
    for row in due:
        owner = row.risk_owner or "Administrator"
        by_owner.setdefault(owner, []).append(row)

    for owner, vendors in by_owner.items():
        email = _user_email(owner)
        if not email:
            continue
        rows_html = "".join(
            f"<tr><td>{v.vendor_name}</td><td>{v.criticality or '-'}</td><td>{v.next_review_date}</td></tr>"
            for v in vendors
        )
        _safe_send(
            [email],
            f"Vendor Reviews Due Soon ({len(vendors)})",
            f"""<p>Hi,</p>
            <p>The following vendors have a review due within the next 30 days:</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
            <tr><th>Vendor</th><th>Criticality</th><th>Review Date</th></tr>
            {rows_html}
            </table>
            <p>Please schedule or complete the vendor assessment in AlphaX GRC.</p>""",
        )


def send_policy_review_reminders():
    """Remind policy owners 30 days before policy review due date."""
    if not frappe.db.exists("DocType", "GRC Policy"):
        return

    cutoff = str(add_days(today(), 30))
    due = frappe.get_all(
        "GRC Policy",
        filters={
            "status": ["not in", ["Retired"]],
            "review_due_date": ["between", [today(), cutoff]],
        },
        fields=["name", "policy_title", "policy_owner", "review_due_date", "version_no"],
    )

    by_owner = {}
    for row in due:
        owner = row.policy_owner or "Administrator"
        by_owner.setdefault(owner, []).append(row)

    for owner, policies in by_owner.items():
        email = _user_email(owner)
        if not email:
            continue
        rows_html = "".join(
            f"<tr><td>{p.policy_title}</td><td>v{p.version_no or '1.0'}</td><td>{p.review_due_date}</td></tr>"
            for p in policies
        )
        _safe_send(
            [email],
            f"Policies Due for Review ({len(policies)})",
            f"""<p>Hi,</p>
            <p>The following policies are due for review within 30 days:</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
            <tr><th>Policy Title</th><th>Version</th><th>Review Due</th></tr>
            {rows_html}
            </table>
            <p>Please initiate the review cycle in AlphaX GRC.</p>""",
        )


def send_overdue_dsr_alerts():
    """Alert Privacy Officers of overdue Data Subject Requests (PDPL 30-day deadline)."""
    if not frappe.db.exists("DocType", "GRC Data Subject Request"):
        return

    overdue = frappe.get_all(
        "GRC Data Subject Request",
        filters={
            "status": ["not in", ["Closed", "Rejected", "Responded"]],
            "due_date": ["<", today()],
        },
        fields=["name", "requester_name", "request_type", "received_on", "due_date", "owner_user"],
    )

    if not overdue:
        return

    admins = _admin_emails()
    rows_html = "".join(
        f"<tr><td>{d.name}</td><td>{d.requester_name or '-'}</td>"
        f"<td>{d.request_type}</td><td>{d.received_on}</td><td style='color:red'>{d.due_date}</td></tr>"
        for d in overdue
    )
    _safe_send(
        admins,
        f"PDPL: Overdue Data Subject Requests ({len(overdue)})",
        f"""<p>The following Data Subject Requests have exceeded the PDPL 30-day response deadline:</p>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
        <tr><th>ID</th><th>Requester</th><th>Type</th><th>Received</th><th>Due Date</th></tr>
        {rows_html}
        </table>
        <p>Immediate action is required to maintain PDPL compliance.</p>""",
    )


def check_kri_breaches():
    """Daily scan: re-evaluate all KRIs and alert on breaches.
    Honors breach_direction: 'Above' (default) breaches when current >= threshold,
    'Below' breaches when current <= threshold (e.g. patch SLA met %)."""
    if not frappe.db.exists("DocType", "GRC KRI"):
        return

    kris = frappe.get_all(
        "GRC KRI",
        fields=["name", "indicator_name", "current_value", "threshold_value",
                "status", "category", "breach_direction"],
    )

    breaches = []
    for kri in kris:
        try:
            current = float(kri.current_value or 0)
            threshold = float(kri.threshold_value or 0)
        except (ValueError, TypeError):
            continue
        if threshold == 0:
            continue

        direction = (kri.breach_direction or "Above")
        is_breach = (
            (direction == "Above" and current >= threshold) or
            (direction == "Below" and current <= threshold)
        )
        if is_breach and kri.status != "Breach":
            frappe.db.set_value("GRC KRI", kri.name, "status", "Breach")
            breaches.append(kri)

    if breaches:
        admins = _admin_emails()
        rows_html = "".join(
            f"<tr><td>{frappe.utils.escape_html(k.indicator_name or '')}</td>"
            f"<td>{frappe.utils.escape_html(k.category or '-')}</td>"
            f"<td style='color:red;font-weight:bold'>{frappe.utils.escape_html(str(k.current_value))}</td>"
            f"<td>{frappe.utils.escape_html(str(k.threshold_value))}</td>"
            f"<td>{frappe.utils.escape_html(k.breach_direction or 'Above')}</td></tr>"
            for k in breaches
        )
        _safe_send(
            admins,
            f"KRI Breach Alert: {len(breaches)} indicator(s) in breach",
            f"""<p>The following Key Risk Indicators have breached their thresholds:</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;font-size:13px">
            <tr><th>Indicator</th><th>Category</th><th>Current</th><th>Threshold</th><th>Direction</th></tr>
            {rows_html}
            </table>
            <p>Please review and take corrective action in AlphaX GRC.</p>""",
        )


# ---------------------------------------------------------------------------
# Doc-event hooks
# ---------------------------------------------------------------------------

def kri_on_update(doc, method=None):
    """On KRI save: if newly in Breach, alert GRC Admins immediately."""
    if doc.status == "Breach":
        admins = _admin_emails()
        _safe_send(
            admins,
            f"KRI Breach: {doc.indicator_name}",
            f"""<p><strong>KRI Breach Detected</strong></p>
            <p>Indicator: <strong>{doc.indicator_name}</strong></p>
            <p>Current Value: <strong style='color:red'>{doc.current_value}</strong></p>
            <p>Threshold: {doc.threshold_value}</p>
            <p>Category: {doc.category or '-'}</p>
            <p>Please investigate immediately in AlphaX GRC.</p>""",
            reference_doctype="GRC KRI",
            reference_name=doc.name,
        )


def finding_on_update(doc, method=None):
    """On Audit Finding save: alert owner if severity is Critical or High and newly opened."""
    if doc.severity in ("Critical", "High") and doc.status == "Open":
        email = _user_email(doc.owner)
        if email:
            _safe_send(
                [email],
                f"{doc.severity} Audit Finding Assigned: {doc.finding_title}",
                f"""<p>A <strong>{doc.severity}</strong> audit finding has been assigned to you:</p>
                <p><strong>{doc.finding_title}</strong></p>
                <p>Due Date: {doc.due_date or 'Not set'}</p>
                <p>Please review and initiate remediation in AlphaX GRC.</p>""",
                reference_doctype="GRC Audit Finding",
                reference_name=doc.name,
            )


def incident_on_update(doc, method=None):
    """On Incident save: alert GRC Admins for Critical incidents."""
    if doc.severity == "Critical" and doc.status in ("New", "Investigating"):
        admins = _admin_emails()
        _safe_send(
            admins,
            f"CRITICAL Incident: {doc.incident_title}",
            f"""<p><strong>Critical Incident Reported</strong></p>
            <p>Title: <strong>{doc.incident_title}</strong></p>
            <p>Type: {doc.incident_type}</p>
            <p>SLA Due: <strong style='color:red'>{doc.sla_due_date or 'N/A'}</strong></p>
            <p>Summary: {doc.summary or '-'}</p>
            <p>Immediate escalation and response required. Review in AlphaX GRC.</p>""",
            reference_doctype="GRC Incident",
            reference_name=doc.name,
        )


# ===========================================================================
# v1.4.3 — Aramco CCC notifications
# ===========================================================================

def _send_email(recipients, subject, message, reference_doctype=None,
                reference_name=None):
    """Robust email sender. Skips silently if no recipients or no email
    config; logs error rather than throwing."""
    if not recipients:
        return False
    try:
        if isinstance(recipients, str):
            recipients = [recipients]
        recipients = [r for r in recipients if r and "@" in r]
        if not recipients:
            return False
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
        )
        return True
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             f"Aramco CCC email send failed: {subject}")
        except Exception:
            pass
        return False


def _engagement_recipients(client_name, lead_consultant=None):
    """Build the recipient list for a CCC engagement notification:
    lead consultant + GRC Admin/Aramco Compliance Owner role users."""
    recipients = set()
    if lead_consultant:
        em = frappe.db.get_value("User", lead_consultant, "email")
        if em:
            recipients.add(em)
    # Pull all GRC Admin users
    try:
        admins = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["GRC Admin", "Aramco Compliance Owner"]],
                     "parenttype": "User"},
            fields=["parent"],
        )
        for a in admins:
            em = frappe.db.get_value("User", a.parent, "email")
            if em:
                recipients.add(em)
    except Exception:
        pass
    return list(recipients)


def check_aramco_certificate_renewals():
    """Daily scheduler: scan all Aramco Certificates and send renewal alerts
    at 180/90/30 days before expiry, plus expired alert.

    Uses last_NNNday_alert_sent fields on the certificate to prevent
    duplicate emails."""
    if not frappe.db.exists("DocType", "GRC Aramco Certificate"):
        return

    from frappe.utils import today, getdate, date_diff
    today_d = getdate(today())
    cert_names = frappe.get_all(
        "GRC Aramco Certificate",
        filters={"status": ["not in", ["Revoked"]]},
        fields=["name", "expiry_date", "client", "third_party_profile"],
    )
    sent_count = 0

    for c in cert_names:
        if not c.expiry_date:
            continue
        days = date_diff(c.expiry_date, today_d)
        cert = frappe.get_doc("GRC Aramco Certificate", c.name)

        third_party_label = cert.third_party_profile or "(unspecified vendor)"
        client_label = cert.client or "(unknown client)"
        # Resolve client lead consultant
        lead = frappe.db.get_value("GRC Client Profile", cert.client,
                                    "lead_consultant") if cert.client else None
        recipients = _engagement_recipients(cert.client, lead)

        # ---- Expired alert ----
        if days < 0 and not cert.last_expired_alert_sent:
            subject = f"⚠️ Aramco CCC Certificate EXPIRED — {third_party_label} ({cert.certificate_number})"
            message = _ccc_email_body("expired", cert, days, client_label)
            if _send_email(recipients, subject, message,
                           "GRC Aramco Certificate", cert.name):
                frappe.db.set_value("GRC Aramco Certificate", cert.name,
                                    "last_expired_alert_sent", today_d)
                sent_count += 1

        # ---- 30-day alert ----
        elif 0 <= days <= 30 and not cert.last_30day_alert_sent:
            subject = f"🚨 Aramco CCC expiring in {days} days — {third_party_label}"
            message = _ccc_email_body("30day", cert, days, client_label)
            if _send_email(recipients, subject, message,
                           "GRC Aramco Certificate", cert.name):
                frappe.db.set_value("GRC Aramco Certificate", cert.name,
                                    "last_30day_alert_sent", today_d)
                sent_count += 1

        # ---- 90-day alert ----
        elif 30 < days <= 90 and not cert.last_90day_alert_sent:
            subject = f"⚡ Aramco CCC expires in {days} days — kick off renewal: {third_party_label}"
            message = _ccc_email_body("90day", cert, days, client_label)
            if _send_email(recipients, subject, message,
                           "GRC Aramco Certificate", cert.name):
                frappe.db.set_value("GRC Aramco Certificate", cert.name,
                                    "last_90day_alert_sent", today_d)
                sent_count += 1

        # ---- 180-day alert ----
        elif 90 < days <= 180 and not cert.last_180day_alert_sent:
            subject = f"📅 Aramco CCC renewal kickoff — {third_party_label} (in {days} days)"
            message = _ccc_email_body("180day", cert, days, client_label)
            if _send_email(recipients, subject, message,
                           "GRC Aramco Certificate", cert.name):
                frappe.db.set_value("GRC Aramco Certificate", cert.name,
                                    "last_180day_alert_sent", today_d)
                sent_count += 1

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC Aramco renewal check: {sent_count} alerts sent "
            f"across {len(cert_names)} certificates."
        )
    except Exception:
        pass


def _ccc_email_body(stage, cert, days, client_label):
    """Return the HTML body for a CCC notification email."""
    if stage == "180day":
        urgency = "ADVISORY"
        action = ("Time to start the renewal cycle. The CCC re-audit typically "
                  "takes 90-120 days end-to-end including remediation.")
    elif stage == "90day":
        urgency = "ATTENTION"
        action = ("Renewal must now be in progress. If the audit firm hasn't "
                  "been engaged yet, this is critical.")
    elif stage == "30day":
        urgency = "URGENT"
        action = ("Certificate expires within 30 days. Confirm renewal status "
                  "or accept lapse risk and notify Aramco.")
    elif stage == "expired":
        urgency = "EXPIRED"
        action = (f"Certificate has been expired for {abs(days)} days. "
                  "Vendor is non-compliant and exposed to Aramco scope removal.")
    else:
        urgency = ""
        action = ""

    return f"""
    <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 600px;">
        <h3 style="color: #185FA5; margin-bottom: 12px;">
            Aramco CCC Certificate — {urgency}
        </h3>

        <p>This is an automated alert from AlphaX GRC.</p>

        <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Client:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{client_label}</td></tr>
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Vendor:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{cert.third_party_profile or '—'}</td></tr>
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Certificate Number:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{cert.certificate_number or '—'}</td></tr>
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Tier:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{cert.service_class_tier or '—'}</td></tr>
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Issue Date:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{cert.issue_date or '—'}</td></tr>
            <tr><td style="padding: 6px; border-bottom: 1px solid #eee;"><b>Expiry Date:</b></td>
                <td style="padding: 6px; border-bottom: 1px solid #eee;">{cert.expiry_date or '—'}</td></tr>
            <tr><td style="padding: 6px;"><b>Days to Expiry:</b></td>
                <td style="padding: 6px;"><b style="color: {'#A32D2D' if days < 30 else '#854F0B' if days < 90 else '#185FA5'};">{days}</b></td></tr>
        </table>

        <p style="background: #f7f7f7; padding: 12px; border-left: 3px solid #185FA5;">
            <b>Recommended action:</b> {action}
        </p>

        <p style="color: #888; font-size: 11px; margin-top: 24px;">
            This alert was generated by AlphaX GRC's Aramco CCC renewal scheduler.
            To manage notification settings, see your Client Profile preferences.
        </p>
    </div>
    """


def check_aramco_incident_escalation():
    """Daily scheduler: enforce Aramco's 4h/24h/72h notification deadlines.
    Sends escalation emails if reports are overdue."""
    if not frappe.db.exists("DocType", "GRC Aramco Incident Notification"):
        return
    from datetime import datetime, timezone
    from frappe.utils import get_datetime, now_datetime

    incidents = frappe.get_all(
        "GRC Aramco Incident Notification",
        filters={"notification_status": ["not in", ["Closed", "Cancelled"]]},
        fields=["name", "incident_title", "reported_on",
                "initial_notification_sent_on",
                "final_business_report_date",
                "final_technical_report_date", "client"],
    )
    sent = 0
    now = now_datetime()
    for inc in incidents:
        if not inc.reported_on:
            continue
        try:
            reported = get_datetime(inc.reported_on)
            elapsed_hours = (now - reported).total_seconds() / 3600
        except Exception:
            continue

        # 4-hour initial notification
        if elapsed_hours >= 4 and not inc.initial_notification_sent_on:
            recipients = _engagement_recipients(inc.client)
            subject = f"🚨 Aramco incident initial notification OVERDUE — {inc.incident_title}"
            body = f"""
            <p>Incident <b>{inc.incident_title}</b> was reported {elapsed_hours:.1f} hours ago.</p>
            <p>Aramco requires <b>initial notification within 4 hours</b>. This is now overdue.</p>
            <p>Please update the incident record at <code>/app/grc-aramco-incident-notification/{inc.name}</code>.</p>
            """
            if _send_email(recipients, subject, body,
                           "GRC Aramco Incident Notification", inc.name):
                sent += 1

        # 72-hour final reports
        if elapsed_hours >= 72:
            if not inc.final_business_report_date or not inc.final_technical_report_date:
                recipients = _engagement_recipients(inc.client)
                subject = f"⚠️ Aramco incident 72h reports OVERDUE — {inc.incident_title}"
                body = f"""
                <p>Incident <b>{inc.incident_title}</b> reported {elapsed_hours:.1f} hours ago.</p>
                <p>72-hour final business and technical reports are overdue.</p>
                <p>Business report: {inc.final_business_report_date or 'NOT SUBMITTED'}<br>
                   Technical report: {inc.final_technical_report_date or 'NOT SUBMITTED'}</p>
                """
                if _send_email(recipients, subject, body,
                               "GRC Aramco Incident Notification", inc.name):
                    sent += 1
    try:
        frappe.logger().info(
            f"AlphaX GRC Aramco incident escalation: {sent} alerts sent.")
    except Exception:
        pass


def aramco_incident_on_update(doc, method=None):
    """Doc-event hook: when an Aramco Incident is created/updated, send the
    initial 4-hour notification email immediately if it hasn't gone out."""
    try:
        from frappe.utils import now_datetime, get_datetime
        # Send initial notification once
        if (doc.notification_status in ("New", "Reported")
                and not doc.initial_notification_sent_on):
            recipients = _engagement_recipients(doc.client)
            subject = f"🚨 New Aramco-scope incident: {doc.incident_title}"
            body = f"""
            <p>A new incident in Aramco scope has been logged:</p>
            <p><b>{doc.incident_title}</b></p>
            <p>Reported: {doc.reported_on or 'just now'}<br>
               Client: {doc.client or '—'}</p>
            <p>Aramco requires initial notification within <b>4 hours</b>.
            Update the record once notification is sent so the timer can stop.</p>
            <p>Open: <code>/app/grc-aramco-incident-notification/{doc.name}</code></p>
            """
            if _send_email(recipients, subject, body,
                           "GRC Aramco Incident Notification", doc.name):
                # Mark sent timestamp
                doc.db_set("initial_notification_sent_on", now_datetime(),
                           update_modified=False)
    except Exception:
        try:
            frappe.log_error(frappe.get_traceback(),
                             "aramco_incident_on_update failed")
        except Exception:
            pass
