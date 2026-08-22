"""GRC CRQ Dashboard — quantitative risk view.

Shows top scenarios by Annual Loss Expectancy with summary stats.
"""

import frappe


_GRC_ROLES = {
    "System Manager", "GRC Admin", "GRC Executive",
    "Compliance Officer", "GRC Auditor", "GRC Assessor",
}


def _check_auth():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    if not (set(frappe.get_roles(frappe.session.user)) & _GRC_ROLES):
        frappe.throw("Not permitted.", frappe.PermissionError)


@frappe.whitelist()
def get_dashboard(client=None, top_n=20):
    """Return CRQ summary + top scenarios sorted by ALE."""
    _check_auth()

    if not frappe.db.exists("DocType", "GRC CRQ Scenario"):
        return {
            "scenarios": [], "summary": {}, "client": client,
            "doctype_missing": True,
        }

    filters = {"is_active": 1}
    if client:
        filters["client"] = client

    try:
        top_n = int(top_n or 20)
    except Exception:
        top_n = 20
    top_n = max(5, min(100, top_n))

    scenarios = frappe.get_all(
        "GRC CRQ Scenario",
        filters=filters,
        fields=[
            "name", "scenario_name", "client", "engagement",
            "framework", "asset_at_risk",
            "threat_event_name", "threat_actor_type",
            "threat_capability", "threat_event_frequency",
            "control_strength", "vulnerability_factor",
            "loss_event_frequency",
            "loss_min", "loss_most_likely", "loss_max",
            "single_loss_expectancy", "annual_loss_expectancy",
            "currency",
            "likelihood_band", "impact_band",
            "inherent_risk_rating", "residual_risk_rating",
            "treatment_recommendation",
        ],
        order_by="annual_loss_expectancy desc",
        limit_page_length=top_n,
    )

    # Aggregates across all in-scope scenarios
    rating_buckets = {"Low": 0, "Moderate": 0, "High": 0, "Very High": 0}
    treatment_buckets = {"Mitigate": 0, "Transfer": 0, "Avoid": 0,
                         "Accept": 0, "Unset": 0}
    total_ale = 0.0
    total_sle_max = 0.0  # worst-case if any one event happens

    # Re-fetch for aggregates (so we count beyond top_n)
    all_scenarios = frappe.get_all(
        "GRC CRQ Scenario", filters=filters,
        fields=["annual_loss_expectancy", "loss_max",
                "inherent_risk_rating", "treatment_recommendation"],
        limit_page_length=2000,
    )
    for s in all_scenarios:
        try:
            total_ale += float(s.annual_loss_expectancy or 0)
        except Exception:
            pass
        try:
            total_sle_max += float(s.loss_max or 0)
        except Exception:
            pass
        rating = s.inherent_risk_rating or "Low"
        if rating in rating_buckets:
            rating_buckets[rating] += 1
        treatment = s.treatment_recommendation or "Unset"
        treatment_buckets[treatment] = treatment_buckets.get(treatment, 0) + 1

    summary = {
        "total_scenarios": len(all_scenarios),
        "total_ale_year": round(total_ale, 2),
        "max_single_event_loss": round(total_sle_max, 2),
        "rating_breakdown": rating_buckets,
        "treatment_breakdown": treatment_buckets,
        "client": client,
    }

    return {
        "scenarios": scenarios, "summary": summary, "client": client,
    }
