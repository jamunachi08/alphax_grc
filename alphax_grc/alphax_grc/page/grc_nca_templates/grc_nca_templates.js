// AlphaX GRC v1.4.2 — NCA Templates Library (UI redesign)
//
// Hero stats strip · category tiles · cards with adoption checkmarks ·
// sticky toolbar · "For this client" side panel · bulk-action bar.
// Theme-aware (uses Frappe CSS vars), bilingual EN/AR ready, mobile-responsive.

frappe.pages['grc-nca-templates'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('NCA Templates Library'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('Re-seed NCA library (admin)'), () => forceSeed());
    page.add_menu_item(__('Coverage gap analysis'), () => showCoverage());
    page.add_menu_item(__('Toggle Arabic / English'), () => toggleLang());

    bindToolbar();
    loadAll();
};

const STATE = {
    lib: { Policy: [], Standard: [], Procedure: [], Form: [] },
    clients: [],
    selectedClient: '',
    selectedCodes: new Set(),
    adoptedCodes: new Set(),
    activeCategory: 'all',
    activeKind: 'Policy',
    searchQuery: '',
    lang: 'en',
};

const CATEGORY_META = {
    'Governance':   {icon: '⚖️', color: '#5B6FD9', en: 'Governance',   ar: 'الحوكمة'},
    'Access':       {icon: '🔒', color: '#0F6E56', en: 'Access',       ar: 'الصلاحيات'},
    'Asset':        {icon: '📦', color: '#854F0B', en: 'Asset',        ar: 'الأصول'},
    'Network':      {icon: '🌐', color: '#185FA5', en: 'Network',      ar: 'الشبكة'},
    'Application':  {icon: '🧩', color: '#534AB7', en: 'Application',  ar: 'التطبيقات'},
    'Data':         {icon: '💾', color: '#993556', en: 'Data',         ar: 'البيانات'},
    'Physical':     {icon: '🏛', color: '#5F5E5A', en: 'Physical',     ar: 'الأمن المادي'},
    'Third Party':  {icon: '🤝', color: '#993C1D', en: 'Third Party',  ar: 'أطراف خارجية'},
    'Resilience':   {icon: '🛡️', color: '#3B6D11', en: 'Resilience',   ar: 'الصمود'},
    'Incident':     {icon: '🚨', color: '#A32D2D', en: 'Incident',     ar: 'الحوادث'},
    'Monitoring':   {icon: '📡', color: '#0C447C', en: 'Monitoring',   ar: 'المراقبة'},
    'Vulnerability':{icon: '🐛', color: '#A32D2D', en: 'Vulnerability',ar: 'الثغرات'},
    'Cryptography': {icon: '🔐', color: '#534AB7', en: 'Cryptography', ar: 'التشفير'},
    'Identity':     {icon: '🪪', color: '#0F6E56', en: 'Identity',     ar: 'الهوية'},
};

const KIND_META = {
    Policy:    {en: 'Policies',    ar: 'السياسات',  icon: '📜'},
    Standard:  {en: 'Standards',   ar: 'المعايير',  icon: '📐'},
    Procedure: {en: 'Procedures',  ar: 'الإجراءات', icon: '📋'},
    Form:      {en: 'Forms',       ar: 'النماذج',   icon: '📝'},
};

function L(en, ar) { return STATE.lang === 'ar' ? ar : en; }

