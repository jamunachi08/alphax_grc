// AlphaX GRC v2.1.1 — Cyber Risk Quantification Dashboard
// Top scenarios by ALE + loss-curve (cumulative SLE chart) + risk-rating mix.

frappe.pages['grc-crq-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Cyber Risk Quantification'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('+ New CRQ Scenario'),
        () => frappe.new_doc('GRC CRQ Scenario'));
    page.add_menu_item(__('All scenarios'),
        () => frappe.set_route('List', 'GRC CRQ Scenario'));

    document.getElementById('crq-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

const RATING_COLORS = {
    'Low':       '#5BA52A',
    'Moderate':  '#C9A227',
    'High':      '#D2691E',
    'Very High': '#A32D2D',
};

function buildShell() {
    return `
    <style>
      .crq { max-width: 1400px; margin: 0 auto; }
      .crq-toolbar { padding: 0 0 14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
      .crq-toolbar select {
        padding:7px 12px; border-radius:8px;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        background:white; font-size:12px; min-width:200px;
      }
      .crq-grid {
        display: grid; grid-template-columns: 2fr 1fr;
        gap: 14px; margin-top: 14px;
      }
      @media (max-width: 900px) { .crq-grid { grid-template-columns: 1fr; } }
      .crq-card {
        background: white;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        border-radius: 10px;
        padding: 18px;
      }
      .crq-card h4 {
        margin: 0 0 12px;
        font-size: 12px; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--grc-primary, #714B67);
      }
      .crq-table {
        width: 100%; border-collapse: collapse; font-size: 12px;
      }
      .crq-table th {
        text-align: left; padding: 8px;
        border-bottom: 2px solid var(--grc-secondary, #5B3A52);
        color: var(--grc-primary, #714B67);
        font-weight: 600; font-size: 10px;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .crq-table td {
        padding: 8px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.06));
        vertical-align: middle;
      }
      .crq-table tr { cursor: pointer; }
      .crq-table tr:hover { background: rgba(113, 75, 103, 0.04); }
      .crq-pill {
        display: inline-block;
        padding: 2px 8px; border-radius: 999px;
        font-size: 9px; font-weight: 700;
        color: white;
      }
      .crq-money {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-weight: 600; font-size: 12px;
      }
      .crq-rating-bar {
        display:flex; height:8px; border-radius:4px; overflow:hidden;
        background: rgba(0,0,0,0.04); margin: 8px 0;
      }
      .crq-rating-seg { height:100%; }
      .crq-curve-svg {
        width: 100%; height: 220px; margin-top: 8px;
      }
      .crq-empty {
        text-align: center; padding: 28px;
        color: var(--grc-muted, #7A6A78); font-size: 12px;
      }
    </style>

    <div class="crq">
      <div class="grc-hero">
        <h2>${__('Cyber Risk Quantification')}</h2>
        <div class="grc-hero-sub">${__('FAIR + NIST SP 800-30 quantitative scenarios. Loss event frequency × single loss expectancy = annual loss expectancy. Built from public methodology.')}</div>
        <div class="grc-hero-stats" id="crq-stats"></div>
      </div>

      <div class="crq-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="crq-client-picker">
          <option value="">${__('— All clients —')}</option>
        </select>
      </div>

      <div class="crq-grid">
        <div class="crq-card">
          <h4>${__('Top scenarios by Annual Loss Expectancy')}</h4>
          <div id="crq-table-wrap"></div>
        </div>
        <div>
          <div class="crq-card" style="margin-bottom:14px;">
            <h4>${__('Inherent risk mix')}</h4>
            <div id="crq-rating-wrap"></div>
          </div>
          <div class="crq-card">
            <h4>${__('Loss curve (sorted ALE)')}</h4>
            <svg class="crq-curve-svg" id="crq-curve" viewBox="0 0 400 220" preserveAspectRatio="none"></svg>
            <div style="font-size:10px;color:var(--grc-muted);text-align:center;margin-top:4px;">${__('Each bar = one scenario, ordered by annualized loss')}</div>
          </div>
        </div>
      </div>
    </div>`;
}

function loadClients() {
    return new Promise((resolve) => {
        if (!(frappe.db && frappe.db.get_list)) return resolve();
        frappe.db.get_list('GRC Client Profile', {
            fields: ['name', 'client_name'], limit: 100,
        }).then((rows) => {
            STATE.clients = rows || [];
            const sel = document.getElementById('crq-client-picker');
            STATE.clients.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                opt.textContent = c.client_name || c.name;
                sel.appendChild(opt);
            });
            resolve();
        }).catch(() => resolve());
    });
}

