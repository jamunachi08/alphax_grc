"""GRC Branded Print Format Seeder — programmatically creates branded print
formats for the most-used transactional doctypes. Each generated print
format wraps the document in a navy/gold gradient header and a
confidentiality footer.
"""

import frappe


# Doctypes that get a "GRC Branded" print format.
BRANDED_PRINT_DOCTYPES = [
    "GRC Risk Register",
    "GRC Audit Finding",
    "GRC Audit Plan",
    "GRC Remediation Action",
    "GRC Aramco Certificate",
    "GRC Aramco CCC Engagement",
    "GRC Aramco Incident Notification",
    "GRC Vendor",
    "GRC Vulnerability",
    "GRC Incident",
    "GRC Risk Acceptance",
    "GRC Exception",
    "GRC ISO42001 Control",
    "GRC NCA ECC Control",
    "GRC GDPR Control",
    "GRC GDPR Catalog",
    "GRC Engagement",
    "GRC Engagement Decision Log",
    "GRC Implementation Task",
    "GRC Document Publication",
    "GRC Evidence Rule",
    "GRC Evidence Rule Evaluation",
    "GRC DR Plan",
    "GRC BIA",
]


_BRANDED_TEMPLATE = r"""
<style>
.grc-print-doc { font-family: 'Arial', 'Segoe UI', sans-serif; color: #1E293B; line-height: 1.5; }
.grc-print-doc .header-bar { background: linear-gradient(135deg, #0F1F40 0%, #185FA5 100%); color: white; padding: 18px 24px; margin: -20px -20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 4px solid #C9A227; }
.grc-print-doc .brand-name { font-size: 22px; font-weight: 700; letter-spacing: 0.02em; }
.grc-print-doc .doc-meta { text-align: right; font-size: 11px; opacity: 0.9; }
.grc-print-doc .doc-meta .doc-type { text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.grc-print-doc .doc-title { font-size: 18px; font-weight: 600; color: #0F1F40; margin: 0 0 4px; }
.grc-print-doc .doc-id { font-family: monospace; font-size: 11px; color: #687178; margin-bottom: 16px; }
.grc-print-doc table.fields { width: 100%; border-collapse: collapse; margin: 8px 0 24px; }
.grc-print-doc table.fields td { padding: 8px 12px; border-bottom: 1px solid rgba(15, 31, 64, 0.08); vertical-align: top; font-size: 12px; }
.grc-print-doc table.fields td.label { width: 30%; color: #687178; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; font-size: 10px; }
.grc-print-doc table.fields td.value { color: #1E293B; }
.grc-print-doc .section-head { color: #0F1F40; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 12px; border-bottom: 2px solid #185FA5; padding: 12px 0 6px; margin: 16px 0 8px; }
.grc-print-doc .footer { margin-top: 32px; padding: 12px 8px; text-align: center; font-size: 9px; color: #687178; border-top: 1px solid rgba(15, 31, 64, 0.08); }
.grc-print-doc .chip { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 600; text-transform: uppercase; }
.grc-print-doc .chip-danger  { background: #FCEBEB; color: #791F1F; }
.grc-print-doc .chip-warning { background: #FAEEDA; color: #6B3F08; }
.grc-print-doc .chip-success { background: #D9F0E2; color: #0A5740; }
.grc-print-doc .chip-info    { background: #E6F1FB; color: #093566; }
</style>
<div class="grc-print-doc">
    <div class="header-bar">
        <div class="brand-name">AlphaX GRC</div>
        <div class="doc-meta">
            <div class="doc-type">{{ doc.doctype }}</div>
            <div>{{ frappe.utils.formatdate(frappe.utils.nowdate(), "long") }}</div>
        </div>
    </div>
    <h1 class="doc-title">
        {% if doc.title %}{{ doc.title }}
        {% elif doc.subject %}{{ doc.subject }}
        {% elif doc.policy_title %}{{ doc.policy_title }}
        {% elif doc.risk_title %}{{ doc.risk_title }}
        {% elif doc.control_title %}{{ doc.control_title }}
        {% elif doc.rule_name %}{{ doc.rule_name }}
        {% else %}{{ doc.name }}{% endif %}
    </h1>
    <div class="doc-id">{{ doc.name }}</div>

    {% set _skip = ["doctype","name","owner","creation","modified","modified_by","docstatus","idx","_user_tags","_comments","_assign","_liked_by"] %}
    <table class="fields">
        {% for f in doc.meta.fields %}
            {% if f.fieldtype == "Section Break" and f.label %}
                </table><div class="section-head">{{ f.label }}</div><table class="fields">
            {% elif f.fieldtype not in ("Section Break","Column Break","Tab Break","HTML","Button") and f.fieldname not in _skip and doc.get(f.fieldname) %}
                <tr>
                    <td class="label">{{ f.label or f.fieldname }}</td>
                    <td class="value">
                        {%- set v = doc.get(f.fieldname) -%}
                        {%- if f.fieldtype == "Date" -%}{{ frappe.utils.formatdate(v, "long") }}
                        {%- elif f.fieldtype == "Datetime" -%}{{ frappe.utils.format_datetime(v, "medium") }}
                        {%- elif f.fieldtype == "Currency" -%}{{ frappe.utils.fmt_money(v) }}
                        {%- elif f.fieldtype == "Percent" -%}{{ "%.1f" | format(v|float) }}%
                        {%- elif f.fieldtype == "Check" -%}{% if v %}<span class="chip chip-success">Yes</span>{% else %}<span class="chip">No</span>{% endif %}
                        {%- elif f.fieldname in ("severity","rule_priority") -%}
                            {%- set sv = (v or "")|string|lower -%}
                            {%- if sv in ("critical","high") -%}<span class="chip chip-danger">{{ v }}</span>
                            {%- elif sv == "medium" -%}<span class="chip chip-warning">{{ v }}</span>
                            {%- elif sv == "low" -%}<span class="chip chip-success">{{ v }}</span>
                            {%- else -%}{{ v }}{%- endif -%}
                        {%- else -%}{{ v }}{%- endif -%}
                    </td>
                </tr>
            {% endif %}
        {% endfor %}
    </table>
    <div class="footer">
        <strong>Confidential</strong> &middot; Generated by AlphaX GRC &middot;
        {{ frappe.utils.format_datetime(frappe.utils.now(), "medium") }}
    </div>
</div>
""".strip()


def seed_branded_print_formats():
    """Create 'GRC Branded' print formats. Idempotent."""
    if not frappe.db.exists("DocType", "Print Format"):
        return

    inserted = 0
    for doctype in BRANDED_PRINT_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            continue
        pf_name = f"GRC Branded {doctype}"
        if frappe.db.exists("Print Format", pf_name):
            continue
        try:
            pf = frappe.get_doc({
                "doctype": "Print Format",
                "name": pf_name,
                "doc_type": doctype,
                "module": "AlphaX GRC",
                "standard": "No",
                "custom_format": 1,
                "html": _BRANDED_TEMPLATE,
                "print_format_type": "Jinja",
                "disabled": 0,
                "default_print_language": "en",
            })
            pf.insert(ignore_permissions=True)
            inserted += 1
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"Print format seed failed: {doctype}")
            except Exception:
                pass

    try:
        frappe.db.commit()
        frappe.logger().info(
            f"AlphaX GRC v1.7.0: Seeded {inserted} branded print formats.")
    except Exception:
        pass