function buildShell() {
    return `
    <style>
      .nca {
        --nca-bg: var(--bg-color, #fff);
        --nca-fg: var(--text-color, #1f272e);
        --nca-muted: var(--text-muted, #687178);
        --nca-border: var(--border-color, rgba(0,0,0,.08));
        --nca-card-bg: var(--card-bg, #fff);
        --nca-shadow: 0 1px 3px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.06);
        --nca-shadow-lift: 0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.06);
        --nca-accent: #185FA5;
        font-family: var(--font-stack, system-ui, -apple-system, 'Segoe UI', sans-serif);
        font-size: 13px; color: var(--nca-fg);
        max-width: 1400px; margin: 0 auto;
      }
      .nca[dir="rtl"] { font-family: 'Tajawal', system-ui, sans-serif; }
      .nca-hero {
        background: linear-gradient(135deg, #185FA5 0%, #0F6E56 100%);
        color: white; padding: 24px 28px; border-radius: 14px;
        margin: 12px 12px 18px; box-shadow: var(--nca-shadow-lift);
      }
      .nca-hero h2 { margin: 0 0 4px; font-size: 18px; font-weight: 600; color: white; }
      .nca-hero .sub { font-size: 12px; opacity: 0.85; margin-bottom: 16px; }
      .nca-stats {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px; margin-top: 12px;
      }
      .nca-stat { background: rgba(255,255,255,.12); border-radius: 8px; padding: 10px 12px; }
      .nca-stat .num { font-size: 22px; font-weight: 600; line-height: 1; color: white; }
      .nca-stat .lbl { font-size: 10px; opacity: 0.85; text-transform: uppercase;
        letter-spacing: .04em; margin-top: 4px; }

      .nca-toolbar {
        position: sticky; top: 0; z-index: 10; background: var(--nca-bg);
        border-bottom: 1px solid var(--nca-border);
        padding: 10px 16px; display: flex; gap: 10px; align-items: center;
        flex-wrap: wrap; margin: 0 12px;
      }
      .nca-toolbar input.search, .nca-toolbar select {
        padding: 8px 12px; border-radius: 8px; border: 1px solid var(--nca-border);
        background: var(--nca-card-bg); color: var(--nca-fg); font-size: 12px;
      }
      .nca-toolbar input.search { flex: 1; min-width: 200px; }
      .nca-toolbar select { min-width: 220px; }
      .nca-toolbar .view-toggle {
        display: flex; border-radius: 8px; border: 1px solid var(--nca-border);
        overflow: hidden;
      }
      .nca-toolbar .view-toggle button {
        background: var(--nca-card-bg); border: none; color: var(--nca-muted);
        padding: 6px 12px; cursor: pointer; font-size: 12px;
      }
      .nca-toolbar .view-toggle button.active {
        background: var(--nca-accent); color: white;
      }

      .nca-tabs {
        display: flex; gap: 4px; margin: 14px 16px 0;
        border-bottom: 1px solid var(--nca-border);
      }
      .nca-tab {
        padding: 10px 16px; cursor: pointer; font-size: 13px; font-weight: 500;
        color: var(--nca-muted); border-bottom: 2px solid transparent;
        transition: all .15s; display: flex; align-items: center; gap: 6px;
      }
      .nca-tab:hover { color: var(--nca-fg); }
      .nca-tab.active { color: var(--nca-accent); border-bottom-color: var(--nca-accent); }
      .nca-tab .count {
        background: var(--nca-border); color: var(--nca-muted);
        padding: 1px 8px; border-radius: 10px; font-size: 10px; font-weight: 500;
      }
      .nca-tab.active .count { background: var(--nca-accent); color: white; }

      .nca-categories {
        display: flex; gap: 8px; margin: 14px 16px; overflow-x: auto;
        padding-bottom: 6px;
      }
      .nca-cat-chip {
        flex-shrink: 0; padding: 6px 12px; border-radius: 999px;
        background: var(--nca-card-bg); border: 1px solid var(--nca-border);
        cursor: pointer; font-size: 11px; display: flex; align-items: center;
        gap: 6px; transition: all .15s; white-space: nowrap;
      }
      .nca-cat-chip:hover { box-shadow: var(--nca-shadow); }
      .nca-cat-chip.active { background: var(--nca-accent); color: white; border-color: var(--nca-accent); }
      .nca-cat-chip .count {
        background: rgba(0,0,0,.08); padding: 0 6px; border-radius: 8px;
        font-size: 10px; min-width: 16px; text-align: center;
      }
      .nca-cat-chip.active .count { background: rgba(255,255,255,.25); }

      .nca-main {
        display: grid; grid-template-columns: 1fr 280px; gap: 16px;
        padding: 0 16px 16px;
      }
      @media (max-width: 900px) {
        .nca-main { grid-template-columns: 1fr; }
        .nca-side { order: -1; }
      }

      .nca-grid { display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
      .nca-grid.list-view { grid-template-columns: 1fr; }

      .nca-card {
        background: var(--nca-card-bg); border: 1px solid var(--nca-border);
        border-radius: 10px; padding: 14px; box-shadow: var(--nca-shadow);
        display: flex; flex-direction: column; gap: 8px;
        transition: all .15s; position: relative;
      }
      .nca-card:hover { box-shadow: var(--nca-shadow-lift); transform: translateY(-1px); }
      .nca-card.adopted { border-left: 3px solid #0F6E56; }
      .nca-card.selected { box-shadow: 0 0 0 2px var(--nca-accent); }

      .nca-card-head { display: flex; justify-content: space-between; gap: 8px; }
      .nca-card-icon {
        width: 32px; height: 32px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px; flex-shrink: 0;
      }
      .nca-card-checkbox { display: flex; align-items: flex-start; }
      .nca-card-checkbox input { cursor: pointer; }
      .nca-card-body { flex: 1; }
      .nca-card-cat { font-size: 10px; color: var(--nca-muted);
        text-transform: uppercase; letter-spacing: .04em; }
      .nca-card-title { font-size: 13px; font-weight: 500; margin: 4px 0;
        line-height: 1.3; color: var(--nca-fg); }
      .nca-card-title-ar { font-size: 11px; color: var(--nca-muted); margin-top: -2px; }
      .nca-card-ecc { display: flex; flex-wrap: wrap; gap: 4px; margin: 6px 0; }
      .nca-card-ecc .chip {
        background: rgba(24,95,165,.1); color: var(--nca-accent);
        padding: 1px 8px; border-radius: 4px; font-size: 10px;
        font-family: ui-monospace, monospace;
      }
      .nca-card-actions {
        display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;
        padding-top: 8px; border-top: 1px solid var(--nca-border);
      }
      .nca-btn {
        padding: 5px 10px; border-radius: 6px; border: 1px solid var(--nca-border);
        background: var(--nca-card-bg); cursor: pointer; font-size: 11px;
        text-decoration: none; color: var(--nca-fg);
        display: inline-flex; align-items: center; gap: 4px;
      }
      .nca-btn:hover { background: var(--nca-border); }
      .nca-btn-primary { background: var(--nca-accent); color: white;
        border-color: var(--nca-accent); }
      .nca-btn-primary:hover { background: #0C447C; color: white; }
      .nca-card-badge-adopted {
        position: absolute; top: 10px; right: 10px;
        background: #0F6E56; color: white; font-size: 9px;
        padding: 2px 7px; border-radius: 999px; font-weight: 500;
      }

      .nca-side {
        background: var(--nca-card-bg); border: 1px solid var(--nca-border);
        border-radius: 10px; padding: 14px; align-self: start;
        position: sticky; top: 70px;
      }
      .nca-side h4 { font-size: 12px; font-weight: 500; margin: 0 0 10px;
        color: var(--nca-fg); text-transform: uppercase; letter-spacing: .04em; }
      .nca-side .meta { font-size: 11px; color: var(--nca-muted); margin-bottom: 10px; }
      .nca-side .progress-wrap {
        background: var(--nca-border); border-radius: 999px; height: 6px;
        overflow: hidden; margin: 6px 0 10px;
      }
      .nca-side .progress-bar { background: #0F6E56; height: 100%;
        border-radius: 999px; transition: width .4s; }
      .nca-side .stat-line {
        display: flex; justify-content: space-between; padding: 4px 0;
        font-size: 12px; border-bottom: 1px solid var(--nca-border);
      }
      .nca-side .stat-line:last-child { border: none; }
      .nca-side .empty {
        text-align: center; padding: 16px 0; font-size: 11px;
        color: var(--nca-muted);
      }

      .nca-bulk-bar {
        position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
        background: var(--nca-fg); color: white; padding: 10px 16px;
        border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.2);
        display: none; align-items: center; gap: 12px; z-index: 100;
        font-size: 12px;
      }
      .nca-bulk-bar.show { display: flex; }
      .nca-bulk-bar .selected-count {
        background: rgba(255,255,255,.2); padding: 2px 8px; border-radius: 10px;
        font-size: 11px;
      }
      .nca-bulk-bar button {
        background: white; color: var(--nca-fg); border: none;
        padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;
        font-weight: 500;
      }
      .nca-bulk-bar button.ghost { background: rgba(255,255,255,.15); color: white; }

      .nca-empty {
        grid-column: 1 / -1;
        text-align: center; padding: 60px 20px; color: var(--nca-muted);
        font-size: 13px;
      }
      .nca-empty .big-icon { font-size: 36px; opacity: 0.4; margin-bottom: 8px; }
    </style>

    <div class="nca" id="nca-root">
      <div class="nca-hero">
        <h2>${__('NCA Cybersecurity Templates Library')}</h2>
        <div class="sub">${__('Official Saudi NCA reference templates · Browse · Adopt for client engagements')}</div>
        <div class="nca-stats" id="nca-stats"></div>
      </div>

      <div class="nca-tabs" id="nca-tabs"></div>
      <div class="nca-categories" id="nca-cats"></div>

      <div class="nca-toolbar">
        <input class="search" id="nca-search" placeholder="${__('Search by name, category or ECC control…')}"/>
        <select id="nca-client-picker">
          <option value="">${__('Select client engagement…')}</option>
        </select>
        <div class="view-toggle">
          <button id="view-grid" class="active" onclick="window.__ncaSetView('grid')">⊞ ${__('Grid')}</button>
          <button id="view-list" onclick="window.__ncaSetView('list')">☰ ${__('List')}</button>
        </div>
      </div>

      <div class="nca-main">
        <div>
          <div class="nca-grid" id="nca-grid"></div>
        </div>
        <div class="nca-side" id="nca-side">
          <h4>${__('For this client')}</h4>
          <div id="nca-side-body"></div>
        </div>
      </div>

      <div class="nca-bulk-bar" id="nca-bulk-bar">
        <span class="selected-count" id="bulk-count">0</span>
        <span>${__('templates selected')}</span>
        <button onclick="window.__ncaBulkAdopt()">+ ${__('Adopt for client')}</button>
        <button class="ghost" onclick="window.__ncaClearSelection()">${__('Clear')}</button>
      </div>
    </div>`;
}

