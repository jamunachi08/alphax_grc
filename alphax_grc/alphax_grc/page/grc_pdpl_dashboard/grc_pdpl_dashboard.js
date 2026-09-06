// AlphaX GRC v2.2.0 — PDPL KSA Privacy Dashboard
// Sections: PDPL Law / Implementing Regulation / Cross-Border / NDMO Guidance
// + DSAR backlog + DPIA risk mix.

frappe.pages['grc-pdpl-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('PDPL — KSA Privacy'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Browse PDPL Catalog'),
        () => frappe.set_route('List', 'GRC PDPL Catalog'));
    page.add_menu_item(__('Per-client PDPL Tracking'),
        () => frappe.set_route('List', 'GRC PDPL Control'));
    page.add_menu_item(__('+ New DSAR Request'),
        () => frappe.new_doc('GRC DSAR Request'));
    page.add_menu_item(__('+ New DPIA'),
        () => frappe.new_doc('GRC DPIA Record'));
    page.add_menu_item(__('All DSAR Requests'),
        () => frappe.set_route('List', 'GRC DSAR Request'));
    page.add_menu_item(__('All DPIAs'),
        () => frappe.set_route('List', 'GRC DPIA Record'));

    document.getElementById('pdpl-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

const SECTION_COLORS = {
    'PDPL Law':                          '#185FA5',
    'Implementing Regulation':           '#714B67',
    'Cross-Border Transfer Regulation':  '#5BA52A',
    'NDMO Guidance':                     '#C9A227',
};

const STATUS_COLORS = {
    'Not Started':            '#9C9C9C',
    'In Progress':            '#C9A227',
    'Implemented':            '#5BA52A',
    'Partially Implemented':  '#D9A632',
    'Not Applicable':         '#687178',
};

const RISK_COLORS = {
    'Low':       '#5BA52A',
    'Moderate':  '#C9A227',
    'High':      '#D2691E',
    'Very High': '#A32D2D',
    'Not Assessed': '#9C9C9C',
};

function buildShell() {
    return `
    <style>
      .pdpl { max-width: 1400px; margin: 0 auto; }
      .pdpl-toolbar { padding: 0 0 14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
      .pdpl-toolbar select {
        padding:7px 12px; border-radius:8px;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        background:white; font-size:12px; min-width:200px;
      }
      .pdpl-grid {
        display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));
        gap:12px; margin-top:10px;
      }
      .pdpl-card {
        background:white;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        border-left-width:4px;
        border-radius:10px;
        padding:18px;
        cursor:pointer;
        transition: transform 0.15s, box-shadow 0.15s;
      }
      .pdpl-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
      }
      .pdpl-card-label {
        font-size:13px; font-weight:600;
        color: var(--grc-primary, #714B67);
        margin: 0 0 6px;
      }
      .pdpl-card-meta {
        font-size: 11px; color: var(--grc-muted, #7A6A78);
        margin: 4px 0 12px;
      }
      .pdpl-status-bar {
        display:flex; height:6px; border-radius:3px; overflow:hidden;
        background: rgba(0,0,0,0.04); margin: 8px 0;
      }
      .pdpl-status-seg { height:100%; }
      .pdpl-score {
        font-size: 22px; font-weight: 700;
        margin-top: 6px;
      }
      .pdpl-score-lbl {
        font-size: 10px; color: var(--grc-muted);
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .pdpl-ops {
        display:grid; grid-template-columns: 1fr 1fr;
        gap:14px; margin-top: 24px;
      }
      @media (max-width: 800px) { .pdpl-ops { grid-template-columns: 1fr; } }
      .pdpl-ops-card {
        background:white;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        border-radius:10px; padding:18px;
      }
      .pdpl-ops-card h4 {
        margin: 0 0 12px;
        font-size: 12px; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--grc-primary, #714B67);
      }
      .pdpl-stat-row {
        display:flex; align-items:center; justify-content:space-between;
        padding: 6px 0;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.04));
        font-size: 12px;
      }
      .pdpl-stat-row:last-child { border-bottom: none; }
      .pdpl-stat-num {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-weight: 600;
      }
      .pdpl-stat-num.alert { color: #A32D2D; }
      .pdpl-stat-num.warn { color: #C9A227; }
      .pdpl-stat-num.ok { color: #5BA52A; }
      .pdpl-pill {
        display:inline-block;
        padding: 1px 8px; border-radius: 999px;
        font-size: 9px; font-weight: 700;
        color:white;
      }
    </style>

    <div class="pdpl">
      <div class="grc-hero">
        <h2>${__('PDPL — KSA Privacy')}</h2>
        <div class="grc-hero-sub">${__('Saudi Personal Data Protection Law — articles, Implementing Regulation, Cross-Border Transfer Regulation, NDMO programme guidance. DSAR and DPIA operational tracking.')}</div>
        <div class="grc-hero-stats" id="pdpl-stats"></div>
      </div>

      <div class="pdpl-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="pdpl-client-picker">
          <option value="">${__('— All clients (catalog totals only) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Compliance by section')}</h4>
        <div class="pdpl-grid" id="pdpl-grid"></div>
      </div>

      <div class="pdpl-ops">
        <div class="pdpl-ops-card">
          <h4>${__('DSAR backlog')}</h4>
          <div id="pdpl-dsar"></div>
        </div>
        <div class="pdpl-ops-card">
          <h4>${__('DPIA risk mix')}</h4>
          <div id="pdpl-dpia"></div>
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
            const sel = document.getElementById('pdpl-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_pdpl_dashboard.grc_pdpl_dashboard.get_dashboard',
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
    renderSections();
    renderDSAR();
    renderDPIA();
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_articles || 0, lbl: __('Articles') },
        { num: s.total_sections || 0, lbl: __('Sections') },
        { num: (STATE.data.dsar && STATE.data.dsar.open) || 0, lbl: __('Open DSARs') },
        { num: (STATE.data.dpia && STATE.data.dpia.high_risk) || 0, lbl: __('High-risk DPIAs') },
    ];
    document.getElementById('pdpl-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderSections() {
    const secs = STATE.data.sections || [];
    const tgt = document.getElementById('pdpl-grid');
    if (!secs.length) {
        tgt.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--grc-muted);">${__('PDPL catalog has not been seeded yet. Run migrate to load it.')}</div>`;
        return;
    }
    tgt.innerHTML = secs.map(sec => {
        const color = SECTION_COLORS[sec.code] || '#714B67';
        const status = sec.status_breakdown || {};
        const total = Object.values(status).reduce((a,b) => a+b, 0);
        const statusBar = total > 0
            ? Object.entries(STATUS_COLORS).map(([s,c]) => {
                const cnt = status[s] || 0;
                if (!cnt) return '';
                const pct = (cnt / total) * 100;
                return `<div class="pdpl-status-seg" style="flex:${pct};background:${c};" title="${s}: ${cnt}"></div>`;
              }).filter(s => s).join('')
            : '<div class="pdpl-status-seg" style="flex:1;background:rgba(0,0,0,0.06);"></div>';
        const navTarget = STATE.client
            ? () => frappe.set_route('List', 'GRC PDPL Control', { 'article_section': sec.code, 'client': STATE.client })
            : () => frappe.set_route('List', 'GRC PDPL Catalog', { 'article_section': sec.code });
        return `<div class="pdpl-card" style="border-left-color:${color};" onclick='(${navTarget.toString()})()'>
          <div class="pdpl-card-label">${frappe.utils.escape_html(sec.code)}</div>
          <div class="pdpl-card-meta">${sec.total_articles} ${__('articles')}</div>
          ${total > 0 ? `<div class="pdpl-status-bar">${statusBar}</div>` : ''}
          ${total > 0 ? `<div class="pdpl-score" style="color:${color};">${sec.avg_score}%<span class="pdpl-score-lbl" style="margin-left:6px;">${__('avg compliance')}</span></div>` : `<div style="font-size:10px;color:var(--grc-muted);text-align:center;padding:6px 0;">${__('Not yet tracked for this client')}</div>`}
        </div>`;
    }).join('');
}

