"""GRC CRQ Scenario — Cyber Risk Quantification.

Implements public-domain quantitative risk methodology:

1. FAIR (Factor Analysis of Information Risk) — published by The Open Group
   as an open standard (O-RA Risk Analysis). Computes:
   - Threat Event Frequency (TEF) = Contact Frequency × Threat Capability factor
   - Loss Event Frequency (LEF) = TEF × Vulnerability factor
   - Single Loss Expectancy (SLE) = PERT-beta of (min, most_likely, max)
   - Annual Loss Expectancy (ALE) = LEF × SLE

2. NIST SP 800-30 — Guide for Conducting Risk Assessments. Public-domain US
   federal publication. Provides 5x5 likelihood × impact matrix yielding
   inherent risk rating.

No proprietary loss dataset, no commercial benchmark. All math is from
public formulas. Inputs come from the user's own threat modeling.
"""

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_months, getdate


# Capability/strength factors used to convert qualitative ratings into the
# 0.0-1.0 multipliers FAIR formulas need. Values follow common industry
# practice for FAIR implementations where qualitative inputs are mapped
# to quantitative factors.
_CAPABILITY_FACTOR = {
    "Very Low":  0.10,
    "Low":       0.30,
    "Medium":    0.50,
    "High":      0.75,
    "Very High": 0.95,
}


def _vulnerability_factor(threat_cap_label, control_strength_label):
    """FAIR-style vulnerability calculation.

    Vulnerability is the probability that a threat event becomes a loss
    event. It depends on the relationship between threat capability and
    control strength:

    - If threat capability > control strength → vulnerability is high
    - If threat capability ≈ control strength → vulnerability is moderate
    - If threat capability < control strength → vulnerability is low

    Returns a percentage 0-100.
    """
    tc = _CAPABILITY_FACTOR.get(threat_cap_label, 0.50)
    cs = _CAPABILITY_FACTOR.get(control_strength_label, 0.50)
    # Difference-based vulnerability: positive = threat exceeds control
    diff = tc - cs
    # Map diff (-0.85 to +0.85) into 0-100 with center around 30%
    # Strong controls vs Very Low threat ≈ 5%
    # Strong controls vs Very High threat ≈ 50% (still some vulnerability)
    # Weak controls vs Very High threat ≈ 95%
    base = 30.0  # baseline vulnerability when threat ≈ control
    sensitivity = 70.0  # how much diff moves the result
    pct = base + (diff * sensitivity)
    return max(2.0, min(98.0, pct))


def _likelihood_band(loss_event_freq):
    """Map continuous Loss Event Frequency (events/year) to NIST SP 800-30
    qualitative likelihood band."""
    if loss_event_freq is None or loss_event_freq <= 0:
        return "Very Low"
    if loss_event_freq < 0.1:    # less than once in 10 years
        return "Very Low"
    if loss_event_freq < 1.0:    # less than once a year
        return "Low"
    if loss_event_freq < 5.0:    # 1-5 times a year
        return "Medium"
    if loss_event_freq < 20.0:   # 5-20 times a year
        return "High"
    return "Very High"           # 20+ times a year


def _impact_band(single_loss_expectancy, currency="SAR"):
    """Map SLE to NIST SP 800-30 qualitative impact band.

    Thresholds expressed in SAR for KSA-first context. For other currencies
    consultants can override the residual_risk_rating manually."""
    if single_loss_expectancy is None or single_loss_expectancy <= 0:
        return "Very Low"
    # Thresholds — SAR-denominated, scaled for typical KSA enterprise
    if single_loss_expectancy < 50_000:
        return "Very Low"
    if single_loss_expectancy < 500_000:
        return "Low"
    if single_loss_expectancy < 5_000_000:
        return "Medium"
    if single_loss_expectancy < 50_000_000:
        return "High"
    return "Very High"


