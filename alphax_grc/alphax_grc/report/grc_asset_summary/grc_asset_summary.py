import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label": "Asset ID",           "fieldname": "name",             "fieldtype": "Link",    "options": "GRC Asset Inventory", "width": 120},
        {"label": "Asset Name",         "fieldname": "asset_name",       "fieldtype": "Data",    "width": 220},
        {"label": "Type",               "fieldname": "asset_type",       "fieldtype": "Data",    "width": 140},
        {"label": "Location",           "fieldname": "asset_location",   "fieldtype": "Data",    "width": 120},
        {"label": "Confidentiality",    "fieldname": "confidentiality",  "fieldtype": "Data",    "width": 120},
        {"label": "Integrity",          "fieldname": "integrity",        "fieldtype": "Data",    "width": 100},
        {"label": "Availability",       "fieldname": "availability",     "fieldtype": "Data",    "width": 110},
        {"label": "Criticality",        "fieldname": "asset_criticality","fieldtype": "Data",    "width": 110},
        {"label": "PDPL",               "fieldname": "contains_personal_data", "fieldtype": "Check", "width": 70},
        {"label": "NCA ECC Domain",     "fieldname": "nca_ecc_domain",   "fieldtype": "Data",    "width": 140},
        {"label": "Status",             "fieldname": "asset_status",     "fieldtype": "Data",    "width": 100},
        {"label": "Last Reviewed",      "fieldname": "last_reviewed",    "fieldtype": "Date",    "width": 110},
    ]

def get_data(filters):
    conditions = ""
    values = {}
    if filters:
        if filters.get("asset_type"):
            conditions += " AND asset_type = %(asset_type)s"
            values["asset_type"] = filters["asset_type"]
        if filters.get("asset_criticality"):
            conditions += " AND asset_criticality = %(asset_criticality)s"
            values["asset_criticality"] = filters["asset_criticality"]

    return frappe.db.sql(f"""
        SELECT
            name, asset_name, asset_type, asset_location,
            confidentiality, integrity, availability,
            asset_criticality, contains_personal_data,
            nca_ecc_domain, asset_status, last_reviewed
        FROM `tabGRC Asset Inventory`
        WHERE 1=1 {conditions}
        ORDER BY
            FIELD(asset_criticality,'Critical','High','Medium','Low','Very Low'),
            asset_name
    """, values, as_dict=True)

def get_chart(data):
    if not data:
        return None
    from collections import Counter
    counts = Counter(r.get("asset_criticality", "Unknown") for r in data)
    order = ["Critical", "High", "Medium", "Low", "Very Low"]
    labels = [s for s in order if s in counts]
    return {
        "data": {"labels": labels, "datasets": [{"name": "Assets", "values": [counts[l] for l in labels]}]},
        "type": "donut",
        "title": "Assets by Criticality",
    }
