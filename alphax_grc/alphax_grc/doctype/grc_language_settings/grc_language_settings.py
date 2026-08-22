import frappe
from frappe.model.document import Document


class GRCLanguageSettings(Document):
    def after_save(self):
        frappe.clear_cache()


@frappe.whitelist()
def get_language_config():
    """Return language/RTL configuration for dashboard injection."""
    defaults = {
        "primary_language": "English",
        "text_direction": "LTR (Left to Right)",
        "enable_bilingual_labels": 1,
        "date_format": "DD/MM/YYYY",
        "report_language": "Bilingual (EN + AR)",
        "dashboard_language": "Bilingual (EN + AR)",
        "hijri_calendar": 0,
        "currency_symbol": "SAR",
        "is_rtl": False,
    }
    if not frappe.db.exists("DocType", "GRC Language Settings"):
        return defaults
    if not frappe.db.exists("GRC Language Settings", "GRC Language Settings"):
        return defaults
    doc = frappe.get_doc("GRC Language Settings", "GRC Language Settings")
    result = {
        "primary_language": doc.primary_language or "English",
        "text_direction": doc.text_direction or "LTR (Left to Right)",
        "enable_bilingual_labels": doc.enable_bilingual_labels,
        "date_format": doc.date_format or "DD/MM/YYYY",
        "report_language": doc.report_language or "Bilingual (EN + AR)",
        "dashboard_language": doc.dashboard_language or "Bilingual (EN + AR)",
        "hijri_calendar": doc.hijri_calendar,
        "currency_symbol": doc.currency_symbol or "SAR",
        "is_rtl": "RTL" in (doc.text_direction or ""),
    }
    return result