function loadAll() {
    const args = {};
    if (STATE.client) args.client = STATE.client;
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_crq_dashboard.grc_crq_dashboard.get_dashboard',
        args,
        callback: (r) => {
            STATE.data = (r && r.message) || null;
            render();
        },
    });
}

function fmtMoney(v) {
    if (v == null) return '—';
    const n = Number(v);
    if (!isFinite(n)) return '—';
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
    if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
    return n.toFixed(0);
}

function render() {
    if (!STATE.data) return;
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_scenarios || 0, lbl: __('Scenarios') },
        { num: fmtMoney(s.total_ale_year), lbl: __('Total ALE / yr') },
        { num: fmtMoney(s.max_single_event_loss), lbl: __('Max event loss') },
        { num: STATE.client ? '1' : __('All'), lbl: __('Client') },
    ];
    document.getElementById('crq-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');

    renderTable();
    renderRatingMix();
    renderLossCurve();
}

function renderTable() {
    const scenarios = STATE.data.scenarios || [];
    const wrap = document.getElementById('crq-table-wrap');
    if (!scenarios.length) {
        wrap.innerHTML = `<div class="crq-empty">${__('No active CRQ scenarios. Click "+ New CRQ Scenario" in the menu to create one.')}</div>`;
        return;
    }
    wrap.innerHTML = `<table class="crq-table">
      <thead><tr>
        <th>${__('Scenario')}</th>
        <th style="width:80px">${__('Risk')}</th>
        <th style="width:90px;text-align:right;">${__('LEF/yr')}</th>
        <th style="width:110px;text-align:right;">${__('SLE')}</th>
        <th style="width:110px;text-align:right;">${__('ALE/yr')}</th>
      </tr></thead>
      <tbody>${scenarios.map(s => {
        const ratingColor = RATING_COLORS[s.inherent_risk_rating] || '#9C9C9C';
        return `<tr onclick="frappe.set_route('Form','GRC CRQ Scenario','${s.name}')">
          <td>
            <div style="font-weight:500;color:var(--grc-primary);">${frappe.utils.escape_html(s.scenario_name || s.name)}</div>
            <div style="font-size:10px;color:var(--grc-muted);margin-top:2px;">
              ${frappe.utils.escape_html(s.client || '')}
              ${s.framework ? '· ' + frappe.utils.escape_html(s.framework) : ''}
            </div>
          </td>
          <td><span class="crq-pill" style="background:${ratingColor};">${frappe.utils.escape_html(s.inherent_risk_rating || '—')}</span></td>
          <td style="text-align:right;font-family:ui-monospace,monospace;font-size:11px;">${(s.loss_event_frequency || 0).toFixed(2)}</td>
          <td style="text-align:right;" class="crq-money">${fmtMoney(s.single_loss_expectancy)}</td>
          <td style="text-align:right;" class="crq-money">${fmtMoney(s.annual_loss_expectancy)}</td>
        </tr>`;
      }).join('')}</tbody>
    </table>`;
}

