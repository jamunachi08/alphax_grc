import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GRCConsultantTimesheet(Document):
    def validate(self):
        if self.hours and self.hours > 24:
            frappe.throw("Hours cannot exceed 24 in a single timesheet entry.")
        if self.hours and self.hours <= 0:
            frappe.throw("Hours must be greater than zero.")

        # Auto-pull hourly rate from the Client Profile if not set
        if self.billable and not self.hourly_rate:
            cp_rate = frappe.db.get_value(
                "GRC Client Profile", self.client, "default_hourly_rate"
            )
            if cp_rate:
                self.hourly_rate = cp_rate

        # Compute amount
        if self.billable:
            self.amount = flt(self.hours) * flt(self.hourly_rate or 0)
        else:
            self.amount = 0


@frappe.whitelist()
def get_client_hours_summary(client=None, from_date=None, to_date=None):
    """Aggregate hours and billable amount per consultant for a client.
    Used by the Client Profile and lifecycle dashboard panels."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)

    filters = {}
    if client:
        filters["client"] = client
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["date"] = [">=", from_date]
    elif to_date:
        filters["date"] = ["<=", to_date]

    rows = frappe.get_all(
        "GRC Consultant Timesheet",
        filters=filters,
        fields=["consultant", "billable",
                "SUM(hours) as total_hours",
                "SUM(amount) as total_amount"],
        group_by="consultant, billable",
    )

    summary = {}
    for r in rows:
        c = r.consultant
        if c not in summary:
            summary[c] = {
                "consultant": c,
                "billable_hours": 0, "non_billable_hours": 0,
                "total_amount": 0,
            }
        if r.billable:
            summary[c]["billable_hours"] = flt(r.total_hours)
            summary[c]["total_amount"] = flt(r.total_amount)
        else:
            summary[c]["non_billable_hours"] = flt(r.total_hours)

    return list(summary.values())


@frappe.whitelist()
def get_my_timesheet_summary():
    """Return current user's hours for the current week, grouped by client."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    from frappe.utils import getdate, add_days, today
    today_d = getdate(today())
    monday = add_days(today_d, -today_d.weekday())
    sunday = add_days(monday, 6)
    rows = frappe.get_all(
        "GRC Consultant Timesheet",
        filters={"consultant": frappe.session.user,
                 "date": ["between", [monday, sunday]]},
        fields=["client", "SUM(hours) as hours",
                "SUM(amount) as amount", "billable"],
        group_by="client, billable",
    )
    by_client = {}
    for r in rows:
        if r.client not in by_client:
            by_client[r.client] = {"client": r.client, "billable": 0,
                                    "non_billable": 0, "amount": 0}
        if r.billable:
            by_client[r.client]["billable"] = flt(r.hours)
            by_client[r.client]["amount"] = flt(r.amount)
        else:
            by_client[r.client]["non_billable"] = flt(r.hours)
    return list(by_client.values())
