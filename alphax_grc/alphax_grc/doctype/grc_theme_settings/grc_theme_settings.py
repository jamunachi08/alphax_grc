import frappe
from frappe.model.document import Document


PRESETS = {
    "AlphaX Navy (Default)": {
        "global_primary": "#0B132B", "global_accent": "#2563EB", "global_secondary": "#1C2541",
        "global_bg": "#F8FAFC", "global_card_bg": "#FFFFFF", "global_text": "#1E293B",
        "global_muted": "#64748B", "colour_critical": "#DC2626", "colour_high": "#D97706",
        "colour_medium": "#F59E0B", "colour_low": "#16A34A", "colour_ok": "#10B981",
        "colour_info": "#0EA5E4", "cc_header_bg": "#0B132B", "cc_kpi_bar_colour": "#0EA5E4",
        "cc_heatmap_low": "#DCFCE7", "cc_heatmap_medium": "#FEF3C7",
        "cc_heatmap_high": "#FEE2E2", "cc_heatmap_critical": "#991B1B",
        "cc_chart_bar_1": "#2563EB", "cc_chart_bar_2": "#0EA5E4",
        "cc_chart_bar_3": "#10B981", "cc_chart_bar_4": "#F59E0B", "cc_chart_bar_5": "#EF4444",
        "neo_bg_start": "#0B132B", "neo_bg_end": "#3A506B", "neo_accent": "#00B4D8",
        "neo_card_bg": "#FFFFFF", "report_cover_bg": "#0B132B", "report_accent": "#2563EB",
        "report_gap_critical": "#FEF2F2", "report_gap_medium": "#FFFBEB",
        "report_table_header": "#1E293B", "matrix_very_low": "#DCFCE7",
        "matrix_low": "#D1FAE5", "matrix_medium": "#FEF3C7",
        "matrix_high": "#FEE2E2", "matrix_critical": "#991B1B",
    },
    "Saudi Green": {
        "global_primary": "#065F46", "global_accent": "#D97706", "global_secondary": "#047857",
        "global_bg": "#F0FDF4", "global_card_bg": "#FFFFFF", "global_text": "#064E3B",
        "global_muted": "#6B7280", "colour_critical": "#DC2626", "colour_high": "#D97706",
        "colour_medium": "#F59E0B", "colour_low": "#059669", "colour_ok": "#10B981",
        "colour_info": "#0EA5E4", "cc_header_bg": "#065F46", "cc_kpi_bar_colour": "#D97706",
        "cc_heatmap_low": "#D1FAE5", "cc_heatmap_medium": "#FEF3C7",
        "cc_heatmap_high": "#FEE2E2", "cc_heatmap_critical": "#991B1B",
        "cc_chart_bar_1": "#065F46", "cc_chart_bar_2": "#D97706",
        "cc_chart_bar_3": "#10B981", "cc_chart_bar_4": "#F59E0B", "cc_chart_bar_5": "#EF4444",
        "neo_bg_start": "#064E3B", "neo_bg_end": "#065F46", "neo_accent": "#D97706",
        "neo_card_bg": "#FFFFFF", "report_cover_bg": "#065F46", "report_accent": "#D97706",
        "report_gap_critical": "#FEF2F2", "report_gap_medium": "#FFFBEB",
        "report_table_header": "#064E3B", "matrix_very_low": "#D1FAE5",
        "matrix_low": "#A7F3D0", "matrix_medium": "#FEF3C7",
        "matrix_high": "#FEE2E2", "matrix_critical": "#7F1D1D",
    },
    "Corporate Blue": {
        "global_primary": "#1D4ED8", "global_accent": "#0EA5E4", "global_secondary": "#1E40AF",
        "global_bg": "#EFF6FF", "global_card_bg": "#FFFFFF", "global_text": "#1E3A8A",
        "global_muted": "#6B7280", "colour_critical": "#DC2626", "colour_high": "#D97706",
        "colour_medium": "#F59E0B", "colour_low": "#16A34A", "colour_ok": "#10B981",
        "colour_info": "#0EA5E4", "cc_header_bg": "#1D4ED8", "cc_kpi_bar_colour": "#0EA5E4",
        "cc_heatmap_low": "#DBEAFE", "cc_heatmap_medium": "#FEF3C7",
        "cc_heatmap_high": "#FEE2E2", "cc_heatmap_critical": "#991B1B",
        "cc_chart_bar_1": "#1D4ED8", "cc_chart_bar_2": "#0EA5E4",
        "cc_chart_bar_3": "#10B981", "cc_chart_bar_4": "#F59E0B", "cc_chart_bar_5": "#EF4444",
        "neo_bg_start": "#1E3A8A", "neo_bg_end": "#1D4ED8", "neo_accent": "#0EA5E4",
        "neo_card_bg": "#FFFFFF", "report_cover_bg": "#1D4ED8", "report_accent": "#0EA5E4",
        "report_gap_critical": "#FEF2F2", "report_gap_medium": "#FFFBEB",
        "report_table_header": "#1E3A8A", "matrix_very_low": "#DBEAFE",
        "matrix_low": "#BFDBFE", "matrix_medium": "#FEF3C7",
        "matrix_high": "#FEE2E2", "matrix_critical": "#991B1B",
    },
    "Dark Mode": {
        "global_primary": "#0F172A", "global_accent": "#7C3AED", "global_secondary": "#1E293B",
        "global_bg": "#020617", "global_card_bg": "#0F172A", "global_text": "#E2E8F0",
        "global_muted": "#94A3B8", "colour_critical": "#F87171", "colour_high": "#FB923C",
        "colour_medium": "#FBBF24", "colour_low": "#4ADE80", "colour_ok": "#34D399",
        "colour_info": "#38BDF8", "cc_header_bg": "#0F172A", "cc_kpi_bar_colour": "#7C3AED",
        "cc_heatmap_low": "#14532D", "cc_heatmap_medium": "#713F12",
        "cc_heatmap_high": "#7F1D1D", "cc_heatmap_critical": "#450A0A",
        "cc_chart_bar_1": "#7C3AED", "cc_chart_bar_2": "#38BDF8",
        "cc_chart_bar_3": "#4ADE80", "cc_chart_bar_4": "#FBBF24", "cc_chart_bar_5": "#F87171",
        "neo_bg_start": "#020617", "neo_bg_end": "#0F172A", "neo_accent": "#7C3AED",
        "neo_card_bg": "#1E293B", "report_cover_bg": "#0F172A", "report_accent": "#7C3AED",
        "report_gap_critical": "#450A0A", "report_gap_medium": "#422006",
        "report_table_header": "#020617", "matrix_very_low": "#14532D",
        "matrix_low": "#166534", "matrix_medium": "#713F12",
        "matrix_high": "#7F1D1D", "matrix_critical": "#450A0A",
    },
    "Sand & Gold": {
        "global_primary": "#44403C", "global_accent": "#B45309", "global_secondary": "#78716C",
        "global_bg": "#FAFAF9", "global_card_bg": "#FFFFFF", "global_text": "#1C1917",
        "global_muted": "#78716C", "colour_critical": "#DC2626", "colour_high": "#B45309",
        "colour_medium": "#D97706", "colour_low": "#16A34A", "colour_ok": "#10B981",
        "colour_info": "#0EA5E4", "cc_header_bg": "#44403C", "cc_kpi_bar_colour": "#B45309",
        "cc_heatmap_low": "#FEF9C3", "cc_heatmap_medium": "#FEF3C7",
        "cc_heatmap_high": "#FEE2E2", "cc_heatmap_critical": "#991B1B",
        "cc_chart_bar_1": "#44403C", "cc_chart_bar_2": "#B45309",
        "cc_chart_bar_3": "#10B981", "cc_chart_bar_4": "#D97706", "cc_chart_bar_5": "#EF4444",
        "neo_bg_start": "#1C1917", "neo_bg_end": "#44403C", "neo_accent": "#B45309",
        "neo_card_bg": "#FEFCE8", "report_cover_bg": "#44403C", "report_accent": "#B45309",
        "report_gap_critical": "#FEF2F2", "report_gap_medium": "#FFFBEB",
        "report_table_header": "#1C1917", "matrix_very_low": "#FEF9C3",
        "matrix_low": "#FEF08A", "matrix_medium": "#FEF3C7",
        "matrix_high": "#FEE2E2", "matrix_critical": "#991B1B",
    },
    "Odoo Mauve": {
        # v1.9.1 — user-specified palette: #714B67 / #DBCED9 / #EAE5E9
        # Risk colors deliberately unchanged for accessibility
        "global_primary": "#714B67", "global_accent": "#875A7B", "global_secondary": "#5B3A52",
        "global_bg": "#EAE5E9", "global_card_bg": "#FFFFFF", "global_text": "#2C1F2C",
        "global_muted": "#7A6A78", "colour_critical": "#DC2626", "colour_high": "#D97706",
        "colour_medium": "#F59E0B", "colour_low": "#16A34A", "colour_ok": "#10B981",
        "colour_info": "#875A7B", "cc_header_bg": "#714B67", "cc_kpi_bar_colour": "#875A7B",
        "cc_heatmap_low": "#DBCED9", "cc_heatmap_medium": "#FEF3C7",
        "cc_heatmap_high": "#FEE2E2", "cc_heatmap_critical": "#991B1B",
        "cc_chart_bar_1": "#714B67", "cc_chart_bar_2": "#875A7B",
        "cc_chart_bar_3": "#DBCED9", "cc_chart_bar_4": "#F59E0B", "cc_chart_bar_5": "#DC2626",
        "neo_bg_start": "#5B3A52", "neo_bg_end": "#714B67", "neo_accent": "#DBCED9",
        "neo_card_bg": "#FFFFFF", "report_cover_bg": "#714B67", "report_accent": "#875A7B",
        "report_gap_critical": "#FEF2F2", "report_gap_medium": "#FFFBEB",
        "report_table_header": "#2C1F2C", "matrix_very_low": "#EAE5E9",
        "matrix_low": "#DBCED9", "matrix_medium": "#FEF3C7",
        "matrix_high": "#FEE2E2", "matrix_critical": "#991B1B",
    },
}