function bindToolbar() {
    document.getElementById('nca-search').addEventListener('input', (e) => {
        STATE.searchQuery = e.target.value.toLowerCase();
        renderGrid();
    });
    document.getElementById('nca-client-picker').addEventListener('change', (e) => {
        STATE.selectedClient = e.target.value;
        loadAdoptionStatus();
        renderSidePanel();
        renderHero();
    });
}

window.__ncaSetView = function(view) {
    document.getElementById('view-grid').classList.toggle('active', view === 'grid');
    document.getElementById('view-list').classList.toggle('active', view === 'list');
    document.getElementById('nca-grid').classList.toggle('list-view', view === 'list');
};

function loadAll() {
    return Promise.all([loadLibrary(), loadClients()]).then(() => {
        renderTabs();
        renderCategoryChips();
        renderHero();
        renderGrid();
        renderSidePanel();
    });
}

function loadLibrary() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.get_template_library',
            callback: (r) => {
                STATE.lib = (r && r.message) || {Policy: [], Standard: [], Procedure: [], Form: []};
                resolve();
            },
        });
    });
}

function loadClients() {
    return new Promise((resolve) => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.doctype.grc_client_profile.grc_client_profile.get_active_clients',
            callback: (r) => {
                STATE.clients = (r && r.message) || [];
                const sel = document.getElementById('nca-client-picker');
                if (sel) {
                    STATE.clients.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.name;
                        opt.textContent = `${c.client_name} — ${c.country}`;
                        sel.appendChild(opt);
                    });
                }
                resolve();
            },
        });
    });
}

