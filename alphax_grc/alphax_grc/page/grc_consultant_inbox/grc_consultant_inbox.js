// AlphaX GRC v1.8.0 — Consultant Cockpit / Inbox
// The unified work queue that opens by default for any GRC consultant.

frappe.pages['grc-consultant-inbox'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Consultant Cockpit'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadInbox(STATE.scope), 'refresh');
    page.add_menu_item(__('+ New engagement'),
        () => frappe.new_doc('GRC Engagement'));
    page.add_menu_item(__('All engagements'),
        () => frappe.set_route('List', 'GRC Engagement'));
    page.add_menu_item(__('All tasks'),
        () => frappe.set_route('List', 'GRC Implementation Task'));

    document.getElementById('inbox-scope-toggle').addEventListener('change', (e) => {
        STATE.scope = e.target.value;
        loadInbox(STATE.scope);
    });

    loadInbox('mine');
};

const STATE = { scope: 'mine', data: null };

function buildShell() {
    return `
    <style>
      .ci { max-width: 1400px; margin: 0 auto; }
      .ci-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .ci-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px;
      }
      .ci-eng-grid {
        display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      }
      .ci-eng-card {
        background: white;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        border-radius: var(--grc-radius-md, 8px);
        padding: 16px;
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
        position: relative;
      }
      .ci-eng-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--grc-shadow-md, 0 2px 8px rgba(0,0,0,.06));
        border-color: var(--grc-secondary, #185FA5);
      }
      .ci-eng-card.overdue {
        border-left: 4px solid #A32D2D;
      }
      .ci-eng-card.draft {
        border-left: 4px solid #C9A227;
      }
      .ci-eng-card .head {
        display: flex; justify-content: space-between; align-items: flex-start;
        gap: 8px; margin-bottom: 8px;
      }
      .ci-eng-card .title {
        font-size: 14px; font-weight: 600; color: var(--grc-primary);
        line-height: 1.3;
      }
      .ci-eng-card .client {
        font-size: 11px; color: var(--grc-muted); margin-top: 2px;
      }
      .ci-eng-card .phase {
        margin: 8px 0 12px; padding: 8px 10px;
        background: rgba(24, 95, 165, 0.06);
        border-radius: 6px;
      }
      .ci-eng-card .phase-num {
        font-size: 10px; color: var(--grc-secondary); font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .ci-eng-card .phase-label {
        font-size: 13px; color: var(--grc-primary); font-weight: 500;
        margin-top: 2px;
      }
      .ci-eng-card .stats {
        display: flex; gap: 12px; flex-wrap: wrap;
        font-size: 11px; color: var(--grc-muted);
      }
      .ci-eng-card .stat {
        display: flex; gap: 4px; align-items: center;
      }
      .ci-eng-card .stat .num {
        font-weight: 700; color: var(--grc-primary);
      }
      .ci-eng-card .stat.alert .num { color: var(--grc-danger); }
      .ci-eng-card .alert-pill {
        position: absolute; top: 12px; right: 12px;
        background: #A32D2D; color: white;
        padding: 2px 7px; border-radius: 999px;
        font-size: 10px; font-weight: 700;
      }
      .ci-task-row {
        display: grid;
        grid-template-columns: 60px 1fr 140px 100px 100px 90px;
        gap: 10px; align-items: center;
        padding: 10px 12px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.08));
        font-size: 12px; cursor: pointer;
        transition: background 0.1s;
      }
      .ci-task-row:hover { background: rgba(24, 95, 165, 0.04); }
      .ci-task-row.overdue { background: rgba(163, 45, 45, 0.04); }
      .ci-task-row .priority-chip {
        padding: 2px 6px; border-radius: 4px;
        font-size: 9px; font-weight: 700; text-align: center;
        text-transform: uppercase;
      }
      .ci-task-row .priority-Critical { background: #FCEBEB; color: #5A0F0F; }
      .ci-task-row .priority-High     { background: #FCEBEB; color: #791F1F; }
      .ci-task-row .priority-Medium   { background: #FAEEDA; color: #6B3F08; }
      .ci-task-row .priority-Low      { background: #EAF3DE; color: #1A3D08; }
      .ci-task-row .due-date {
        font-family: ui-monospace, monospace;
        font-size: 11px;
      }
      .ci-task-row.overdue .due-date {
        color: #A32D2D; font-weight: 600;
      }
      .ci-section-head {
        display: flex; justify-content: space-between; align-items: center;
        margin: 0 0 12px;
      }
      .ci-section-head .count-pill {
        background: var(--grc-secondary, #185FA5); color: white;
        padding: 2px 9px; border-radius: 999px;
        font-size: 11px; font-weight: 700;
      }
      .ci-section-head .count-pill.alert { background: #A32D2D; }
      .ci-empty {
        text-align: center; padding: 28px;
        color: var(--grc-muted); font-size: 12px;
      }
      .ci-failure-row {
        padding: 10px 12px; margin-bottom: 6px;
        background: rgba(163, 45, 45, 0.04);
        border-left: 3px solid #A32D2D;
        border-radius: 0 6px 6px 0;
        font-size: 12px;
      }
      .ci-failure-row .head {
        display: flex; justify-content: space-between;
        margin-bottom: 4px;
      }
      .ci-failure-row .meta {
        font-size: 10px; color: var(--grc-muted);
      }

      /* v1.9.3 — Orientation rail (How AlphaX GRC Works) */
      .ci-orientation {
        margin: 0 0 18px;
        padding: 22px 24px 24px;
        background: var(--grc-card-bg, #FFFFFF);
        border: 1px solid var(--grc-border, rgba(15, 31, 64, 0.08));
        border-radius: var(--grc-radius-lg, 12px);
      }
      .ci-orientation .head {
        font-size: 13px; font-weight: 700;
        color: var(--grc-primary, #714B67);
        text-transform: uppercase; letter-spacing: 0.06em;
        text-align: center; margin: 0 0 4px;
      }
      .ci-orientation .sub {
        font-size: 11px; color: var(--grc-muted, #7A6A78);
        text-align: center; margin: 0 0 22px;
      }
      .ci-orientation .rail {
        display: flex; align-items: flex-start;
        justify-content: space-between;
        position: relative; padding: 0 4%;
      }
      .ci-orientation .rail::before {
        content: ''; position: absolute;
        top: 22px; left: 9%; right: 9%;
        height: 1px;
        background: var(--grc-accent, #875A7B);
        opacity: 0.4;
        z-index: 0;
      }
      .ci-orientation .step {
        flex: 1; text-align: center;
        position: relative; z-index: 1;
        cursor: pointer;
        transition: transform 0.15s ease;
        padding: 0 6px;
      }
      .ci-orientation .step:hover {
        transform: translateY(-2px);
      }
      .ci-orientation .step:hover .circle {
        background: var(--grc-primary, #714B67);
        color: white;
        border-color: var(--grc-primary, #714B67);
      }
      .ci-orientation .step:hover .title {
        text-decoration: underline;
      }
      .ci-orientation .circle {
        width: 44px; height: 44px;
        margin: 0 auto 12px;
        background: var(--grc-card-bg, #FFFFFF);
        border: 2px solid var(--grc-accent, #875A7B);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 700;
        color: var(--grc-primary, #714B67);
        font-family: ui-monospace, 'SF Mono', monospace;
        transition: all 0.15s ease;
      }
      .ci-orientation .title {
        font-size: 12px; font-weight: 600;
        color: var(--grc-primary, #714B67);
        margin: 0 0 4px;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .ci-orientation .desc {
        font-size: 11px; color: var(--grc-muted, #7A6A78);
        line-height: 1.4;
        max-width: 220px; margin: 0 auto;
      }
      .ci-orientation .count-badge {
        display: inline-block;
        background: var(--grc-primary, #714B67); color: white;
        border-radius: 999px;
        padding: 1px 7px;
        font-size: 9px; font-weight: 700;
        margin-left: 5px;
        vertical-align: middle;
      }
    </style>

    <div class="ci">
      <div class="grc-hero">
        <h2>${__('Consultant Cockpit')}</h2>
        <div class="grc-hero-sub">${__('Your unified work queue across every engagement. Sorted by urgency. One click to action.')}</div>
        <div class="grc-hero-stats" id="ci-stats"></div>
      </div>

      <div class="ci-orientation">
        <div class="head">${__('How AlphaX GRC Works')}</div>
        <div class="sub">${__('Four steps. Click any step to drill into the document level — no hunting.')}</div>
        <div class="rail">
          <div class="step" onclick="window.__ciNav('client_profile')">
            <div class="circle">01</div>
            <div class="title">${__('Onboard the client')}</div>
            <div class="desc">${__('Capture profile, sector, scope, and risk appetite')}<span id="ci-step-client-count"></span></div>
          </div>
          <div class="step" onclick="window.__ciNav('engagement')">
            <div class="circle">02</div>
            <div class="title">${__('Run the engagement')}</div>
            <div class="desc">${__('Lifecycle phases drive every step from kickoff to closure')}<span id="ci-step-engagement-count"></span></div>
          </div>
          <div class="step" onclick="window.__ciNav('monitoring')">
            <div class="circle">03</div>
            <div class="title">${__('Track posture live')}</div>
            <div class="desc">${__('Continuous control monitoring across all frameworks')}<span id="ci-step-monitoring-count"></span></div>
          </div>
          <div class="step" onclick="window.__ciNav('board')">
            <div class="circle">04</div>
            <div class="title">${__('Deliver to the board')}</div>
            <div class="desc">${__('Enterprise risk summary and inspection-ready audit pack')}<span id="ci-step-board-count"></span></div>
          </div>
        </div>
      </div>

      <div class="ci-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Showing:')}</label>
        <select id="inbox-scope-toggle">
          <option value="mine">${__('My engagements only')}</option>
          <option value="all">${__('All engagements (firm-wide)')}</option>
        </select>
      </div>

      <div class="grc-section">
        <div class="ci-section-head">
          <h4>${__('Active engagements')}</h4>
          <span class="count-pill" id="ci-eng-count">0</span>
        </div>
        <div class="ci-eng-grid" id="ci-engagements"></div>
      </div>

      <div class="grc-section">
        <div class="ci-section-head">
          <h4>${__('Overdue tasks')}</h4>
          <span class="count-pill alert" id="ci-overdue-count">0</span>
        </div>
        <div id="ci-overdue-tasks"></div>
      </div>

      <div class="grc-section">
        <div class="ci-section-head">
          <h4>${__('Due in next 7 days')}</h4>
          <span class="count-pill" id="ci-soon-count">0</span>
        </div>
        <div id="ci-soon-tasks"></div>
      </div>

      <div class="grc-section">
        <div class="ci-section-head">
          <h4>${__('Recent control monitoring failures')}</h4>
          <span class="count-pill" id="ci-fail-count">0</span>
        </div>
        <div id="ci-failures"></div>
      </div>
    </div>`;
}