# NIST SP 800-30 5x5 risk matrix
# Rows: likelihood (Very Low → Very High)
# Cols: impact (Very Low → Very High)
_NIST_RISK_MATRIX = {
    ("Very Low", "Very Low"):     "Low",
    ("Very Low", "Low"):          "Low",
    ("Very Low", "Medium"):       "Low",
    ("Very Low", "High"):         "Low",
    ("Very Low", "Very High"):    "Low",

    ("Low", "Very Low"):          "Low",
    ("Low", "Low"):               "Low",
    ("Low", "Medium"):             "Low",
    ("Low", "High"):              "Moderate",
    ("Low", "Very High"):         "Moderate",

    ("Medium", "Very Low"):       "Low",
    ("Medium", "Low"):            "Low",
    ("Medium", "Medium"):         "Moderate",
    ("Medium", "High"):           "Moderate",
    ("Medium", "Very High"):      "High",

    ("High", "Very Low"):         "Low",
    ("High", "Low"):              "Moderate",
    ("High", "Medium"):           "Moderate",
    ("High", "High"):             "High",
    ("High", "Very High"):        "Very High",

    ("Very High", "Very Low"):    "Low",
    ("Very High", "Low"):         "Moderate",
    ("Very High", "Medium"):      "High",
    ("Very High", "High"):        "Very High",
    ("Very High", "Very High"):   "Very High",
}


class GRCCRQScenario(Document):
    def validate(self):
        # Compute FAIR/NIST values on every save
        self._compute_threat_event_frequency()
        self._compute_vulnerability()
        self._compute_loss_event_frequency()
        self._compute_loss_expectancy()
        self._classify_risk()
        # Auto-set next review date if last_reviewed changes
        if self.has_value_changed("last_reviewed") and self.last_reviewed:
            if not self.next_review_due:
                self.next_review_due = add_months(self.last_reviewed, 12)

    # -- FAIR: Threat Event Frequency -------------------------------------
    def _compute_threat_event_frequency(self):
        contact = float(self.contact_frequency_per_year or 0)
        cap_factor = _CAPABILITY_FACTOR.get(self.threat_capability or "Medium", 0.50)
        # FAIR's TEF = contact frequency × threat capability factor
        # (Contact Frequency × probability of action)
        self.threat_event_frequency = round(contact * cap_factor, 4)

    # -- FAIR: Vulnerability ---------------------------------------------
    def _compute_vulnerability(self):
        self.vulnerability_factor = _vulnerability_factor(
            self.threat_capability or "Medium",
            self.control_strength or "Medium",
        )

    # -- FAIR: Loss Event Frequency ---------------------------------------
    def _compute_loss_event_frequency(self):
        tef = float(self.threat_event_frequency or 0)
        vuln = float(self.vulnerability_factor or 0) / 100.0
        self.loss_event_frequency = round(tef * vuln, 4)

    # -- FAIR: PERT-beta SLE + ALE -----------------------------------------
    def _compute_loss_expectancy(self):
        lo = float(self.loss_min or 0)
        ml = float(self.loss_most_likely or 0)
        hi = float(self.loss_max or 0)
        # PERT-beta approximation: SLE = (min + 4*most_likely + max) / 6
        if lo == 0 and ml == 0 and hi == 0:
            self.single_loss_expectancy = 0
        else:
            self.single_loss_expectancy = round((lo + 4 * ml + hi) / 6.0, 2)
        sle = float(self.single_loss_expectancy or 0)
        lef = float(self.loss_event_frequency or 0)
        # ALE = SLE × LEF (annualized expected loss)
        self.annual_loss_expectancy = round(sle * lef, 2)

    # -- NIST SP 800-30: Risk Classification ------------------------------
    def _classify_risk(self):
        likelihood = _likelihood_band(float(self.loss_event_frequency or 0))
        impact = _impact_band(
            float(self.single_loss_expectancy or 0),
            self.currency or "SAR",
        )
        self.likelihood_band = likelihood
        self.impact_band = impact
        self.inherent_risk_rating = _NIST_RISK_MATRIX.get(
            (likelihood, impact), "Low")
        # If user hasn't set residual, default to inherent
        if not self.residual_risk_rating:
            self.residual_risk_rating = self.inherent_risk_rating
