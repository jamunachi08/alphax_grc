// AlphaX GRC — ITGC Audit Programme Tracker v1.1.0
// Full bilingual EN/AR, RTL, Chart.js, live Frappe data
frappe.pages['grc-itgc-program'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'ITGC Audit Programme',
        single_column: true
    });

    // ── i18n ──────────────────────────────────────────────────────────
    const T = {
        en: {
            title: 'IT General Controls Audit Programme',
            subtitle: 'Shahidul Islam CISA·CISM·CISSP·CCSP | v1.1.0 | 145 Controls across 7 Domains',
            total: 'Total Controls', delivered: 'Delivered', pending: 'Pending',
            satisfactory: 'Satisfactory', improvement: 'Needs Improvement', unsatisfactory: 'Unsatisfactory',
            completion: 'Overall Completion', by_domain: 'Completion by Domain',
            by_type: 'Control Types', fw_coverage: 'Framework Coverage',
            domain_breakdown: 'Domain-by-Domain Progress',
            open_list: 'View All Controls', add_new: 'Add Control', refresh: 'Refresh',
            lang_btn: 'العربية', loading: 'Loading audit programme...',
            domain: 'Domain', controls: 'Controls', pct: 'Delivered %',
            review: 'Review Status', glba: 'GLBA', dlp: 'DLP',
            patch: 'Patch Mgmt', vendor: 'Vendor Mgmt',
            network: 'Network Sec', isp: 'InfoSec Program', ir: 'Incident Resp',
            admin_ctrl: 'Administrative', tech_ctrl: 'Technical', phys_ctrl: 'Physical',
        },
        ar: {
            title: 'برنامج تدقيق الضوابط العامة لتقنية المعلومات',
            subtitle: 'شاهدول إسلام CISA·CISM·CISSP·CCSP | v1.1.0 | 145 ضابطاً في 7 مجالات',
            total: 'إجمالي الضوابط', delivered: 'مُسلَّمة', pending: 'معلّقة',
            satisfactory: 'مُرضية', improvement: 'تحتاج تحسين', unsatisfactory: 'غير مُرضية',
            completion: 'نسبة الإنجاز الكلية', by_domain: 'الإنجاز حسب المجال',
            by_type: 'أنواع الضوابط', fw_coverage: 'تغطية الأطر',
            domain_breakdown: 'التفصيل حسب المجال',
            open_list: 'عرض كل الضوابط', add_new: 'إضافة ضابط', refresh: 'تحديث',
            lang_btn: 'English', loading: 'جارٍ تحميل برنامج التدقيق...',
            domain: 'المجال', controls: 'الضوابط', pct: 'نسبة التسليم',
            review: 'حالة المراجعة',
            glba: 'GLBA', dlp: 'DLP', patch: 'التصحيح', vendor: 'الموردون',
            network: 'أمن الشبكات', isp: 'برنامج أمن المعلومات', ir: 'الاستجابة للحوادث',
            admin_ctrl: 'إدارية', tech_ctrl: 'تقنية', phys_ctrl: 'مادية',
        }
    };
    let lang = (frappe.boot.lang === 'ar') ? 'ar' : 'en';
    const t = k => T[lang][k] || T.en[k] || k;

    // ── Colour theme ──────────────────────────────────────────────────
    const C = {
        primary: '#0B132B', accent: '#2563EB', bg: '#F8FAFC', card: '#FFFFFF',
        text: '#1E293B', muted: '#64748B',
        delivered: '#10B981', pending: '#F59E0B', overdue: '#DC2626',
        satisfactory: '#10B981', improvement: '#F59E0B', unsatisfactory: '#EF4444',
        glba: '#2563EB', dlp: '#7C3AED', patch: '#D97706',
        vendor: '#0891B2', network: '#DC2626', isp: '#059669', ir: '#F59E0B',
        admin: '#3B82F6', tech: '#10B981', phys: '#F59E0B',
    };

    const DOMAIN_COLOURS = {
        'GLBA Compliance': C.glba, 'Data Loss Prevention': C.dlp,
        'Patch Management': C.patch, 'Vendor Management': C.vendor,
        'Network Security': C.network, 'Information Security Program': C.isp,
        'Incident Response': C.ir
    };

    let DATA = null;
    let domainChart = null, typeChart = null, fwChart = null;

    function loadScript(src, cb) {
        if (window.Chart) { cb(); return; }
        const s = document.createElement('script'); s.src = src; s.onload = cb;
        document.head.appendChild(s);
    }

    function fetchData(cb) {
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_itgc_program.grc_itgc_program.get_itgc_summary',
            callback(r) { DATA = (r && r.message) || null; cb(); },
            error() { DATA = null; cb(); }
        });
    }

    function render() {
        const dir = lang === 'ar' ? 'rtl' : 'ltr';
        const d = DATA || {};
        const total = d.total || 145;
        const delivered = d.delivered || 0;
        const pending = d.pending || 0;
        const satisfactory = d.satisfactory || 0;
        const improvement = d.requires_improvement || 0;
        const unsatisfactory = d.unsatisfactory || 0;
        const pct = d.completion_pct || 0;

        // Progress ring
        const ring = progressRing(pct, C.accent, 80);

        // Domain table
        const domains = d.domains || [];
        const domainRows = domains.map(dom => {
            const dpct = dom.total ? Math.round(dom.delivered / dom.total * 100) : 0;
            const col = DOMAIN_COLOURS[dom.control_domain] || C.accent;
            const shortName = domainShort(dom.control_domain);
            return `<tr>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;font-size:12px;color:${C.text}">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${col};margin-${dir==='rtl'?'left':'right'}:6px"></span>${shortName}
              </td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;font-weight:600">${dom.total}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;color:${C.delivered}">${dom.delivered}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;color:${C.pending}">${dom.pending}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;min-width:120px">
                <div style="height:6px;border-radius:4px;background:#f1f5f9;overflow:hidden">
                  <div style="height:100%;width:${dpct}%;background:${col};border-radius:4px"></div>
                </div>
                <div style="font-size:10px;color:${C.muted};margin-top:2px;text-align:center">${dpct}%</div>
              </td>
            </tr>`;
        }).join('');

        // Framework coverage badges
        const fw = d.fw_coverage || {};
        const fwItems = [
            ['GLBA', fw.glba||0, '#2563EB'], ['NIST', fw.nist||0, '#10B981'],
            ['ISO 27001', fw.iso||0, '#D97706'], ['PCI DSS', fw.pci_dss||0, '#7C3AED'],
            ['COBIT', fw.cobit||0, '#0891B2'], ['CIS Top 20', fw.cis||0, '#DC2626'],
            ['FFIEC', fw.ffiec||0, '#059669'], ['NCUA', fw.ncua||0, '#F59E0B'],
            ['NCA ECC', fw.nca_ecc||0, '#EF4444'], ['SAMA', fw.sama||0, '#6366F1'],
        ];
        const fwBadges = fwItems.map(([name, count, col]) =>
            `<div style="background:${C.card};border:.5px solid #e2e8f0;border-radius:8px;padding:10px 14px;text-align:center;border-top:3px solid ${col}">
              <div style="font-size:20px;font-weight:700;color:${col}">${count}</div>
              <div style="font-size:10px;color:${C.muted};margin-top:2px">${name}</div>
            </div>`
        ).join('');

        const html = `
<div style="direction:${dir};font-family:'Segoe UI',Tahoma,system-ui,sans-serif;background:${C.bg};min-height:100vh">

  <!-- HEADER -->
  <div style="background:${C.primary};color:#fff;padding:14px 24px;border-bottom:3px solid ${C.accent}">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
      <div>
        <div style="font-size:17px;font-weight:700">${t('title')}</div>
        <div style="font-size:11px;opacity:.6;margin-top:3px">${t('subtitle')}</div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button onclick="window.location.href='/app/grc-itgc-audit-item/new'" style="padding:6px 14px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:${C.accent};color:#fff;cursor:pointer;font-size:12px;font-weight:600">+ ${t('add_new')}</button>
        <a href="/app/grc-itgc-audit-item" style="padding:6px 14px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font-size:12px;text-decoration:none">${t('open_list')}</a>
        <button id="itgc-lang" style="padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;cursor:pointer;font-size:12px">${t('lang_btn')}</button>
        <button id="itgc-refresh" style="padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;cursor:pointer;font-size:12px">${t('refresh')}</button>
      </div>
    </div>
  </div>

  <div style="padding:18px;display:flex;flex-direction:column;gap:16px">

    <!-- KPI ROW -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px">
      ${kpi(total, t('total'), C.accent)}
      ${kpi(delivered, t('delivered'), C.delivered)}
      ${kpi(pending, t('pending'), C.pending)}
      ${kpi(satisfactory, t('satisfactory'), C.satisfactory)}
      ${kpi(improvement, t('improvement'), C.improvement)}
      ${kpi(unsatisfactory, t('unsatisfactory'), C.unsatisfactory)}
    </div>

    <!-- COMPLETION + CHARTS ROW -->
    <div style="display:grid;grid-template-columns:180px 1fr 1fr;gap:16px">

      <!-- Progress ring -->
      <div class="gc" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">
        <div style="font-size:12px;font-weight:600;color:${C.text}">${t('completion')}</div>
        ${ring}
      </div>

      <!-- Domain bar chart -->
      <div class="gc">
        <div class="gct">${t('by_domain')}</div>
        <div style="position:relative;height:200px;background:#ffffff;border-radius:6px"><canvas id="itgc-domain-chart" aria-label="${t('by_domain')}"></canvas></div>
      </div>

      <!-- Control type + framework doughnut -->
      <div class="gc">
        <div class="gct">${t('by_type')}</div>
        <div style="position:relative;height:200px;background:#ffffff;border-radius:6px"><canvas id="itgc-type-chart" aria-label="${t('by_type')}"></canvas></div>
        <div id="itgc-type-leg" style="display:flex;gap:10px;justify-content:center;margin-top:8px;font-size:11px;flex-wrap:wrap"></div>
      </div>

    </div>

    <!-- FRAMEWORK COVERAGE -->
    <div class="gc">
      <div class="gct">${t('fw_coverage')}</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:10px">
        ${fwBadges}
      </div>
    </div>

    <!-- DOMAIN TABLE -->
    <div class="gc">
      <div class="gct">${t('domain_breakdown')}</div>
      <table style="width:100%;border-collapse:collapse">
        <thead><tr style="background:#f8fafc">
          <th style="padding:8px 10px;text-align:${dir==='rtl'?'right':'left'};font-size:11px;color:${C.muted};font-weight:600;text-transform:uppercase;border-bottom:1px solid #e2e8f0">${t('domain')}</th>
          <th style="padding:8px 10px;text-align:center;font-size:11px;color:${C.muted};font-weight:600;text-transform:uppercase;border-bottom:1px solid #e2e8f0">${t('controls')}</th>
          <th style="padding:8px 10px;text-align:center;font-size:11px;color:${C.muted};font-weight:600;text-transform:uppercase;border-bottom:1px solid #e2e8f0">${t('delivered')}</th>
          <th style="padding:8px 10px;text-align:center;font-size:11px;color:${C.muted};font-weight:600;text-transform:uppercase;border-bottom:1px solid #e2e8f0">${t('pending')}</th>
          <th style="padding:8px 10px;font-size:11px;color:${C.muted};font-weight:600;text-transform:uppercase;border-bottom:1px solid #e2e8f0;min-width:140px">${t('pct')}</th>
        </tr></thead>
        <tbody>${domainRows || defaultDomainRows(dir)}</tbody>
      </table>
    </div>

  </div>
</div>
<style>
.gc{background:${C.card};border:.5px solid #e2e8f0;border-radius:12px;padding:16px}
.gct{font-size:13px;font-weight:600;margin-bottom:12px;color:${C.text}}
</style>`;

        $(page.body).html(html);

        // Wire buttons
        $('#itgc-lang').on('click', () => { lang = lang === 'en' ? 'ar' : 'en'; render(); drawCharts(); });
        $('#itgc-refresh').on('click', () => {
            $(page.body).html(`<div style="padding:60px;text-align:center;color:${C.muted}">${t('loading')}</div>`);
            fetchData(() => { render(); drawCharts(); });
        });

        drawCharts();
    }

    function kpi(val, label, colour) {
        return `<div style="background:${C.card};border:.5px solid #e2e8f0;border-radius:10px;padding:14px 16px;border-top:3px solid ${colour}">
          <div style="font-size:26px;font-weight:700;color:${colour}">${val}</div>
          <div style="font-size:10px;color:${C.muted};text-transform:uppercase;letter-spacing:.06em;margin-top:4px">${label}</div>
        </div>`;
    }

    function progressRing(pct, colour, size) {
        const r = (size - 12) / 2;
        const circ = 2 * Math.PI * r;
        const filled = (pct / 100) * circ;
        return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
          <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="8"/>
          <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${colour}" stroke-width="8"
            stroke-dasharray="${filled} ${circ - filled}" stroke-dashoffset="${circ/4}" stroke-linecap="round"/>
          <text x="${size/2}" y="${size/2 + 6}" text-anchor="middle" font-size="16" font-weight="700" fill="${colour}">${pct}%</text>
        </svg>`;
    }

    function domainShort(domain) {
        const m = {'GLBA Compliance':'GLBA','Data Loss Prevention':'DLP',
            'Patch Management':'Patch Mgmt','Vendor Management':'Vendor Mgmt',
            'Network Security':'Network Sec','Information Security Program':'InfoSec Program',
            'Incident Response':'Incident Resp'};
        return m[domain] || domain;
    }

    function defaultDomainRows(dir) {
        const defaults = [
            ['GLBA Compliance', 22], ['Data Loss Prevention', 23], ['Patch Management', 10],
            ['Vendor Management', 11], ['Network Security', 39], ['Information Security Program', 33], ['Incident Response', 8]
        ];
        return defaults.map(([d, n]) => {
            const col = DOMAIN_COLOURS[d] || C.accent;
            return `<tr>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;font-size:12px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${col};margin-${dir==='rtl'?'left':'right'}:6px"></span>${d}
              </td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;font-weight:600">${n}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;color:${C.delivered}">0</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9;text-align:center;font-size:12px;color:${C.pending}">${n}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid #f1f5f9">
                <div style="height:6px;border-radius:4px;background:#f1f5f9;overflow:hidden">
                  <div style="height:100%;width:0%;background:${col};border-radius:4px"></div>
                </div>
                <div style="font-size:10px;color:${C.muted};margin-top:2px;text-align:center">0%</div>
              </td>
            </tr>`;
        }).join('');
    }

    function drawCharts() {
        if (!window.Chart) return;
        if (domainChart) { try { domainChart.destroy(); } catch(e) {} }
        if (typeChart) { try { typeChart.destroy(); } catch(e) {} }

        const d = DATA || {};
        const domains = d.domains && d.domains.length ? d.domains : [
            {control_domain:'GLBA Compliance',total:22,delivered:0},
            {control_domain:'Data Loss Prevention',total:23,delivered:0},
            {control_domain:'Patch Management',total:10,delivered:0},
            {control_domain:'Vendor Management',total:11,delivered:0},
            {control_domain:'Network Security',total:39,delivered:0},
            {control_domain:'Information Security Program',total:33,delivered:0},
            {control_domain:'Incident Response',total:8,delivered:0},
        ];

        const domainLabels = domains.map(d => domainShort(d.control_domain));
        const domainTotals = domains.map(d => d.total || 0);
        const domainDelivered = domains.map(d => d.delivered || 0);
        const domainCols = domains.map(d => DOMAIN_COLOURS[d.control_domain] || C.accent);

        const domEl = document.getElementById('itgc-domain-chart');
        if (domEl) {
            domainChart = new Chart(domEl, {
                type: 'bar',
                data: {
                    labels: domainLabels,
                    datasets: [
                        { label: lang === 'ar' ? 'الإجمالي' : 'Total', data: domainTotals, backgroundColor: domainCols.map(c => c + '44'), borderRadius: 4 },
                        { label: lang === 'ar' ? 'مُسلَّم' : 'Delivered', data: domainDelivered, backgroundColor: domainCols, borderRadius: 4 },
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top', labels: { font: { size: 10 }, color: C.muted, boxWidth: 10 } } },
                    scales: {
                        x: { ticks: { font: { size: 9 }, color: C.muted, maxRotation: 35, autoSkip: false }, grid: { display: false } },
                        y: { ticks: { font: { size: 9 }, color: C.muted, precision: 0 }, grid: { color: 'rgba(0,0,0,.04)' }, beginAtZero: true }
                    }
                }
            });
        }

        // Control type doughnut
        const ct = d.ctrl_types || {};
        const typeLabels = lang === 'ar' ? ['إدارية','تقنية','مادية'] : ['Administrative','Technical','Physical'];
        const typeVals = [ct.administrative||0, ct.technical||0, ct.physical||0];
        const typeCols = [C.admin, C.tech, C.phys];

        const typeEl = document.getElementById('itgc-type-chart');
        if (typeEl) {
            typeChart = new Chart(typeEl, {
                type: 'doughnut',
                data: { labels: typeLabels, datasets: [{ data: typeVals, backgroundColor: typeCols, borderWidth: 2 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '58%', plugins: { legend: { display: false } } }
            });
            document.getElementById('itgc-type-leg').innerHTML = typeLabels.map((l, i) =>
                `<span style="display:flex;align-items:center;gap:4px;font-size:11px">
                  <span style="width:10px;height:10px;border-radius:50%;background:${typeCols[i]}"></span>
                  <span style="color:${C.muted}">${l} (${typeVals[i]})</span>
                </span>`
            ).join('');
        }
    }

    // ── INIT ──────────────────────────────────────────────────────────
    $(page.body).html(`<div style="padding:60px;text-align:center;color:#64748b">Loading ITGC Audit Programme...</div>`);
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js', () => {
        if (window.Chart && !window.__grcBgPluginReg) {
            window.__grcBgPluginReg = true;
            Chart.register({
                id: 'grcWhiteBg',
                beforeDraw(chart) {
                    const ctx = chart.canvas.getContext('2d');
                    ctx.save();
                    ctx.globalCompositeOperation = 'destination-over';
                    ctx.fillStyle = '#ffffff';
                    ctx.fillRect(0, 0, chart.width, chart.height);
                    ctx.restore();
                }
            });
        }
        fetchData(() => { render(); drawCharts(); });
    });
};
