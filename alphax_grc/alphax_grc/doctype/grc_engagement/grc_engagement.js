// AlphaX GRC v1.8.0 — Engagement Cockpit
// Form script for the GRC Engagement doctype. Augments the standard
// Frappe form with a visual phase timeline at the top, a "next action"
// hint, and one-click phase advance / kickoff buttons.

frappe.ui.form.on('GRC Engagement', {
    refresh(frm) {
        renderEngagementCockpit(frm);
        addEngagementButtons(frm);
    },
    after_save(frm) {
        renderEngagementCockpit(frm);
    },
});

function addEngagementButtons(frm) {
    if (frm.is_new()) return;

    // KICKOFF button — only visible on Draft engagements
    if (frm.doc.engagement_status === 'Draft') {
        frm.add_custom_button(__('🚀 Kickoff'), () => {
            frappe.call({
                method: 'alphax_grc.alphax_grc.doctype.grc_engagement.grc_engagement.kickoff_engagement',
                args: { engagement_name: frm.doc.name },
                freeze: true,
                freeze_message: __('Kicking off engagement…'),
                callback: (r) => {
                    if (r.message && r.message.ok) {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: 'green',
                        });
                        frm.reload_doc();
                    } else {
                        frappe.show_alert({
                            message: (r.message && r.message.message) || __('Kickoff failed'),
                            indicator: 'orange',
                        });
                    }
                },
            });
        }).addClass('btn-primary');
    }

    // ADVANCE PHASE button — visible on Active engagements
    if (frm.doc.engagement_status === 'Active') {
        frm.add_custom_button(__('▶ Advance Phase'), () => advancePhase(frm, 0))
            .addClass('btn-primary');
        // v2.0.0 — AI-assisted phase advancement advisor
        frm.add_custom_button(__('🤖 Ask Advisor'), () => askAdvisor(frm))
            .addClass('btn-default');
        frm.add_custom_button(__('⚠ Force Advance (admin)'), () => {
            frappe.confirm(
                __('Force-advance ignores blocking criteria. This will be logged in the Decision Log. Continue?'),
                () => advancePhase(frm, 1));
        }, __('Admin'));
    }

    // VIEW DECISION LOG
    frm.add_custom_button(__('Decision Log'), () => {
        frappe.set_route('List', 'GRC Engagement Decision Log',
            { engagement: frm.doc.name });
    }, __('AlphaX GRC'));

    // VIEW LINKED TASKS
    frm.add_custom_button(__('Implementation Tasks'), () => {
        frappe.set_route('List', 'GRC Implementation Task',
            { engagement: frm.doc.name });
    }, __('AlphaX GRC'));

    // Open the consultant inbox
    frm.add_custom_button(__('Consultant Inbox'), () => {
        frappe.set_route('grc-consultant-inbox');
    }, __('AlphaX GRC'));
}

function advancePhase(frm, force) {
    frappe.call({
        method: 'alphax_grc.alphax_grc.doctype.grc_engagement.grc_engagement.advance_engagement_phase',
        args: { engagement_name: frm.doc.name, force: force ? 1 : 0 },
        freeze: true,
        freeze_message: __('Checking blockers and advancing…'),
        callback: (r) => {
            const m = r && r.message;
            if (!m) return;
            if (m.ok) {
                frappe.show_alert({
                    message: m.message,
                    indicator: m.completed ? 'blue' : 'green',
                });
                frm.reload_doc();
            } else if (m.blockers && m.blockers.length) {
                showBlockersModal(m.blockers);
            } else {
                frappe.show_alert({
                    message: m.message || __('Cannot advance'),
                    indicator: 'orange',
                });
            }
        },
    });
}

function showBlockersModal(blockers) {
    const html = `
        <div style="padding: 8px;">
            <p style="color: #A32D2D; font-weight: 600; margin-bottom: 12px;">
                ${__('Cannot advance — these blockers must be resolved first:')}
            </p>
            <ul style="padding-left: 20px;">
                ${blockers.map(b => `<li style="margin: 4px 0; color: #1E293B;">${frappe.utils.escape_html(b)}</li>`).join('')}
            </ul>
            <p style="margin-top: 16px; font-size: 11px; color: #687178;">
                ${__('A System Manager can override using "Force Advance" in the Admin menu.')}
            </p>
        </div>`;
    const d = new frappe.ui.Dialog({
        title: __('Phase Advance Blocked'),
        size: 'small',
    });
    $(d.body).html(html);
    d.show();
}

