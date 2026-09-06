import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_months


class GRCDRPlan(Document):
    def validate(self):
        if self.status == "Approved" and not self.approval_date:
            self.approval_date = today()
        if self.last_tested and not self.next_test_date:
            self.next_test_date = str(add_months(getdate(self.last_tested), 12))
        if self.next_test_date and getdate(self.next_test_date) < getdate(today()) \
                and self.status == "Active":
            frappe.msgprint(
                f"DR Plan test is overdue (next test was due: {self.next_test_date}). "
                "Schedule a DR exercise immediately.",
                indicator="red", alert=True
            )
