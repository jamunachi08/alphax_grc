// AlphaX GRC v2.0.0 — Annual Audit Calendar
// Year-at-a-glance view + tabular planner + auto-roll-forward.

frappe.pages['grc-annual-audit-calendar'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Annual Audit Calendar'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('+ New audit plan'),
        () => frappe.new_doc('GRC Audit Plan'));
    page.add_menu_item(__('All audit plans'),
        () => frappe.set_route('List', 'GRC Audit Plan'));
    page.add_menu_item(__('Roll recurring audits forward'),
        () => promptRollForward());

    document.getElementById('cal-year-picker').addEventListener('change', (e) => {
        STATE.year = parseInt(e.target.value, 10);
        loadAll();
    });
    document.getElementById('cal-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = {
    year: new Date().getFullYear(),
    client: '',
    clients: [],
    data: null,
};

const MONTH_NAMES = [
    __('Jan'), __('Feb'), __('Mar'), __('Apr'), __('May'), __('Jun'),
    __('Jul'), __('Aug'), __('Sep'), __('Oct'), __('Nov'), __('Dec'),
];

const STATUS_COLORS = {
    'Planned':     { bg: 'rgba(24, 95, 165, 0.10)', fg: '#185FA5' },
    'Scheduled':   { bg: 'rgba(24, 95, 165, 0.10)', fg: '#185FA5' },
    'In Progress': { bg: 'rgba(201, 162, 39, 0.15)', fg: '#7A5C0E' },
    'Completed':   { bg: 'rgba(91, 165, 42, 0.15)',  fg: '#3A6A1A' },
    'Cancelled':   { bg: 'rgba(105, 113, 120, 0.15)', fg: '#3D4248' },
    '':            { bg: 'rgba(105, 113, 120, 0.10)', fg: '#5A5F66' },
};

function buildShell() {
    const currentYear = new Date().getFullYear();
    const years = [currentYear - 1, currentYear, currentYear + 1, currentYear + 2];
    const yearOpts = years.map(y =>
        `<option value="${y}" ${y === currentYear ? 'selected' : ''}>${y}</option>`
    ).join('');

    return `
    <style>
      .cal { max-width: 1400px; margin: 0 auto; }
      .cal-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .cal-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px; min-width: 120px;
      }
      .cal-month-strip {
        display: grid; grid-template-columns: repeat(12, 1fr);
        gap: 6px; margin-top: 12px;
      }
      .cal-month-cell {
        background: white;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        border-radius: 6px;
        padding: 8px;
        min-height: 120px;
      }
      .cal-month-cell .head {
        font-size: 10px; font-weight: 700;
        color: var(--grc-primary, #714B67);
        text-transform: uppercase; letter-spacing: 0.04em;
        margin-bottom: 8px;
      }
      .cal-month-cell .count {
        font-size: 18px; font-weight: 700;
        color: var(--grc-primary, #714B67);
        line-height: 1; margin-bottom: 8px;
      }
      .cal-audit-chip {
        font-size: 10px; padding: 3px 6px;
        border-radius: 3px;
        margin: 3px 0;
        cursor: pointer;
        line-height: 1.2;
      }
      .cal-audit-chip:hover { filter: brightness(0.95); }
      .cal-table {
        width: 100%; border-collapse: collapse; font-size: 12px;
        margin-top: 18px;
      }
      .cal-table th {
        text-align: left; padding: 10px;
        border-bottom: 2px solid var(--grc-secondary, #5B3A52);
        color: var(--grc-primary, #714B67);
        font-weight: 600; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .cal-table td {
        padding: 10px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.08));
        vertical-align: middle;
      }
      .cal-table tr {
        cursor: pointer;
      }
      .cal-table tr:hover { background: rgba(113, 75, 103, 0.04); }
      .cal-status-pill {
        display: inline-block;
        padding: 2px 8px; border-radius: 999px;
        font-size: 10px; font-weight: 600;
      }
      .cal-recurring-badge {
        display: inline-block;
        background: var(--grc-accent, #875A7B);
        color: white;
        padding: 1px 6px; border-radius: 999px;
        font-size: 9px; font-weight: 700;
        margin-left: 6px;
        text-transform: uppercase;
      }
      .cal-empty {
        text-align: center; padding: 28px;
        color: var(--grc-muted, #7A6A78); font-size: 12px;
      }
      .cal-month-cell.empty {
        background: rgba(0,0,0,0.01);
        opacity: 0.6;
      }
    </style>

    <div class="cal">
      <div class="grc-hero">
        <h2>${__('Annual Audit Calendar')}</h2>
        <div class="grc-hero-sub">${__('Year-at-a-glance plus tabular planner. Auto-roll-forward replicates recurring audits to the next year in one click.')}</div>
        <div class="grc-hero-stats" id="cal-stats"></div>
      </div>

      <div class="cal-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Year:')}</label>
        <select id="cal-year-picker">${yearOpts}</select>

        <label style="font-size:12px;color:var(--grc-muted);margin-left:14px;">${__('Client:')}</label>
        <select id="cal-client-picker">
          <option value="">${__('— All clients —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Months')}</h4>
        <div class="cal-month-strip" id="cal-months"></div>
      </div>

      <div class="grc-section">
        <h4>${__('All audits this year')}</h4>
        <div id="cal-table-wrap"></div>
      </div>
    </div>`;
}

