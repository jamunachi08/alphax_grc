// AlphaX GRC v1.9.0 — GDPR Dashboard

frappe.pages['grc-gdpr-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('GDPR — EU Data Protection'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Browse catalog'),
        () => frappe.set_route('List', 'GRC GDPR Catalog'));
    page.add_menu_item(__('Per-client tracking'),
        () => frappe.set_route('List', 'GRC GDPR Control'));
    page.add_menu_item(__('+ Track new article for client'),
        () => frappe.new_doc('GRC GDPR Control'));

    document.getElementById('gdpr-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null, selectedChapter: null };

const CHAPTER_COLORS = {
    'CH-II':    { c1: '#185FA5', c2: '#0F1F40', label: 'Principles' },
    'CH-III':   { c1: '#0F6E56', c2: '#0A4D3C', label: 'Data Subject Rights' },
    'CH-IV':    { c1: '#854F0B', c2: '#5D3608', label: 'Controller / Processor' },
    'CH-V':     { c1: '#A32D2D', c2: '#791F1F', label: 'Third-Country Transfers' },
    'CH-VI':    { c1: '#3C3489', c2: '#251E5C', label: 'Authorities' },
    'CH-VII':   { c1: '#1F7A8C', c2: '#125560', label: 'Co-operation' },
    'CH-VIII':  { c1: '#C25C1F', c2: '#8C3F12', label: 'Remedies & Penalties' },
    'RECITALS': { c1: '#5A8C2A', c2: '#3F6219', label: 'Interpretive' },
};

function buildShell() {
    return `
    <style>
      .gdpr { max-width: 1400px; margin: 0 auto; }
      .gdpr-toolbar {
        padding: 0 0 14px;
        display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      }
      .gdpr-toolbar select {
        padding: 7px 12px; border-radius: 8px;
        border: 1px solid var(--grc-border, rgba(0,0,0,.08));
        background: white; font-size: 12px; min-width: 240px;
      }
      .gdpr-chapter-card {
        position: relative;
        padding: 16px 14px;
        border-radius: var(--grc-radius-md, 8px);
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s;
        color: white;
        overflow: hidden;
      }
      .gdpr-chapter-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--grc-shadow-md, 0 2px 8px rgba(0,0,0,.06));
      }
      .gdpr-chapter-card .num {
        font-size: 32px; font-weight: 600; line-height: 1; margin-bottom: 4px;
      }
      .gdpr-chapter-card .code {
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: .04em;
        opacity: 0.85; margin-bottom: 4px;
      }
      .gdpr-chapter-card .lbl {
        font-size: 13px; font-weight: 500; line-height: 1.3;
      }
      .gdpr-chapter-card .progress-mini {
        margin-top: 10px; height: 4px; border-radius: 2px;
        background: rgba(255,255,255,.2); overflow: hidden;
      }
      .gdpr-chapter-card .progress-mini > div {
        height: 100%; background: rgba(255,255,255,.85);
      }
      .gdpr-articles-table {
        width: 100%; border-collapse: collapse; font-size: 13px;
      }
      .gdpr-articles-table th {
        text-align: left; padding: 10px;
        border-bottom: 2px solid var(--grc-secondary, #185FA5);
        color: var(--grc-primary, #0F1F40);
        font-weight: 600; font-size: 11px;
        text-transform: uppercase; letter-spacing: .04em;
      }
      .gdpr-articles-table td {
        padding: 10px;
        border-bottom: 1px solid var(--grc-border, rgba(0,0,0,.08));
        vertical-align: top;
      }
      .gdpr-articles-table tr:hover {
        background: rgba(24, 95, 165, 0.04); cursor: pointer;
      }
      .gdpr-articles-table .code {
        font-family: ui-monospace, 'SF Mono', monospace;
        font-size: 11px; font-weight: 600; color: var(--grc-secondary, #185FA5);
      }
      .gdpr-empty {
        text-align: center; padding: 32px;
        color: var(--grc-muted, #687178); font-size: 12px;
      }
    </style>

    <div class="gdpr">
      <div class="grc-hero">
        <h2>${__('GDPR — Regulation (EU) 2016/679')}</h2>
        <div class="grc-hero-sub">${__('43 articles covering data subject rights, controller/processor obligations, security, breach notification, third-country transfers, and DPO requirements. Cross-references to ISO 27701.')}</div>
        <div class="grc-hero-stats" id="gdpr-stats"></div>
      </div>

      <div class="gdpr-toolbar">
        <label style="font-size:12px;color:var(--grc-muted);">${__('Client:')}</label>
        <select id="gdpr-client-picker">
          <option value="">${__('— Catalog only (no client) —')}</option>
        </select>
      </div>

      <div class="grc-section">
        <h4>${__('Chapters — click any card to drill into its articles')}</h4>
        <div class="grc-card-grid" id="gdpr-chapter-cards"></div>
      </div>

      <div class="grc-section" id="gdpr-drilldown-section" style="display:none">
        <h4 id="gdpr-drilldown-title"></h4>
        <div id="gdpr-drilldown"></div>
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
                const sel = document.getElementById('gdpr-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_gdpr_dashboard.grc_gdpr_dashboard.get_gdpr_dashboard',
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
    renderChapterCards();
    if (STATE.selectedChapter) loadDrilldown(STATE.selectedChapter);
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_articles || 0, lbl: __('Articles') },
        { num: s.chapters || 0, lbl: __('Chapters') },
    ];
    if (STATE.client) {
        stats.push({ num: s.tracked_for_client || 0, lbl: __('Tracked') });
    }
    document.getElementById('gdpr-stats').innerHTML = stats.map(x =>
        `<div class="grc-hero-stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderChapterCards() {
    const chapters = STATE.data.chapters_rollup || [];
    const impl = STATE.data.chapter_implementation || {};
    const tgt = document.getElementById('gdpr-chapter-cards');

    if (!chapters.length) {
        tgt.innerHTML = `<div class="gdpr-empty">${__('No catalog data — run bench migrate.')}</div>`;
        return;
    }

    tgt.innerHTML = chapters.map(d => {
        const c = CHAPTER_COLORS[d.code] || { c1: '#185FA5', c2: '#0F1F40' };
        const implData = impl[d.code];
        let progress = '';
        let metric = '';
        if (implData && implData.total > 0) {
            const implementedPct = (implData['Implemented'] / implData.total * 100).toFixed(0);
            progress = `<div class="progress-mini"><div style="width:${implementedPct}%"></div></div>`;
            metric = `<div style="font-size:10px;opacity:.85;margin-top:4px;">${implData['Implemented']} of ${implData.total} ${__('implemented')}</div>`;
        }
        return `<div class="gdpr-chapter-card"
                style="background: linear-gradient(135deg, ${c.c1} 0%, ${c.c2} 100%);"
                onclick="window.__gdprDrillChapter('${d.code}')">
          <div class="code">${frappe.utils.escape_html(d.code)}</div>
          <div class="num">${d.count}</div>
          <div class="lbl">${frappe.utils.escape_html(d.label || c.label || '')}</div>
          ${progress}${metric}
        </div>`;
    }).join('');
}

window.__gdprDrillChapter = function(code) {
    STATE.selectedChapter = code;
    loadDrilldown(code);
};

function loadDrilldown(code) {
    const args = { chapter_code: code };
    if (STATE.client) args.client = STATE.client;

    document.getElementById('gdpr-drilldown-section').style.display = 'block';
    document.getElementById('gdpr-drilldown-title').textContent =
        __('Chapter {0} — articles', [code]);
    document.getElementById('gdpr-drilldown').innerHTML =
        `<div class="gdpr-empty">${__('Loading…')}</div>`;

    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_gdpr_dashboard.grc_gdpr_dashboard.get_chapter_articles',
        args,
        callback: (r) => {
            const m = (r && r.message) || {};
            renderDrilldown(m.articles || []);
        },
    });
}

