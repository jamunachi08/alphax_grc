// AlphaX GRC v1.5.0 — NCA ECC-2:2024 Dashboard
// Hero · 4-domain wheel · subdomain grid (with bilingual EN⇄AR toggle) · drilldown panel

frappe.pages['grc-ecc2-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('NCA ECC-2:2024'),
        single_column: true,
    });

    const $body = $(wrapper).find('.layout-main-section');
    $body.empty().append(buildShell());

    page.set_primary_action(__('Refresh'), () => loadAll(), 'refresh');
    page.add_menu_item(__('+ Track new control for client'),
        () => frappe.new_doc('GRC NCA ECC Control'));
    page.add_menu_item(__('Browse full catalog'),
        () => frappe.set_route('List', 'GRC NCA ECC2 Catalog'));
    page.add_menu_item(__('Per-client tracking'),
        () => frappe.set_route('List', 'GRC NCA ECC Control'));

    document.getElementById('ecc2-client-picker').addEventListener('change', (e) => {
        STATE.client = e.target.value;
        loadAll();
    });
    document.getElementById('ecc2-lang-toggle').addEventListener('click', () => {
        STATE.lang = STATE.lang === 'en' ? 'ar' : 'en';
        document.getElementById('ecc2-lang-toggle').textContent = STATE.lang === 'en' ? 'العربية' : 'English';
        render();
    });

    loadClients().then(() => loadAll());
};

const STATE = { client: '', clients: [], data: null, lang: 'en', selectedSubdomain: null };

const DOMAIN_COLORS = {
    '1': { bg: '#185FA5', light: '#E6F1FB', dark: '#0C447C', label_en: 'Cybersecurity Governance', label_ar: 'حوكمة الأمن السيبراني' },
    '2': { bg: '#A32D2D', light: '#FCEBEB', dark: '#791F1F', label_en: 'Cybersecurity Defense', label_ar: 'تعزيز الأمن السيبراني' },
    '3': { bg: '#0F6E56', light: '#EAF3DE', dark: '#27500A', label_en: 'Cybersecurity Resilience', label_ar: 'صمود الأمن السيبراني' },
    '4': { bg: '#854F0B', light: '#FAEEDA', dark: '#633806', label_en: 'Third-Party & Cloud', label_ar: 'الأمن السيبراني للطرف الخارجي والحوسبة السحابية' },
};

