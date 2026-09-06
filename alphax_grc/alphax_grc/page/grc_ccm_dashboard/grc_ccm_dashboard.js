// AlphaX GRC v1.7.0 — Continuous Control Monitoring Dashboard

frappe.pages['grc-ccm-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Continuous Control Monitoring'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('+ New Evidence Rule'),
        () => frappe.new_doc('GRC Evidence Rule'));
    page.add_menu_item(__('Browse all rules'),
        () => frappe.set_route('List', 'GRC Evidence Rule'));
    page.add_menu_item(__('Browse evaluations'),
        () => frappe.set_route('List', 'GRC Evidence Rule Evaluation'));

    document.getElementById('ccm-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

function buildShell() {
    return `
    <style>
      .ccm { max-width: 1400px; margin: 0 auto; }
      .ccm-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .ccm-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px; min-width: 240px;
      }
      .ccm-framework-grid {
        display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      }
      .ccm-fw-card {
        padding: 14px; border-radius: var(--grc-radius-md, 8px);
        background: white; border: 1px solid var(--grc-border, rgba(0,0,0,.08));
      }
      .ccm-fw-card .name {
        font-size: 12px; font-weight: 600; text-transform: uppercase;
        letter-spacing: .04em; color: var(--grc-primary, #0F1F40);
        margin-bottom: 8px;
      }
      .ccm-fw-bar {
        display: flex; height: 12px; border-radius: 6px;
        overflow: hidden; background: rgba(0,0,0,0.06); margin-bottom: 8px;
      }
      .ccm-fw-bar > div { height: 100%; }
      .ccm-fw-stats {
        display: flex; gap: 12px; font-size: 11px; color: var(--grc-muted);
      }
      .ccm-fw-stats span { display: flex; align-items: center; gap: 4px; }
      .ccm-fw-stats .dot {
        width: 8px; height: 8px; border-radius: 50%;
      }
      .ccm-rules-table {
        width: 100%; border-collapse: collapse; font-size: 13px;
      }
      .ccm-rules-table th {
        text-align: left; padding: 10px;
        border-bottom: 2px solid var(--grc-secondary, #185FA5);
        color: var(--grc-primary, #0F1F40);
        font-weight: 600; font-size: 11px;
        text-transform: uppercase; letter-spacing: .04em;
      }
      .ccm-rules-table td {
        padding: 10px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.08));
        vertical-align: middle;
      }
      .ccm-rules-table tr:hover {
        background: rgba(24, 95, 165, 0.04);
      }
      .ccm-pass-bar {
        display: inline-block; width: 60px; height: 8px; border-radius: 4px;
        background: rgba(0,0,0,.06); overflow: hidden;
        vertical-align: middle; margin-right: 8px;
      }
      .ccm-pass-bar > div { height: 100%; }
      .ccm-priority {
        display: inline-block; padding: 2px 6px; border-radius: 4px;
        font-size: 10px; font-weight: 600; text-transform: uppercase;
      }
      .ccm-priority-High   { background: #FCEBEB; color: #791F1F; }
      .ccm-priority-Medium { background: #FAEEDA; color: #854F0B; }
      .ccm-priority-Low    { background: #EAF3DE; color: #27500A; }
      .ccm-failure-card {
        background: #FCF5F5; border-left: 4px solid #A32D2D;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px; margin-bottom: 8px;
      }
      .ccm-failure-card .head {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px;
      }
      .ccm-failure-card .name {
        font-weight: 600; color: #791F1F; font-size: 13px;
      }
      .ccm-failure-card .when {
        font-size: 11px; color: var(--grc-muted);
      }
      .ccm-failure-card .meta {
        font-size: 11px; color: var(--grc-muted);
      }
      .ccm-empty {
        text-align: center; padding: 32px;
        color: var(--grc-muted, #687178); font-size: 12px;
      }
      .ccm-eval-btn {
        padding: 4px 10px; border-radius: 6px;
        background: var(--grc-secondary, #185FA5); color: white;
        font-size: 11px; font-weight: 500; border: none; cursor: pointer;
      }
      .ccm-eval-btn:hover { background: var(--grc-primary, #0F1F40); }
    </style>

    <div class="ccm">
      <div class="grc-hero">
        <h2>${__('Continuous Control Monitoring')}</h2>
        <div class="grc-hero-sub">${__('Live compliance posture from ERPNext data · evidence rules evaluate on every save · daily scheduler re-tests every active rule')}</div>
        <div class="grc-hero-stats" id="ccm-stats"></div>
      </div>

      <div class="ccm-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client filter:')}</label>
        <select id="ccm-client-picker">
          <option value="">${__('— All clients (firm-wide) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('By framework')}</h4>
        <div class="ccm-framework-grid" id="ccm-frameworks"></div>
      </div>

      <div class="grc-section">
        <h4>${__('Recent failures')}</h4>
        <div id="ccm-failures"></div>
      </div>

      <div class="grc-section">
        <h4>${__('All active rules')}</h4>
        <div id="ccm-rules"></div>
      </div>
    </div>`;
}

function loadClients() {
    return new Promise((resolve) => {
        if (frappe.db && frappe.db.get_list) {
            frappe.db.get_list('GRC Client Profile', {
                fields: ['name', 'client_name', 'country'],
                limit: 100,
            }).then((rows) => {
                STATE.clients = rows || [];
                const sel = document.getElementById('ccm-client-picker');
                if (sel) {
                    STATE.clients.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.name;
                        opt.textContent = `${c.client_name || c.name}${c.country ? ' — ' + c.country : ''}`;
                        sel.appendChild(opt);
                    });
                }
                resolve();
            }).catch(() => resolve());
        } else { resolve(); }
    });
}