function renderDrilldown(articles) {
    const tgt = document.getElementById('gdpr-drilldown');
    if (!articles.length) {
        tgt.innerHTML = `<div class="gdpr-empty">${__('No articles in this chapter.')}</div>`;
        return;
    }
    tgt.innerHTML = `<table class="gdpr-articles-table">
      <thead><tr>
        <th style="width:90px">${__('Article')}</th>
        <th>${__('Title and summary')}</th>
        <th style="width:140px">${__('Applies To')}</th>
        <th style="width:120px">${__('Status')}</th>
      </tr></thead>
      <tbody>${articles.map(c => {
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
        return `<tr onclick="frappe.set_route('Form', 'GRC GDPR Catalog', '${c.name}')">
          <td><span class="code">${frappe.utils.escape_html(c.article_code)}</span></td>
          <td>
            <div style="font-weight:500;color:var(--grc-primary);">${frappe.utils.escape_html(c.article_title)}</div>
            <div style="font-size:11px;color:var(--grc-muted);margin-top:4px;">${frappe.utils.escape_html((c.summary || '').substring(0, 220))}${(c.summary || '').length > 220 ? '…' : ''}</div>
          </td>
          <td style="font-size:10px;color:var(--grc-muted);">${frappe.utils.escape_html(c.applicability || '—')}</td>
          <td>${statusHtml}</td>
        </tr>`;
      }).join('')}</tbody>
    </table>`;
}