function loadClients() {
    return new Promise((resolve) => {
        if (frappe.db && frappe.db.get_list) {
            frappe.db.get_list('GRC Client Profile', {
                fields: ['name', 'client_name'],
                limit: 100,
            }).then((rows) => {
                STATE.clients = rows || [];
                const sel = document.getElementById('cal-client-picker');
                if (sel) {
                    STATE.clients.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.name;
                        opt.textContent = c.client_name || c.name;
                        sel.appendChild(opt);
                    });
                }
                resolve();
            }).catch(() => resolve());
        } else { resolve(); }
    });
}

function loadAll() {
    const args = { year: STATE.year };
    if (STATE.client) args.client = STATE.client;
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_annual_audit_calendar.grc_annual_audit_calendar.get_calendar',
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
    renderMonthStrip();
    renderTable();
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_audits || 0, lbl: __('Total {0}', [STATE.year]) },
        { num: s.completed || 0, lbl: __('Completed') },
        { num: s.in_progress || 0, lbl: __('In progress') },
        { num: s.planned || 0, lbl: __('Planned') },
        { num: s.overdue || 0, lbl: __('Overdue') },
        { num: s.recurring_templates || 0, lbl: __('Recurring') },
    ];
    document.getElementById('cal-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderMonthStrip() {
    const months = STATE.data.months || {};
    const tgt = document.getElementById('cal-months');
    tgt.innerHTML = MONTH_NAMES.map((name, idx) => {
        const monthNum = idx + 1;
        const audits = months[monthNum] || [];
        const cls = audits.length === 0 ? 'cal-month-cell empty' : 'cal-month-cell';
        const chips = audits.slice(0, 4).map(a => {
            const c = STATUS_COLORS[a.status || ''] || STATUS_COLORS[''];
            return `<div class="cal-audit-chip"
                  style="background:${c.bg};color:${c.fg};"
                  onclick="event.stopPropagation();frappe.set_route('Form','GRC Audit Plan','${a.name}')">
              ${frappe.utils.escape_html((a.audit_title || a.name).substring(0, 40))}
            </div>`;
        }).join('');
        const more = audits.length > 4
            ? `<div style="font-size:9px;color:var(--grc-muted);text-align:center;margin-top:4px;">+${audits.length - 4} ${__('more')}</div>`
            : '';
        return `<div class="${cls}">
            <div class="head">${name}</div>
            <div class="count">${audits.length}</div>
            ${chips}${more}
        </div>`;
    }).join('');
}

