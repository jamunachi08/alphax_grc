import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Risk ID",          "fieldname": "name",              "fieldtype": "Link",   "options": "GRC Risk Register", "width": 130},
        {"label": "Risk Title",       "fieldname": "risk_title",        "fieldtype": "Data",   "width": 220},
        {"label": "Category",         "fieldname": "risk_category",     "fieldtype": "Data",   "width": 130},
        {"label": "Owner",            "fieldname": "risk_owner",        "fieldtype": "Link",   "options": "User", "width": 130},
        {"label": "Likelihood",       "fieldname": "likelihood",        "fieldtype": "Int",    "width": 100},
        {"label": "Impact",           "fieldname": "impact",            "fieldtype": "Int",    "width": 100},
        {"label": "Inherent Score",   "fieldname": "inherent_score",    "fieldtype": "Int",    "width": 110},
        {"label": "Residual Score",   "fieldname": "residual_score",    "fieldtype": "Int",    "width": 110},
        {"label": "Rating",           "fieldname": "risk_rating",       "fieldtype": "Data",   "width": 100},
        {"label": "Status",           "fieldname": "status",            "fieldtype": "Data",   "width": 110},
        {"label": "Framework",        "fieldname": "linked_framework",  "fieldtype": "Link",   "options": "GRC Framework", "width": 140},
        {"label": "Next Review",      "fieldname": "next_review_date",  "fieldtype": "Date",   "width": 110},
    ]

def get_data(filters):
    conditions = ""
    values = {}
    if filters:
        if filters.get("risk_rating"):
            conditions += " AND risk_rating = %(risk_rating)s"
            values["risk_rating"] = filters["risk_rating"]
        if filters.get("status"):
            conditions += " AND status = %(status)s"
            values["status"] = filters["status"]
        if filters.get("risk_category"):
            conditions += " AND risk_category = %(risk_category)s"
            values["risk_category"] = filters["risk_category"]
        if filters.get("linked_framework"):
            conditions += " AND linked_framework = %(linked_framework)s"
            values["linked_framework"] = filters["linked_framework"]

    return frappe.db.sql(f"""
        SELECT
            name, risk_title, risk_category, risk_owner,
            likelihood, impact, inherent_score, residual_score,
            risk_rating, status, linked_framework, next_review_date
        FROM `tabGRC Risk Register`
        WHERE 1=1 {conditions}
        ORDER BY inherent_score DESC,
                 FIELD(risk_rating,'Critical','High','Medium','Low')
    """, values, as_dict=True)

def get_chart(data):
    if not data:
        return None
    from collections import Counter
    counts = Counter(r.get("risk_rating") or "Unknown" for r in data)
    order = ["Critical", "High", "Medium", "Low"]
    labels = [s for s in order if s in counts]
    return {
        "data": {"labels": labels, "datasets": [{"name": "Risks", "values": [counts[l] for l in labels]}]},
        "type": "bar",
        "title": "Risks by Rating",
    }
