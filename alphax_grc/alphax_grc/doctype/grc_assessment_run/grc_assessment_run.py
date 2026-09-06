
import frappe
from frappe.model.document import Document


NAMED_ANSWER_SCORES = {
    "Yes": 5,
    "Fully Implemented": 5,
    "Partial": 3,
    "Partially Implemented": 3,
    "No": 0,
    "Not Implemented": 0,
    "Not Applicable": None,  # excluded from denominator
}

MATURITY_LABEL = {
    range(0, 20): "Initial",
    range(20, 40): "Developing",
    range(40, 60): "Defined",
    range(60, 80): "Managed",
    range(80, 101): "Optimised",
}


def _maturity_label(score):
    for r, label in MATURITY_LABEL.items():
        if int(score) in r:
            return label
    return "Initial"


class GRCAssessmentRun(Document):
    def validate(self):
        self._score_responses()
        self._validate_completion_status()

    def _score_responses(self):
        yes_score = partial_score = no_score = na_score = 0
        total_weight = earned = 0.0

        for row in self.responses or []:
            weight = float(row.weight or 1)
            ans = (row.answer_option or "").strip()

            if ans in NAMED_ANSWER_SCORES:
                score = NAMED_ANSWER_SCORES[ans]
                if score is None:
                    # Not Applicable — exclude from denominator
                    na_score += 1
                    row.maturity_score = 0
                    row.gap_score = 0
                    continue
                if score == 5:
                    yes_score += 1
                elif score == 3:
                    partial_score += 1
                else:
                    no_score += 1
            else:
                # Numeric response (e.g. maturity scale 1-5 entered directly)
                try:
                    raw = float(ans) if ans else float(row.maturity_score or 0)
                    score = max(0.0, min(5.0, raw))
                except (ValueError, TypeError):
                    score = 0.0

            row.maturity_score = score
            row.gap_score = max(0, 5 - float(score))
            row.max_score = 5
            total_weight += weight * 5
            earned += weight * float(score)

        self.yes_score = yes_score
        self.partial_score = partial_score
        self.no_score = no_score
        self.total_weight = total_weight
        self.maturity_score = round((earned / total_weight) * 100, 2) if total_weight else 0
        self.maturity_label = _maturity_label(self.maturity_score)

    def _validate_completion_status(self):
        if self.status == "Completed":
            unanswered = sum(
                1 for r in (self.responses or [])
                if not (r.answer_option or r.maturity_score)
            )
            if unanswered > 0:
                frappe.msgprint(
                    f"{unanswered} question(s) have no answer. "
                    "Assessment marked Completed with unanswered questions — "
                    "maturity score may not be representative.",
                    indicator="orange",
                )
