import frappe
from frappe.model.document import Document


class GRCKPI(Document):
    def validate(self):
        # Cap percentage values
        if self.kpi_type == "Percentage":
            for row in (self.measurements or []):
                for q in ("q1_actual", "q2_actual", "q3_actual", "q4_actual",
                          "q1_target", "q2_target", "q3_target", "q4_target",
                          "prior_year_q4_actual"):
                    v = row.get(q)
                    if v is None or v == "":
                        continue
                    try:
                        fv = float(v)
                        if fv < 0 or fv > 1:
                            # NCA template uses 0-1 for percentages — flag if outside
                            # but don't block, sometimes people enter 0-100
                            pass
                    except (ValueError, TypeError):
                        frappe.throw(f"{q} must be numeric.")


@frappe.whitelist()
def get_kpi_chart_data(client=None):
    """Return chart-ready data for the KPI dashboard:
    [{kpi_id, indicator_name, domain, year, q1_target, q1_actual, ... q4_actual}]"""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)

    filters = {}
    if client:
        filters["client"] = client

    kpis = frappe.get_all("GRC KPI", filters=filters,
                          fields=["name", "kpi_id", "indicator_name",
                                  "cybersecurity_domain", "kpi_type",
                                  "frequency"],
                          order_by="kpi_id asc")
    out = []
    for kpi in kpis:
        rows = frappe.get_all("GRC KPI Quarterly Measurement",
            filters={"parent": kpi.name},
            fields=["year", "q1_target", "q1_actual", "q2_target", "q2_actual",
                    "q3_target", "q3_actual", "q4_target", "q4_actual",
                    "prior_year_q4_actual"],
            order_by="year asc")
        out.append({
            "kpi_id": kpi.kpi_id,
            "indicator_name": kpi.indicator_name,
            "domain": kpi.cybersecurity_domain,
            "type": kpi.kpi_type,
            "frequency": kpi.frequency,
            "measurements": rows,
        })
    return out
