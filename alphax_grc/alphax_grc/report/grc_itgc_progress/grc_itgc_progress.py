import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary()
    return columns, data, None, chart, summary

def get_columns():
    return [
        {"label": "Domain",             "fieldname": "control_domain",   "fieldtype": "Data",    "width": 200},
        {"label": "Total Controls",     "fieldname": "total",            "fieldtype": "Int",     "width": 120},
        {"label": "Delivered",          "fieldname": "delivered",        "fieldtype": "Int",     "width": 110},
        {"label": "Pending",            "fieldname": "pending",          "fieldtype": "Int",     "width": 110},
        {"label": "Not Applicable",     "fieldname": "not_applicable",   "fieldtype": "Int",     "width": 120},
        {"label": "Completion %",       "fieldname": "completion_pct",   "fieldtype": "Percent", "width": 120},
        {"label": "Satisfactory",       "fieldname": "satisfactory",     "fieldtype": "Int",     "width": 110},
        {"label": "Needs Improvement",  "fieldname": "needs_improvement","fieldtype": "Int",     "width": 140},
    ]

def get_data(filters):
    rows = frappe.db.sql("""
        SELECT
            control_domain,
            COUNT(*) as total,
            SUM(CASE WHEN delivery_status='Delivered' THEN 1 ELSE 0 END) as delivered,
            SUM(CASE WHEN delivery_status='Pending' OR delivery_status='' OR delivery_status IS NULL THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN delivery_status='Not Applicable' THEN 1 ELSE 0 END) as not_applicable,
            SUM(CASE WHEN review_status='Satisfactory' THEN 1 ELSE 0 END) as satisfactory,
            SUM(CASE WHEN review_status='Requires Improvement' THEN 1 ELSE 0 END) as needs_improvement
        FROM `tabGRC ITGC Audit Item`
        GROUP BY control_domain
        ORDER BY total DESC
    """, as_dict=True)
    for r in rows:
        t = r.total or 1
        d = r.delivered or 0
        r.completion_pct = round(d / t * 100, 1)
    return rows

def get_chart(data):
    if not data:
        return None
    labels = [r.control_domain for r in data]
    delivered = [r.delivered for r in data]
    total = [r.total for r in data]
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Total", "values": total},
                {"name": "Delivered", "values": delivered},
            ]
        },
        "type": "bar",
        "title": "ITGC Controls — Delivery Progress by Domain",
    }

def get_summary():
    result = frappe.db.sql("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN delivery_status='Delivered' THEN 1 ELSE 0 END) as delivered
        FROM `tabGRC ITGC Audit Item`
    """, as_dict=True)
    if not result:
        return []
    r = result[0]
    total = r.total or 0
    delivered = r.delivered or 0
    pct = round(delivered / total * 100, 1) if total else 0
    return [
        {"label": "Total Controls", "value": total, "datatype": "Int"},
        {"label": "Delivered",      "value": delivered, "datatype": "Int"},
        {"label": "Completion",     "value": pct, "datatype": "Percent"},
    ]
