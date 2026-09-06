import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_to_date


class GRCAramcoCCCEngagement(Document):
    def validate(self):
        self._compute_compliance()
        self._auto_status_transitions()

    def _compute_compliance(self):
        rows = self.control_assessments or []
        if not rows:
            self.controls_assessed = 0
            self.compliance_percentage = 0
            return
        self.controls_assessed = len(rows)
        # Count non-NA rows; map status → score
        status_scores = {
            "Compliant": 100, "Partially Compliant": 50,
            "Non-Compliant": 0, "In Progress": 25, "Not Started": 0,
        }
        scored = []
        for r in rows:
            if r.assessment_status == "N/A":
                continue
            if r.compliance_score is not None and r.compliance_score != "":
                scored.append(int(r.compliance_score))
            elif r.assessment_status in status_scores:
                scored.append(status_scores[r.assessment_status])
        self.compliance_percentage = round(sum(scored) / len(scored), 1) if scored else 0

    def _auto_status_transitions(self):
        # Self-assessment completion
        if (self.engagement_status == "Self-Assessment"
                and self.self_assessment_completed_date
                and self.audit_scheduled_date):
            self.engagement_status = "Audit Scheduled"
        # Audit scheduled → in progress
        if (self.engagement_status == "Audit Scheduled"
                and self.audit_scheduled_date
                and getdate(self.audit_scheduled_date) <= getdate(today())
                and not self.audit_completed_date):
            self.engagement_status = "Audit In Progress"
        # Audit completed → findings (if any) or certified
        if (self.engagement_status in ("Audit In Progress", "Audit Scheduled")
                and self.audit_completed_date):
            if self.audit_findings_open and self.audit_findings_open > 0:
                self.engagement_status = "Findings"
            elif self.linked_certificate:
                self.engagement_status = "Certified"

    @frappe.whitelist()
    def populate_controls_from_library(self):
        """Bulk-load every active SACS-002 control as a row in
        control_assessments, applicable to the engagement's tier."""
        if not frappe.db.exists("DocType", "GRC Aramco SACS002 Control"):
            frappe.throw("SACS-002 Control library not installed.")

        if self.control_assessments:
            existing_codes = {r.control for r in self.control_assessments if r.control}
        else:
            existing_codes = set()

        controls = frappe.get_all(
            "GRC Aramco SACS002 Control",
            filters={"is_active": 1},
            fields=["name", "control_id", "applicability_tier"],
            order_by="control_id asc",
        )
        added = 0
        for c in controls:
            if c.name in existing_codes:
                continue
            # Filter by tier
            if c.applicability_tier == "Critical Only" and self.service_class_tier != "Critical":
                continue
            if (c.applicability_tier == "Critical & High"
                    and self.service_class_tier not in ("Critical", "High")):
                continue
            if (c.applicability_tier == "High & Medium"
                    and self.service_class_tier not in ("High", "Medium")):
                continue
            if (c.applicability_tier == "Medium & Low"
                    and self.service_class_tier not in ("Medium", "Low")):
                continue
            self.append("control_assessments", {
                "control": c.name,
                "assessment_status": "Not Started",
            })
            added += 1
        self.save()
        return {"added": added, "total_in_engagement": len(self.control_assessments or [])}


@frappe.whitelist()
def populate_engagement_controls(engagement_name):
    """Whitelisted wrapper for the populate_controls_from_library method."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    doc = frappe.get_doc("GRC Aramco CCC Engagement", engagement_name)
    return doc.populate_controls_from_library()
