// AlphaX GRC — Interactive Risk Dashboard v1.3.2
// Live data via dashboards_live.get_live_dashboard, auto-refresh every 30s,
// realtime invalidation on data change, per-user theme.

frappe.pages['grc-risk-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('GRC Risk Dashboard'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(render_shell());

    // Live indicator pill in the page header
    const $indicator = frappe.alphaxGRC.makeIndicator();
    page.page_actions.prepend($indicator);

    page.set_primary_action(__('Refresh now'),
        () => LIVE && LIVE.forceServerRefresh(), 'refresh');
    page.add_menu_item(__('Customize colours'), () => open_theme_panel());

    // Boot: load theme then start live polling
    load_user_theme().then((theme) => {
        if (theme && Object.keys(theme).length) {
            Object.assign(STATE, theme);
        }
        apply_theme();
        build_colour_rows();
        start_live($indicator);
    });
};

let LIVE = null;
function start_live($indicator) {
    LIVE = frappe.alphaxGRC.live({
        endpoint: 'alphax_grc.dashboards_live.get_live_dashboard',
        // Risk Dashboard has no client picker yet — show firm-wide.
        // Future: add a client picker and return {client: CURRENT_CLIENT}.
        getArgs: () => ({}),
        invalidateOnAnyClient: true,
        indicatorEl: $indicator,
        refreshSeconds: 30,
        onData: (payload) => {
            CURRENT = adapt_payload(payload);
            render_all();
        },
    });
    LIVE.start();
}

// Adapt the new server payload to the structure render_*() functions
// already expect (preserves the existing rendering code).
function adapt_payload(payload) {
    const h = payload.headline || {};
    return {
        kpis: {
            critical_risks: h.critical_risks || 0,
            open_findings:  h.open_findings || 0,
            compliance_score: h.compliance_score || 0,
            overdue_actions:  h.overdue_actions || 0,
        },
        heatmap: payload.heatmap || [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        top_risks: payload.top_risks || [],
        frameworks: payload.by_framework || [],
        kris: payload.kris || [],
        severity: payload.by_severity || {Critical:0, High:0, Medium:0, Low:0},
    };
}

// ---------- Theme ----------

const DEFAULTS = {
    p: '#0B132B', a: '#2563EB', card: '#FFFFFF', bg: '#F8FAFC',
    txt: '#1E293B', mut: '#64748B',
    crit: '#DC2626', high: '#D97706', med: '#F59E0B',
    low: '#16A34A', ok: '#10B981', info: '#0EA5E4',
    hml: '#DCFCE7', hmm: '#FEF3C7', hmh: '#FEE2E2', hmc: '#991B1B',
};

const PRESETS = {
    navy:  { ...DEFAULTS },
    green: { ...DEFAULTS, p:'#064E3B', a:'#059669', info:'#14B8A6' },
    blue:  { ...DEFAULTS, p:'#1E3A8A', a:'#3B82F6' },
    dark:  { ...DEFAULTS, p:'#020617', a:'#60A5FA',
             card:'#1E293B', bg:'#0F172A', txt:'#E2E8F0', mut:'#94A3B8' },
    sand:  { ...DEFAULTS, p:'#78350F', a:'#D97706',
             bg:'#FEF3C7', card:'#FFFBEB', txt:'#451A03' },
};

const STATE = { ...DEFAULTS };

function set_var(key, value) {
    STATE[key] = value;
    document.documentElement.style.setProperty('--alp-' + key, value);
}

function apply_theme() {
    Object.entries(STATE).forEach(([k, v]) => {
        document.documentElement.style.setProperty('--alp-' + k, v);
    });
}

function apply_preset(name) {
    const p = PRESETS[name];
    if (!p) return;
    Object.assign(STATE, p);
    apply_theme();
    build_colour_rows();
    render_all();
    save_theme_debounced();
}

function reset_theme() {
    Object.assign(STATE, DEFAULTS);
    apply_theme();
    build_colour_rows();
    render_all();
    save_theme_debounced();
}

let _save_timer = null;
function save_theme_debounced() {
    clearTimeout(_save_timer);
    _save_timer = setTimeout(() => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_risk_dashboard.grc_risk_dashboard.save_user_theme',
            args: { theme_json: JSON.stringify(STATE) },
            callback: () => {},
        });
    }, 500);
}

