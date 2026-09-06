// AlphaX GRC v1.4.3 — Aramco CCC Dashboard
// Hero strip · stage breakdown · certificate expiry table · client filter

frappe.pages['grc-aramco-ccc'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Aramco CCC'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    const $indicator = frappe.alphaxGRC.makeIndicator
        ? frappe.alphaxGRC.makeIndicator() : null;
    if ($indicator) page.page_actions.prepend($indicator);

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('+ New CCC Engagement'),
        () => frappe.new_doc('GRC Aramco CCC Engagement'));
    page.add_menu_item(__('+ New Certificate'),
        () => frappe.new_doc('GRC Aramco Certificate'));
    page.add_menu_item(__('Audit Firm Directory'),
        () => frappe.set_route('List', 'GRC Aramco Audit Firm'));
    page.add_menu_item(__('SACS-002 Control Library'),
        () => frappe.set_route('List', 'GRC Aramco SACS002 Control'));

    document.getElementById('aramco-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', data: null, clients: [] };

const CCC_STAGES = [
    {id: 1, name: 'Scoping',          sub: 'Service class & tier',    detail: 'Determine which CCC service classes apply (network connectivity, infrastructure, data processor, software, cloud) and assign vendor tier (Critical / High / Medium / Low).'},
    {id: 2, name: 'Self-Assessment',  sub: 'SACS-002 controls',       detail: 'Vendor completes self-assessment against applicable SACS-002 controls. Evidence uploaded per control.'},
    {id: 3, name: 'Audit Scheduled',  sub: 'Accredited firm booked',  detail: 'Independent assessment scheduled with an Aramco-accredited audit firm. Lead assessor named.'},
    {id: 4, name: 'Audit In Progress',sub: 'Fieldwork',               detail: 'Audit firm performs fieldwork: inspection, inquiry, sample testing, evidence review.'},
    {id: 5, name: 'Findings',         sub: 'Gaps identified',         detail: 'Audit findings raised. Severity classified. Owner assigned per finding.'},
    {id: 6, name: 'Remediation',      sub: 'Close gaps',              detail: 'Remediation actions tracked to closure. Re-test of controls after fixes deployed.'},
    {id: 7, name: 'Certified',        sub: 'CCC issued',              detail: 'Certificate issued by Aramco. Issue date, expiry date, scope statement, certificate number recorded.'},
    {id: 8, name: 'Renewal Due',      sub: '180 days before expiry',  detail: 'Renewal cycle auto-triggers at 180 days. Email alerts at 180/90/30/0 days before expiry.'},
];

const STAGE_TO_STATUSES = {
    'Scoping':           ['Scoping'],
    'Self-Assessment':   ['Self-Assessment'],
    'Audit Scheduled':   ['Audit Scheduled'],
    'Audit In Progress': ['Audit In Progress'],
    'Findings':          ['Findings'],
    'Remediation':       ['Remediation'],
    'Certified':         ['Certified'],
    'Renewal Due':       ['Renewal Due', 'Lapsed'],
};

const STATUS_COLORS = {
    'Scoping':            {bg: '#E6F1FB', fg: '#0C447C'},
    'Self-Assessment':    {bg: '#FAEEDA', fg: '#854F0B'},
    'Audit Scheduled':    {bg: '#EEEDFE', fg: '#3C3489'},
    'Audit In Progress':  {bg: '#EEEDFE', fg: '#3C3489'},
    'Findings':           {bg: '#FCEBEB', fg: '#791F1F'},
    'Remediation':        {bg: '#FAEEDA', fg: '#633806'},
    'Certified':          {bg: '#EAF3DE', fg: '#27500A'},
    'Renewal Due':        {bg: '#FAEEDA', fg: '#854F0B'},
    'Lapsed':             {bg: '#FCEBEB', fg: '#791F1F'},
    'Active':             {bg: '#EAF3DE', fg: '#27500A'},
    'Expiring Soon':      {bg: '#FAEEDA', fg: '#854F0B'},
    'Pending Renewal':    {bg: '#FAEEDA', fg: '#854F0B'},
    'Expired':            {bg: '#FCEBEB', fg: '#791F1F'},
    'Revoked':            {bg: '#F1EFE8', fg: '#5F5E5A'},
};