function renderRatingMix() {
    const breakdown = (STATE.data.summary || {}).rating_breakdown || {};
    const wrap = document.getElementById('crq-rating-wrap');
    const total = Object.values(breakdown).reduce((a, b) => a + b, 0);
    if (!total) {
        wrap.innerHTML = `<div class="crq-empty" style="padding:14px;">${__('No scenarios')}</div>`;
        return;
    }
    const order = ['Low', 'Moderate', 'High', 'Very High'];
    const segs = order.map(r => {
        const cnt = breakdown[r] || 0;
        if (cnt === 0) return '';
        const pct = (cnt / total) * 100;
        return `<div class="crq-rating-seg" style="flex:${pct};background:${RATING_COLORS[r]};" title="${r}: ${cnt}"></div>`;
    }).filter(s => s).join('');
    const legend = order.map(r => `
        <div style="display:flex;align-items:center;justify-content:space-between;font-size:11px;margin:4px 0;">
            <div style="display:flex;align-items:center;gap:6px;">
                <span style="width:10px;height:10px;border-radius:50%;background:${RATING_COLORS[r]};"></span>
                <span>${r}</span>
            </div>
            <span style="font-family:ui-monospace,monospace;color:var(--grc-muted);">${breakdown[r] || 0}</span>
        </div>`).join('');
    wrap.innerHTML = `
        <div class="crq-rating-bar">${segs}</div>
        ${legend}`;
}

function renderLossCurve() {
    // Sort scenarios by ALE descending; render as horizontal bars.
    const scenarios = (STATE.data.scenarios || []).slice();
    scenarios.sort((a, b) => (b.annual_loss_expectancy || 0) - (a.annual_loss_expectancy || 0));
    const svg = document.getElementById('crq-curve');
    if (!scenarios.length) {
        svg.innerHTML = `<text x="200" y="110" text-anchor="middle" fill="#9C9C9C" font-size="11">${__('No data')}</text>`;
        return;
    }
    const W = 400, H = 220;
    const PAD_L = 35, PAD_R = 8, PAD_T = 8, PAD_B = 18;
    const innerW = W - PAD_L - PAD_R;
    const innerH = H - PAD_T - PAD_B;
    const maxAle = Math.max(...scenarios.map(s => s.annual_loss_expectancy || 0));
    if (maxAle === 0) {
        svg.innerHTML = `<text x="200" y="110" text-anchor="middle" fill="#9C9C9C" font-size="11">${__('Loss values not yet entered')}</text>`;
        return;
    }
    const n = scenarios.length;
    const barW = innerW / Math.max(n, 1) * 0.85;
    const gap = innerW / Math.max(n, 1) * 0.15;
    let bars = '';
    let xLabels = '';
    scenarios.forEach((s, i) => {
        const ale = s.annual_loss_expectancy || 0;
        const h = (ale / maxAle) * innerH;
        const x = PAD_L + i * (barW + gap);
        const y = PAD_T + (innerH - h);
        const color = RATING_COLORS[s.inherent_risk_rating] || '#714B67';
        bars += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" fill="${color}" opacity="0.85" rx="1">
                   <title>${frappe.utils.escape_html(s.scenario_name)}: ${fmtMoney(ale)}</title>
                 </rect>`;
    });
    // Y-axis: just max & mid label
    const yAxis = `
        <line x1="${PAD_L}" y1="${PAD_T}" x2="${PAD_L}" y2="${H - PAD_B}" stroke="#E5E5E5" stroke-width="1"/>
        <line x1="${PAD_L}" y1="${H - PAD_B}" x2="${W - PAD_R}" y2="${H - PAD_B}" stroke="#E5E5E5" stroke-width="1"/>
        <text x="${PAD_L - 4}" y="${PAD_T + 4}" text-anchor="end" font-size="9" fill="#7A6A78">${fmtMoney(maxAle)}</text>
        <text x="${PAD_L - 4}" y="${H - PAD_B}" text-anchor="end" font-size="9" fill="#7A6A78">0</text>`;
    svg.innerHTML = yAxis + bars;
}
