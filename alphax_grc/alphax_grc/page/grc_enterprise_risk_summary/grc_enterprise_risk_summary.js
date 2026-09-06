// AlphaX GRC v1.9.0 — Enterprise Risk Summary
// Board-level rollup. Designed to be printable as a one-pager.

frappe.pages['grc-enterprise-risk-summary'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Enterprise Risk Summary'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Print this page'), () => window.print());
    page.add_menu_item(__('All risks'),
        () => frappe.set_route('List', 'GRC Risk Register'));
    page.add_menu_item(__('Edit appetite'), () => {
        if (STATE.client) {
            frappe.set_route('Form', 'GRC Client Profile', STATE.client);
        } else {
            frappe.show_alert({ message: __('Pick a client first'), indicator: 'orange' });
        }
    });

    document.getElementById('ers-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

const APPETITE_COLORS = {
    'None': { bg: '#791F1F', fg: 'white' },
    'Low': { bg: '#C25C1F', fg: 'white' },
    'Moderate': { bg: '#854F0B', fg: 'white' },
    'High': { bg: '#5BA52A', fg: 'white' },
    '': { bg: '#9C9C9C', fg: 'white' },
};

function buildShell() {
    return `
    <style>
      .ers { max-width: 1200px; margin: 0 auto; }
      .ers-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .ers-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px; min-width: 240px;
      }
      .ers-statement {
        padding: 14px 16px;
        background: rgba(201, 162, 39, 0.08);
        border-left: 4px solid #C9A227;
        border-radius: 0 8px 8px 0;
        margin-bottom: 18px;
        font-size: 13px;
        font-style: italic;
        color: var(--grc-primary);
      }
      .ers-cat-grid {
        display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      }
      .ers-cat-card {
        padding: 14px;
        background: white;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        border-radius: 8px;
        position: relative;
      }
      .ers-cat-card.breach {
        border-left: 4px solid #A32D2D;
        background: rgba(163, 45, 45, 0.03);
      }
      .ers-cat-card .head {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 8px;
      }
      .ers-cat-card .name {
        font-size: 13px; font-weight: 600; color: var(--grc-primary);
      }
      .ers-cat-card .appetite-pill {
        padding: 2px 8px; border-radius: 999px;
        font-size: 9px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .ers-cat-card .breach-flag {
        position: absolute; top: 8px; right: 8px;
        font-size: 10px; color: #A32D2D; font-weight: 700;
      }
      .ers-cat-card .stripe {
        display: flex; height: 8px; border-radius: 4px;
        overflow: hidden; margin: 8px 0;
        background: rgba(0,0,0,0.04);
      }
      .ers-cat-card .stripe > div { height: 100%; }
      .ers-cat-card .counts {
        display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 4px; font-size: 10px; margin-top: 8px;
      }
      .ers-cat-card .count {
        text-align: center; padding: 4px;
        border-radius: 4px;
      }
      .ers-cat-card .count.crit { background: #FCEBEB; color: #5A0F0F; }
      .ers-cat-card .count.high { background: #FFE8D6; color: #8C3F0F; }
      .ers-cat-card .count.med  { background: #FAEEDA; color: #6B3F08; }
      .ers-cat-card .count.low  { background: #EAF3DE; color: #1A3D08; }
      .ers-cat-card .count .num { font-size: 14px; font-weight: 700; display: block; }
      .ers-cat-card .count .lbl {
        text-transform: uppercase; letter-spacing: 0.04em;
        font-size: 8px; opacity: 0.85;
      }
      .ers-risks-table {
        width: 100%; border-collapse: collapse; font-size: 12px;
      }
      .ers-risks-table th {
        text-align: left; padding: 8px 10px;
        border-bottom: 2px solid var(--grc-secondary, #185FA5);
        color: var(--grc-primary);
        font-weight: 600; font-size: 10px;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .ers-risks-table td {
        padding: 8px 10px;
        border-bottom: 1px solid var(--grc-border);
      }
      .ers-risks-table tr:hover { background: rgba(24, 95, 165, 0.04); cursor: pointer; }
      .ers-empty {
        text-align: center; padding: 28px;
        color: var(--grc-muted); font-size: 12px;
      }
      .ers-rating-chip {
        padding: 2px 8px; border-radius: 999px;
        font-size: 10px; font-weight: 600;
      }
      .ers-rating-Critical { background: #FCEBEB; color: #5A0F0F; }
      .ers-rating-High     { background: #FFE8D6; color: #8C3F0F; }
      .ers-rating-Medium   { background: #FAEEDA; color: #6B3F08; }
      .ers-rating-Low      { background: #EAF3DE; color: #1A3D08; }
      @media print {
        .page-head, .ers-toolbar { display: none; }
        .ers { max-width: 100%; }
        .grc-hero { page-break-inside: avoid; }
        .grc-section { page-break-inside: avoid; }
      }
    </style>

    <div class="ers">
      <div class="grc-hero">
        <h2>${__('Enterprise Risk Summary')}</h2>
        <div class="grc-hero-sub">${__('Board / audit-committee one-pager. Risk count by category vs board-approved appetite. Print as a quarterly board pack.')}</div>
        <div class="grc-hero-stats" id="ers-stats"></div>
      </div>

      <div class="ers-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="ers-client-picker">
          <option value="">${__('— Firm-wide (all clients) —')}</option>
        </select>
      </div>

      <div id="ers-statement-wrap"></div>

      <div class="grc-section">
        <h4>${__('Risk by category vs appetite')}</h4>
        <div class="ers-cat-grid" id="ers-categories"></div>
      </div>

      <div class="grc-section">
        <h4>${__('Top 10 open risks by severity')}</h4>
        <div id="ers-top-risks"></div>
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
                const sel = document.getElementById('ers-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_enterprise_risk_summary.grc_enterprise_risk_summary.get_summary',
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
    renderStatement();
    renderCategories();
    renderTopRisks();
}

function renderHero() {
    const t = STATE.data.totals || {};
    const stats = [
        { num: t.total_risks || 0, lbl: __('Total risks') },
        { num: t.open_risks || 0, lbl: __('Open') },
        { num: t.critical_risks || 0, lbl: __('Critical') },
        { num: t.high_risks || 0, lbl: __('High') },
        { num: t.tolerance_breaches || 0, lbl: __('Appetite breaches') },
        { num: t.uncategorized || 0, lbl: __('Uncategorized') },
    ];
    document.getElementById('ers-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderStatement() {
    const tgt = document.getElementById('ers-statement-wrap');
    const stmt = STATE.data.appetite_statement;
    if (stmt && stmt.trim()) {
        tgt.innerHTML = `<div class="ers-statement">"${frappe.utils.escape_html(stmt)}"</div>`;
    } else {
        tgt.innerHTML = '';
    }
}

function renderCategories() {
    const cats = (STATE.data.categories || []).filter(c => c.total > 0 || c.appetite);
    const tgt = document.getElementById('ers-categories');
    if (!cats.length) {
        tgt.innerHTML = `<div class="ers-empty">${__('No risks recorded yet for this client')}</div>`;
        return;
    }
    tgt.innerHTML = cats.map(c => {
        const total = c.total || 1;
        const critPct = (c.Critical / total * 100).toFixed(1);
        const highPct = (c.High / total * 100).toFixed(1);
        const medPct = (c.Medium / total * 100).toFixed(1);
        const lowPct = (c.Low / total * 100).toFixed(1);
        const appCol = APPETITE_COLORS[c.appetite || ''] || APPETITE_COLORS[''];
        return `<div class="ers-cat-card ${c.tolerance_breach ? 'breach' : ''}">
            ${c.tolerance_breach ? `<div class="breach-flag">⚠ ${__('BREACH')}</div>` : ''}
            <div class="head">
                <div class="name">${frappe.utils.escape_html(c.category)}</div>
            </div>
            <div style="display:flex;gap:6px;align-items:center;margin-bottom:6px;">
                <span style="font-size:9px;text-transform:uppercase;color:var(--grc-muted);">${__('Appetite:')}</span>
                <span class="appetite-pill" style="background:${appCol.bg};color:${appCol.fg};">
                    ${frappe.utils.escape_html(c.appetite || '—')}
                </span>
            </div>
            ${c.total > 0 ? `
                <div class="stripe">
                    <div style="width:${critPct}%;background:#791F1F"></div>
                    <div style="width:${highPct}%;background:#C25C1F"></div>
                    <div style="width:${medPct}%;background:#E5A82E"></div>
                    <div style="width:${lowPct}%;background:#5BA52A"></div>
                </div>
                <div class="counts">
                    <div class="count crit"><span class="num">${c.Critical}</span><span class="lbl">${__('Crit')}</span></div>
                    <div class="count high"><span class="num">${c.High}</span><span class="lbl">${__('High')}</span></div>
                    <div class="count med"><span class="num">${c.Medium}</span><span class="lbl">${__('Med')}</span></div>
                    <div class="count low"><span class="num">${c.Low}</span><span class="lbl">${__('Low')}</span></div>
                </div>
                <div style="font-size:10px;color:var(--grc-muted);margin-top:6px;">
                    ${c.open} ${__('open')} · ${c.total} ${__('total')}
                </div>
            ` : `<div style="font-size:11px;color:var(--grc-muted);">${__('No risks in this category')}</div>`}
        </div>`;
    }).join('');
}

function renderTopRisks() {
    const risks = STATE.data.top_open_risks || [];
    const tgt = document.getElementById('ers-top-risks');
    if (!risks.length) {
        tgt.innerHTML = `<div class="ers-empty">${__('No open risks 🎉')}</div>`;
        return;
    }
    tgt.innerHTML = `<table class="ers-risks-table">
        <thead><tr>
            <th style="width:80px">${__('Rating')}</th>
            <th>${__('Risk')}</th>
            <th style="width:130px">${__('Category')}</th>
            <th style="width:140px">${__('Owner')}</th>
            <th style="width:100px">${__('Status')}</th>
        </tr></thead>
        <tbody>${risks.map(r => `
            <tr onclick="frappe.set_route('Form','GRC Risk Register','${r.name}')">
                <td><span class="ers-rating-chip ers-rating-${r.risk_rating || 'Low'}">${frappe.utils.escape_html(r.risk_rating || '—')}</span></td>
                <td><div style="font-weight:500;color:var(--grc-primary);">${frappe.utils.escape_html(r.risk_title || r.name)}</div>
                    <div style="font-size:10px;color:var(--grc-muted);margin-top:2px;">${frappe.utils.escape_html(r.client || '')}</div></td>
                <td style="font-size:11px">${frappe.utils.escape_html(r.risk_category || '—')}</td>
                <td style="font-size:11px">${frappe.utils.escape_html(r.risk_owner || '—')}</td>
                <td style="font-size:11px">${frappe.utils.escape_html(r.status || '—')}</td>
            </tr>
        `).join('')}</tbody>
    </table>`;
}