function load_user_theme() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_risk_dashboard.grc_risk_dashboard.load_user_theme',
            callback: (r) => resolve((r && r.message) || {}),
        });
    });
}

// ---------- Shell ----------

function render_shell() {
    return `
    <style>
      .grc-dash { font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
        background: var(--alp-bg); color: var(--alp-txt);
        padding: 16px; border-radius: 8px; min-height: 620px;
        position: relative; font-size: 13px; }
      .grc-dash .row-kpi { display: grid; grid-template-columns: repeat(4, 1fr);
        gap: 10px; margin-bottom: 14px; }
      .grc-dash .kpi { background: var(--alp-card);
        border: 1px solid rgba(0,0,0,.08); border-radius: 8px;
        padding: 12px 14px; }
      .grc-dash .kpi-val { font-size: 26px; font-weight: 500; line-height: 1; }
      .grc-dash .kpi-lbl { font-size: 11px; color: var(--alp-mut);
        text-transform: uppercase; letter-spacing: .05em; margin-top: 4px; }
      .grc-dash .row-main { display: grid; grid-template-columns: 1.4fr 1fr;
        gap: 14px; margin-bottom: 14px; }
      .grc-dash .row-three { display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 14px; }
      .grc-dash .card { background: var(--alp-card);
        border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 14px; }
      .grc-dash .card h4 { font-size: 13px; font-weight: 500; margin: 0 0 12px;
        color: var(--alp-txt); }
      .grc-dash .heatmap { display: grid;
        grid-template-columns: auto repeat(5, 1fr); gap: 3px; font-size: 10px; }
      .grc-dash .hm-cell { height: 30px; border-radius: 4px; display: flex;
        align-items: center; justify-content: center;
        font-weight: 500; font-size: 12px; }
      .grc-dash .hm-label { display: flex; align-items: center;
        justify-content: flex-end; padding-right: 6px;
        color: var(--alp-mut); font-size: 10px; }
      .grc-dash .hm-col-label { text-align: center; color: var(--alp-mut);
        padding-bottom: 2px; font-size: 10px; }
      .grc-dash table.rt { width: 100%; border-collapse: collapse;
        font-size: 12px; }
      .grc-dash table.rt th { text-align: left; padding: 6px 8px;
        border-bottom: 1px solid rgba(0,0,0,.08);
        color: var(--alp-mut); font-weight: 500; font-size: 10px;
        text-transform: uppercase; letter-spacing: .04em; }
      .grc-dash table.rt td { padding: 7px 8px;
        border-bottom: 1px solid rgba(0,0,0,.06); }
      .grc-dash .badge { display: inline-block; padding: 2px 8px;
        border-radius: 999px; font-size: 10px; font-weight: 500; }
      .grc-dash .pb { height: 6px; border-radius: 999px;
        background: rgba(0,0,0,.08); overflow: hidden; margin-top: 3px; }
      .grc-dash .pb > div { height: 100%; border-radius: 999px; }
      .grc-dash .kri-row { display: flex; justify-content: space-between;
        align-items: center; padding: 7px 0;
        border-bottom: 1px solid rgba(0,0,0,.06); font-size: 12px; }
      .grc-dash .kri-row:last-child { border-bottom: none; }
      .grc-dash .overlay { display: none; position: absolute; top: 0; left: 0;
        right: 0; bottom: 0; background: rgba(0,0,0,.45); z-index: 10;
        align-items: flex-start; justify-content: center; padding-top: 30px; }
      .grc-dash .panel { background: var(--alp-card); border-radius: 10px;
        padding: 18px 20px; width: 420px; max-height: 85%; overflow-y: auto; }
      .grc-dash .panel h3 { font-size: 15px; font-weight: 500;
        margin: 0 0 16px; }
      .grc-dash .panel .group-lbl { font-size: 11px; text-transform: uppercase;
        letter-spacing: .06em; color: var(--alp-mut);
        margin: 0 0 8px; display: block; }
      .grc-dash .presets { display: flex; gap: 6px; flex-wrap: wrap;
        margin-bottom: 16px; }
      .grc-dash .preset-btn { padding: 5px 12px; border-radius: 999px;
        border: 1px solid rgba(0,0,0,.15); cursor: pointer; font-size: 12px;
        background: transparent; color: var(--alp-txt); }
      .grc-dash .preset-btn:hover { background: rgba(0,0,0,.05); }
      .grc-dash .colour-row { display: flex; align-items: center; gap: 10px;
        margin-bottom: 6px; }
      .grc-dash .colour-row span { flex: 1; font-size: 12px; }
      .grc-dash .colour-row input[type=color] { width: 36px; height: 26px;
        border: 1px solid rgba(0,0,0,.15); border-radius: 4px;
        cursor: pointer; padding: 2px; background: transparent; }
      .grc-dash .close-x { float: right; background: none; border: none;
        cursor: pointer; font-size: 20px; color: var(--alp-mut);
        padding: 0; line-height: 1; margin-top: -2px; }
      .grc-dash .toolbar { display: flex; justify-content: space-between;
        align-items: center; margin-bottom: 14px; }
      .grc-dash .btn-theme { padding: 6px 14px; border-radius: 6px;
        border: 1px solid rgba(0,0,0,.15); background: var(--alp-card);
        color: var(--alp-txt); cursor: pointer; font-size: 12px; }
      .grc-dash .btn-theme:hover { background: rgba(0,0,0,.05); }
      .grc-dash .loading { text-align: center; padding: 40px;
        color: var(--alp-mut); font-size: 13px; }
      .grc-dash .empty { color: var(--alp-mut); font-size: 11px;
        font-style: italic; padding: 8px 0; }
      .grc-dash .row-kpi .pill-c { color: var(--alp-crit); }
      .grc-dash .row-kpi .pill-h { color: var(--alp-high); }
      .grc-dash .row-kpi .pill-o { color: var(--alp-ok); }
      .grc-dash .row-kpi .pill-m { color: var(--alp-med); }
    </style>
    <div class="grc-dash" id="grc-dash-root">
      <div class="toolbar">
        <div>
          <div style="font-size:15px;font-weight:500">${__('Risk Dashboard')}</div>
          <div style="font-size:11px;color:var(--alp-mut);margin-top:2px">
            ${__('Live data from Risk Register, Findings, KRIs & Frameworks')}
          </div>
        </div>
        <button class="btn-theme" onclick="window.__grcOpenTheme()">
          ${__('Customize colours')}
        </button>
      </div>
      <div class="row-kpi">
        <div class="kpi"><div class="kpi-val pill-c" id="kpi-crit">–</div>
          <div class="kpi-lbl">${__('Critical Risks')}</div></div>
        <div class="kpi"><div class="kpi-val pill-h" id="kpi-find">–</div>
          <div class="kpi-lbl">${__('Open Findings')}</div></div>
        <div class="kpi"><div class="kpi-val pill-o" id="kpi-comp">–</div>
          <div class="kpi-lbl">${__('Compliance Score')}</div></div>
        <div class="kpi"><div class="kpi-val pill-m" id="kpi-over">–</div>
          <div class="kpi-lbl">${__('Overdue Actions')}</div></div>
      </div>
      <div class="row-main">
        <div class="card"><h4>${__('Risk Heatmap — 5×5 Matrix')}</h4>
          <div id="heatmap"></div></div>
        <div class="card"><h4>${__('Top Open Risks')}</h4>
          <table class="rt" id="risk-table"></table></div>
      </div>
      <div class="row-three">
        <div class="card"><h4>${__('Framework Compliance')}</h4>
          <div id="frameworks"></div></div>
        <div class="card"><h4>${__('KRI Status')}</h4>
          <div id="kris"></div></div>
        <div class="card"><h4>${__('Findings by Severity')}</h4>
          <div id="severity"></div></div>
      </div>

      <div class="overlay" id="theme-overlay">
        <div class="panel">
          <button class="close-x" onclick="window.__grcCloseTheme()">×</button>
          <h3>${__('Colour Settings')}</h3>
          <span class="group-lbl">${__('Theme preset')}</span>
          <div class="presets">
            <button class="preset-btn" onclick="window.__grcPreset('navy')">
              ${__('AlphaX Navy')}</button>
            <button class="preset-btn" onclick="window.__grcPreset('green')">
              ${__('Saudi Green')}</button>
            <button class="preset-btn" onclick="window.__grcPreset('blue')">
              ${__('Corporate Blue')}</button>
            <button class="preset-btn" onclick="window.__grcPreset('dark')">
              ${__('Dark Mode')}</button>
            <button class="preset-btn" onclick="window.__grcPreset('sand')">
              ${__('Sand & Gold')}</button>
            <button class="preset-btn" onclick="window.__grcReset()">
              ${__('Reset')}</button>
          </div>
          <span class="group-lbl">${__('Global colours')}</span>
          <div id="cg-global"></div>
          <span class="group-lbl" style="margin-top:12px">
            ${__('Risk level colours')}</span>
          <div id="cg-risk"></div>
          <span class="group-lbl" style="margin-top:12px">
            ${__('Heatmap cell colours')}</span>
          <div id="cg-heat"></div>
          <div style="margin-top:14px;padding-top:10px;border-top:1px solid rgba(0,0,0,.08);font-size:11px;color:var(--alp-mut)">
            ${__('Theme is saved per user — your colleagues see their own.')}
          </div>
        </div>
      </div>
    </div>`;
}

