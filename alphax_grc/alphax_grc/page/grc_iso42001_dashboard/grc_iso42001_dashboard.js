// AlphaX GRC v1.7.0 — ISO 42001 Dashboard
// Uses global theme classes from grc_global_theme.css

frappe.pages['grc-iso42001-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('ISO 42001 — AI Management System'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Browse Catalog'),
        () => frappe.set_route('List', 'GRC ISO42001 Catalog'));
    page.add_menu_item(__('Per-Client Tracking'),
        () => frappe.set_route('List', 'GRC ISO42001 Control'));
    page.add_menu_item(__('+ Track new control for client'),
        () => frappe.new_doc('GRC ISO42001 Control'));

    document.getElementById('iso42-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null, selectedDomain: null };

const DOMAIN_COLORS = {
    'A.2': { c1: '#185FA5', c2: '#0F1F40', label: 'AI Policies' },
    'A.3': { c1: '#0F6E56', c2: '#0A4D3C', label: 'Internal Organization' },
    'A.4': { c1: '#854F0B', c2: '#5D3608', label: 'Resources' },
    'A.5': { c1: '#A32D2D', c2: '#791F1F', label: 'Impact Assessment' },
    'A.6': { c1: '#3C3489', c2: '#251E5C', label: 'AI Lifecycle' },
    'A.7': { c1: '#1F7A8C', c2: '#125560', label: 'Data' },
    'A.8': { c1: '#C25C1F', c2: '#8C3F12', label: 'Information' },
    'A.9': { c1: '#5A8C2A', c2: '#3F6219', label: 'Use of AI' },
    'A.10': { c1: '#854F8C', c2: '#5C355F', label: 'Third Parties' },
};

function buildShell() {
    return `
    <style>
      .iso42 { max-width: 1400px; margin: 0 auto; }
      .iso42-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .iso42-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px; min-width: 240px;
      }
      .iso42-domain-card {
        position: relative;
        padding: 16px 14px;
        border-radius: var(--grc-radius-md, 8px);
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s;
        color: white;
        overflow: hidden;
      }
      .iso42-domain-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--grc-shadow-md, 0 2px 8px rgba(0,0,0,.06));
      }
      .iso42-domain-card .num {
        font-size: 32px; font-weight: 600; line-height: 1; margin-bottom: 4px;
      }
      .iso42-domain-card .code {
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: .04em;
        opacity: 0.85; margin-bottom: 4px;
      }
      .iso42-domain-card .lbl {
        font-size: 13px; font-weight: 500; line-height: 1.3;
      }
      .iso42-domain-card .progress-mini {
        margin-top: 10px; height: 4px; border-radius: 2px;
        background: rgba(255,255,255,.2); overflow: hidden;
      }
      .iso42-domain-card .progress-mini > div {
        height: 100%; background: rgba(255,255,255,.85);
      }
      .iso42-controls-table {
        width: 100%; border-collapse: collapse; font-size: 13px;
      }
      .iso42-controls-table th {
        text-align: left; padding: 10px;
        border-bottom: 2px solid var(--grc-secondary, #185FA5);
        color: var(--grc-primary, #0F1F40);
        font-weight: 600; font-size: 11px;
        text-transform: uppercase; letter-spacing: .04em;
      }
      .iso42-controls-table td {
        padding: 10px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.08));
        vertical-align: top;
      }
      .iso42-controls-table tr:hover {
        background: rgba(24, 95, 165, 0.04); cursor: pointer;
      }
      .iso42-controls-table .code {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-size: 11px; font-weight: 600; color: var(--grc-secondary, #185FA5);
      }
      .iso42-doc-pill {
        display: inline-block;
        padding: 2px 8px; border-radius: 4px;
        background: rgba(24, 95, 165, 0.08); color: var(--grc-secondary, #185FA5);
        font-size: 10px; font-weight: 600; font-family: ui-monospace, monospace;
      }
      .iso42-empty {
        text-align: center; padding: 32px;
        color: var(--grc-muted, #687178); font-size: 12px;
      }
    </style>

    <div class="iso42">
      <div class="grc-hero">
        <h2>${__('ISO/IEC 42001:2023 — AI Management System')}</h2>
        <div class="grc-hero-sub">${__('38 controls across 9 domains · evidence document codes (AIMS-XXX-001) for each control · cross-references to related ISO standards')}</div>
        <div class="grc-hero-stats" id="iso42-stats"></div>
      </div>

      <div class="iso42-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="iso42-client-picker">
          <option value="">${__('— Catalog only (no client) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Domains — click any card to drill into its controls')}</h4>
        <div class="grc-card-grid" id="iso42-domain-cards"></div>
      </div>

      <div class="grc-section" id="iso42-drilldown-section" style="display:none">
        <h4 id="iso42-drilldown-title"></h4>
        <div id="iso42-drilldown"></div>
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
                const sel = document.getElementById('iso42-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_iso42001_dashboard.grc_iso42001_dashboard.get_iso42001_dashboard',
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
    renderDomainCards();
    if (STATE.selectedDomain) loadDrilldown(STATE.selectedDomain);
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_controls || 0, lbl: __('Controls') },
        { num: s.domains || 0, lbl: __('Domains') },
        { num: 38, lbl: __('Evidence Docs') },
    ];
    if (STATE.client) {
        stats.push({ num: s.tracked_for_client || 0, lbl: __('Tracked for client') });
    }
    document.getElementById('iso42-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderDomainCards() {
    const domains = STATE.data.domains_rollup || [];
    const impl = STATE.data.domain_implementation || {};
    const tgt = document.getElementById('iso42-domain-cards');

    if (!domains.length) {
        tgt.innerHTML = `<div class="iso42-empty">${__('No catalog data — run bench migrate.')}</div>`;
        return;
    }

    tgt.innerHTML = domains.map(d => {
        const c = DOMAIN_COLORS[d.code] || { c1: '#185FA5', c2: '#0F1F40' };
        const implData = impl[d.code];
        let progress = '';
        let metric = '';
        if (implData && implData.total > 0) {
            const implementedPct = (implData['Implemented'] / implData.total * 100).toFixed(0);
            progress = `<div class="progress-mini"><div style="width:${implementedPct}%"></div></div>`;
            metric = `<div style="font-size:10px;opacity:.85;margin-top:4px;">${implData['Implemented']} of ${implData.total} ${__('implemented')}</div>`;
        }
        return `<div class="iso42-domain-card"
                style="background: linear-gradient(135deg, ${c.c1} 0%, ${c.c2} 100%);"
                onclick="window.__iso42DrillDomain('${d.code}')">
          <div class="code">${frappe.utils.escape_html(d.code)}</div>
          <div class="num">${d.count}</div>
          <div class="lbl">${frappe.utils.escape_html(d.label)}</div>
          ${progress}${metric}
        </div>`;
    }).join('');
}

window.__iso42DrillDomain = function(code) {
    STATE.selectedDomain = code;
    loadDrilldown(code);
};

function loadDrilldown(code) {
    const args = { domain_code: code };
    if (STATE.client) args.client = STATE.client;

    document.getElementById('iso42-drilldown-section').style.display = 'block';
    document.getElementById('iso42-drilldown-title').textContent =
        __('Domain {0} — controls', [code]);
    document.getElementById('iso42-drilldown').innerHTML =
        `<div class="iso42-empty">${__('Loading…')}</div>`;

    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_iso42001_dashboard.grc_iso42001_dashboard.get_domain_controls',
        args,
        callback: (r) => {
            const m = (r && r.message) || {};
            renderDrilldown(m.controls || []);
        },
    });
}

function renderDrilldown(controls) {
    const tgt = document.getElementById('iso42-drilldown');
    if (!controls.length) {
        tgt.innerHTML = `<div class="iso42-empty">${__('No controls in this domain.')}</div>`;
        return;
    }
    tgt.innerHTML = `<table class="iso42-controls-table">
      <thead><tr>
        <th style="width:90px">${__('Code')}</th>
        <th>${__('Control')}</th>
        <th style="width:160px">${__('Doc')}</th>
        <th style="width:120px">${__('Status')}</th>
      </tr></thead>
      <tbody>${controls.map(c => {
        const cs = c.client_status;
        let statusHtml = `<span class="grc-chip grc-chip-untracked">${__('Untracked')}</span>`;
        if (cs) {
            let cls = 'grc-chip-not-impl';
            const s = cs.compliance_status || '';
            if (s.includes('Implemented') && !s.includes('Partial'))     cls = 'grc-chip-implemented';
            else if (s.includes('Partial'))                              cls = 'grc-chip-partial';
            else if (s.includes('Not Applicable'))                       cls = 'grc-chip-not-applic';
            else if (s.includes('In Progress'))                          cls = 'grc-chip-info';
            statusHtml = `<span class="grc-chip ${cls}">${frappe.utils.escape_html(s)}</span>`;
        }
        return `<tr onclick="frappe.set_route('Form', 'GRC ISO42001 Catalog', '${c.name}')">
          <td><span class="code">${frappe.utils.escape_html(c.control_code)}</span></td>
          <td>
            <div style="font-weight:500;color:var(--grc-primary);">${frappe.utils.escape_html(c.control_title)}</div>
            <div style="font-size:11px;color:var(--grc-muted);margin-top:4px;">${frappe.utils.escape_html((c.implementation_guidance || '').substring(0, 180))}${(c.implementation_guidance || '').length > 180 ? '…' : ''}</div>
          </td>
          <td><span class="iso42-doc-pill">${frappe.utils.escape_html(c.document_to_prepare_code || '—')}</span></td>
          <td>${statusHtml}</td>
        </tr>`;
      }).join('')}</tbody>
    </table>`;
}