function loadAdoptionStatus() {
    if (!STATE.selectedClient) {
        STATE.adoptedCodes = new Set();
        renderGrid();
        return;
    }
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.get_client_adoption_status',
        args: { client: STATE.selectedClient },
        callback: (r) => {
            STATE.adoptedCodes = new Set(((r && r.message) || {}).adopted_codes || []);
            renderGrid();
            renderSidePanel();
            renderHero();
        },
    });
}

function renderHero() {
    const el = document.getElementById('nca-stats');
    if (!el) return;
    const total = Object.values(STATE.lib).reduce((a, l) => a + l.length, 0);
    const stats = [
        { num: total, lbl: __('Total templates') },
        { num: (STATE.lib.Policy || []).length, lbl: __('Policies') },
        { num: (STATE.lib.Standard || []).length, lbl: __('Standards') },
        { num: (STATE.lib.Procedure || []).length, lbl: __('Procedures') },
        { num: (STATE.lib.Form || []).length, lbl: __('Forms') },
    ];
    if (STATE.selectedClient) {
        stats.push({ num: STATE.adoptedCodes.size, lbl: __('Adopted by client') });
    }
    el.innerHTML = stats.map(s =>
        `<div class="nca-stat"><div class="num">${s.num}</div><div class="lbl">${s.lbl}</div></div>`
    ).join('');
}