function renderDSAR() {
    const dsar = STATE.data.dsar || {};
    const tgt = document.getElementById('pdpl-dsar');
    if (!dsar.total) {
        tgt.innerHTML = `<div style="text-align:center;padding:14px;color:var(--grc-muted);font-size:12px;">${__('No DSAR requests recorded yet.')}</div>`;
        return;
    }
    const overdueClass = dsar.overdue > 0 ? 'alert' : 'ok';
    let html = `
      <div class="pdpl-stat-row">
        <span>${__('Total requests')}</span>
        <span class="pdpl-stat-num">${dsar.total}</span>
      </div>
      <div class="pdpl-stat-row">
        <span>${__('Open (in workflow)')}</span>
        <span class="pdpl-stat-num warn">${dsar.open}</span>
      </div>
      <div class="pdpl-stat-row">
        <span>${__('Overdue (past 30-day SLA)')}</span>
        <span class="pdpl-stat-num ${overdueClass}">${dsar.overdue}</span>
      </div>`;
    const byStatus = dsar.by_status || {};
    if (Object.keys(byStatus).length > 0) {
        html += `<div style="margin-top:10px;font-size:10px;color:var(--grc-muted);text-transform:uppercase;letter-spacing:.05em;">${__('By status')}</div>`;
        Object.entries(byStatus).forEach(([s, n]) => {
            html += `<div class="pdpl-stat-row" style="font-size:11px;">
              <span>${frappe.utils.escape_html(s)}</span>
              <span class="pdpl-stat-num">${n}</span>
            </div>`;
        });
    }
    tgt.innerHTML = html;
}

