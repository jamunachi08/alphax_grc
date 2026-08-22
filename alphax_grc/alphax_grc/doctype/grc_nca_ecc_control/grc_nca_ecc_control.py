import frappe
from frappe.model.document import Document
from frappe.utils import today


class GRCNCAECCControl(Document):
    def validate(self):
        if not self.last_assessed and self.compliance_status not in ('Not Assessed', 'Not Applicable'):
            self.last_assessed = today()
        # Auto-set compliance score from status
        if not self.compliance_score:
            score_map = {'Compliant': 100.0, 'Partially Compliant': 50.0,
                         'Non-Compliant': 0.0, 'Not Assessed': 0.0, 'Not Applicable': 100.0}
            self.compliance_score = score_map.get(self.compliance_status, 0.0)
        # Auto-set pillar flags based on control number
        pillar_map = {
            '2.2': ['pillar_zero_trust'],
            '2.3': ['pillar_cyber_resilience', 'pillar_data_sovereignty'],
            '2.9': ['pillar_cyber_resilience'],
            '2.12': ['pillar_ai_automation', 'pillar_cyber_resilience'],
            '3.1': ['pillar_data_sovereignty'],
            '1.3': ['pillar_data_sovereignty'],
            '4.2': ['pillar_zero_trust', 'pillar_cyber_resilience'],
        }
        cn = self.control_number or ''
        for ctrl, pillars in pillar_map.items():
            if cn.startswith(ctrl):
                for p in pillars:
                    setattr(self, p, 1)
