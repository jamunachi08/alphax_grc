// AlphaX GRC v1.3.2 — Lifecycle Dashboard (live)
// 8-stage process cycle wheel, client picker, auto-refresh + realtime push.

frappe.pages['grc-lifecycle'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('GRC Lifecycle'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(render_shell());

    const $indicator = frappe.alphaxGRC.makeIndicator();
    page.page_actions.prepend($indicator);

    page.set_primary_action(__('Refresh now'),
        () => LIVE && LIVE.forceServerRefresh(CURRENT_CLIENT), 'refresh');
    page.add_menu_item(__('Firm overview'), () => show_firm_overview());
    page.add_menu_item(__('New client'), () => frappe.new_doc('GRC Client Profile'));

    load_clients().then(() => start_live($indicator));
};

let LIVE = null;
function start_live($indicator) {
    LIVE = frappe.alphaxGRC.live({
        endpoint: 'alphax_grc.alphax_grc.page.grc_lifecycle.grc_lifecycle.get_lifecycle_data',
        getArgs: () => CURRENT_CLIENT ? { client: CURRENT_CLIENT } : {},
        invalidateOnAnyClient: true,
        indicatorEl: $indicator,
        refreshSeconds: 30,
        onData: (payload) => {
            LIFECYCLE_DATA = payload;
            render_all();
        },
    });
    LIVE.start();
}

const STAGES = [
    {id:1, name:'Setup',     sub:'Country & sector profile',  detail:'Pick country, sector and frameworks. Seeds the right controls.'},
    {id:2, name:'Register',  sub:'Risks & assets',             detail:'Risk Register + Asset Inventory. Classify, score, assign owners.'},
    {id:3, name:'Assess',    sub:'Maturity & gaps',            detail:'Run framework assessments. Score weighted questions.'},
    {id:4, name:'Control',   sub:'Implement & evidence',       detail:'Map findings to controls. Upload evidence.'},
    {id:5, name:'Audit',     sub:'Test effectiveness',         detail:'Audit programme, ITGC, third-party. Generate findings.'},
    {id:6, name:'Remediate', sub:'Close gaps',                 detail:'Track due dates, escalation, verification.'},
    {id:7, name:'Report',    sub:'Board & regulator',          detail:'Compliance score, KRI status, board reports.'},
    {id:8, name:'Review',    sub:'Periodic & continuous',      detail:'Calendar-driven reviews feed back into setup.'},
];

const STATUS_COLORS = {
    green: {fill:'#EAF3DE', stroke:'#3B6D11', text:'#27500A'},
    amber: {fill:'#FAEEDA', stroke:'#854F0B', text:'#633806'},
    red:   {fill:'#FCEBEB', stroke:'#A32D2D', text:'#791F1F'},
    empty: {fill:'#F1EFE8', stroke:'#888780', text:'#5F5E5A'},
};

let CLIENTS = [];
let CURRENT_CLIENT = null;
let LIFECYCLE_DATA = null;

function render_shell() {
    return `
    <style>
      .grc-lc { font-family: system-ui,-apple-system,'Segoe UI',sans-serif;
                padding: 16px; min-height: 700px; font-size: 13px; }
      .grc-lc .header { display: flex; justify-content: space-between;
                        align-items: center; margin-bottom: 14px; gap: 12px; flex-wrap: wrap; }
      .grc-lc .title { font-size: 16px; font-weight: 500; }
      .grc-lc .subtitle { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
      .grc-lc .picker-row { display: flex; gap: 8px; align-items: center; }
      .grc-lc select.client-picker { min-width: 280px; padding: 6px 10px;
        border-radius: 6px; border: 1px solid rgba(0,0,0,.15);
        background: white; font-size: 13px; }
      .grc-lc .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 10px; margin-bottom: 14px; }
      .grc-lc .kpi-card { background: white; border: 1px solid rgba(0,0,0,.08);
        border-radius: 8px; padding: 12px 14px; }
      .grc-lc .kpi-val { font-size: 22px; font-weight: 500; line-height: 1; }
      .grc-lc .kpi-lbl { font-size: 10px; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: .05em; margin-top: 4px; }
      .grc-lc .main { display: grid; grid-template-columns: 1.1fr 0.9fr;
        gap: 14px; }
      .grc-lc .panel { background: white; border: 1px solid rgba(0,0,0,.08);
        border-radius: 10px; padding: 14px; }
      .grc-lc .panel h4 { font-size: 13px; font-weight: 500; margin: 0 0 10px; }
      .grc-lc .stage-detail { padding: 10px 12px;
        background: rgba(0,0,0,.03); border-radius: 6px;
        margin-bottom: 12px; min-height: 52px; font-size: 12px;
        color: var(--text-muted); line-height: 1.5; }
      .grc-lc .stage-detail strong { color: var(--text-color);
        font-weight: 500; display: block; margin-bottom: 3px; font-size: 13px; }
      .grc-lc .frameworks-row { display: flex; flex-wrap: wrap; gap: 5px;
        margin-bottom: 12px; }
      .grc-lc .frameworks-row .pill { padding: 3px 9px; border-radius: 999px;
        background: #E6F1FB; color: #0C447C; font-size: 11px; font-weight: 500; }
      .grc-lc .stage-list { font-size: 12px; }
      .grc-lc .stage-row { display: flex; justify-content: space-between;
        align-items: center; padding: 8px 0;
        border-bottom: 1px solid rgba(0,0,0,.06); cursor: pointer;
        transition: background .15s; }
      .grc-lc .stage-row:hover { background: rgba(0,0,0,.02); }
      .grc-lc .stage-row:last-child { border-bottom: none; }
      .grc-lc .stage-name { display: flex; align-items: center; gap: 8px; }
      .grc-lc .stage-num { width: 18px; height: 18px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 9px; font-weight: 500; }
      .grc-lc .stage-pb { width: 80px; height: 5px; border-radius: 999px;
        background: rgba(0,0,0,.08); overflow: hidden; }
      .grc-lc .stage-pb > div { height: 100%; border-radius: 999px; }
      .grc-lc .stage-pct { font-size: 11px; font-weight: 500;
        min-width: 40px; text-align: right; }
      .grc-lc .empty-state { padding: 40px 20px; text-align: center;
        color: var(--text-muted); font-size: 13px; }
      .grc-lc .empty-state button { margin-top: 14px; padding: 8px 16px;
        border-radius: 6px; border: 1px solid rgba(0,0,0,.15);
        background: white; cursor: pointer; font-size: 13px; }
    </style>

    <div class="grc-lc" id="grc-lc-root">
      <div class="header">
        <div>
          <div class="title">${__('GRC Lifecycle')}</div>
          <div class="subtitle">${__('End-to-end process cycle for GRC engagements')}</div>
        </div>
        <div class="picker-row">
          <label style="font-size:12px;color:var(--text-muted)">${__('Client:')}</label>
          <select class="client-picker" id="client-picker" onchange="window.__grcSelectClient(this.value)">
            <option value="">${__('— Firm-wide overview —')}</option>
          </select>
        </div>
      </div>

      <div id="frameworks-row" class="frameworks-row" style="display:none"></div>
      <div id="kpi-grid" class="kpi-grid"></div>

      <div class="main">
        <div class="panel">
          <h4>${__('Process cycle')}</h4>
          <div class="stage-detail" id="stage-detail">
            <strong>${__('Hover any stage')}</strong>
            ${__('See live progress and deep-link into that module.')}
          </div>
          <div id="cycle-svg-container"></div>
        </div>
        <div class="panel">
          <h4>${__('Stage progress')}</h4>
          <div class="stage-list" id="stage-list"></div>
        </div>
      </div>
    </div>`;
}

window.__grcSelectClient = function(client_name) {
    CURRENT_CLIENT = client_name || null;
    load_all();
};

function load_clients() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.doctype.grc_client_profile.grc_client_profile.get_active_clients',
            callback: (r) => {
                CLIENTS = (r && r.message) || [];
                const sel = document.getElementById('client-picker');
                if (!sel) return resolve();
                CLIENTS.forEach(c => {
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

function load_all() {
    // Defer to the live module — it tracks current client via the getArgs closure
    if (LIVE) LIVE.refreshNow();
}

function render_all() {
    render_kpis();
    render_frameworks();
    render_cycle();
    render_stage_list();
}

function render_kpis() {
    const grid = document.getElementById('kpi-grid');
    if (!grid || !LIFECYCLE_DATA) return;
    let kpis;
    if (CURRENT_CLIENT) {
        const client = CLIENTS.find(c => c.name === CURRENT_CLIENT) || {};
        kpis = [
            {lbl: __('Compliance Score'), val: (client.compliance_score || 0) + '%', col: '#10B981'},
            {lbl: __('Open Risks'),       val: client.open_risks || 0,                col: '#DC2626'},
            {lbl: __('Open Findings'),    val: client.open_findings || 0,             col: '#D97706'},
            {lbl: __('Engagement'),       val: client.engagement_type || '—',         col: '#0EA5E4'},
        ];
    } else {
        kpis = [
            {lbl: __('Active Clients'),  val: CLIENTS.length,                            col: '#0EA5E4'},
            {lbl: __('Open Risks'),      val: CLIENTS.reduce((a,c) => a + (c.open_risks || 0), 0),    col: '#DC2626'},
            {lbl: __('Open Findings'),   val: CLIENTS.reduce((a,c) => a + (c.open_findings || 0), 0), col: '#D97706'},
            {lbl: __('Avg Compliance'),  val: CLIENTS.length
                ? Math.round(CLIENTS.reduce((a,c) => a + (c.compliance_score || 0), 0) / CLIENTS.length) + '%'
                : '0%', col: '#10B981'},
        ];
    }
    grid.innerHTML = kpis.map(k =>
        `<div class="kpi-card">
           <div class="kpi-val" style="color:${k.col}">${frappe.utils.escape_html(String(k.val))}</div>
           <div class="kpi-lbl">${frappe.utils.escape_html(k.lbl)}</div>
         </div>`
    ).join('');
}

function render_frameworks() {
    const row = document.getElementById('frameworks-row');
    if (!row) return;
    if (!CURRENT_CLIENT) {
        row.style.display = 'none';
        return;
    }
    frappe.db.get_value('GRC Client Profile', CURRENT_CLIENT, 'applicable_frameworks').then((r) => {
        const fws = (r.message && r.message.applicable_frameworks || '')
            .split('\n').map(s => s.trim()).filter(Boolean);
        if (!fws.length) { row.style.display = 'none'; return; }
        row.style.display = 'flex';
        row.innerHTML = `<span style="font-size:11px;color:var(--text-muted);align-self:center">${__('Frameworks:')}</span>` +
            fws.map(f => `<span class="pill">${frappe.utils.escape_html(f)}</span>`).join('');
    });
}

function render_cycle() {
    const container = document.getElementById('cycle-svg-container');
    if (!container || !LIFECYCLE_DATA) return;

    const cx = 220, cy = 200, r = 130;
    const W = 440, H = 400;

    let svg = `<svg width="100%" viewBox="0 0 ${W} ${H}" style="max-width:480px;display:block;margin:auto">
      <defs>
        <marker id="lc-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>`;

    // Centre disc — current scope
    const scope_label = CURRENT_CLIENT
        ? (CLIENTS.find(c => c.name === CURRENT_CLIENT) || {}).client_name || CURRENT_CLIENT
        : __('All clients');
    const scope_sub = CURRENT_CLIENT
        ? `${(CLIENTS.find(c => c.name === CURRENT_CLIENT) || {}).country || ''} / ${(CLIENTS.find(c => c.name === CURRENT_CLIENT) || {}).sector || ''}`
        : `${CLIENTS.length} ${__('active')}`;
    svg += `<circle cx="${cx}" cy="${cy}" r="55" fill="rgba(0,0,0,.04)" stroke="rgba(0,0,0,.1)" stroke-width="0.5"/>`;
    svg += `<text x="${cx}" y="${cy - 5}" text-anchor="middle" font-size="11" font-weight="500" fill="var(--text-color)">${frappe.utils.escape_html(scope_label.substring(0, 20))}</text>`;
    svg += `<text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="9" fill="var(--text-muted)">${frappe.utils.escape_html(scope_sub.substring(0, 28))}</text>`;

    // Stage nodes
    LIFECYCLE_DATA.stages.forEach((stage, i) => {
        const angle = (i / 8) * 2 * Math.PI - Math.PI / 2;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        const colors = STATUS_COLORS[stage.status] || STATUS_COLORS.empty;

        svg += `<g style="cursor:pointer"
            onclick="window.__grcGoToStage(${i})"
            onmouseenter="window.__grcShowStage(${i})">
          <circle cx="${x}" cy="${y}" r="32"
                  fill="${colors.fill}" stroke="${colors.stroke}" stroke-width="0.5"/>
          <text x="${x}" y="${y - 5}" text-anchor="middle" font-size="9"
                fill="${colors.text}" opacity="0.6">${stage.id}</text>
          <text x="${x}" y="${y + 7}" text-anchor="middle" font-size="11"
                font-weight="500" fill="${colors.text}">${frappe.utils.escape_html(stage.name)}</text>`;
        if (stage.total > 0) {
            svg += `<text x="${x}" y="${y + 19}" text-anchor="middle" font-size="9"
                          fill="${colors.text}" opacity="0.7">${stage.pct}%</text>`;
        }
        svg += `</g>`;

        // Sub-label outside the node
        const subAngle = angle;
        const subX = cx + (r + 50) * Math.cos(subAngle);
        const subY = cy + (r + 50) * Math.sin(subAngle);
        const sub = STAGES[i].sub;
        svg += `<text x="${subX}" y="${subY}" text-anchor="middle" font-size="9"
                      fill="var(--text-muted)">${frappe.utils.escape_html(sub)}</text>`;
    });

    // Arcs between stages
    for (let i = 0; i < 8; i++) {
        const a1 = (i / 8) * 2 * Math.PI - Math.PI / 2;
        const a2 = ((i + 1) / 8) * 2 * Math.PI - Math.PI / 2;
        const r1 = r - 24;
        const x1 = cx + r1 * Math.cos(a1 + 0.18);
        const y1 = cy + r1 * Math.sin(a1 + 0.18);
        const x2 = cx + r1 * Math.cos(a2 - 0.18);
        const y2 = cy + r1 * Math.sin(a2 - 0.18);
        svg += `<path d="M ${x1} ${y1} A ${r1} ${r1} 0 0 1 ${x2} ${y2}"
                fill="none" stroke="rgba(0,0,0,.25)" stroke-width="1"
                marker-end="url(#lc-arrow)"/>`;
    }

    svg += `</svg>`;
    container.innerHTML = svg;
}

window.__grcGoToStage = function(idx) {
    const stage = LIFECYCLE_DATA.stages[idx];
    if (stage && stage.route) {
        frappe.set_route(stage.route.replace('/app/', '').split('/'));
    }
};

window.__grcShowStage = function(idx) {
    const stage = LIFECYCLE_DATA.stages[idx];
    const meta = STAGES[idx];
    const detail = document.getElementById('stage-detail');
    if (!detail) return;
    let counts = '';
    if (stage.total > 0) {
        counts = ` <span style="color:var(--text-muted)">(${stage.complete}/${stage.total})</span>`;
    }
    detail.innerHTML =
        `<strong>${stage.id}. ${frappe.utils.escape_html(stage.name)} — ${frappe.utils.escape_html(meta.sub)}${counts}</strong>${frappe.utils.escape_html(meta.detail)}`;
};

function render_stage_list() {
    const list = document.getElementById('stage-list');
    if (!list || !LIFECYCLE_DATA) return;
    list.innerHTML = LIFECYCLE_DATA.stages.map((stage, i) => {
        const colors = STATUS_COLORS[stage.status] || STATUS_COLORS.empty;
        const meta = STAGES[i];
        return `
        <div class="stage-row" onclick="window.__grcGoToStage(${i})">
          <div class="stage-name">
            <span class="stage-num" style="background:${colors.fill};color:${colors.text}">${stage.id}</span>
            <div>
              <div style="font-weight:500">${frappe.utils.escape_html(stage.name)}</div>
              <div style="font-size:10px;color:var(--text-muted)">${frappe.utils.escape_html(meta.sub)}</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px">
            <div class="stage-pb"><div style="width:${stage.pct}%;background:${colors.stroke}"></div></div>
            <span class="stage-pct" style="color:${colors.text}">${stage.total ? stage.pct + '%' : '—'}</span>
          </div>
        </div>`;
    }).join('');
}

function show_firm_overview() {
    frappe.set_route('client_profile_list');
}