function renderEngagementCockpit(frm) {
    if (frm.is_new()) return;

    frappe.call({
        method: 'alphax_grc.alphax_grc.doctype.grc_engagement.grc_engagement.get_engagement_overview',
        args: { engagement_name: frm.doc.name },
        callback: (r) => {
            if (r && r.message) drawCockpit(frm, r.message);
        },
    });
}

function drawCockpit(frm, data) {
    // Find or create cockpit container above the form
    let $container = $(frm.fields_dict.section_identity.wrapper)
        .find('.grc-engagement-cockpit');
    if (!$container.length) {
        $container = $('<div class="grc-engagement-cockpit"></div>');
        $(frm.fields_dict.section_identity.wrapper).before($container);
    }

    const phases = data.all_phases || [];
    const log = data.phase_log || [];
    const phaseStatus = {};
    log.forEach(p => { phaseStatus[p.phase_number] = p; });

    const currentPhase = data.current_phase_number || 0;
    const isOverdue = !!data.is_overdue;
    const blockers = data.blockers || [];
    const health = data.health || {};

    // Build the timeline HTML
    const phaseDots = phases.map(p => {
        const log = phaseStatus[p.phase_number] || {};
        let cls = 'locked';
        let badge = '';
        if (log.status === 'Completed') {
            cls = 'completed'; badge = '✓';
        } else if (log.status === 'In Progress' || p.phase_number === currentPhase) {
            cls = 'current'; badge = p.icon || p.phase_number;
        } else if (log.status === 'Skipped') {
            cls = 'skipped'; badge = '⊘';
        } else {
            badge = p.phase_number;
        }
        return `
            <div class="phase-step ${cls}" title="${frappe.utils.escape_html(p.phase_label)}">
                <div class="phase-dot">${badge}</div>
                <div class="phase-label">${frappe.utils.escape_html(p.phase_label)}</div>
            </div>`;
    }).join('<div class="phase-connector"></div>');

    const heroBg = data.status === 'Completed'
        ? 'linear-gradient(135deg, #0F6E56 0%, #5BA52A 100%)'
        : isOverdue
            ? 'linear-gradient(135deg, #791F1F 0%, #C25C1F 50%, #185FA5 100%)'
            : 'linear-gradient(135deg, #0F1F40 0%, #185FA5 50%, #0F6E56 100%)';

    const currentPhaseTmpl = phases.find(p => p.phase_number === currentPhase) || {};

    $container.html(`
        <style>
            .grc-engagement-cockpit { margin: 0 0 18px; padding: 0; }
            .grc-engagement-cockpit .hero {
                background: ${heroBg};
                color: white; border-radius: 12px;
                padding: 20px 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                position: relative; overflow: hidden;
            }
            .grc-engagement-cockpit .hero::before {
                content: ''; position: absolute; top: -40px; right: -40px;
                width: 200px; height: 200px; border-radius: 50%;
                background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            }
            .grc-engagement-cockpit .hero-row1 {
                display: flex; justify-content: space-between; align-items: flex-start;
                margin-bottom: 14px; position: relative;
            }
            .grc-engagement-cockpit .hero-title {
                font-size: 17px; font-weight: 600; margin: 0; color: white;
            }
            .grc-engagement-cockpit .hero-sub {
                font-size: 11px; opacity: 0.85; margin-top: 2px;
            }
            .grc-engagement-cockpit .hero-status-chip {
                background: rgba(255,255,255,0.15); padding: 3px 10px;
                border-radius: 999px; font-size: 11px; font-weight: 600;
                text-transform: uppercase; letter-spacing: 0.04em;
            }
            .grc-engagement-cockpit .timeline {
                display: flex; align-items: center; padding: 16px 0 12px;
                margin-top: 4px; gap: 0;
            }
            .grc-engagement-cockpit .phase-step {
                display: flex; flex-direction: column; align-items: center;
                flex: 0 0 auto; min-width: 80px;
            }
            .grc-engagement-cockpit .phase-dot {
                width: 36px; height: 36px; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 13px; font-weight: 700;
                background: rgba(255,255,255,0.15); color: white;
                border: 2px solid rgba(255,255,255,0.35);
                transition: all 0.2s;
            }
            .grc-engagement-cockpit .phase-step.completed .phase-dot {
                background: rgba(91, 165, 42, 0.9); border-color: white;
            }
            .grc-engagement-cockpit .phase-step.current .phase-dot {
                background: #C9A227; border-color: white;
                box-shadow: 0 0 0 4px rgba(201, 162, 39, 0.3);
                font-size: 16px;
            }
            .grc-engagement-cockpit .phase-step.skipped .phase-dot {
                background: rgba(105, 113, 120, 0.6);
            }
            .grc-engagement-cockpit .phase-label {
                font-size: 9px; color: rgba(255,255,255,0.85);
                text-transform: uppercase; letter-spacing: 0.04em;
                margin-top: 5px; text-align: center; max-width: 90px;
                line-height: 1.2; font-weight: 500;
            }
            .grc-engagement-cockpit .phase-step.current .phase-label {
                color: white; font-weight: 600;
            }
            .grc-engagement-cockpit .phase-connector {
                flex: 1 1 auto; height: 2px;
                background: rgba(255,255,255,0.25);
                margin: 0 -10px 22px;
            }
            .grc-engagement-cockpit .next-action {
                margin-top: 14px; padding: 12px 14px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px; font-size: 12px;
                border-left: 3px solid #C9A227;
            }
            .grc-engagement-cockpit .next-action .head {
                font-size: 10px; opacity: 0.8;
                text-transform: uppercase; letter-spacing: 0.04em;
                margin-bottom: 2px;
            }
            .grc-engagement-cockpit .next-action .body { font-size: 13px; }
            .grc-engagement-cockpit .health-strip {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
                gap: 10px; margin-top: 14px;
            }
            .grc-engagement-cockpit .health-card {
                background: rgba(255,255,255,0.1); padding: 8px 10px;
                border-radius: 6px;
            }
            .grc-engagement-cockpit .health-card .num {
                font-size: 18px; font-weight: 700; color: white; line-height: 1;
            }
            .grc-engagement-cockpit .health-card .lbl {
                font-size: 9px; opacity: 0.8;
                text-transform: uppercase; letter-spacing: 0.04em;
                margin-top: 4px;
            }
            .grc-engagement-cockpit .health-card.alert .num { color: #FFD700; }
            .grc-engagement-cockpit .blockers-pill {
                display: inline-block; background: #791F1F; color: white;
                padding: 2px 8px; border-radius: 999px;
                font-size: 10px; font-weight: 700;
                margin-left: 8px;
            }
        </style>

        <div class="hero">
            <div class="hero-row1">
                <div>
                    <div class="hero-title">
                        ${frappe.utils.escape_html(data.title || data.engagement)}
                        ${blockers.length ? `<span class="blockers-pill">${blockers.length} blocker${blockers.length === 1 ? '' : 's'}</span>` : ''}
                    </div>
                    <div class="hero-sub">
                        ${frappe.utils.escape_html(data.client || '')} ·
                        ${frappe.utils.escape_html(data.type || '')} ·
                        ${data.current_phase_label ? __('Phase {0}: {1}', [data.current_phase_number, data.current_phase_label]) : __('Not started')}
                        ${isOverdue ? ' · <span style="color:#FFD700;">' + __('OVERDUE') + '</span>' : ''}
                    </div>
                </div>
                <div class="hero-status-chip">${frappe.utils.escape_html(data.status || '')}</div>
            </div>

            <div class="timeline">${phaseDots}</div>

            ${currentPhase ? `
                <div class="next-action">
                    <div class="head">${__('Current phase purpose')}</div>
                    <div class="body">${frappe.utils.escape_html((currentPhaseTmpl.purpose_summary || data.current_phase_purpose || '').substring(0, 240))}</div>
                </div>
            ` : `
                <div class="next-action">
                    <div class="head">${__('Next step')}</div>
                    <div class="body">${__('This engagement is in Draft. Click 🚀 Kickoff to start phase 1.')}</div>
                </div>
            `}

            <div class="health-strip">
                <div class="health-card ${health.open_findings > 0 ? 'alert' : ''}">
                    <div class="num">${health.open_findings || 0}</div>
                    <div class="lbl">${__('Open findings')}</div>
                </div>
                <div class="health-card ${health.high_risks > 0 ? 'alert' : ''}">
                    <div class="num">${health.high_risks || 0}</div>
                    <div class="lbl">${__('High/Critical risks')}</div>
                </div>
                <div class="health-card">
                    <div class="num">${health.tasks_pending || 0}</div>
                    <div class="lbl">${__('Pending tasks')}</div>
                </div>
                <div class="health-card ${health.tasks_overdue > 0 ? 'alert' : ''}">
                    <div class="num">${health.tasks_overdue || 0}</div>
                    <div class="lbl">${__('Overdue tasks')}</div>
                </div>
                <div class="health-card ${health.evidence_rule_failures > 0 ? 'alert' : ''}">
                    <div class="num">${health.evidence_rule_failures || 0}</div>
                    <div class="lbl">${__('Rule failures (30d)')}</div>
                </div>
                <div class="health-card">
                    <div class="num">${data.days_in_phase || 0}<span style="font-size:11px; opacity:0.7;">d</span></div>
                    <div class="lbl">${__('Days in phase')}</div>
                </div>
            </div>
        </div>
    `);
}

