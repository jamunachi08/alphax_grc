
import frappe
from frappe.model.document import Document


# Bands per NCA National Framework for Cybersecurity Risk Management
# (NFCRM-1:2025), Figure 3 "Cybersecurity Risk Levels":
#   Very Low 1-2 | Low 3-7 | Medium 8-14 | High 15-19 | Critical 20-25
# These are the bands entities are assessed against, so they are not
# configurable. Risks rated Critical or High must be reported to the NCA
# immediately on identification (NFCRM 5.5).
NFCRM_BANDS = (
    (20, "Critical"),
    (15, "High"),
    (8, "Medium"),
    (3, "Low"),
    (0, "Very Low"),
)

NCA_REPORTABLE_RATINGS = ("Critical", "High")

# GRC Client Profile records appetite per category as None / Low / Moderate /
# High. Each maps to the highest residual rating the client is willing to
# carry in that category. Anything above it needs a treatment decision or a
# formal acceptance — "is the remaining risk acceptable to the business?"
APPETITE_CEILING = {
    "None": "Very Low",
    "Low": "Low",
    "Moderate": "Medium",
    "High": "High",
}
RATING_ORDER = ["Very Low", "Low", "Medium", "High", "Critical"]

# Risk Register categories -> Client Profile appetite fields
APPETITE_FIELD = {
    "Strategic": "appetite_strategic",
    "Operational": "appetite_operational",
    "Financial": "appetite_financial",
    "Compliance": "appetite_compliance",
    "Legal": "appetite_compliance",
    "Cybersecurity": "appetite_cybersecurity",
    "Privacy": "appetite_privacy",
    "Third-Party": "appetite_third_party",
    "Reputational": "appetite_reputational",
    "Environmental": "appetite_operational",
}


def _rank(rating):
    try:
        return RATING_ORDER.index(rating)
    except ValueError:
        return -1


def appetite_ceiling_for(client: str, category: str):
    """The highest residual rating this client accepts in this category, or None."""
    field = APPETITE_FIELD.get(category or "")
    if not client or not field:
        return None
    try:
        appetite = frappe.db.get_value("GRC Client Profile", client, field)
    except Exception:
        return None
    return APPETITE_CEILING.get(appetite) if appetite else None


def evaluate_appetite(client: str, category: str, residual_rating: str, risk_response: str,
                      acceptance_reference: str | None) -> dict:
    """Compare a residual rating against the client's appetite for that category.

    Returns within_appetite (0/1/None when appetite is undefined), the ceiling,
    and a plain-English status.
    """
    ceiling = appetite_ceiling_for(client, category)
    if not ceiling or residual_rating in (None, "", "N/A"):
        return {"within_appetite": None, "ceiling": ceiling, "status": "Appetite not set"}

    within = _rank(residual_rating) <= _rank(ceiling)
    if within:
        return {"within_appetite": 1, "ceiling": ceiling, "status": "Within appetite"}
    if risk_response == "Accept" and acceptance_reference:
        return {"within_appetite": 0, "ceiling": ceiling,
                "status": "Above appetite — formally accepted"}
    return {"within_appetite": 0, "ceiling": ceiling,
            "status": "Above appetite — needs treatment or acceptance"}


def _score_to_rating(score):
    score = int(score or 0)
    if score <= 0:
        return "N/A"
    for threshold, rating in NFCRM_BANDS:
        if score >= threshold:
            return rating
    return "Very Low"


def _derived_impact(doc):
    """NFCRM Figure 4 grades impact against confidentiality, integrity and
    availability separately. A breach of any one of them sets the level, so
    the overall impact is the highest of the three."""
    parts = [
        int(doc.get(f) or 0)
        for f in ("impact_confidentiality", "impact_integrity", "impact_availability")
    ]
    return max(parts) if any(parts) else None


class GRCRiskRegister(Document):
    def validate(self):
        derived = _derived_impact(self)
        if derived:
            self.impact = str(derived)

        self.inherent_score = int(self.impact or 0) * int(self.likelihood or 0)
        self.risk_rating = _score_to_rating(self.inherent_score)

        if self.residual_impact and self.residual_likelihood:
            self.residual_score = int(self.residual_impact or 0) * int(self.residual_likelihood or 0)
        elif not self.residual_score:
            self.residual_score = 0

        self.residual_rating = _score_to_rating(self.residual_score)

        # NFCRM 5.5 — Critical (5) and High (4) risks are reportable to the NCA
        # immediately on identification. The effective rating is the manual
        # override where the risk owner has set one.
        effective = self.manual_rating_override or self.risk_rating
        self.nca_reportable = 1 if effective in NCA_REPORTABLE_RATINGS else 0

        # Question 5: is the remaining risk acceptable to the business?
        if self.meta.get_field("within_appetite"):
            verdict = evaluate_appetite(
                self.client, self.risk_category, self.residual_rating,
                self.risk_response, self.acceptance_reference,
            )
            self.within_appetite = verdict["within_appetite"]
            self.appetite_ceiling = verdict["ceiling"]
            self.appetite_status = verdict["status"]

        if self.risk_response == "Accept" and not self.acceptance_reference:
            frappe.msgprint(
                "Risk response is 'Accept' but no Risk Acceptance record is linked. "
                "Create a GRC Risk Acceptance record and link it here.",
                indicator="orange",
                alert=True,
            )

        if self.inherent_score >= 20 and self.escalation_status == "Normal":
            self.escalation_status = "Escalated"
            frappe.msgprint(
                f"Risk score {self.inherent_score} is very high. Escalation status set to 'Escalated'.",
                indicator="red",
                alert=True,
            )
