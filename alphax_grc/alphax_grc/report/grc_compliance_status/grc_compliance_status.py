import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Framework",       "fieldname": "framework_name",        "fieldtype": "Data", "width": 160},
        {"label": "Control ID",      "fieldname": "name",                  "fieldtype": "Link", "options": "GRC Control", "width": 130},
        {"label": "Control Title",   "fieldname": "control_title",         "fieldtype": "Data", "width": 240},
        {"label": "Domain",          "fieldname": "control_domain",        "fieldtype": "Data", "width": 140},
        {"label": "Control Type",    "fieldname": "control_type",          "fieldtype": "Data", "width": 120},
        {"label": "Implementation",  "fieldname": "implementation_status", "fieldtype": "Data", "width": 140},
        {"label": "Owner",           "fieldname": "control_owner",         "fieldtype": "Link", "options": "User", "width": 140},
    ]

def get_data(filters):
    conditions = ""
    values = {}
    if filters and filters.get("framework"):
        conditions += " AND c.framework = %(framework)s"
        values["framework"] = filters["framework"]
    if filters and filters.get("implementation_status"):
        conditions += " AND c.implementation_status = %(implementation_status)s"
        values["implementation_status"] = filters["implementation_status"]
    if filters and filters.get("control_type"):
        conditions += " AND c.control_type = %(control_type)s"
        values["control_type"] = filters["control_type"]

    return frappe.db.sql(f"""
        SELECT
            COALESCE(f.framework_name, c.framework) AS framework_name,
            c.name, c.control_title, c.control_domain, c.control_type,
            c.implementation_status, c.control_owner
        FROM `tabGRC Control` c
        LEFT JOIN `tabGRC Framework` f ON f.name = c.framework
        WHERE 1=1 {conditions}
        ORDER BY framework_name, c.control_title
    """, values, as_dict=True)

def get_chart(data):
    if not data:
        return None
    from collections import Counter
    counts = Counter(r.get("implementation_status") or "Unknown" for r in data)
    order = ["Implemented", "In Progress", "Planned", "Not Applicable", "Unknown"]
    labels = [s for s in order if s in counts]
    return {
        "data": {"labels": labels, "datasets": [{"name": "Controls", "values": [counts[l] for l in labels]}]},
        "type": "donut",
        "title": "Implementation Status",
    }