function buildShell() {
    return `
    <style>
      .ecc2 {
        --ecc2-bg: var(--bg-color, #fff);
        --ecc2-fg: var(--text-color, #1f272e);
        --ecc2-muted: var(--text-muted, #687178);
        --ecc2-border: var(--border-color, rgba(0,0,0,.08));
        --ecc2-card-bg: var(--card-bg, #fff);
        font-family: var(--font-stack, system-ui, -apple-system, 'Segoe UI', sans-serif);
        font-size: 13px; color: var(--ecc2-fg); max-width: 1400px; margin: 0 auto;
      }
      .ecc2-hero {
        background: linear-gradient(135deg, #0F1F40 0%, #185FA5 50%, #0F6E56 100%);
        color: white; padding: 26px 28px; border-radius: 14px;
        margin: 12px 12px 18px; position: relative; overflow: hidden;
      }
      .ecc2-hero::before {
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 200px; height: 200px; border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,.08) 0%, transparent 70%);
      }
      .ecc2-hero h2 { color: white; margin: 0 0 4px; font-size: 19px; font-weight: 600; }
      .ecc2-hero .sub { font-size: 12px; opacity: 0.85; margin-bottom: 18px; }
      .ecc2-hero .stats { display: grid; gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); position: relative; }
      .ecc2-hero .stat { background: rgba(255,255,255,.12); padding: 12px 14px;
        border-radius: 10px; backdrop-filter: blur(10px); }
      .ecc2-hero .stat .num { font-size: 24px; font-weight: 600; line-height: 1; color: white; }
      .ecc2-hero .stat .lbl { font-size: 10px; opacity: 0.85;
        text-transform: uppercase; letter-spacing: .04em; margin-top: 4px; }
      .ecc2-toolbar {
        padding: 0 16px 14px; display: flex; gap: 10px; align-items: center;
        flex-wrap: wrap;
      }
      .ecc2-toolbar select, .ecc2-toolbar button {
        padding: 7px 12px; border-radius: 8px; border: 1px solid var(--ecc2-border);
        background: var(--ecc2-card-bg); color: var(--ecc2-fg); font-size: 12px;
      }
      .ecc2-toolbar select { min-width: 240px; }
      .ecc2-toolbar button { cursor: pointer; font-weight: 500; }
      .ecc2-toolbar button:hover { background: rgba(0,0,0,.04); }
      .ecc2-section {
        background: var(--ecc2-card-bg); border: 1px solid var(--ecc2-border);
        border-radius: 12px; padding: 16px; margin: 0 16px 16px;
      }
      .ecc2-section h4 { font-size: 13px; font-weight: 500; margin: 0 0 14px;
        text-transform: uppercase; letter-spacing: .04em; color: var(--ecc2-muted); }
      .ecc2-domains {
        display: grid; gap: 14px; grid-template-columns: repeat(4, 1fr);
      }
      @media (max-width: 720px) { .ecc2-domains { grid-template-columns: 1fr 1fr; } }
      .ecc2-domain-card {
        padding: 16px; border-radius: 12px; cursor: pointer;
        transition: all .15s; border: 2px solid transparent;
      }
      .ecc2-domain-card:hover { transform: translateY(-2px); border-color: rgba(0,0,0,.1); }
      .ecc2-domain-card .num {
        font-size: 28px; font-weight: 600; line-height: 1; margin-bottom: 6px;
      }
      .ecc2-domain-card .lbl { font-size: 11px; font-weight: 500; line-height: 1.3; }
      .ecc2-domain-card .sub { font-size: 10px; opacity: 0.7; margin-top: 4px; }
      .ecc2-subdomains {
        display: grid; gap: 10px;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      }
      .ecc2-subdomain {
        background: rgba(0,0,0,.02); border: 1px solid var(--ecc2-border);
        border-radius: 10px; padding: 12px; cursor: pointer;
        transition: all .15s; position: relative;
      }
      .ecc2-subdomain:hover { background: rgba(0,0,0,.05); transform: translateY(-1px); }
      .ecc2-subdomain.selected {
        border-color: var(--accent-color, #185FA5); border-width: 2px; padding: 11px;
        background: rgba(24,95,165,.05);
      }
      .ecc2-subdomain .code-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
      .ecc2-subdomain .code {
        font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
        font-variant-numeric: tabular-nums;
      }
      .ecc2-subdomain .total { font-size: 10px; color: var(--ecc2-muted); }
      .ecc2-subdomain .lbl {
        font-size: 12px; font-weight: 500; line-height: 1.4; margin-bottom: 8px;
        min-height: 32px;
      }
      .ecc2-subdomain.ar .lbl { direction: rtl; text-align: right; }
      .ecc2-subdomain .progress {
        display: flex; height: 6px; border-radius: 3px; overflow: hidden;
        background: rgba(0,0,0,.06);
      }
      .ecc2-subdomain .progress > div { height: 100%; }
      .ecc2-subdomain .legend {
        display: flex; gap: 8px; margin-top: 6px; font-size: 9px;
        color: var(--ecc2-muted); flex-wrap: wrap;
      }
      .ecc2-subdomain .legend span { display: flex; align-items: center; gap: 3px; }
      .ecc2-subdomain .legend .dot { width: 6px; height: 6px; border-radius: 50%; }
      .ecc2-controls-table { width: 100%; border-collapse: collapse; font-size: 12px; }
      .ecc2-controls-table th { text-align: left; padding: 8px 10px;
        border-bottom: 1px solid var(--ecc2-border); color: var(--ecc2-muted);
        font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }
      .ecc2-controls-table td { padding: 8px 10px;
        border-bottom: 1px solid var(--ecc2-border); vertical-align: top; }
      .ecc2-controls-table tr:hover { background: rgba(0,0,0,.02); }
      .ecc2-controls-table .code {
        font-family: ui-monospace, 'SF Mono', 'Cascadia Mono', monospace;
        font-size: 11px; font-weight: 500;
      }
      .ecc2-controls-table.ar td.text-cell { direction: rtl; text-align: right; }
      .ecc2-empty { text-align: center; padding: 32px; color: var(--ecc2-muted); font-size: 12px; }
      .ecc2-status-chip {
        display: inline-block; padding: 2px 6px; border-radius: 4px;
        font-size: 9px; font-weight: 500;
      }
      .ecc2-status-implemented { background: #EAF3DE; color: #27500A; }
      .ecc2-status-partial { background: #FAEEDA; color: #854F0B; }
      .ecc2-status-not { background: #FCEBEB; color: #791F1F; }
      .ecc2-status-na { background: #F1EFE8; color: #5F5E5A; }
      .ecc2-status-untracked { background: rgba(0,0,0,.04); color: var(--ecc2-muted); }
    </style>

    <div class="ecc2">
      <div class="ecc2-hero">
        <h2>${__('NCA Essential Cybersecurity Controls — ECC-2:2024')}</h2>
        <div class="sub">${__('Saudi National Cybersecurity Authority · 198 controls across 4 domains, 31 subdomains · bilingual')}</div>
        <div class="stats" id="ecc2-stats"></div>
      </div>

      <div class="ecc2-toolbar">
        <label style="font-size:12px;color:var(--ecc2-muted)">${__('Client:')}</label>
        <select id="ecc2-client-picker">
          <option value="">${__('— Catalog only (no client) —')}</option>
        </select>
        <button id="ecc2-lang-toggle" title="${__('Switch language')}">العربية</button>
      </div>

      <div class="ecc2-section">
        <h4>${__('Domains')}</h4>
        <div class="ecc2-domains" id="ecc2-domain-cards"></div>
      </div>

      <div class="ecc2-section">
        <h4 id="ecc2-subdomains-title">${__('Subdomains — click any to drill into its controls')}</h4>
        <div class="ecc2-subdomains" id="ecc2-subdomains"></div>
      </div>

      <div class="ecc2-section" id="ecc2-drilldown-section" style="display:none">
        <h4 id="ecc2-drilldown-title"></h4>
        <div id="ecc2-drilldown"></div>
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
                const sel = document.getElementById('ecc2-client-picker');
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
        method: 'alphax_grc.alphax_grc.page.grc_ecc2_dashboard.grc_ecc2_dashboard.get_ecc2_dashboard',
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
    renderSubdomains();
    if (STATE.selectedSubdomain) {
        loadDrilldown(STATE.selectedSubdomain);
    }
}

function renderHero() {
    const s = STATE.data.summary || {};
    const stats = [
        { num: s.total_controls || 0, lbl: __('Total controls') },
        { num: s.main_controls || 0, lbl: __('Main controls') },
        { num: s.sub_controls || 0, lbl: __('Sub-controls') },
        { num: Object.keys(s.domains_rollup || {}).length, lbl: __('Domains') },
    ];
    if (STATE.client) {
        stats.push({ num: s.tracked_for_client || 0, lbl: __('Tracked for client') });
    }
    document.getElementById('ecc2-stats').innerHTML = stats.map(x =>
        `<div class="stat"><div class="num">${x.num}</div><div class="lbl">${x.lbl}</div></div>`
    ).join('');
}

function renderDomainCards() {
    const rollup = (STATE.data.summary && STATE.data.summary.domains_rollup) || {};
    const subs = (STATE.data.subdomains) || [];
    const tgt = document.getElementById('ecc2-domain-cards');

    const domains = ['1', '2', '3', '4'];
    tgt.innerHTML = domains.map(d => {
        const colors = DOMAIN_COLORS[d];
        const total = Object.entries(rollup).find(([k, _]) => k.startsWith(d + ' '))?.[1] || 0;
        const subCount = subs.filter(s => (s.subdomain_code || '').startsWith(d + '-')).length;
        const label = STATE.lang === 'ar' ? colors.label_ar : colors.label_en;
        return `<div class="ecc2-domain-card" style="background:${colors.light};color:${colors.dark}"
                onclick="window.__ecc2FilterByDomain('${d}')">
            <div class="num" style="color:${colors.bg}">${total}</div>
            <div class="lbl"${STATE.lang === 'ar' ? ' style="direction:rtl;text-align:right"' : ''}>
                ${__('Domain') + ' ' + d + ' — ' + frappe.utils.escape_html(label)}
            </div>
            <div class="sub">${subCount} ${__('subdomains')}</div>
        </div>`;
    }).join('');
}

window.__ecc2FilterByDomain = function(domain) {
    // Scroll subdomains into view, briefly highlight matching ones
    const subdomainsEl = document.getElementById('ecc2-subdomains');
    if (!subdomainsEl) return;
    document.getElementById('ecc2-subdomains-title').textContent =
        __('Subdomains — Domain {0} — click any card to drill into controls', [domain]);
    subdomainsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    Array.from(subdomainsEl.children).forEach(child => {
        const code = child.getAttribute('data-subdomain') || '';
        child.style.opacity = code.startsWith(domain + '-') ? '1' : '0.35';
    });
};

function renderSubdomains() {
    const subs = (STATE.data.subdomains) || [];
    const impl = (STATE.data.subdomain_implementation) || {};
    const tgt = document.getElementById('ecc2-subdomains');
    if (!subs.length) {
        tgt.innerHTML = `<div class="ecc2-empty">${__('No catalog data — run bench migrate.')}</div>`;
        return;
    }

    // Sort subdomains numerically
    const sorted = [...subs].sort((a, b) => {
        const ap = (a.subdomain_code || '').split('-').map(Number);
        const bp = (b.subdomain_code || '').split('-').map(Number);
        return ap[0] - bp[0] || ap[1] - bp[1];
    });

    tgt.innerHTML = sorted.map(s => {
        const domainKey = (s.subdomain_code || '').split('-')[0];
        const colors = DOMAIN_COLORS[domainKey] || DOMAIN_COLORS['1'];
        const label = STATE.lang === 'ar'
            ? (s.subdomain_label_ar || s.subdomain_label_en || '')
            : (s.subdomain_label_en || s.subdomain_label_ar || '');
        const isSelected = STATE.selectedSubdomain === s.subdomain_code;

        // Implementation breakdown if client selected
        const subImpl = impl[s.subdomain_code];
        let progressBar = '';
        let legend = '';
        if (subImpl && subImpl.total > 0) {
            const pct = (k) => (subImpl[k] / subImpl.total * 100);
            progressBar = `<div class="progress">
                <div style="width:${pct('Implemented')}%; background:#5BA52A"></div>
                <div style="width:${pct('Partially Implemented')}%; background:#E5A82E"></div>
                <div style="width:${pct('Not Implemented')}%; background:#D44C4C"></div>
                <div style="width:${pct('Not Applicable')}%; background:#9C9C9C"></div>
                <div style="width:${pct('Untracked')}%; background:rgba(0,0,0,.06)"></div>
            </div>
            <div class="legend">
                <span><span class="dot" style="background:#5BA52A"></span>${subImpl['Implemented']}</span>
                <span><span class="dot" style="background:#E5A82E"></span>${subImpl['Partially Implemented']}</span>
                <span><span class="dot" style="background:#D44C4C"></span>${subImpl['Not Implemented']}</span>
                <span><span class="dot" style="background:#9C9C9C"></span>${subImpl['Not Applicable']}</span>
                <span style="opacity:.6">${subImpl['Untracked']} ${__('untracked')}</span>
            </div>`;
        }

        return `<div class="ecc2-subdomain ${isSelected ? 'selected' : ''} ${STATE.lang === 'ar' ? 'ar' : ''}"
                data-subdomain="${frappe.utils.escape_html(s.subdomain_code)}"
                onclick="window.__ecc2DrillSubdomain('${frappe.utils.escape_html(s.subdomain_code)}')">
            <div class="code-row">
                <span class="code" style="background:${colors.light};color:${colors.dark}">${frappe.utils.escape_html(s.subdomain_code)}</span>
                <span class="total">${s.total_controls} ${__('controls')}</span>
            </div>
            <div class="lbl">${frappe.utils.escape_html(label)}</div>
            ${progressBar}
        </div>`;
    }).join('');
}

window.__ecc2DrillSubdomain = function(code) {
    STATE.selectedSubdomain = code;
    renderSubdomains();
    loadDrilldown(code);
};

function loadDrilldown(code) {
    const args = { subdomain_code: code };
    if (STATE.client) args.client = STATE.client;

    document.getElementById('ecc2-drilldown-section').style.display = 'block';
    document.getElementById('ecc2-drilldown-title').textContent =
        __('Subdomain {0} — controls', [code]);
    document.getElementById('ecc2-drilldown').innerHTML =
        `<div class="ecc2-empty">${__('Loading…')}</div>`;

    frappe.call({
        method: 'alphax_grc.alphax_grc.page.grc_ecc2_dashboard.grc_ecc2_dashboard.get_subdomain_controls',
        args,
        callback: (r) => {
            const m = (r && r.message) || {};
            renderDrilldown(m.controls || []);
        },
    });
}

function renderDrilldown(controls) {
    const tgt = document.getElementById('ecc2-drilldown');
    if (!controls.length) {
        tgt.innerHTML = `<div class="ecc2-empty">${__('No controls in this subdomain.')}</div>`;
        return;
    }
    const ar = STATE.lang === 'ar';
    const headers = ar
        ? ['الرمز', 'النص', 'طريقة التطبيق', 'الحالة']
        : ['Code', 'Control', 'Implementation', 'Status'];

    tgt.innerHTML = `<table class="ecc2-controls-table ${ar ? 'ar' : ''}">
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>${controls.map(c => {
            const isSub = c.is_subcontrol;
            const text = ar ? (c.control_text_ar || c.control_text_en || '')
                            : (c.control_text_en || c.control_text_ar || '');
            const impl = ar ? (c.implementation_method_ar || '')
                            : (c.expected_output_ar ? '(see Arabic field)' : '');
            const cs = c.client_status || null;
            let statusHtml = `<span class="ecc2-status-chip ecc2-status-untracked">${__('Untracked')}</span>`;
            if (cs && cs.compliance_status) {
                let cls = 'ecc2-status-not';
                if (cs.compliance_status.includes('Implement') && cs.compliance_status.includes('Partial')) cls = 'ecc2-status-partial';
                else if (cs.compliance_status.includes('Implement')) cls = 'ecc2-status-implemented';
                else if (cs.compliance_status.includes('Applicable') || cs.compliance_status.includes('N/A')) cls = 'ecc2-status-na';
                statusHtml = `<span class="ecc2-status-chip ${cls}">${frappe.utils.escape_html(cs.compliance_status)}</span>`;
                if (cs.compliance_score) statusHtml += ` <span style="font-size:10px;color:var(--ecc2-muted)">${cs.compliance_score}%</span>`;
            }
            return `<tr onclick="frappe.set_route('Form', 'GRC NCA ECC2 Catalog', '${c.name}')">
                <td><span class="code">${frappe.utils.escape_html(c.control_code)}${isSub ? ' <span style="opacity:.6">↳</span>' : ''}</span></td>
                <td class="text-cell" style="max-width:400px">${frappe.utils.escape_html((text || '').substring(0, 220))}${(text || '').length > 220 ? '…' : ''}</td>
                <td class="text-cell" style="max-width:300px;font-size:11px;color:var(--ecc2-muted)">${frappe.utils.escape_html((impl || '').substring(0, 160))}${(impl || '').length > 160 ? '…' : ''}</td>
                <td>${statusHtml}</td>
            </tr>`;
        }).join('')}</tbody>
    </table>`;
}