function buildShell() {
    return `
    <style>
      .acc {
        --acc-bg: var(--bg-color, #fff);
        --acc-fg: var(--text-color, #1f272e);
        --acc-muted: var(--text-muted, #687178);
        --acc-border: var(--border-color, rgba(0,0,0,.08));
        --acc-card-bg: var(--card-bg, #fff);
        font-family: var(--font-stack, system-ui, -apple-system, 'Segoe UI', sans-serif);
        font-size: 13px; color: var(--acc-fg); max-width: 1400px; margin: 0 auto;
      }
      .acc-hero {
        background: linear-gradient(135deg, #00553C 0%, #185FA5 100%);
        color: white; padding: 24px 28px; border-radius: 14px;
        margin: 12px 12px 18px;
      }
      .acc-hero h2 { margin: 0 0 4px; font-size: 18px; font-weight: 600; color: white; }
      .acc-hero .sub { font-size: 12px; opacity: 0.85; margin-bottom: 16px; }
      .acc-stats { display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
      .acc-stat { background: rgba(255,255,255,.12); padding: 10px 12px;
        border-radius: 8px; }
      .acc-stat .num { font-size: 22px; font-weight: 600; line-height: 1; color: white; }
      .acc-stat .lbl { font-size: 10px; opacity: 0.85; text-transform: uppercase;
        letter-spacing: .04em; margin-top: 4px; }
      .acc-toolbar {
        padding: 0 16px 14px; display: flex; gap: 10px; align-items: center;
        flex-wrap: wrap;
      }
      .acc-toolbar select {
        padding: 8px 12px; border-radius: 8px; border: 1px solid var(--acc-border);
        background: var(--acc-card-bg); color: var(--acc-fg); font-size: 12px;
        min-width: 240px;
      }
      .acc-section {
        background: var(--acc-card-bg); border: 1px solid var(--acc-border);
        border-radius: 10px; padding: 14px; margin: 0 16px 16px;
      }
      .acc-section h4 { font-size: 13px; font-weight: 500; margin: 0 0 12px;
        text-transform: uppercase; letter-spacing: .04em; color: var(--acc-muted); }
      .acc-grid { display: grid; gap: 10px;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
      .acc-pill {
        background: rgba(0,0,0,.04); padding: 10px 12px; border-radius: 8px;
      }
      .acc-pill .num { font-size: 18px; font-weight: 500; line-height: 1; }
      .acc-pill .lbl { font-size: 10px; color: var(--acc-muted);
        text-transform: uppercase; margin-top: 4px; }
      .acc-table {
        width: 100%; border-collapse: collapse; font-size: 12px;
      }
      .acc-table th {
        text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--acc-border);
        color: var(--acc-muted); font-weight: 500; font-size: 11px;
        text-transform: uppercase; letter-spacing: .04em;
      }
      .acc-table td {
        padding: 8px 10px; border-bottom: 1px solid var(--acc-border);
      }
      .acc-table tr:hover { background: rgba(0,0,0,.02); cursor: pointer; }
      .acc-status-chip {
        display: inline-block; padding: 2px 8px; border-radius: 999px;
        font-size: 10px; font-weight: 500;
      }
      .acc-tier-chip {
        display: inline-block; padding: 2px 6px; border-radius: 4px;
        font-size: 10px; background: rgba(0,0,0,.06); color: var(--acc-fg);
      }
      .acc-days-num { font-variant-numeric: tabular-nums; font-weight: 500; }
      .acc-days-num.danger { color: #A32D2D; }
      .acc-days-num.warn { color: #854F0B; }
      .acc-days-num.ok { color: #0F6E56; }
      .acc-empty { text-align: center; padding: 32px; color: var(--acc-muted);
        font-size: 12px; }

      .acc-stage-detail {
        padding: 12px 14px; background: rgba(0,0,0,.04);
        border-radius: 8px; margin-bottom: 12px; min-height: 60px;
        font-size: 12px; color: var(--acc-muted); line-height: 1.5;
      }
      .acc-stage-detail strong {
        color: var(--acc-fg); font-weight: 500;
        display: block; margin-bottom: 4px; font-size: 13px;
      }
      .acc-stage-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 0; border-bottom: 1px solid var(--acc-border);
        cursor: pointer; transition: background .15s;
      }
      .acc-stage-row:hover { background: rgba(0,0,0,.02); }
      .acc-stage-row:last-child { border-bottom: none; }
      .acc-stage-row .name { display: flex; align-items: center; gap: 8px; }
      .acc-stage-row .num {
        width: 18px; height: 18px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 9px; font-weight: 500;
      }
      .acc-stage-row .pb {
        width: 60px; height: 5px; border-radius: 999px;
        background: rgba(0,0,0,.08); overflow: hidden;
      }
      .acc-stage-row .pb > div { height: 100%; border-radius: 999px; }
      .acc-stage-row .count {
        font-size: 11px; font-weight: 500; min-width: 28px;
        text-align: right; font-variant-numeric: tabular-nums;
      }
      @media (max-width: 900px) {
        .acc-section [style*="grid-template-columns"] {
          grid-template-columns: 1fr !important;
        }
      }
    </style>

    <div class="acc">
      <div class="acc-hero">
        <h2>${__('Saudi Aramco — Cybersecurity Compliance Certificate')}</h2>
        <div class="sub">${__('CCC engagement and certificate lifecycle, scoped to a client or firm-wide')}</div>
        <div class="acc-stats" id="acc-stats"></div>
      </div>

      <div class="acc-toolbar">
        <label style="font-size:12px;color:var(--acc-muted)">${__('Client:')}</label>
        <select id="aramco-client-picker">
          <option value="">${__('— Firm-wide —')}</option>
        </select>
      </div>

      <div class="acc-section">
        <h4>${__('Engagements by stage')}</h4>
        <div class="acc-grid" id="acc-stage-grid"></div>
      </div>

      <div class="acc-section">
        <h4>${__('CCC lifecycle process')}</h4>
        <div style="display:grid;grid-template-columns:1fr 280px;gap:16px;align-items:start">
          <div id="acc-wheel-container"></div>
          <div>
            <div class="acc-stage-detail" id="acc-stage-detail">
              ${__('Hover any stage to see what it covers. Click to drill into the matching list, filtered to your client.')}
            </div>
            <div id="acc-stage-list"></div>
          </div>
        </div>
      </div>

      <div class="acc-section">
        <h4>${__('Active engagements')}</h4>
        <div id="acc-engagements-table"></div>
      </div>

      <div class="acc-section">
        <h4>${__('Certificates — sorted by expiry')}</h4>
        <div id="acc-certs-table"></div>
      </div>
    </div>`;
}

