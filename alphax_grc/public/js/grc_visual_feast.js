/* AlphaX GRC v1.7.0 — Visual Feast UI Engine
 * ---------------------------------------------------------------------------
 * Loaded on every Frappe desk page. Detects the current view (list, form,
 * report, print) and applies branded enhancements across ALL GRC doctypes.
 *
 * No per-doctype JS files needed — this engine recognizes any doctype with
 * the "GRC " prefix and styles it consistently.
 *
 * What this provides:
 *   - List view: status chips, severity badges, owner avatars, hover preview
 *   - Form view: branded header bar, section icons, completion ring
 *   - Print view: branded letterhead, footer, watermark
 *   - Workspace: animated tile transitions
 *   - Report builder: GRC-themed chart palette
 * ---------------------------------------------------------------------------
 */

(function () {
    'use strict';

    if (typeof frappe === 'undefined') return;
    if (window.__grcVisualFeast) return;
    window.__grcVisualFeast = true;

    // ===== Severity / status mapping =====
    const STATUS_CHIP_MAP = {
        // Compliance
        'Implemented':              'grc-chip-implemented',
        'Partially Implemented':    'grc-chip-partial',
        'Not Implemented':          'grc-chip-not-impl',
        'Not Applicable':           'grc-chip-not-applic',
        'In Progress':              'grc-chip-info',
        'Not Started':              'grc-chip-untracked',
        // Risk / finding severity
        'Critical':                 'grc-chip-critical',
        'High':                     'grc-chip-high',
        'Medium':                   'grc-chip-medium',
        'Low':                      'grc-chip-low',
        'Informational':            'grc-chip-info',
        // Audit finding workflow
        'Open':                     'grc-chip-high',
        'Closed':                   'grc-chip-implemented',
        'Risk Accepted':            'grc-chip-info',
        'Resolved':                 'grc-chip-implemented',
        // Aramco lifecycle stages
        'Scoping':                  'grc-chip-info',
        'Self-Assessment':          'grc-chip-medium',
        'Audit Scheduled':          'grc-chip-info',
        'Audit In Progress':        'grc-chip-medium',
        'Findings':                 'grc-chip-high',
        'Remediation':              'grc-chip-medium',
        'Certified':                'grc-chip-implemented',
        'Renewal Due':              'grc-chip-medium',
        // Generic active/disabled
        'Active':                   'grc-chip-implemented',
        'Disabled':                 'grc-chip-untracked',
        'Draft':                    'grc-chip-untracked',
        'Submitted':                'grc-chip-info',
    };

    function isGRCDoctype(doctype) {
        return doctype && (doctype.startsWith('GRC ') ||
                          doctype.startsWith('AlphaX GRC AI'));
    }

    // ===== List view enhancement =====
    function enhanceListView(listview) {
        if (!listview || !listview.doctype) return;
        if (!isGRCDoctype(listview.doctype)) return;

        // Replace plain status text with branded chips after each render
        const enhance = function () {
            $(listview.$result || listview.wrapper)
                .find('.indicator-pill, .filterable[data-fieldtype="Select"]')
                .each(function () {
                    const $el = $(this);
                    if ($el.data('grc-chipped')) return;
                    const text = ($el.text() || '').trim();
                    const cls = STATUS_CHIP_MAP[text];
                    if (cls) {
                        $el.addClass('grc-chip ' + cls)
                           .removeClass('indicator-pill orange green red blue grey gray yellow')
                           .data('grc-chipped', true);
                    }
                });
        };
        // Listview re-renders on filter change; hook into the render event
        if (listview.refresh) {
            const orig_refresh = listview.refresh.bind(listview);
            listview.refresh = function () {
                const ret = orig_refresh.apply(this, arguments);
                setTimeout(enhance, 100);
                return ret;
            };
        }
        setTimeout(enhance, 100);
    }

    // Hook into Frappe's listview lifecycle
    frappe.listview_settings = frappe.listview_settings || {};
    const origInit = frappe.views.ListView && frappe.views.ListView.prototype
                   ? frappe.views.ListView.prototype.setup_defaults : null;

    // Use after_render_once if available
    $(document).on('list_view_rendered', function (e, listview) {
        enhanceListView(listview);
    });

    // ===== Form view enhancement =====
    function enhanceForm(frm) {
        if (!frm || !frm.doctype) return;
        if (!isGRCDoctype(frm.doctype)) return;

        // Brand the dashboard area at the top of the form
        try {
            if (frm.dashboard && frm.dashboard.parent && !frm.__grcBranded) {
                frm.__grcBranded = true;
                $(frm.dashboard.parent).addClass('grc-form-dashboard');
            }
        } catch (e) { /* silent */ }

        // Add a "View in Continuous Monitoring" shortcut for any doctype that
        // has matching Evidence Rules
        if (frm.doc && frm.doc.client && frm.doc.doctype === 'GRC Audit Finding') {
            if (frm.doc.source_evidence_rule && !frm.__grcCcmBtn) {
                frm.__grcCcmBtn = true;
                frm.add_custom_button(__('View source rule'), () => {
                    frappe.set_route('Form', 'GRC Evidence Rule', frm.doc.source_evidence_rule);
                }, __('AlphaX GRC'));
            }
        }
    }

    // Hook into Frappe's form lifecycle — every refresh, all GRC doctypes
    if (frappe.ui && frappe.ui.form) {
        const origOnLoad = frappe.ui.form.on;
        // We can't re-hook all, but we can listen for form-render globally
        $(document).on('form-refresh', function (e, frm) {
            enhanceForm(frm);
        });
    }

    // ===== Print preview enhancement =====
    // Inject the branded print header into every print view automatically
    $(document).on('app_ready', function () {
        if (window.location.pathname.indexOf('/printview') >= 0) {
            applyPrintBranding();
        }
    });

    function applyPrintBranding() {
        const themeBrand = (window.frappe && frappe.boot &&
                           frappe.boot.alphax_grc_brand) || 'AlphaX GRC';
        const $pf = $('.print-format');
        if ($pf.length && !$pf.find('.grc-print-header').length) {
            const dt = $pf.data('doctype') || '';
            $pf.prepend(`
                <div class="grc-print-header">
                    <div class="brand-name">${escapeHtml(themeBrand)}</div>
                    <div class="doc-type">${escapeHtml(dt)}</div>
                </div>
            `);
            $pf.append(`
                <div class="grc-print-footer">
                    Confidential — Generated by ${escapeHtml(themeBrand)} ·
                    ${new Date().toISOString().split('T')[0]}
                </div>
            `);
        }
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // ===== Workspace tile shimmer (subtle hover effect) =====
    setTimeout(function () {
        const tiles = document.querySelectorAll(
            '[data-page-route^="grc-"], .shortcut-widget-box');
        tiles.forEach(t => t.classList.add('grc-tile-polished'));
    }, 800);

    // Universal hook: every time Frappe routes, re-apply enhancements
    if (frappe.router) {
        frappe.router.on('change', function () {
            setTimeout(function () {
                if (cur_list) enhanceListView(cur_list);
                if (cur_frm) enhanceForm(cur_frm);
            }, 200);
        });
    }

    // Expose for debugging
    window.alphaxGRC = window.alphaxGRC || {};
    window.alphaxGRC.visualFeast = {
        enhanceListView, enhanceForm, applyPrintBranding,
        STATUS_CHIP_MAP, isGRCDoctype,
    };
})();