function renderTabs() {
    const el = document.getElementById('nca-tabs');
    if (!el) return;
    const order = ['Policy', 'Standard', 'Procedure', 'Form'];
    el.innerHTML = order.map(k => {
        const meta = KIND_META[k] || {};
        const active = k === STATE.activeKind ? 'active' : '';
        return `<div class="nca-tab ${active}" onclick="window.__ncaSetKind('${k}')">
            <span>${meta.icon || ''}</span>
            <span>${L(meta.en, meta.ar)}</span>
            <span class="count">${(STATE.lib[k] || []).length}</span>
        </div>`;
    }).join('');
}

window.__ncaSetKind = function(k) {
    STATE.activeKind = k;
    STATE.activeCategory = 'all';
    STATE.selectedCodes.clear();
    renderTabs();
    renderCategoryChips();
    renderGrid();
    updateBulkBar();
};

function renderCategoryChips() {
    const el = document.getElementById('nca-cats');
    if (!el) return;
    const items = STATE.lib[STATE.activeKind] || [];
    const counts = {};
    items.forEach(i => {
        const c = i.category || 'Other';
        counts[c] = (counts[c] || 0) + 1;
    });
    const cats = Object.keys(counts).sort();
    const allActive = STATE.activeCategory === 'all' ? 'active' : '';
    let html = `<div class="nca-cat-chip ${allActive}" onclick="window.__ncaSetCat('all')">
        <span>📚</span><span>${__('All')}</span><span class="count">${items.length}</span>
    </div>`;
    cats.forEach(c => {
        const meta = CATEGORY_META[c] || { icon: '•', en: c, ar: c };
        const active = c === STATE.activeCategory ? 'active' : '';
        const safeC = c.replace(/'/g, "\\'");
        html += `<div class="nca-cat-chip ${active}" onclick="window.__ncaSetCat('${safeC}')">
            <span>${meta.icon}</span>
            <span>${frappe.utils.escape_html(L(meta.en, meta.ar))}</span>
            <span class="count">${counts[c]}</span>
        </div>`;
    });
    el.innerHTML = html;
}

window.__ncaSetCat = function(c) {
    STATE.activeCategory = c;
    renderCategoryChips();
    renderGrid();
};

function renderGrid() {
    const grid = document.getElementById('nca-grid');
    if (!grid) return;
    const items = (STATE.lib[STATE.activeKind] || []).filter(r => {
        if (STATE.activeCategory !== 'all' && r.category !== STATE.activeCategory) return false;
        if (STATE.searchQuery) {
            const hay = `${r.template_name} ${r.template_name_ar || ''} ${r.ecc_controls || ''} ${r.category || ''}`.toLowerCase();
            if (!hay.includes(STATE.searchQuery)) return false;
        }
        return true;
    });

    if (!items.length) {
        grid.innerHTML = `<div class="nca-empty">
            <div class="big-icon">🔍</div>
            <div>${__('No templates match your filter.')}</div>
        </div>`;
        return;
    }

    grid.innerHTML = items.map(r => {
        const meta = CATEGORY_META[r.category] || { icon: '•', color: '#5F5E5A' };
        const adopted = STATE.adoptedCodes.has(r.template_code);
        const selected = STATE.selectedCodes.has(r.template_code);
        const eccList = (r.ecc_controls || '').split(',').filter(s => s.trim());
        const eccChips = eccList.slice(0, 4).map(c =>
            `<span class="chip">${frappe.utils.escape_html(c.trim())}</span>`
        ).join('');
        const moreEcc = Math.max(0, eccList.length - 4);

        return `<div class="nca-card ${adopted ? 'adopted' : ''} ${selected ? 'selected' : ''}">
            ${adopted ? `<div class="nca-card-badge-adopted">✓ ${__('Adopted')}</div>` : ''}
            <div class="nca-card-head">
                <div class="nca-card-icon" style="background:${meta.color}22; color:${meta.color}">
                    ${meta.icon}
                </div>
                <div class="nca-card-checkbox">
                    <input type="checkbox" ${selected ? 'checked' : ''}
                        onchange="window.__ncaToggleSelect('${r.template_code}', this.checked)"
                        title="${__('Select for bulk adopt')}"/>
                </div>
            </div>
            <div class="nca-card-body">
                <div class="nca-card-cat">${frappe.utils.escape_html(r.category || '—')}</div>
                <div class="nca-card-title">${frappe.utils.escape_html(r.template_name)}</div>
                ${r.template_name_ar ? `<div class="nca-card-title-ar">${frappe.utils.escape_html(r.template_name_ar)}</div>` : ''}
                ${eccChips ? `<div class="nca-card-ecc">${eccChips}${moreEcc > 0 ? `<span class="chip">+${moreEcc}</span>` : ''}</div>` : ''}
            </div>
            <div class="nca-card-actions">
                ${r.official_word_url ? `<a class="nca-btn" href="${r.official_word_url}" target="_blank" rel="noopener">📄 Word</a>` : ''}
                ${r.official_pdf_url ? `<a class="nca-btn" href="${r.official_pdf_url}" target="_blank" rel="noopener">📑 PDF</a>` : ''}
                <button class="nca-btn nca-btn-primary"
                    onclick="window.__adoptTemplate('${r.template_code}')"
                    ${adopted ? 'disabled style="opacity:.5;cursor:not-allowed"' : ''}>
                    ${adopted ? '✓ ' + __('Adopted') : '+ ' + __('Adopt')}
                </button>
            </div>
        </div>`;
    }).join('');
}

function renderSidePanel() {
    const body = document.getElementById('nca-side-body');
    if (!body) return;
    if (!STATE.selectedClient) {
        body.innerHTML = `<div class="empty">
            ${__('Pick a client engagement above to see adoption progress and one-click gap fixes.')}
        </div>`;
        return;
    }
    const client = STATE.clients.find(c => c.name === STATE.selectedClient) || {};
    const adopted = STATE.adoptedCodes.size;
    const total = Object.values(STATE.lib).reduce((a, l) => a + l.length, 0);
    const pct = total ? Math.round((adopted / total) * 100) : 0;

    const kindStats = ['Policy', 'Standard', 'Procedure', 'Form'].map(k => {
        const items = STATE.lib[k] || [];
        const adoptedHere = items.filter(i => STATE.adoptedCodes.has(i.template_code)).length;
        return { kind: k, adopted: adoptedHere, total: items.length };
    });

    body.innerHTML = `
        <div class="meta"><b>${frappe.utils.escape_html(client.client_name || STATE.selectedClient)}</b></div>
        <div class="meta">${frappe.utils.escape_html(client.country || '—')} · ${frappe.utils.escape_html(client.sector || '—')}</div>
        <div class="meta" style="margin-top:8px"><b>${pct}%</b> ${__('NCA library coverage')}</div>
        <div class="progress-wrap">
            <div class="progress-bar" style="width:${pct}%"></div>
        </div>
        ${kindStats.map(s => `
            <div class="stat-line">
                <span>${KIND_META[s.kind].icon} ${L(KIND_META[s.kind].en, KIND_META[s.kind].ar)}</span>
                <span><b>${s.adopted}</b> / ${s.total}</span>
            </div>
        `).join('')}
        <div style="margin-top:10px">
            <button class="nca-btn nca-btn-primary" style="width:100%; justify-content:center"
                onclick="window.__ncaShowCoverage()">
                📊 ${__('Coverage gap analysis')}
            </button>
        </div>
    `;
}

window.__ncaToggleSelect = function(code, checked) {
    if (checked) STATE.selectedCodes.add(code);
    else STATE.selectedCodes.delete(code);
    updateBulkBar();
    renderGrid();
};

window.__ncaClearSelection = function() {
    STATE.selectedCodes.clear();
    updateBulkBar();
    renderGrid();
};

function updateBulkBar() {
    const bar = document.getElementById('nca-bulk-bar');
    const count = document.getElementById('bulk-count');
    if (!bar) return;
    if (STATE.selectedCodes.size > 0) {
        bar.classList.add('show');
        count.textContent = STATE.selectedCodes.size;
    } else {
        bar.classList.remove('show');
    }
}

window.__ncaBulkAdopt = function() {
    if (!STATE.selectedClient) {
        frappe.msgprint(__('Pick a client first (toolbar dropdown).'));
        return;
    }
    if (STATE.selectedCodes.size === 0) return;
    frappe.confirm(__('Adopt {0} templates for client {1}?',
        [STATE.selectedCodes.size, STATE.selectedClient]), () => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.bulk_adopt_for_client',
            args: {
                client: STATE.selectedClient,
                kind: STATE.activeKind,
                template_codes: JSON.stringify([...STATE.selectedCodes]),
            },
            callback: (r) => {
                const m = (r && r.message) || {};
                frappe.show_alert({ message: m.summary || __('Done.'), indicator: 'green' });
                STATE.selectedCodes.clear();
                updateBulkBar();
                loadAdoptionStatus();
            },
        });
    });
};

