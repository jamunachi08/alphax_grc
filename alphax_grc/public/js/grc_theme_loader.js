/* AlphaX GRC v1.7.0 — Theme Loader
   ------------------------------------------------------------------
   Runs once per page load. Reads GRC Theme Settings via the get_theme
   API and injects CSS variables on :root. After this runs, any CSS that
   references var(--grc-primary), var(--grc-secondary), etc., picks up
   the configured colours.
*/
(function() {
    'use strict';

    // Only run inside the Frappe app — not on portal/website pages
    if (typeof frappe === 'undefined' || !frappe.call) return;

    // Don't run multiple times if loaded multiple times
    if (window.__grcThemeLoaded) return;
    window.__grcThemeLoaded = true;

    function applyTheme(vars) {
        if (!vars || typeof vars !== 'object') return;
        const root = document.documentElement;
        Object.keys(vars).forEach(key => {
            if (key.startsWith('--')) {
                root.style.setProperty(key, vars[key]);
            }
        });
    }

    // Default fallback theme — applied immediately so first paint isn't unstyled
    applyTheme({
        '--grc-primary':   '#0F1F40',
        '--grc-secondary': '#185FA5',
        '--grc-accent':    '#C9A227',
        '--grc-success':   '#0F6E56',
        '--grc-warning':   '#854F0B',
        '--grc-danger':    '#A32D2D',
    });

    // Try to load configured theme. Silent failure — defaults already applied.
    function loadConfiguredTheme() {
        try {
            frappe.call({
                method: 'alphax_grc.alphax_grc.doctype.grc_theme_settings.grc_theme_settings.get_theme',
                callback: function(r) {
                    if (r && r.message) applyTheme(r.message);
                },
                error: function() { /* silent */ },
            });
        } catch (e) {
            // Silent — default theme already applied
        }
    }

    // Wait for frappe to be fully ready then load. If already ready, load now.
    if (frappe.boot && frappe.boot.user) {
        loadConfiguredTheme();
    } else if (typeof frappe.after_ajax === 'function') {
        frappe.after_ajax(loadConfiguredTheme);
    } else {
        document.addEventListener('DOMContentLoaded', loadConfiguredTheme);
    }
})();
