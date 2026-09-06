// AlphaX GRC v1.4.0 — KPI Dashboard
// Browse KPIs by client, see quarterly target vs actual, latest year.

frappe.pages['grc-kpi-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('KPI Dashboard'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(`
    <style>
      .kpi-dash { font-family: system-ui,-apple-system,sans-serif; padding: 16px; font-size: 13px; }
      .kpi-dash .header { display:flex; justify-content:space-between;
        align-items:center; gap:12px; margin-bottom:14px; flex-wrap:wrap; }
      .kpi-dash .picker { padding: 6px 10px; border-radius: 6px;
        border: 1px solid rgba(0,0,0,.15); background: white; min-width: 240px; }
      .kpi-dash .grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 14px; }
      .kpi-dash .card { background: white; border:1px solid rgba(0,0,0,.08);
        border-radius: 10px; padding: 14px; }
      .kpi-dash .card h4 { font-size: 13px; font-weight: 500; margin: 0 0 4px;
        line-height: 1.3; }
      .kpi-dash .card .domain { font-size: 11px; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: .04em; margin-bottom: 10px; }
      .kpi-dash .qrow { display:grid; grid-template-columns: 36px 1fr 90px;
        align-items:center; gap:8px; font-size:12px; padding:6px 0;
        border-bottom: 1px solid rgba(0,0,0,.05); }
      .kpi-dash .qrow:last-child { border:none; }
      .kpi-dash .qlabel { font-weight: 500; color: var(--text-muted); }
      .kpi-dash .qbar { height: 8px; background: rgba(0,0,0,.06);
        border-radius: 999px; position: relative; overflow: hidden; }
      .kpi-dash .qbar > .actual { position: absolute; top: 0; left: 0;
        height: 100%; border-radius: 999px; transition: width .4s; }
      .kpi-dash .qbar > .target-mark { position: absolute; top: -2px;
        width: 2px; height: 12px; background: rgba(0,0,0,.6); }
      .kpi-dash .qval { text-align: right; font-variant-numeric: tabular-nums;
        font-size: 11px; color: var(--text-muted); }
      .kpi-dash .empty { text-align: center; padding: 40px; color: var(--text-muted); }
    </style>

    <div class="kpi-dash">
      <div class="header">
        <div>
          <div style="font-size:15px; font-weight:500">${__('KPI Dashboard')}</div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px">
            ${__('Quarterly KPI performance per client')}
          </div>
        </div>
        <div>
          <label style="font-size:12px; color:var(--text-muted); margin-right:6px">${__('Client:')}</label>
          <select class="picker" id="kpi-client-picker" onchange="window.__loadKPIs()">
            <option value="">${__('— Firm-wide —')}</option>
          </select>
        </div>
      </div>

      <div id="kpi-grid" class="grid"></div>
    </div>
    `);

    page.set_primary_action(__('Refresh'), () => window.__loadKPIs(), 'refresh');
    page.add_menu_item(__('New KPI'), () => frappe.new_doc('GRC KPI'));

    loadClients().then(() => window.__loadKPIs());
};

function loadClients() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.doctype.grc_client_profile.grc_client_profile.get_active_clients',
            callback: (r) => {
                const sel = document.getElementById('kpi-client-picker');
                if (!sel) return resolve();
                ((r && r.message) || []).forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.name;
                    opt.textContent = `${c.client_name} — ${c.country} / ${c.sector}`;
                    sel.appendChild(opt);
                });
                resolve();
            },
        });
    });
}

window.__loadKPIs = function() {
    const client = document.getElementById('kpi-client-picker').value;
    const args = client ? { client } : {};
    frappe.call({
        method: 'alphax_grc.alphax_grc.doctype.grc_kpi.grc_kpi.get_kpi_chart_data',
        args,
        callback: (r) => render((r && r.message) || []),
    });
};

function render(kpis) {
    const grid = document.getElementById('kpi-grid');
    if (!grid) return;
    if (!kpis.length) {
        grid.innerHTML = '<div class="empty">No KPIs yet. Click "New KPI" to add one.</div>';
        return;
    }
    grid.innerHTML = kpis.map(kpi => {
        const latest = (kpi.measurements || []).slice(-1)[0];
        const cardBody = latest
            ? renderQuarters(latest, kpi.type)
            : '<div class="empty" style="padding:18px">No measurements yet</div>';
        return `<div class="card">
            <div class="domain">${frappe.utils.escape_html(kpi.domain || '—')} · KPI ${kpi.kpi_id}</div>
            <h4>${frappe.utils.escape_html(kpi.indicator_name || '')}</h4>
            ${cardBody}
        </div>`;
    }).join('');
}

function renderQuarters(m, kpiType) {
    const isPct = kpiType === 'Percentage';
    const fmt = (v) => {
        if (v === null || v === undefined || v === '') return '—';
        const n = parseFloat(v);
        if (isNaN(n)) return '—';
        return isPct ? (n <= 1 ? Math.round(n * 100) : Math.round(n)) + '%' : n.toFixed(1);
    };
    return ['q1', 'q2', 'q3', 'q4'].map(q => {
        const t = m[`${q}_target`];
        const a = m[`${q}_actual`];
        const tNum = parseFloat(t || 0);
        const aNum = parseFloat(a || 0);
        const max = Math.max(tNum, aNum, isPct ? 1 : 1);
        const aPct = max > 0 ? Math.min(100, (aNum / max) * 100) : 0;
        const tPct = max > 0 ? Math.min(100, (tNum / max) * 100) : 0;
        const meeting = tNum > 0 && aNum >= tNum;
        const color = meeting ? '#0F6E56' : (aNum > 0 ? '#854F0B' : '#888780');
        return `<div class="qrow">
            <div class="qlabel">${q.toUpperCase()}</div>
            <div class="qbar">
              <div class="actual" style="width:${aPct}%; background:${color}"></div>
              <div class="target-mark" style="left:${tPct}%"></div>
            </div>
            <div class="qval">${fmt(a)} / ${fmt(t)}</div>
          </div>`;
    }).join('');
}