function loadInbox(scope) {
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_consultant_inbox.grc_consultant_inbox.get_inbox',
        args: { scope },
        callback: (r) => {
            STATE.data = (r && r.message) || null;
            render();
        },
    });
}

function render() {
    if (!STATE.data) return;
    const d = STATE.data;
    renderHeroStats(d);
    renderEngagements(d.engagements || []);
    renderTasks('ci-overdue-tasks', d.tasks_overdue || [], true);
    renderTasks('ci-soon-tasks', d.tasks_due_soon || [], false);
    renderFailures(d.rule_failures || []);
    document.getElementById('ci-eng-count').textContent = (d.engagements || []).length;
    document.getElementById('ci-overdue-count').textContent = (d.tasks_overdue || []).length;
    document.getElementById('ci-soon-count').textContent = (d.tasks_due_soon || []).length;
    document.getElementById('ci-fail-count').textContent = (d.rule_failures || []).length;
    // v1.9.3 — orientation rail count badges
    try { window.__ciUpdateOrientationCounts(); } catch (e) {}
}

function renderHeroStats(d) {
    const s = d.summary || {};
    const stats = [
        { num: s.total_engagements || 0, lbl: __('Engagements') },
        { num: s.overdue_engagements || 0, lbl: __('Overdue phases') },
        { num: s.tasks_overdue || 0, lbl: __('Tasks overdue') },
        { num: s.tasks_due_soon || 0, lbl: __('Due this week') },
        { num: s.open_findings || 0, lbl: __('Findings open') },
        { num: s.rule_failures_7d || 0, lbl: __('Rule fails (7d)') },
    ];
    document.getElementById('ci-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderEngagements(engs) {
    const tgt = document.getElementById('ci-engagements');
    if (!engs.length) {
        tgt.innerHTML = `<div class="ci-empty">${__('No active engagements. Click "+ New engagement" in the menu to start one.')}</div>`;
        return;
    }
    tgt.innerHTML = engs.map(e => {
        const isOverdue = e.is_overdue;
        const isDraft = e.engagement_status === 'Draft';
        let cls = '';
        if (isOverdue) cls = 'overdue';
        else if (isDraft) cls = 'draft';
        const alertCount = (e.tasks_overdue_count || 0) + (e.evidence_rule_failures || 0);
        const phaseInfo = e.current_phase_number
            ? `<div class="phase-num">${__('Phase')} ${e.current_phase_number}${e.days_in_current_phase ? ' · ' + e.days_in_current_phase + 'd' : ''}</div>
               <div class="phase-label">${frappe.utils.escape_html(e.current_phase_label || '')}</div>`
            : `<div class="phase-num">${__('Status')}</div>
               <div class="phase-label">${frappe.utils.escape_html(e.engagement_status)}${isDraft ? ' — ' + __('click to kickoff') : ''}</div>`;
        return `<div class="ci-eng-card ${cls}" onclick="frappe.set_route('Form','GRC Engagement','${e.name}')">
            ${alertCount > 0 ? `<div class="alert-pill">${alertCount}</div>` : ''}
            <div class="head">
                <div>
                    <div class="title">${frappe.utils.escape_html(e.engagement_title || e.name)}</div>
                    <div class="client">${frappe.utils.escape_html(e.client || '')} · ${frappe.utils.escape_html(e.engagement_type || '')}</div>
                </div>
            </div>
            <div class="phase">${phaseInfo}</div>
            <div class="stats">
                <span class="stat ${e.open_findings_count > 0 ? 'alert' : ''}"><span class="num">${e.open_findings_count || 0}</span>${__('findings')}</span>
                <span class="stat ${e.high_risks_count > 0 ? 'alert' : ''}"><span class="num">${e.high_risks_count || 0}</span>${__('high risks')}</span>
                <span class="stat"><span class="num">${e.tasks_pending_count || 0}</span>${__('tasks')}</span>
                <span class="stat ${e.tasks_overdue_count > 0 ? 'alert' : ''}"><span class="num">${e.tasks_overdue_count || 0}</span>${__('overdue')}</span>
            </div>
        </div>`;
    }).join('');
}

function renderTasks(targetId, tasks, isOverdue) {
    const tgt = document.getElementById(targetId);
    if (!tasks.length) {
        tgt.innerHTML = `<div class="ci-empty">${isOverdue ? __('No overdue tasks 🎉') : __('No tasks due this week')}</div>`;
        return;
    }
    tgt.innerHTML = tasks.map(t => {
        const dueText = t.due_date ? frappe.datetime.str_to_user(t.due_date) : '—';
        return `<div class="ci-task-row ${isOverdue ? 'overdue' : ''}"
                 onclick="frappe.set_route('Form','GRC Implementation Task','${t.name}')">
            <span class="priority-chip priority-${t.priority || 'Medium'}">${(t.priority || 'Med').substring(0,3)}</span>
            <div>
                <div style="font-weight:500;color:var(--grc-primary);">${frappe.utils.escape_html(t.task_title)}</div>
                <div style="font-size:10px;color:var(--grc-muted);margin-top:2px;">
                    ${frappe.utils.escape_html(t.client || '')} · ${frappe.utils.escape_html(t.framework || '')} · ${frappe.utils.escape_html(t.control_reference || '')}
                </div>
            </div>
            <span style="color:var(--grc-muted);">${frappe.utils.escape_html(t.responsible_team || '—')}</span>
            <span style="color:var(--grc-muted);">${frappe.utils.escape_html(t.category || '—')}</span>
            <span class="due-date">${dueText}</span>
            <span style="color:var(--grc-muted);">${frappe.utils.escape_html(t.status || '')}</span>
        </div>`;
    }).join('');
}

function renderFailures(failures) {
    const tgt = document.getElementById('ci-failures');
    if (!failures.length) {
        tgt.innerHTML = `<div class="ci-empty">${__('No control monitoring failures in the last 7 days 🎉')}</div>`;
        return;
    }
    tgt.innerHTML = failures.map(f => {
        const when = f.evaluated_at ? frappe.datetime.comment_when(f.evaluated_at) : '';
        return `<div class="ci-failure-row" onclick="frappe.set_route('Form','GRC Evidence Rule Evaluation','${f.name}')" style="cursor:pointer">
            <div class="head">
                <strong style="color:#791F1F;">${frappe.utils.escape_html(f.rule || '')}</strong>
                <span style="font-size:10px;color:var(--grc-muted);">${when}</span>
            </div>
            <div class="meta">
                ${frappe.utils.escape_html(f.framework || '')} · ${frappe.utils.escape_html(f.control_reference || '')} ·
                ${f.fail_count} ${__('failure(s)')} · ${__('client:')} ${frappe.utils.escape_html(f.client || '')}
                ${f.finding_created ? ' · <span style="color:#A32D2D">' + __('Finding created') + '</span>' : ''}
            </div>
        </div>`;
    }).join('');
}

// v1.9.3 — orientation rail navigation
// Maps each step to the right route. Smart defaults: if the user already
// has clients/engagements, jump to the list; otherwise jump to "+ new".
window.__ciNav = function(target) {
    const data = STATE.data || {};
    const summary = data.summary || {};

    if (target === 'client_profile') {
        // Step 1 — Onboard the client
        // If clients exist, show the list. If none, jump straight to "new"
        // so the consultant doesn't have to find the New button.
        if ((summary.total_clients || 0) > 0) {
            frappe.set_route('List', 'GRC Client Profile');
        } else {
            frappe.new_doc('GRC Client Profile');
        }
        return;
    }

    if (target === 'engagement') {
        // Step 2 — Run the engagement
        if ((summary.total_engagements || 0) > 0) {
            frappe.set_route('List', 'GRC Engagement');
        } else {
            frappe.new_doc('GRC Engagement');
        }
        return;
    }

    if (target === 'monitoring') {
        // Step 3 — Track posture live
        // CCM dashboard is the right page. If it doesn't load, fall back
        // to the Evidence Rule list.
        try {
            frappe.set_route('grc-ccm-dashboard');
        } catch (e) {
            frappe.set_route('List', 'GRC Evidence Rule');
        }
        return;
    }

    if (target === 'board') {
        // Step 4 — Deliver to the board
        try {
            frappe.set_route('grc-enterprise-risk-summary');
        } catch (e) {
            frappe.set_route('List', 'GRC Risk Register');
        }
        return;
    }
};

// v1.9.3 — populate live count badges next to step descriptions, called
// after STATE.data loads. Fails silently if the elements don't exist
// (e.g. the orientation rail is hidden by CSS in some context).
window.__ciUpdateOrientationCounts = function() {
    const data = STATE.data || {};
    const summary = data.summary || {};

    function setCount(id, n, label) {
        const el = document.getElementById(id);
        if (!el) return;
        if (n && n > 0) {
            el.innerHTML = `<span class="count-badge">${n}</span>`;
            el.title = label || '';
        } else {
            el.innerHTML = '';
        }
    }

    // Step 1: count of clients
    setCount('ci-step-client-count', summary.total_clients || 0,
             __('clients onboarded'));
    // Step 2: active engagements
    setCount('ci-step-engagement-count', summary.total_engagements || 0,
             __('active engagements'));
    // Step 3: rule failures last 7d (drives attention to step 3 when failing)
    setCount('ci-step-monitoring-count', summary.rule_failures_7d || 0,
             __('rule failures (7d)'));
    // Step 4: open critical+high findings (signals "board needs to know")
    setCount('ci-step-board-count', summary.open_findings || 0,
             __('open findings'));
};