window.__adoptTemplate = function(code) {
    if (!STATE.selectedClient) {
        frappe.msgprint(__('Pick a client first (toolbar dropdown).'));
        return;
    }
    if (STATE.adoptedCodes.has(code)) return;
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.adopt_template_for_client',
        args: { client: STATE.selectedClient, kind: STATE.activeKind, template_code: code },
        callback: (r) => {
            if (r && r.message && r.message.name) {
                frappe.show_alert({ message: __('Adopted: ') + r.message.name, indicator: 'green' });
                STATE.adoptedCodes.add(code);
                renderGrid(); renderSidePanel(); renderHero();
            }
        },
    });
};

window.__ncaShowCoverage = function() {
    if (!STATE.selectedClient) {
        frappe.msgprint(__('Pick a client first.'));
        return;
    }
    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.get_client_policy_coverage',
        args: { client: STATE.selectedClient },
        callback: (r) => {
            const m = (r && r.message) || {};
            const s = m.summary || {};
            const html = `
                <div style="font-size:13px">
                  <div style="background:rgba(0,0,0,.04); padding:12px; border-radius:8px; margin-bottom:12px">
                    <div><b>${frappe.utils.escape_html(STATE.selectedClient)}</b></div>
                    <div>${__('Adopted policies:')} ${s.adopted_policies || 0}</div>
                    <div>${__('Coverage:')} ${s.controls_covered || 0} / ${s.total_template_controls || 0}
                         (<b>${s.coverage_pct || 0}%</b>)</div>
                  </div>
                  <details ${(m.gaps || []).length ? 'open' : ''}>
                    <summary><b>${__('Gap controls')}</b> (${(m.gaps || []).length})</summary>
                    <div style="margin-top:6px; max-height:240px; overflow:auto; font-size:12px">
                      ${(m.gaps || []).map(c => `<div style="padding:2px 0; font-family:monospace">${frappe.utils.escape_html(c)}</div>`).join('') || __('None — full coverage.')}
                    </div>
                  </details>
                  <details style="margin-top:8px">
                    <summary><b>${__('Covered controls')}</b> (${(m.covered || []).length})</summary>
                    <div style="margin-top:6px; max-height:240px; overflow:auto; font-size:12px">
                      ${(m.covered || []).map(c => `<div style="padding:2px 0; font-family:monospace">${frappe.utils.escape_html(c)}</div>`).join('') || '—'}
                    </div>
                  </details>
                </div>`;
            frappe.msgprint({
                title: __('NCA Coverage Gap Analysis'),
                message: html, wide: true, indicator: 'blue',
            });
        },
    });
};

function forceSeed() {
    frappe.confirm(__('Re-run NCA library seeders? Idempotent — safe to run multiple times.'), () => {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates.force_seed_libraries',
            callback: (r) => {
                const results = (r && r.message) || {};
                const lines = Object.entries(results).map(([k, v]) => `${k}: ${v}`).join('<br>');
                frappe.msgprint({ title: __('Re-seed results'), message: lines || __('Done.'), indicator: 'green' });
                loadAll();
            },
        });
    });
}

function showCoverage() {
    if (!STATE.selectedClient) {
        frappe.msgprint(__('Pick a client first (toolbar dropdown).'));
        return;
    }
    window.__ncaShowCoverage();
}

function toggleLang() {
    STATE.lang = STATE.lang === 'en' ? 'ar' : 'en';
    document.getElementById('nca-root').setAttribute('dir', STATE.lang === 'ar' ? 'rtl' : 'ltr');
    renderTabs(); renderCategoryChips(); renderGrid(); renderSidePanel(); renderHero();
    frappe.show_alert({ message: STATE.lang === 'ar' ? 'العربية' : 'English' });
}