function loadAll() {
    const args = STATE.client ? { client: STATE.client } : {};
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_ccm_dashboard.grc_ccm_dashboard.get_ccm_dashboard',
        args,
        callback: (r) => {
            STATE.data = (r && r.message) || null;
            render();
        },
    });
}

function render() {
    if (!STATE.data) return;
    renderHero();
    renderFrameworks();
    renderFailures();
    renderRules();
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_rules || 0, lbl: __('Active rules') },
        { num: s.failing_rules || 0, lbl: __('Currently failing') },
        { num: s.perfect_rules || 0, lbl: __('Perfect score') },
        { num: s.never_evaluated || 0, lbl: __('Untested') },
        { num: (s.avg_pass_rate || 0) + '%', lbl: __('Avg pass rate') },
    ];
    document.getElementById('ccm-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderFrameworks() {
    const fwData = STATE.data.framework_breakdown || {};
    const tgt = document.getElementById('ccm-frameworks');
    const entries = Object.entries(fwData);
    if (!entries.length) {
        tgt.innerHTML = `<div class="ccm-empty">${__('No active rules. Create one to get started.')}</div>`;
        return;
    }
    tgt.innerHTML = entries.map(([fw, d]) => {
        const total = d.total || 1;
        const passingPct = (d.passing / total * 100);
        const failingPct = (d.failing / total * 100);
        const untestedPct = (d.untested / total * 100);
        return `<div class="ccm-fw-card">
            <div class="name">${frappe.utils.escape_html(fw)}</div>
            <div class="ccm-fw-bar">
                <div style="width:${passingPct}%; background:#5BA52A"></div>
                <div style="width:${failingPct}%; background:#D44C4C"></div>
                <div style="width:${untestedPct}%; background:#9C9C9C"></div>
            </div>
            <div class="ccm-fw-stats">
                <span><span class="dot" style="background:#5BA52A"></span>${d.passing} ${__('pass')}</span>
                <span><span class="dot" style="background:#D44C4C"></span>${d.failing} ${__('fail')}</span>
                <span><span class="dot" style="background:#9C9C9C"></span>${d.untested} ${__('untested')}</span>
            </div>
        </div>`;
    }).join('');
}

function renderFailures() {
    const failures = STATE.data.recent_failures || [];
    const tgt = document.getElementById('ccm-failures');
    if (!failures.length) {
        tgt.innerHTML = `<div class="ccm-empty">${__('No recent failures — all evaluated rules are passing 🎉')}</div>`;
        return;
    }
    tgt.innerHTML = failures.map(f => {
        const when = f.evaluated_at
            ? frappe.datetime.comment_when(f.evaluated_at)
            : '';
        return `<div class="ccm-failure-card" onclick="frappe.set_route('Form','GRC Evidence Rule Evaluation','${f.name}')" style="cursor:pointer">
            <div class="head">
                <div class="name">${frappe.utils.escape_html(f.rule)}</div>
                <div class="when">${when}</div>
            </div>
            <div class="meta">
                <strong>${frappe.utils.escape_html(f.framework || '')}</strong>
                · ${frappe.utils.escape_html(f.control_reference || '')}
                · ${f.fail_count} ${__('record(s) failed')}
                · ${__('triggered by')} ${frappe.utils.escape_html(f.trigger_type || '')}
                ${f.finding_created ? '· <span style="color:#A32D2D">' + __('Finding created: ') + f.finding_created + '</span>' : ''}
            </div>
        </div>`;
    }).join('');
}

