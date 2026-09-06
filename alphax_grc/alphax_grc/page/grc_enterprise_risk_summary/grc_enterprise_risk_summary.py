"""GRC Enterprise Risk Summary — board / audit-committee view.

One-page rollup per client showing risk count by category vs board-approved
appetite. Used in quarterly board packs.
"""

import frappe
from frappe.utils import today


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive",
    "Compliance Officer", "GRC Auditor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


# Map of risk_category option → Client Profile appetite field
_APPETITE_MAP = {
    "Strategic": "appetite_strategic",
    "Operational": "appetite_operational",
    "Financial": "appetite_financial",
    "Compliance": "appetite_compliance",
    "Cybersecurity": "appetite_cybersecurity",
    "Privacy": "appetite_privacy",
    "Third-Party": "appetite_third_party",
    "Reputational": "appetite_reputational",
}

# Numeric weight for appetite levels (higher = tolerates more)
_APPETITE_WEIGHT = {
    "None": 0,
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "": 1,  # default to Low if blank
    None: 1,
}

# Numeric weight for risk rating (higher = more severe)
_RATING_WEIGHT = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "": 0,
    None: 0,
}


@frappe.whitelist()
def get_summary(client=None):
    """Return board-level risk summary for one client (or firm-wide)."""
    _check_auth()

    risks = []
    if frappe.db.exists("DocType", "GRC Risk Register"):
        filters = {}
        if client:
            filters["client"] = client
        risks = frappe.get_all(
            "GRC Risk Register",
            filters=filters,
            fields=["name", "client", "risk_title", "risk_category",
                    "risk_owner", "risk_rating", "status",
                    "next_review_date", "treatment_plan"],
            limit_page_length=2000,
        )

    # Get appetite if we have a single client
    appetite = {}
    if client and frappe.db.exists("GRC Client Profile", client):
        try:
            cp = frappe.get_doc("GRC Client Profile", client)
            for cat, field in _APPETITE_MAP.items():
                appetite[cat] = cp.get(field) or ""
            appetite_statement = cp.get("appetite_statement") or ""
        except Exception:
            appetite_statement = ""
    else:
        appetite_statement = ""

    # Bucket risks by category and rating
    categories = {}
    for cat in (list(_APPETITE_MAP.keys()) + ["Legal", "Environmental", "(Uncategorized)"]):
        categories[cat] = {
            "category": cat,
            "appetite": appetite.get(cat, ""),
            "Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unrated": 0,
            "total": 0,
            "open": 0,
            "tolerance_breach": False,
        }

    for r in risks:
        cat = r.risk_category or "(Uncategorized)"
        if cat not in categories:
            categories[cat] = {
                "category": cat, "appetite": "",
                "Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Unrated": 0,
                "total": 0, "open": 0, "tolerance_breach": False,
            }
        rating = (r.risk_rating or "").strip()
        if rating in ("Critical", "High", "Medium", "Low"):
            categories[cat][rating] += 1
        else:
            categories[cat]["Unrated"] += 1
        categories[cat]["total"] += 1
        if (r.status or "").lower() not in ("closed", "accepted", "transferred"):
            categories[cat]["open"] += 1

    # Compute tolerance breach: if any High/Critical exists in a category
    # whose appetite is None or Low, flag it
    for cat, data in categories.items():
        appetite_level = (data["appetite"] or "Low").strip()
        appetite_weight = _APPETITE_WEIGHT.get(appetite_level, 1)
        # Critical risks are tolerable only at appetite High
        if data["Critical"] > 0 and appetite_weight < 3:
            data["tolerance_breach"] = True
        # High risks tolerable only at Moderate or High appetite
        elif data["High"] > 0 and appetite_weight < 2:
            data["tolerance_breach"] = True

    # Top open risks by severity (limit 10)
    rating_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "": 4}
    sorted_risks = sorted(
        [r for r in risks
         if (r.status or "").lower() not in ("closed", "accepted", "transferred")],
        key=lambda r: rating_order.get(r.risk_rating or "", 9),
    )[:10]

    # Aggregate counts
    totals = {
        "total_risks": len(risks),
        "open_risks": sum(1 for r in risks
                          if (r.status or "").lower() not in ("closed", "accepted", "transferred")),
        "critical_risks": sum(1 for r in risks if r.risk_rating == "Critical"),
        "high_risks": sum(1 for r in risks if r.risk_rating == "High"),
        "tolerance_breaches": sum(1 for c in categories.values() if c["tolerance_breach"]),
        "uncategorized": sum(1 for r in risks if not r.risk_category),
    }

    return {
        "client": client,
        "appetite_statement": appetite_statement,
        "categories": list(categories.values()),
        "top_open_risks": sorted_risks,
        "totals": totals,
        "generated_at": str(frappe.utils.now()),
    }