// Expose handler functions for inline onclick (Frappe pages can't use event
// delegation reliably across bench refreshes).
window.__grcOpenTheme  = open_theme_panel;
window.__grcCloseTheme = close_theme_panel;
window.__grcPreset     = apply_preset;
window.__grcReset      = reset_theme;

function open_theme_panel()  { document.getElementById('theme-overlay').style.display = 'flex'; }
function close_theme_panel() { document.getElementById('theme-overlay').style.display = 'none'; }

// ---------- Colour pickers ----------

const GLOBAL_KEYS = [['p','Primary (sidebar / header)'], ['a','Accent / action'],
    ['card','Card background'], ['bg','Page background'],
    ['txt','Body text'], ['mut','Muted text']];
const RISK_KEYS = [['crit','Critical'], ['high','High'], ['med','Medium'],
    ['low','Low'], ['ok','OK / success'], ['info','Info / neutral']];
const HEAT_KEYS = [['hml','Low cells'], ['hmm','Medium cells'],
    ['hmh','High cells'], ['hmc','Critical cells']];

function build_colour_rows() {
    const row = ([k, label]) => `
      <div class="colour-row">
        <span>${__(label)}</span>
        <input type="color" value="${STATE[k]}"
               oninput="window.__grcSetVar('${k}', this.value)">
      </div>`;
    const g = document.getElementById('cg-global');
    const r = document.getElementById('cg-risk');
    const h = document.getElementById('cg-heat');
    if (!g || !r || !h) return;
    g.innerHTML = GLOBAL_KEYS.map(row).join('');
    r.innerHTML = RISK_KEYS.map(row).join('');
    h.innerHTML = HEAT_KEYS.map(row).join('');
}