function loadClients() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.doctype.grc_client_profile.grc_client_profile.get_active_clients',
            callback: (r) => {
                STATE.clients = (r && r.message) || [];
                const sel = document.getElementById('aramco-client-picker');
                STATE.clients.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.name;
                    opt.textContent = `${c.client_name} — ${c.country}`;
                    sel.appendChild(opt);
                });
                resolve();
            },
        });
    });
}

function loadAll() {
    const args = STATE.client ? { client: STATE.client } : {};
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_aramco_ccc.grc_aramco_ccc.get_aramco_ccc_dashboard',
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
    renderStageGrid();
    renderWheel();
    renderStageList();
    renderEngagementsTable();
    renderCertsTable();
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_engagements || 0, lbl: __('Engagements') },
        { num: s.total_certificates || 0, lbl: __('Certificates') },
        { num: s.active_certificates || 0, lbl: __('Active') },
        { num: s.expiring_30 || 0, lbl: __('Expiring 30 days') },
        { num: s.expiring_90 || 0, lbl: __('Expiring 90 days') },
        { num: s.expired || 0, lbl: __('Expired') },
    ];
    document.getElementById('acc-stats').innerHTML = stats.map(x =>
        `<div class="acc-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderStageGrid() {
    const by = STATE.data.summary.by_status || {};
    const order = ['Scoping','Self-Assessment','Audit Scheduled','Audit In Progress',
                   'Findings','Remediation','Certified','Renewal Due','Lapsed'];
    const html = order.map(s => {
        const count = by[s] || 0;
        const colors = STATUS_COLORS[s] || {bg:'#F1EFE8', fg:'#5F5E5A'};
        return `<div class="acc-pill" style="background:${colors.bg}; color:${colors.fg}">
            <div class="num">${count}</div>
            <div class="lbl">${frappe.utils.escape_html(s)}</div>
        </div>`;
    }).join('');
    document.getElementById('acc-stage-grid').innerHTML = html;
}

function renderEngagementsTable() {
    const rows = STATE.data.engagements || [];
    const tgt = document.getElementById('acc-engagements-table');
    if (!rows.length) {
        tgt.innerHTML = `<div class="acc-empty">${__('No engagements yet — click + New CCC Engagement.')}</div>`;
        return;
    }
    const headers = ['Engagement', 'Client', 'Vendor', 'Tier', 'Status', 'Compliance', 'Open Findings', 'Lead'];
    tgt.innerHTML = `<table class="acc-table">
        <thead><tr>${headers.map(h => `<th>${__(h)}</th>`).join('')}</tr></thead>
        <tbody>${rows.map(r => {
            const colors = STATUS_COLORS[r.engagement_status] || {bg:'#F1EFE8', fg:'#5F5E5A'};
            return `<tr onclick="frappe.set_route('Form', 'GRC Aramco CCC Engagement', '${r.name}')">
                <td><b>${frappe.utils.escape_html(r.engagement_title || r.name)}</b></td>
                <td>${frappe.utils.escape_html(r.client || '—')}</td>
                <td>${frappe.utils.escape_html(r.third_party_profile || '—')}</td>
                <td><span class="acc-tier-chip">${frappe.utils.escape_html(r.service_class_tier || '—')}</span></td>
                <td><span class="acc-status-chip" style="background:${colors.bg};color:${colors.fg}">${frappe.utils.escape_html(r.engagement_status || '—')}</span></td>
                <td>${r.compliance_percentage || 0}%</td>
                <td>${r.audit_findings_open || 0}</td>
                <td>${frappe.utils.escape_html(r.lead_consultant || '—')}</td>
            </tr>`;
        }).join('')}</tbody>
    </table>`;
}

function renderCertsTable() {
    const rows = STATE.data.certificates || [];
    const tgt = document.getElementById('acc-certs-table');
    if (!rows.length) {
        tgt.innerHTML = `<div class="acc-empty">${__('No certificates yet.')}</div>`;
        return;
    }
    const headers = ['Cert #', 'Vendor', 'Tier', 'Issue', 'Expiry', 'Days', 'Status', 'Audit Firm'];
    tgt.innerHTML = `<table class="acc-table">
        <thead><tr>${headers.map(h => `<th>${__(h)}</th>`).join('')}</tr></thead>
        <tbody>${rows.map(r => {
            const colors = STATUS_COLORS[r.status] || {bg:'#F1EFE8', fg:'#5F5E5A'};
            const days = r.days_to_expiry;
            const daysClass = days === null || days === undefined ? '' :
                days < 0 ? 'danger' : days <= 30 ? 'danger' :
                days <= 90 ? 'warn' : 'ok';
            return `<tr onclick="frappe.set_route('Form', 'GRC Aramco Certificate', '${r.name}')">
                <td><b>${frappe.utils.escape_html(r.certificate_number || r.name)}</b></td>
                <td>${frappe.utils.escape_html(r.third_party_profile || '—')}</td>
                <td><span class="acc-tier-chip">${frappe.utils.escape_html(r.service_class_tier || '—')}</span></td>
                <td>${r.issue_date || '—'}</td>
                <td>${r.expiry_date || '—'}</td>
                <td><span class="acc-days-num ${daysClass}">${days !== null && days !== undefined ? days : '—'}</span></td>
                <td><span class="acc-status-chip" style="background:${colors.bg};color:${colors.fg}">${frappe.utils.escape_html(r.status || '—')}</span></td>
                <td>${frappe.utils.escape_html(r.audit_firm || '—')}</td>
            </tr>`;
        }).join('')}</tbody>
    </table>`;
}

// ---------------------------------------------------------------------------
// Process wheel — clickable 8-stage CCC lifecycle with drilldown
// ---------------------------------------------------------------------------

function _stageStatusColor(count, total) {
    // Map (count, total) → red/amber/green/empty
    if (total === 0) return STATUS_COLORS['Scoping'];  // neutral blue
    if (count === 0) return {bg: '#F1EFE8', fg: '#5F5E5A'};  // empty
    const pct = total > 0 ? (count / total) * 100 : 0;
    if (pct >= 50) return {bg: '#EAF3DE', fg: '#27500A'};  // green
    if (pct >= 20) return {bg: '#FAEEDA', fg: '#854F0B'};  // amber
    return {bg: '#FCEBEB', fg: '#791F1F'};  // red
}

function renderWheel() {
    const container = document.getElementById('acc-wheel-container');
    if (!container) return;

    const byStatus = (STATE.data && STATE.data.summary && STATE.data.summary.by_status) || {};
    const totalEngagements = Object.values(byStatus).reduce((a, b) => a + b, 0);

    // Compute per-stage count
    const stageCounts = CCC_STAGES.map(s => {
        const statuses = STAGE_TO_STATUSES[s.name] || [s.name];
        return statuses.reduce((sum, st) => sum + (byStatus[st] || 0), 0);
    });

    const cx = 220, cy = 200, r = 130, W = 440, H = 400;
    let svg = `<svg width="100%" viewBox="0 0 ${W} ${H}" style="max-width:480px;display:block;margin:auto">
        <defs>
            <marker id="ccc-arrow" viewBox="0 0 10 10" refX="8" refY="5"
                markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
                    stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </marker>
        </defs>`;

    // Centre disc with current scope
    const scopeLabel = STATE.client
        ? (STATE.clients.find(c => c.name === STATE.client) || {}).client_name || STATE.client
        : __('All clients');
    const scopeSub = totalEngagements + ' ' + __('engagements');
    svg += `<circle cx="${cx}" cy="${cy}" r="55" fill="rgba(0,0,0,.04)"
            stroke="rgba(0,0,0,.1)" stroke-width="0.5"/>`;
    svg += `<text x="${cx}" y="${cy - 6}" text-anchor="middle" font-size="11"
            font-weight="500" fill="var(--acc-fg)">${frappe.utils.escape_html(String(scopeLabel).substring(0, 20))}</text>`;
    svg += `<text x="${cx}" y="${cy + 10}" text-anchor="middle" font-size="9"
            fill="var(--acc-muted)">${frappe.utils.escape_html(scopeSub.substring(0, 28))}</text>`;
    svg += `<text x="${cx}" y="${cy + 26}" text-anchor="middle" font-size="9"
            fill="var(--acc-muted)" opacity="0.7">CCC Lifecycle</text>`;

    // Stage nodes
    CCC_STAGES.forEach((stage, i) => {
        const angle = (i / 8) * 2 * Math.PI - Math.PI / 2;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        const count = stageCounts[i];
        const colors = _stageStatusColor(count, totalEngagements);

        svg += `<g style="cursor:pointer"
            onclick="window.__cccGoToStage(${i})"
            onmouseenter="window.__cccShowStage(${i})">
            <circle cx="${x}" cy="${y}" r="32"
                fill="${colors.bg}" stroke="${colors.fg}" stroke-width="0.5"/>
            <text x="${x}" y="${y - 5}" text-anchor="middle" font-size="9"
                fill="${colors.fg}" opacity="0.6">${stage.id}</text>
            <text x="${x}" y="${y + 8}" text-anchor="middle" font-size="10"
                font-weight="500" fill="${colors.fg}">${frappe.utils.escape_html(stage.name.substring(0, 10))}</text>`;
        if (count > 0) {
            svg += `<text x="${x}" y="${y + 21}" text-anchor="middle" font-size="9"
                fill="${colors.fg}" opacity="0.8" font-weight="500">${count}</text>`;
        }
        svg += `</g>`;

        // External sub-label
        const subX = cx + (r + 50) * Math.cos(angle);
        const subY = cy + (r + 50) * Math.sin(angle);
        svg += `<text x="${subX}" y="${subY}" text-anchor="middle" font-size="9"
            fill="var(--acc-muted)">${frappe.utils.escape_html(stage.sub)}</text>`;
    });

    // Curved connector arcs between stages
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
            marker-end="url(#ccc-arrow)"/>`;
    }

    svg += `</svg>`;
    container.innerHTML = svg;
}

