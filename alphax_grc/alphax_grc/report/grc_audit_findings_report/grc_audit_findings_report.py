import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Finding ID",     "fieldname": "name",            "fieldtype": "Link", "options": "GRC Audit Finding", "width": 130},
        {"label": "Finding Title",  "fieldname": "finding_title",   "fieldtype": "Data", "width": 240},
        {"label": "Audit Plan",     "fieldname": "audit_plan",      "fieldtype": "Link", "options": "GRC Audit Plan", "width": 150},
        {"label": "Framework",      "fieldname": "framework",       "fieldtype": "Link", "options": "GRC Framework", "width": 130},
        {"label": "Severity",       "fieldname": "severity",        "fieldtype": "Data", "width": 100},
        {"label": "Status",         "fieldname": "status",          "fieldtype": "Data", "width": 130},
        {"label": "Owner",          "fieldname": "owner",           "fieldtype": "Link", "options": "User", "width": 130},
        {"label": "Due Date",       "fieldname": "due_date",        "fieldtype": "Date", "width": 110},
        {"label": "Days Open",      "fieldname": "days_open",       "fieldtype": "Int",  "width": 90},
        {"label": "Root Cause",     "fieldname": "root_cause",      "fieldtype": "Data", "width": 160},
        {"label": "Closed On",      "fieldname": "closed_on",       "fieldtype": "Date", "width": 110},
    ]

def get_data(filters):
    conditions = ""
    values = {}
    if filters:
        if filters.get("severity"):
            conditions += " AND severity = %(severity)s"
            values["severity"] = filters["severity"]
        if filters.get("status"):
            conditions += " AND status = %(status)s"
            values["status"] = filters["status"]
        if filters.get("audit_plan"):
            conditions += " AND audit_plan = %(audit_plan)s"
            values["audit_plan"] = filters["audit_plan"]
        if filters.get("framework"):
            conditions += " AND framework = %(framework)s"
            values["framework"] = filters["framework"]

    rows = frappe.db.sql(f"""
        SELECT
            name, finding_title, audit_plan, framework, severity, status,
            owner, due_date, root_cause, closed_on,
            DATEDIFF(IFNULL(closed_on, CURDATE()), DATE(creation)) AS days_open
        FROM `tabGRC Audit Finding`
        WHERE 1=1 {conditions}
        ORDER BY
            FIELD(severity,'Critical','High','Medium','Low'),
            FIELD(status,'Open','In Remediation','Pending Verification','Verified','Closed'),
            modified DESC
    """, values, as_dict=True)
    return rows

def get_chart(data):
    if not data:
        return None
    from collections import Counter
    counts = Counter(r.get("severity") or "Unknown" for r in data)
    order = ["Critical", "High", "Medium", "Low"]
    labels = [s for s in order if s in counts]
    values = [counts[s] for s in labels]
    return {
        "data": {"labels": labels, "datasets": [{"name": "Findings", "values": values}]},
        "type": "bar",
        "title": "Findings by Severity",
    }