function renderDPIA() {
    const dpia = STATE.data.dpia || {};
    const tgt = document.getElementById('pdpl-dpia');
    if (!dpia.total) {
        tgt.innerHTML = `<div style="text-align:center;padding:14px;color:var(--grc-muted);font-size:12px;">${__('No DPIAs recorded yet.')}</div>`;
        return;
    }
    let html = `
      <div class="pdpl-stat-row">
        <span>${__('Total DPIAs')}</span>
        <span class="pdpl-stat-num">${dpia.total}</span>
      </div>
      <div class="pdpl-stat-row">
        <span>${__('High-risk processing')}</span>
        <span class="pdpl-stat-num ${dpia.high_risk > 0 ? 'warn' : 'ok'}">${dpia.high_risk}</span>
      </div>`;
    const byRisk = dpia.by_inherent_risk || {};
    if (Object.keys(byRisk).length > 0) {
        html += `<div style="margin-top:10px;font-size:10px;color:var(--grc-muted);text-transform:uppercase;letter-spacing:.05em;">${__('Inherent risk')}</div>`;
        ['Very High','High','Moderate','Low','Not Assessed'].forEach(r => {
            const n = byRisk[r] || 0;
            if (n === 0) return;
            const c = RISK_COLORS[r] || '#9C9C9C';
            html += `<div class="pdpl-stat-row" style="font-size:11px;">
              <span><span class="pdpl-pill" style="background:${c};">${r}</span></span>
              <span class="pdpl-stat-num">${n}</span>
            </div>`;
        });
    }
    const byDecision = dpia.by_decision || {};
    if (Object.keys(byDecision).length > 0) {
        html += `<div style="margin-top:10px;font-size:10px;color:var(--grc-muted);text-transform:uppercase;letter-spacing:.05em;">${__('Decision')}</div>`;
        Object.entries(byDecision).forEach(([d, n]) => {
            html += `<div class="pdpl-stat-row" style="font-size:11px;">
              <span>${frappe.utils.escape_html(d)}</span>
              <span class="pdpl-stat-num">${n}</span>
            </div>`;
        });
    }
    tgt.innerHTML = html;
}