function renderStageList() {
    const list = document.getElementById('acc-stage-list');
    if (!list) return;
    const byStatus = (STATE.data && STATE.data.summary && STATE.data.summary.by_status) || {};
    const totalEngagements = Object.values(byStatus).reduce((a, b) => a + b, 0);

    list.innerHTML = CCC_STAGES.map((stage, i) => {
        const statuses = STAGE_TO_STATUSES[stage.name] || [stage.name];
        const count = statuses.reduce((sum, st) => sum + (byStatus[st] || 0), 0);
        const colors = _stageStatusColor(count, totalEngagements);
        const pct = totalEngagements > 0 ? Math.round((count / totalEngagements) * 100) : 0;
        return `<div class="acc-stage-row" onclick="window.__cccGoToStage(${i})">
            <div class="name">
                <span class="num" style="background:${colors.bg};color:${colors.fg}">${stage.id}</span>
                <div>
                    <div style="font-weight:500;font-size:12px">${frappe.utils.escape_html(stage.name)}</div>
                    <div style="font-size:10px;color:var(--acc-muted)">${frappe.utils.escape_html(stage.sub)}</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
                <div class="pb"><div style="width:${pct}%;background:${colors.fg}"></div></div>
                <span class="count" style="color:${colors.fg}">${count}</span>
            </div>
        </div>`;
    }).join('');
}

