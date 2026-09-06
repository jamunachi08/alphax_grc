// AlphaX GRC v2.1.0 — NIST CSF 2.0 Dashboard
// Six function cards (GV/ID/PR/DE/RS/RC) with tier breakdown and avg score.

frappe.pages['grc-nist-csf-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('NIST CSF 2.0 Dashboard'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Browse NIST CSF Catalog'),
        () => frappe.set_route('List', 'GRC NIST CSF Catalog'));
    page.add_menu_item(__('Per-client NIST CSF Tracking'),
        () => frappe.set_route('List', 'GRC NIST CSF Control'));

    document.getElementById('csf-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null };

const FUNCTION_COLORS = {
    'GV': '#714B67',  // Govern — primary mauve (the new function in 2.0)
    'ID': '#185FA5',  // Identify — blue
    'PR': '#5BA52A',  // Protect — green
    'DE': '#C9A227',  // Detect — gold
    'RS': '#A32D2D',  // Respond — red
    'RC': '#5B3A52',  // Recover — secondary mauve
};

function buildShell() {
    return `
    <style>
      .csf { max-width: 1400px; margin: 0 auto; }
      .csf-toolbar { padding: 0 0 14px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
      .csf-toolbar select {
        padding:7px 12px; border-radius:8px;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        background:white; font-size:12px; min-width:200px;
      }
      .csf-fn-grid {
        display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
        gap:12px; margin-top:14px;
      }
      .csf-fn-card {
        background:white;
        border:1px solid var(--grc-border, rgba(0,0,0,.08));
        border-left-width:4px;
        border-radius:10px;
        padding:18px;
        cursor:pointer;
        transition: transform 0.15s, box-shadow 0.15s;
      }
      .csf-fn-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
      }
      .csf-fn-code {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-size: 22px; font-weight: 700;
        letter-spacing: 0.05em;
      }
      .csf-fn-label {
        font-size:14px; font-weight:600;
        color: var(--grc-primary, #714B67);
        margin: 6px 0;
      }
      .csf-fn-meta {
        font-size: 11px; color: var(--grc-muted, #7A6A78);
        margin: 4px 0 12px;
      }
      .csf-tier-bar {
        display:flex; height:6px; border-radius:3px; overflow:hidden;
        background: rgba(0,0,0,0.04); margin: 8px 0;
      }
      .csf-tier-seg { height:100%; transition: flex 0.4s; }
      .csf-score {
        font-size: 24px; font-weight: 700;
        margin-top: 8px;
      }
      .csf-score-label {
        font-size: 10px; color: var(--grc-muted);
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      .csf-tier-legend {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 4px; margin-top: 10px;
        font-size: 10px;
      }
      .csf-tier-legend-item {
        display: flex; align-items: center; gap: 5px;
      }
      .csf-tier-dot {
        width: 8px; height: 8px; border-radius: 50%;
      }
    </style>

    <div class="csf">
      <div class="grc-hero">
        <h2>${__('NIST CSF 2.0 Dashboard')}</h2>
        <div class="grc-hero-sub">${__('Six functions, twenty-two categories, 106 subcategories. NIST CSF 2.0 introduces Govern as a new function — the first major structural change since the framework launched in 2014.')}</div>
        <div class="grc-hero-stats" id="csf-stats"></div>
      </div>

      <div class="csf-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="csf-client-picker">
          <option value="">${__('— All clients (catalog totals only) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Functions')}</h4>
        <div class="csf-fn-grid" id="csf-fn-grid"></div>
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
            const sel = document.getElementById('csf-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_nist_csf_dashboard.grc_nist_csf_dashboard.get_dashboard',
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
    renderFunctions();
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_subcategories || 0, lbl: __('Subcategories') },
        { num: s.total_functions || 0, lbl: __('Functions') },
        { num: s.tracked_overall || 0, lbl: __('Tracked Records') },
        { num: STATE.client ? '1' : __('All'), lbl: __('Client Scope') },
    ];
    document.getElementById('csf-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderFunctions() {
    const fns = STATE.data.functions || [];
    const tgt = document.getElementById('csf-fn-grid');
    if (!fns.length) {
        tgt.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--grc-muted);">${__('NIST CSF catalog has not been seeded yet. Run migrate to load it.')}</div>`;
        return;
    }
    tgt.innerHTML = fns.map(fn => {
        const color = FUNCTION_COLORS[fn.code] || '#714B67';
        const tiers = fn.tier_breakdown || {};
        const tierTotal = Object.values(tiers).reduce((a,b) => a+b, 0);
        const tierColors = {
            'Tier 1: Partial':       '#D9A632',
            'Tier 2: Risk Informed': '#C9A227',
            'Tier 3: Repeatable':    '#5BA52A',
            'Tier 4: Adaptive':      '#185FA5',
            'Not Assessed':          '#9C9C9C',
        };
        const tierBar = tierTotal > 0
            ? Object.entries(tierColors).map(([t,c]) => {
                const cnt = tiers[t] || 0;
                const pct = (cnt / tierTotal) * 100;
                return cnt > 0 ? `<div class="csf-tier-seg" style="flex:${pct};background:${c};"></div>` : '';
              }).join('')
            : '<div class="csf-tier-seg" style="flex:1;background:rgba(0,0,0,0.06);"></div>';
        const legend = Object.entries(tierColors).map(([t,c]) => {
            const cnt = tiers[t] || 0;
            if (!cnt && tierTotal > 0) return '';
            return `<div class="csf-tier-legend-item"><span class="csf-tier-dot" style="background:${c};"></span>${t.replace('Tier ', 'T')}: ${cnt}</div>`;
        }).filter(s => s).join('');
        const navTarget = STATE.client
            ? () => frappe.set_route('List', 'GRC NIST CSF Control', { 'function_code': fn.code, 'client': STATE.client })
            : () => frappe.set_route('List', 'GRC NIST CSF Catalog', { 'function_code': fn.code });
        return `<div class="csf-fn-card" style="border-left-color:${color};" onclick='(${navTarget.toString()})()'>
          <div class="csf-fn-code" style="color:${color};">${fn.code}</div>
          <div class="csf-fn-label">${frappe.utils.escape_html(fn.label)}</div>
          <div class="csf-fn-meta">${fn.total_subcategories} ${__('subcategories')} · ${fn.category_count} ${__('categories')}</div>
          ${tierTotal > 0 ? `<div class="csf-tier-bar">${tierBar}</div>` : ''}
          ${tierTotal > 0 ? `<div class="csf-tier-legend">${legend}</div>` : `<div style="font-size:10px;color:var(--grc-muted);text-align:center;padding:6px 0;">${__('Not yet tracked for this client')}</div>`}
          ${tierTotal > 0 ? `<div class="csf-score" style="color:${color};">${fn.avg_score}%<span class="csf-score-label" style="margin-left:6px;">${__('avg implementation')}</span></div>` : ''}
        </div>`;
    }).join('');
}
