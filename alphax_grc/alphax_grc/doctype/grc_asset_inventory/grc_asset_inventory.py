import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_months


CIA_SCORE = {
    'Low (L)': 1, 'Low': 1,
    'Medium (M)': 2, 'Medium': 2,
    'High (H)': 3, 'High': 3,
}


class GRCAssetInventory(Document):
    def validate(self):
        self._set_criticality()
        self._set_review_dates()
        self._check_overdue()
        self._set_nca_domain()

    def _set_criticality(self):
        """Auto-calculate overall criticality from CIA scores."""
        c = CIA_SCORE.get(self.confidentiality or '', 1)
        i = CIA_SCORE.get(self.integrity or '', 1)
        a = CIA_SCORE.get(self.availability or '', 1)
        avg = (c + i + a) / 3
        max_score = max(c, i, a)
        # Weighted: max score matters more than average for security
        combined = (avg * 0.4) + (max_score * 0.6)
        if combined >= 2.8:
            self.asset_criticality = 'Critical'
        elif combined >= 2.3:
            self.asset_criticality = 'High'
        elif combined >= 1.7:
            self.asset_criticality = 'Medium'
        elif combined >= 1.2:
            self.asset_criticality = 'Low'
        else:
            self.asset_criticality = 'Very Low'

    def _set_review_dates(self):
        if not self.last_reviewed:
            self.last_reviewed = today()
        if not self.next_review_date and self.last_reviewed:
            # Critical/High assets reviewed every 6 months, others annually
            months = 6 if self.asset_criticality in ('Critical', 'High') else 12
            self.next_review_date = str(add_months(getdate(self.last_reviewed), months))

    def _check_overdue(self):
        if (self.next_review_date and
                getdate(self.next_review_date) < getdate(today()) and
                self.asset_status == 'Active'):
            frappe.msgprint(
                f"Asset '{self.asset_name}' review is overdue (due: {self.next_review_date}). "
                "Schedule a review immediately.",
                indicator="orange", alert=True
            )
        if (self.end_of_life_date and
                getdate(self.end_of_life_date) <= getdate(today()) and
                self.asset_status == 'Active'):
            frappe.msgprint(
                f"ALERT: Asset '{self.asset_name}' has reached End of Life ({self.end_of_life_date}). "
                "Update status or plan replacement.",
                indicator="red", alert=True
            )

    def _set_nca_domain(self):
        """Auto-map asset type to NCA ECC-2:2024 domain."""
        type_to_domain = {
            'Server': 'Defense',
            'Network Device': 'Defense',
            'Laptop': 'Defense',
            'Desktop': 'Defense',
            'Software': 'Defense',
            'Media / Portable Device': 'Defense',
            'Cloud Service': 'Technical Systems',
            'Physical / Facility': 'Resilience',
            'Service': 'External Parties',
        }
        if self.asset_type and not self.nca_ecc_domain:
            self.nca_ecc_domain = type_to_domain.get(self.asset_type, 'Defense')