function renderTable() {
    const plans = STATE.data.plans || [];
    const tgt = document.getElementById('cal-table-wrap');
    if (!plans.length) {
        tgt.innerHTML = `<div class="cal-empty">${__('No audits scheduled for {0}', [STATE.year])}</div>`;
        return;
    }
    tgt.innerHTML = `<table class="cal-table">
      <thead><tr>
        <th style="width:90px">${__('Start')}</th>
        <th>${__('Audit Title')}</th>
        <th style="width:160px">${__('Client')}</th>
        <th style="width:120px">${__('Auditor')}</th>
        <th style="width:90px">${__('Frequency')}</th>
        <th style="width:120px">${__('Status')}</th>
      </tr></thead>
      <tbody>${plans.map(p => {
        const c = STATUS_COLORS[p.status || ''] || STATUS_COLORS[''];
        return `<tr onclick="frappe.set_route('Form','GRC Audit Plan','${p.name}')">
          <td style="font-family:ui-monospace,monospace;font-size:11px;">${p.planned_start_date || '—'}</td>
          <td>
            <div style="font-weight:500;color:var(--grc-primary);">
              ${frappe.utils.escape_html(p.audit_title || p.name)}
              ${p.is_recurring_template ? `<span class="cal-recurring-badge">${__('Recurring')}</span>` : ''}
            </div>
            <div style="font-size:10px;color:var(--grc-muted);margin-top:2px;">
              ${frappe.utils.escape_html(p.linked_framework || '')} · ${frappe.utils.escape_html(p.audit_type || '')}
            </div>
          </td>
          <td style="font-size:11px;">${frappe.utils.escape_html(p.client || '—')}</td>
          <td style="font-size:11px;">${frappe.utils.escape_html(p.lead_auditor || '—')}</td>
          <td style="font-size:11px;">${frappe.utils.escape_html(p.frequency || '—')}</td>
          <td><span class="cal-status-pill" style="background:${c.bg};color:${c.fg};">${frappe.utils.escape_html(p.status || '—')}</span></td>
        </tr>`;
      }).join('')}</tbody>
    </table>`;
}

function promptRollForward() {
    const d = new frappe.ui.Dialog({
        title: __('Roll Recurring Audits Forward'),
        fields: [
            { fieldname: 'source_year', label: __('Source year'),
              fieldtype: 'Int', default: STATE.year, reqd: 1 },
            { fieldname: 'target_year', label: __('Target year'),
              fieldtype: 'Int', default: STATE.year + 1, reqd: 1 },
            { fieldname: 'client', label: __('Client (optional)'),
              fieldtype: 'Link', options: 'GRC Client Profile' },
            { fieldname: 'note', fieldtype: 'HTML',
              options: `<div style="font-size:11px;color:var(--grc-muted);padding:8px;background:rgba(113,75,103,0.05);border-radius:4px;">
                ${__('This creates new GRC Audit Plan records for every recurring template in the source year, dated 12 months ahead. Idempotent — already-rolled-forward audits are skipped.')}
              </div>` },
        ],
        primary_action_label: __('Roll Forward'),
        primary_action: (values) => {
            frappe.call({
                method: 'alphax_grc.alphax_grc.page.grc_annual_audit_calendar.grc_annual_audit_calendar.roll_forward_recurring',
                args: values,
                freeze: true,
                freeze_message: __('Rolling forward…'),
                callback: (r) => {
                    const m = r && r.message;
                    if (m && m.ok) {
                        frappe.show_alert({
                            message: __('Rolled forward {0} audits to {1}. Skipped {2} already-existing. Failed {3}.',
                                [m.rolled_forward, m.target_year, m.skipped_already_exists, m.failed]),
                            indicator: m.failed > 0 ? 'orange' : 'green',
                        });
                        d.hide();
                        // Switch year picker to target_year and reload
                        STATE.year = m.target_year;
                        document.getElementById('cal-year-picker').value = String(m.target_year);
                        loadAll();
                    } else {
                        frappe.show_alert({
                            message: (m && m.error) || __('Roll forward failed'),
                            indicator: 'red',
                        });
                    }
                },
            });
        },
    });
    d.show();
}