class GRCThemeSettings(Document):
    def validate(self):
        preset = self.theme_preset or "Custom"
        if preset != "Custom" and preset in PRESETS:
            colours = PRESETS[preset]
            for field, value in colours.items():
                setattr(self, field, value)

    def after_save(self):
        """Clear page cache so dashboards pick up new colours immediately."""
        frappe.clear_cache()


@frappe.whitelist()
def get_theme():
    """Return current theme as CSS variable dict for injection into pages."""
    if not frappe.db.exists("DocType", "GRC Theme Settings"):
        return _default_theme()
    if not frappe.db.exists("GRC Theme Settings", "GRC Theme Settings"):
        return _default_theme()
    doc = frappe.get_doc("GRC Theme Settings", "GRC Theme Settings")
    return {
        "--grc-primary":       doc.global_primary or "#0B132B",
        "--grc-accent":        doc.global_accent or "#2563EB",
        "--grc-secondary":     doc.global_secondary or "#1C2541",
        "--grc-bg":            doc.global_bg or "#F8FAFC",
        "--grc-card-bg":       doc.global_card_bg or "#FFFFFF",
        "--grc-text":          doc.global_text or "#1E293B",
        "--grc-muted":         doc.global_muted or "#64748B",
        "--grc-critical":      doc.colour_critical or "#DC2626",
        "--grc-high":          doc.colour_high or "#D97706",
        "--grc-medium":        doc.colour_medium or "#F59E0B",
        "--grc-low":           doc.colour_low or "#16A34A",
        "--grc-ok":            doc.colour_ok or "#10B981",
        "--grc-info":          doc.colour_info or "#0EA5E4",
        "--grc-cc-header":     doc.cc_header_bg or "#0B132B",
        "--grc-cc-bar":        doc.cc_kpi_bar_colour or "#0EA5E4",
        "--grc-heatmap-low":   doc.cc_heatmap_low or "#DCFCE7",
        "--grc-heatmap-med":   doc.cc_heatmap_medium or "#FEF3C7",
        "--grc-heatmap-high":  doc.cc_heatmap_high or "#FEE2E2",
        "--grc-heatmap-crit":  doc.cc_heatmap_critical or "#991B1B",
        "--grc-chart-1":       doc.cc_chart_bar_1 or "#2563EB",
        "--grc-chart-2":       doc.cc_chart_bar_2 or "#0EA5E4",
        "--grc-chart-3":       doc.cc_chart_bar_3 or "#10B981",
        "--grc-chart-4":       doc.cc_chart_bar_4 or "#F59E0B",
        "--grc-chart-5":       doc.cc_chart_bar_5 or "#EF4444",
        "--grc-neo-bg-start":  doc.neo_bg_start or "#0B132B",
        "--grc-neo-bg-end":    doc.neo_bg_end or "#3A506B",
        "--grc-neo-accent":    doc.neo_accent or "#00B4D8",
        "--grc-neo-card":      doc.neo_card_bg or "#FFFFFF",
        "--grc-report-cover":  doc.report_cover_bg or "#0B132B",
        "--grc-report-accent": doc.report_accent or "#2563EB",
        "--grc-report-gap-crit": doc.report_gap_critical or "#FEF2F2",
        "--grc-report-gap-med":  doc.report_gap_medium or "#FFFBEB",
        "--grc-report-header": doc.report_table_header or "#1E293B",
        "--grc-matrix-vlow":   doc.matrix_very_low or "#DCFCE7",
        "--grc-matrix-low":    doc.matrix_low or "#D1FAE5",
        "--grc-matrix-med":    doc.matrix_medium or "#FEF3C7",
        "--grc-matrix-high":   doc.matrix_high or "#FEE2E2",
        "--grc-matrix-crit":   doc.matrix_critical or "#991B1B",
    }


def _default_theme():
    return PRESETS["AlphaX Navy (Default)"]
