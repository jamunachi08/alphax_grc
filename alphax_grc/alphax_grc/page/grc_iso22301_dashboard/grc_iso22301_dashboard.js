// AlphaX GRC v2.1.0 — ISO 22301 BCMS Dashboard
// Seven section cards (Context / Leadership / Planning / Support /
// Operation / Performance Evaluation / Improvement) with compliance status.

frappe.pages['grc-iso22301-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('ISO 22301 BCMS Dashboard'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Browse ISO 22301 Catalog'),
        () => frappe.set_route('List', 'GRC ISO22301 Catalog'));
    page.add_menu_item(__('Per-client BCMS Tracking'),
        () => frappe.set_route('List', 'GRC ISO22301 Control'));
    page.add_menu_item(__('Business Impact Analysis'),
        () => { try { frappe.set_route('List', 'GRC BIA'); } catch (e) { frappe.show_alert(__('GRC BIA doctype not available'), 5); } });
    page.add_menu_item(__('DR Plans'),
        () => { try { frappe.set_route('List', 'GRC DR Plan'); } catch (e) { frappe.show_alert(__('GRC DR Plan doctype not available'), 5); } });

    document.getElementById('bcms-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

const SECTION_COLORS = {
    '4 Context':                '#185FA5',
    '5 Leadership':             '#714B67',
    '6 Planning':               '#5B3A52',
    '7 Support':                '#5BA52A',
    '8 Operation':              '#C9A227',
    '9 Performance Evaluation': '#A32D2D',
    '10 Improvement':           '#3A6A1A',
};

const STATUS_COLORS = {
    'Not Started':            '#9C9C9C',
    'In Progress':            '#C9A227',
    'Implemented':            '#5BA52A',
    'Partially Implemented':  '#D9A632',
    'Not Applicable':         '#687178',
};

function buildShell() {
    return `
    <style>
      .bcms { max-width: 1400px; margin: 0 auto; }
      .bcms-toolbar { padding: 0 0 14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
      .bcms-toolbar select {
        padding:7px 12px; border-radius:8px;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        background:white; font-size:12px; min-width:200px;
      }
      .bcms-sec-grid {
        display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
        gap:12px; margin-top:14px;
      }
      .bcms-sec-card {
        background:white;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        border-left-width:4px;
        border-radius:10px;
        padding:18px;
        cursor:pointer;
        transition: transform 0.15s, box-shadow 0.15s;
      }
      .bcms-sec-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
      }
      .bcms-sec-num {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-size: 22px; font-weight: 700;
      }
      .bcms-sec-label {
        font-size:14px; font-weight:600;
        color: var(--grc-primary, #714B67);
        margin: 6px 0;
      }
      .bcms-sec-meta {
        font-size: 11px; color: var(--grc-muted, #7A6A78);
        margin: 4px 0 12px;
      }
      .bcms-status-bar {
        display:flex; height:6px; border-radius:3px; overflow:hidden;
        background: rgba(0,0,0,0.04); margin: 8px 0;
      }
      .bcms-status-seg { height:100%; }
      .bcms-score {
        font-size: 24px; font-weight: 700;
        margin-top: 8px;
      }
      .bcms-score-label {
        font-size: 10px; color: var(--grc-muted);
        text-transform: uppercase; letter-spacing: 0.04em;
      }
    </style>

    <div class="bcms">
      <div class="grc-hero">
        <h2>${__('ISO 22301 BCMS Dashboard')}</h2>
        <div class="grc-hero-sub">${__('Business Continuity Management System per ISO 22301:2019. Seven sections from Context through Improvement.')}</div>
        <div class="grc-hero-stats" id="bcms-stats"></div>
      </div>

      <div class="bcms-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="bcms-client-picker">
          <option value="">${__('— All clients (catalog totals only) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Sections')}</h4>
        <div class="bcms-sec-grid" id="bcms-sec-grid"></div>
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
            const sel = document.getElementById('bcms-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_iso22301_dashboard.grc_iso22301_dashboard.get_dashboard',
        args,
        callback: (r) => {
            STATE.data = (r && r.message) || null;
            render();
        },
    });
}

function render() {
    if (!STATE.data) return;
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_clauses || 0, lbl: __('Clauses') },
        { num: s.total_sections || 0, lbl: __('Sections') },
        { num: s.tracked_overall || 0, lbl: __('Tracked Records') },
        { num: STATE.client ? '1' : __('All'), lbl: __('Client Scope') },
    ];
    document.getElementById('bcms-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');

    const secs = STATE.data.sections || [];
    const tgt = document.getElementById('bcms-sec-grid');
    if (!secs.length) {
        tgt.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--grc-muted);">${__('ISO 22301 catalog has not been seeded yet. Run migrate to load it.')}</div>`;
        return;
    }
    tgt.innerHTML = secs.map(sec => {
        const color = SECTION_COLORS[sec.code] || '#714B67';
        const status = sec.status_breakdown || {};
        const total = Object.values(status).reduce((a,b) => a+b, 0);
        const statusBar = total > 0
            ? Object.entries(STATUS_COLORS).map(([s,c]) => {
                const cnt = status[s] || 0;
                const pct = (cnt / total) * 100;
                return cnt > 0 ? `<div class="bcms-status-seg" style="flex:${pct};background:${c};"></div>` : '';
              }).join('')
            : '<div class="bcms-status-seg" style="flex:1;background:rgba(0,0,0,0.06);"></div>';
        const navTarget = STATE.client
            ? () => frappe.set_route('List', 'GRC ISO22301 Control', { 'section_number': sec.code, 'client': STATE.client })
            : () => frappe.set_route('List', 'GRC ISO22301 Catalog', { 'section_number': sec.code });
        const sec_num = sec.code.split(' ')[0];
        return `<div class="bcms-sec-card" style="border-left-color:${color};" onclick='(${navTarget.toString()})()'>
          <div class="bcms-sec-num" style="color:${color};">${sec_num}</div>
          <div class="bcms-sec-label">${frappe.utils.escape_html(sec.label)}</div>
          <div class="bcms-sec-meta">${sec.total_clauses} ${__('clauses')}</div>
          ${total > 0 ? `<div class="bcms-status-bar">${statusBar}</div>` : ''}
          ${total > 0 ? `<div class="bcms-score" style="color:${color};">${sec.avg_score}%<span class="bcms-score-label" style="margin-left:6px;">${__('avg compliance')}</span></div>` : `<div style="font-size:10px;color:var(--grc-muted);text-align:center;padding:6px 0;">${__('Not yet tracked for this client')}</div>`}
        </div>`;
    }).join('');
}