window.__cccShowStage = function(idx) {
    const stage = CCC_STAGES[idx];
    const detail = document.getElementById('acc-stage-detail');
    if (!detail) return;
    const statuses = STAGE_TO_STATUSES[stage.name] || [stage.name];
    const byStatus = (STATE.data && STATE.data.summary && STATE.data.summary.by_status) || {};
    const count = statuses.reduce((sum, st) => sum + (byStatus[st] || 0), 0);
    detail.innerHTML = `<strong>${stage.id}. ${frappe.utils.escape_html(stage.name)} ` +
        `<span style="color:var(--acc-muted);font-weight:400">(${count} ${__('engagements')})</span></strong>` +
        `${frappe.utils.escape_html(stage.detail)}`;
};

window.__cccGoToStage = function(idx) {
    // Drill down: navigate to the CCC Engagement list, filtered by status
    // and (if a client is selected) by client.
    const stage = CCC_STAGES[idx];
    const statuses = STAGE_TO_STATUSES[stage.name] || [stage.name];
    const route_options = {};
    if (statuses.length === 1) {
        route_options['engagement_status'] = statuses[0];
    } else {
        route_options['engagement_status'] = ['in', statuses];
    }
    if (STATE.client) {
        route_options['client'] = STATE.client;
    }
    frappe.route_options = route_options;
    frappe.set_route('List', 'GRC Aramco CCC Engagement');
};