// v2.0.0 — AI-assisted phase advancement advisor
function askAdvisor(frm) {
    frappe.call({
        method: 'alphax_grc.engagement_automation.recommend_phase_advance',
        args: { engagement_name: frm.doc.name },
        freeze: true,
        freeze_message: __('Asking the advisor…'),
        callback: (r) => {
            const m = r && r.message;
            if (!m) return;
            renderAdvisorDialog(m);
        },
    });
}

function renderAdvisorDialog(m) {
    const recColors = {
        'advance': { bg: '#5BA52A', label: __('ADVANCE') },
        'review':  { bg: '#C9A227', label: __('REVIEW') },
        'hold':    { bg: '#A32D2D', label: __('HOLD') },
    };
    const rec = recColors[m.recommendation] || recColors['review'];
    const confidencePct = Math.round((m.confidence || 0) * 100);
    const blockersHtml = (m.blockers && m.blockers.length)
        ? `<div style="margin-top:14px;padding:10px;background:rgba(163,45,45,0.05);border-left:3px solid #A32D2D;border-radius:0 4px 4px 0;">
             <div style="font-size:10px;color:#791F1F;font-weight:700;text-transform:uppercase;margin-bottom:6px;">${__('Blockers')}</div>
             <ul style="margin:0;padding-left:18px;font-size:12px;">
               ${m.blockers.map(b => `<li style="margin:2px 0;">${frappe.utils.escape_html(b)}</li>`).join('')}
             </ul>
           </div>`
        : '';
    const aiBadge = m.ai_used
        ? `<span style="background:#185FA5;color:white;padding:2px 7px;border-radius:999px;font-size:9px;font-weight:700;margin-left:8px;">${__('AI')}</span>`
        : `<span style="background:#9C9C9C;color:white;padding:2px 7px;border-radius:999px;font-size:9px;font-weight:700;margin-left:8px;">${__('RULE-BASED')}</span>`;
    const html = `
      <div style="padding:8px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
          <div>
            <div style="font-size:10px;color:#687178;text-transform:uppercase;letter-spacing:0.04em;">${__('Recommendation for phase')} ${m.current_phase}</div>
            <div style="font-size:14px;font-weight:600;color:var(--grc-primary,#0F1F40);margin-top:4px;">${frappe.utils.escape_html(m.current_phase_label)}</div>
          </div>
          <div style="text-align:right;">
            <span style="background:${rec.bg};color:white;padding:6px 14px;border-radius:6px;font-size:13px;font-weight:700;letter-spacing:0.04em;">${rec.label}</span>${aiBadge}
            <div style="font-size:10px;color:#687178;margin-top:6px;">${confidencePct}% ${__('confidence')}</div>
          </div>
        </div>
        <div style="font-size:13px;line-height:1.5;color:#1E293B;background:rgba(15,31,64,0.03);padding:12px;border-radius:6px;">
          ${frappe.utils.escape_html(m.reasoning || '')}
        </div>
        ${blockersHtml}
        <div style="margin-top:14px;font-size:10px;color:#687178;text-align:center;">
          ${m.ai_used
            ? __('Recommendation includes AI analysis from alphax_grc_ai. Use your professional judgment as the final authority.')
            : __('Rule-based recommendation. Install alphax_grc_ai for richer AI-assisted analysis.')}
        </div>
      </div>`;
    const d = new frappe.ui.Dialog({
        title: __('Phase Advance Advisor'),
        size: 'large',
    });
    $(d.body).html(html);
    d.show();
}