function renderRules() {
    const rules = STATE.data.rules || [];
    const tgt = document.getElementById('ccm-rules');
    if (!rules.length) {
        tgt.innerHTML = `<div class="ccm-empty">${__('No rules. Click + New Evidence Rule to define one.')}</div>`;
        return;
    }
    tgt.innerHTML = `<table class="ccm-rules-table">
        <thead><tr>
            <th style="width:80px">${__('Priority')}</th>
            <th>${__('Rule')}</th>
            <th style="width:140px">${__('Framework')}</th>
            <th style="width:80px">${__('Control')}</th>
            <th style="width:160px">${__('Source')}</th>
            <th style="width:160px">${__('Pass rate')}</th>
            <th style="width:140px">${__('Last evaluated')}</th>
            <th style="width:90px"></th>
        </tr></thead>
        <tbody>${rules.map(r => {
            const passColor = (r.last_pass_rate >= 95) ? '#5BA52A'
                            : (r.last_pass_rate >= 70) ? '#E5A82E' : '#D44C4C';
            const lastEval = r.last_evaluated
                ? frappe.datetime.comment_when(r.last_evaluated)
                : `<em style="color:var(--grc-muted)">${__('Never')}</em>`;
            return `<tr>
                <td><span class="ccm-priority ccm-priority-${r.rule_priority || 'Medium'}">${r.rule_priority || 'Med'}</span></td>
                <td>
                    <a href="#" onclick="frappe.set_route('Form','GRC Evidence Rule','${r.name}'); return false"
                       style="color:var(--grc-primary);font-weight:500;">
                        ${frappe.utils.escape_html(r.rule_name)}
                    </a>
                </td>
                <td style="font-size:11px;color:var(--grc-muted)">${frappe.utils.escape_html(r.framework || '')}</td>
                <td style="font-family:ui-monospace,monospace;font-size:11px">${frappe.utils.escape_html(r.control_reference || '')}</td>
                <td style="font-size:11px;color:var(--grc-muted)">${frappe.utils.escape_html(r.source_doctype || '')}</td>
                <td>
                    ${r.last_evaluated ? `
                    <span class="ccm-pass-bar"><div style="width:${r.last_pass_rate || 0}%; background:${passColor}"></div></span>
                    <span style="font-weight:600;color:${passColor};font-size:12px;">${(r.last_pass_rate || 0).toFixed(0)}%</span>
                    <span style="font-size:10px;color:var(--grc-muted);">(${r.last_pass_count || 0}/${(r.last_pass_count || 0) + (r.last_fail_count || 0)})</span>
                    ` : '<em style="color:var(--grc-muted);font-size:11px">' + __('Not yet evaluated') + '</em>'}
                </td>
                <td style="font-size:11px;color:var(--grc-muted)">${lastEval}</td>
                <td><button class="ccm-eval-btn" onclick="window.__ccmEvalNow('${r.name}')">${__('Run')}</button></td>
            </tr>`;
        }).join('')}</tbody>
    </table>`;
}

window.__ccmEvalNow = function(rule_name) {
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_ccm_dashboard.grc_ccm_dashboard.evaluate_now',
        args: { rule_name },
        freeze: true,
        freeze_message: __('Evaluating…'),
        callback: (r) => {
            const m = r && r.message;
            if (m && m.ok) {
                frappe.show_alert({
                    message: __('Evaluation complete: {0} pass, {1} fail ({2}%)',
                                [m.pass_count, m.fail_count, m.pass_rate.toFixed(0)]),
                    indicator: m.fail_count === 0 ? 'green' : 'red',
                });
                loadAll();
            } else {
                frappe.show_alert({ message: (m && m.message) || __('Evaluation failed'), indicator: 'orange' });
            }
        },
    });
};