window.__grcSetVar = (key, value) => {
    set_var(key, value);
    render_all();
    save_theme_debounced();
};

// ---------- Data load ----------

let CURRENT = null;

function empty_data() {
    return {
        kpis: {critical_risks:0, open_findings:0, compliance_score:0, overdue_actions:0},
        heatmap: [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        top_risks: [], frameworks: [], kris: [],
        severity: {Critical:0, High:0, Medium:0, Low:0},
    };
}

// ---------- Render ----------

const ROW_LABELS = ['Very low','Low','Medium','High','Very high'];
const COL_LABELS = ['Negligible','Minor','Moderate','Major','Catastrophic'];

function hm_colour(score) {
    if (score >= 20) return STATE.hmc;
    if (score >= 12) return STATE.hmh;
    if (score >= 6)  return STATE.hmm;
    return STATE.hml;
}

function text_on(bg) {
    const hex = bg.replace('#', '');
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return (r * 0.299 + g * 0.587 + b * 0.114) > 140 ? STATE.txt : '#fff';
}

function draw_heatmap() {
    const el = document.getElementById('heatmap');
    if (!el || !CURRENT) return;
    let h = '<div class="heatmap"><div></div>';
    COL_LABELS.forEach(l => {
        h += `<div class="hm-col-label">${__(l)}</div>`;
    });
    for (let ri = 0; ri < 5; ri++) {
        h += `<div class="hm-label">${__(ROW_LABELS[ri])}</div>`;
        for (let ci = 0; ci < 5; ci++) {
            const score = (ri + 1) * (ci + 1);
            const bg = hm_colour(score);
            const cnt = CURRENT.heatmap[ri][ci];
            h += `<div class="hm-cell" style="background:${bg};color:${text_on(bg)}">${cnt > 0 ? cnt : ''}</div>`;
        }
    }
    h += '</div>';
    el.innerHTML = h;
}

function rating_colour(r) {
    return r === 'Critical' ? STATE.crit :
           r === 'High'     ? STATE.high :
           r === 'Medium'   ? STATE.med  : STATE.low;
}

function draw_kpis() {
    if (!CURRENT) return;
    const k = CURRENT.kpis;
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set('kpi-crit', k.critical_risks);
    set('kpi-find', k.open_findings);
    set('kpi-comp', (k.compliance_score || 0) + '%');
    set('kpi-over', k.overdue_actions);
}

function draw_risks() {
    const el = document.getElementById('risk-table');
    if (!el || !CURRENT) return;
    if (!CURRENT.top_risks.length) {
        el.innerHTML = `<tbody><tr><td class="empty">${__('No open risks.')}</td></tr></tbody>`;
        return;
    }
    const head = `<thead><tr>
      <th>${__('Risk')}</th><th>${__('Score')}</th><th>${__('Rating')}</th>
    </tr></thead>`;
    const body = CURRENT.top_risks.map(r => {
        const col = rating_colour(r.rating);
        const safeTitle = frappe.utils.escape_html(r.title || '');
        const safeRating = frappe.utils.escape_html(r.rating || '');
        return `<tr>
          <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
            <a href="/app/grc-risk-register/${encodeURIComponent(r.name)}"
               style="color:var(--alp-txt)">${safeTitle}</a>
          </td>
          <td><strong>${r.score}</strong></td>
          <td><span class="badge" style="background:${col}22;color:${col}">${safeRating}</span></td>
        </tr>`;
    }).join('');
    el.innerHTML = head + '<tbody>' + body + '</tbody>';
}

function draw_frameworks() {
    const el = document.getElementById('frameworks');
    if (!el || !CURRENT) return;
    if (!CURRENT.frameworks.length) {
        el.innerHTML = `<div class="empty">${__('No frameworks defined.')}</div>`;
        return;
    }
    el.innerHTML = CURRENT.frameworks.map(f => {
        const col = f.score >= 70 ? STATE.ok : f.score >= 50 ? STATE.med : STATE.crit;
        const name = frappe.utils.escape_html(f.name || '');
        return `
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
            <span>${name}</span>
            <span style="color:${col};font-weight:500">${f.score}%</span>
          </div>
          <div class="pb"><div style="width:${f.score}%;background:${col}"></div></div>
        </div>`;
    }).join('');
}

function kri_colour(s) {
    return s === 'Breach' ? STATE.crit :
           s === 'Warn'   ? STATE.high :
           s === 'Alert'  ? STATE.med  : STATE.ok;
}

function draw_kris() {
    const el = document.getElementById('kris');
    if (!el || !CURRENT) return;
    if (!CURRENT.kris.length) {
        el.innerHTML = `<div class="empty">${__('No KRIs defined.')}</div>`;
        return;
    }
    el.innerHTML = CURRENT.kris.map(k => {
        const col = kri_colour(k.status);
        const name = frappe.utils.escape_html(k.name || '');
        const cur  = frappe.utils.escape_html(String(k.current || ''));
        const thr  = frappe.utils.escape_html(String(k.threshold || ''));
        const st   = frappe.utils.escape_html(k.status || 'OK');
        return `<div class="kri-row">
          <span style="flex:1">${name}</span>
          <span style="color:var(--alp-mut);margin:0 8px;font-size:11px">${cur} / ${thr}</span>
          <span class="badge" style="background:${col}22;color:${col}">${st}</span>
        </div>`;
    }).join('');
}

function draw_severity() {
    const el = document.getElementById('severity');
    if (!el || !CURRENT) return;
    const order = [['Critical','crit'],['High','high'],['Medium','med'],['Low','low']];
    const max = Math.max(1, ...order.map(([n]) => CURRENT.severity[n] || 0));
    el.innerHTML = order.map(([label, key]) => {
        const v = CURRENT.severity[label] || 0;
        const col = STATE[key];
        return `<div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
            <span>${__(label)}</span>
            <span style="color:${col};font-weight:500">${v}</span>
          </div>
          <div class="pb"><div style="width:${(v/max*100).toFixed(0)}%;background:${col}"></div></div>
        </div>`;
    }).join('');
}

function render_all() {
    draw_kpis();
    draw_heatmap();
    draw_risks();
    draw_frameworks();
    draw_kris();
    draw_severity();
}
