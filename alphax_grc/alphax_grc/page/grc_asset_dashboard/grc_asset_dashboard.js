// AlphaX GRC — Asset Inventory & NCA ECC-2:2024 Dashboard v1.2.0
// ISO 27001 Asset Register (6 types: Software, Network Devices, Servers, Laptops, Media, Desktops)
// NCA ECC-2:2024 Technology Mapping with 4 strategic pillars
// Full bilingual EN/AR with RTL layout switching
frappe.pages['grc-asset-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, title: 'Asset Inventory Dashboard', single_column: true });

    // ── i18n ──────────────────────────────────────────────────────────
    const T = {
        en: {
            title: 'Asset Inventory & NCA ECC-2:2024 Dashboard',
            subtitle: 'ISO 27001 Asset Register · 6 Asset Types · CIA Classification · NCA ECC Technology Mapping',
            kpi_total: 'Total Assets', kpi_critical: 'Critical', kpi_high: 'High Criticality',
            kpi_pdpl: 'Contains PDPL Data', kpi_eol: 'End of Life', kpi_overdue: 'Overdue Review',
            sec_type: 'Assets by Type', sec_crit: 'Assets by Criticality',
            sec_nca_status: 'NCA ECC-2:2024 Compliance Status',
            sec_pillars: 'ECC-2:2024 Strategic Pillars',
            sec_nca_map: 'NCA ECC-2:2024 Technology Mapping — Full Control Set',
            sec_recent: 'Recently Added Assets',
            pillar_zt: 'Zero Trust Architecture (ZTA)',
            pillar_res: 'Cyber Resilience',
            pillar_pdpl: 'Data Sovereignty & Privacy (PDPL)',
            pillar_ai: 'Automation & AI (SOAR)',
            nca_compliant: 'Compliant', nca_partial: 'Partially Compliant',
            nca_non: 'Non-Compliant', nca_assessed: 'Not Assessed',
            col_domain: 'Domain', col_ctrl: 'Control', col_name: 'Control Name & Pillars',
            col_tech: 'Technology Type', col_vendors: 'Recommended Vendors',
            btn_add: 'New Asset', btn_all: 'View All', btn_refresh: 'Refresh', btn_lang: 'العربية',
            filter_all: 'All Domains', loading: 'Loading dashboard data...',
            score: 'Avg Compliance Score', controls_mapped: 'controls mapped',
        },
        ar: {
            title: 'لوحة جرد الأصول و NCA ECC-2:2024',
            subtitle: 'سجل الأصول ISO 27001 · 6 أنواع أصول · تصنيف CIA · خريطة تقنيات NCA ECC',
            kpi_total: 'إجمالي الأصول', kpi_critical: 'حرجة', kpi_high: 'عالية الأهمية',
            kpi_pdpl: 'تحتوي بيانات PDPL', kpi_eol: 'انتهاء العمر', kpi_overdue: 'مراجعة متأخرة',
            sec_type: 'الأصول حسب النوع', sec_crit: 'الأصول حسب الأهمية',
            sec_nca_status: 'حالة امتثال NCA ECC-2:2024',
            sec_pillars: 'الركائز الاستراتيجية ECC-2:2024',
            sec_nca_map: 'خريطة تقنيات NCA ECC-2:2024 — مجموعة الضوابط الكاملة',
            sec_recent: 'الأصول المضافة حديثاً',
            pillar_zt: 'الثقة الصفرية (ZTA)',
            pillar_res: 'المرونة الإلكترونية',
            pillar_pdpl: 'السيادة على البيانات والخصوصية (PDPL)',
            pillar_ai: 'الأتمتة والذكاء الاصطناعي (SOAR)',
            nca_compliant: 'ممتثلة', nca_partial: 'ممتثلة جزئياً',
            nca_non: 'غير ممتثلة', nca_assessed: 'لم تُقيَّم',
            col_domain: 'المجال', col_ctrl: 'الضابط', col_name: 'اسم الضابط والركائز',
            col_tech: 'نوع التقنية', col_vendors: 'الموردون الموصى بهم',
            btn_add: 'أصل جديد', btn_all: 'عرض الكل', btn_refresh: 'تحديث', btn_lang: 'English',
            filter_all: 'كل المجالات', loading: 'جارٍ تحميل بيانات اللوحة...',
            score: 'متوسط درجة الامتثال', controls_mapped: 'ضابطاً مرتبطاً',
        }
    };
    let lang = (frappe.boot.lang === 'ar') ? 'ar' : 'en';
    const t = k => T[lang][k] || T.en[k] || k;

    // ── Colour palette ─────────────────────────────────────────────────
    const C = {
        nav: '#0B132B', accent: '#2563EB', bg: '#F8FAFC', card: '#FFFFFF',
        text: '#1E293B', muted: '#64748B', border: '#E2E8F0',
        critical: '#DC2626', high: '#D97706', medium: '#F59E0B', low: '#16A34A', vlow: '#10B981',
        ok: '#10B981', warn: '#F59E0B', danger: '#EF4444',
        gov: '#2563EB', def: '#DC2626', res: '#10B981', ext: '#7C3AED', tech: '#0891B2',
    };

    const TYPE_META = {
        'Software':              { icon: '💾', colour: '#2563EB', ar: 'برمجيات' },
        'Network Device':        { icon: '🔌', colour: '#7C3AED', ar: 'أجهزة شبكة' },
        'Server':                { icon: '🖥️', colour: '#DC2626', ar: 'خوادم' },
        'Laptop':                { icon: '💻', colour: '#D97706', ar: 'أجهزة محمولة' },
        'Desktop':               { icon: '🖱️', colour: '#059669', ar: 'أجهزة مكتبية' },
        'Media / Portable Device':{ icon: '💿', colour: '#0891B2', ar: 'وسائط متنقلة' },
        'Cloud Service':         { icon: '☁️', colour: '#F59E0B', ar: 'خدمات سحابية' },
        'Physical / Facility':   { icon: '🏢', colour: '#6366F1', ar: 'مباني ومرافق' },
        'Service':               { icon: '⚙️', colour: '#EF4444', ar: 'خدمات' },
    };
    const CRIT_META = {
        'Critical': C.critical, 'High': C.high, 'Medium': C.medium, 'Low': C.low, 'Very Low': C.vlow,
    };
    const DOMAIN_META = {
        'Governance': { colour: C.gov }, 'Defense': { colour: C.def },
        'Resilience':  { colour: C.res }, 'External Parties': { colour: C.ext },
        'Technical Systems': { colour: C.tech },
    };
    const PILLARS_DEF = [
        { key: 'zero_trust',        en: 'Zero Trust Architecture (ZTA)', ar: 'الثقة الصفرية (ZTA)',     colour: '#7C3AED' },
        { key: 'cyber_resilience',  en: 'Cyber Resilience',              ar: 'المرونة الإلكترونية',      colour: '#059669' },
        { key: 'data_sovereignty',  en: 'Data Sovereignty & Privacy',    ar: 'السيادة على البيانات',     colour: '#0891B2' },
        { key: 'ai_automation',     en: 'Automation & AI (SOAR)',        ar: 'الذكاء الاصطناعي والأتمتة', colour: '#D97706' },
    ];

    // NCA ECC full control set (from CYBERSECURITY_TECHNOLOGY_MAPPING.pdf)
    const NCA_CONTROLS = [
        { domain:'Governance', ctrl:'1.3-1.5', name:'Cybersecurity Policies & Risk',    name_ar:'سياسات الأمن السيبراني والمخاطر',    type:'GRC Solutions',             vendors:'ServiceNow / Archer / CyberImtithal',    pillars:['data_sovereignty'] },
        { domain:'Governance', ctrl:'1.10',    name:'Awareness & Training',             name_ar:'التوعية والتدريب',                    type:'Security Awareness Systems', vendors:'KnowBe4 / Proofpoint / PhishRod',        pillars:[] },
        { domain:'Defense',    ctrl:'2.1',     name:'Asset Management (ITAM/CAASM)',    name_ar:'إدارة الأصول',                        type:'ITAM / CAASM',               vendors:'ServiceNow / Axonius / ManageEngine',    pillars:[] },
        { domain:'Defense',    ctrl:'2.2',     name:'Identity & Access (IAM/PAM/IGA)',  name_ar:'إدارة الهوية والوصول',               type:'IAM / PAM / IGA',            vendors:'CyberArk / SailPoint / Okta / BeyondTrust', pillars:['zero_trust'] },
        { domain:'Defense',    ctrl:'2.3',     name:'Systems Protection (EDR/XDR)',     name_ar:'حماية الأنظمة',                       type:'EDR / XDR',                  vendors:'CrowdStrike / SentinelOne / Trend Micro', pillars:['cyber_resilience'] },
        { domain:'Defense',    ctrl:'2.3',     name:'Data Protection (DLP/DSPM)',       name_ar:'حماية البيانات',                       type:'DLP / DSPM / Purview',       vendors:'Forcepoint / Varonis / MS Purview',      pillars:['data_sovereignty','cyber_resilience'] },
        { domain:'Defense',    ctrl:'2.4',     name:'Email Security (SEG)',             name_ar:'أمن البريد الإلكتروني',               type:'Cloud Email Security (SEG)', vendors:'Proofpoint / Mimecast / Ironscales',     pillars:[] },
        { domain:'Defense',    ctrl:'2.5',     name:'Network Security (NGFW/ZTNA)',     name_ar:'أمن الشبكات (ZTNA)',                  type:'NGFW / NAC / ZTNA',          vendors:'Palo Alto / Fortinet / Cisco / Illumio', pillars:['zero_trust'] },
        { domain:'Defense',    ctrl:'2.5',     name:'Web & App Security (WAF/WAAP)',    name_ar:'أمن الويب والتطبيقات',               type:'WAF / WAAP / API Security',  vendors:'F5 / Imperva / Akamai / Cloudflare',     pillars:[] },
        { domain:'Defense',    ctrl:'2.10',    name:'Vulnerability Management (RBVM)',  name_ar:'إدارة الثغرات',                       type:'RBVM / VM',                  vendors:'Tenable / Qualys / Rapid7',              pillars:[] },
        { domain:'Defense',    ctrl:'2.11',    name:'Penetration Testing (BAS)',        name_ar:'اختبار الاختراق',                     type:'BAS / Pentest Tools',        vendors:'XM Cyber / Pentera / Metasploit',        pillars:[] },
        { domain:'Resilience', ctrl:'2.9',     name:'Backup & Recovery (Immutable)',    name_ar:'النسخ الاحتياطي والاسترداد',         type:'Immutable Backup / DR',      vendors:'Veeam / Cohesity / Rubrik / Veritas',    pillars:['cyber_resilience'] },
        { domain:'Resilience', ctrl:'2.12',    name:'Security Monitoring (SIEM/SOAR)', name_ar:'مراقبة الأمن (SIEM/SOAR)',           type:'Next-Gen SIEM / SOAR',       vendors:'Splunk / MS Sentinel / IBM QRadar',      pillars:['cyber_resilience','ai_automation'] },
        { domain:'External Parties', ctrl:'3.1', name:'Supply Chain Security (TPRM)', name_ar:'أمن سلسلة التوريد',                   type:'TPRM / VRM',                 vendors:'BitSight / SecurityScorecard',            pillars:['data_sovereignty'] },
        { domain:'Technical Systems', ctrl:'4.2', name:'Cloud Security (CSPM/CNAPP)', name_ar:'أمن السحابة',                         type:'CSPM / CWPP / CNAPP',        vendors:'Wiz / Prisma Cloud / Orca Security',     pillars:['zero_trust','cyber_resilience'] },
    ];

    let DATA = null, NCA_DATA = null;
    let typeChart = null, critChart = null;
    let activeDomain = 'all';

    // ── Script loader ──────────────────────────────────────────────────
    function loadScript(src, cb) {
        if (window.Chart) { cb(); return; }
        const s = document.createElement('script'); s.src = src; s.onload = cb;
        document.head.appendChild(s);
    }

    // ── API calls ──────────────────────────────────────────────────────
    function fetchAll(cb) {
        let done = 0;
        const finish = () => { if (++done === 2) cb(); };
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_asset_dashboard.grc_asset_dashboard.get_asset_summary',
            callback(r) { DATA = (r && r.message) || null; finish(); },
            error() { DATA = null; finish(); }
        });
        frappe.call({
            method: 'alphax_grc.alphax_grc.page.grc_asset_dashboard.grc_asset_dashboard.get_nca_ecc_summary',
            callback(r) { NCA_DATA = (r && r.message) || null; finish(); },
            error() { NCA_DATA = null; finish(); }
        });
    }

    // ── Helpers ────────────────────────────────────────────────────────
    function pillarBadge(key) {
        const p = PILLARS_DEF.find(x => x.key === key);
        if (!p) return '';
        const abbr = { zero_trust: 'ZTA', cyber_resilience: 'CR', data_sovereignty: 'PDPL', ai_automation: 'AI' }[key] || key;
        return `<span style="background:${p.colour}22;color:${p.colour};padding:1px 5px;border-radius:3px;font-size:9px;font-weight:600;margin-left:3px">${abbr}</span>`;
    }

    // ── RENDER ─────────────────────────────────────────────────────────
    function render() {
        const dir  = lang === 'ar' ? 'rtl' : 'ltr';
        const flip = lang === 'ar' ? 'right' : 'left';
        const d = DATA || {};
        const n = NCA_DATA || {};

        /* ── KPI values ── */
        const total    = d.total           || 0;
        const critical = d.critical        || 0;
        const high     = d.high            || 0;
        const pdpl     = d.personal_data   || 0;
        const eol      = d.end_of_life     || 0;
        const overdue  = d.overdue         || 0;

        /* ── NCA compliance bar ── */
        const ncaCompliant = n.compliant    || 0;
        const ncaPartial   = n.partial      || 0;
        const ncaNon       = n.non_compliant|| 0;
        const ncaNotAssess = n.not_assessed || 0;
        const ncaTotal     = n.total        || 15;
        const ncaScore     = n.score        || 0;

        /* ── Pillar counts ── */
        const bp = n.by_pillar || {};

        /* ── NCA domain progress ── */
        const byDomain = n.by_domain || [];

        /* ── Recent assets ── */
        const recent = (d.recent || []).slice(0, 8);

        // Filtered NCA controls
        const filteredNCA = activeDomain === 'all'
            ? NCA_CONTROLS
            : NCA_CONTROLS.filter(c => c.domain.toLowerCase().replace(/ /g,'-') === activeDomain);

        const ncaRows = filteredNCA.map(row => {
            const dc = DOMAIN_META[row.domain] || { colour: C.accent };
            const name = lang === 'ar' ? row.name_ar : row.name;
            const badges = row.pillars.map(pillarBadge).join('');
            return `<tr onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background=''">
              <td style="padding:8px 10px;border-bottom:.5px solid ${C.border}">
                <span style="background:${dc.colour}20;color:${dc.colour};padding:2px 7px;border-radius:3px;font-size:9px;font-weight:700;white-space:nowrap">${row.domain}</span>
              </td>
              <td style="padding:8px 10px;border-bottom:.5px solid ${C.border};text-align:center;font-size:11px;font-weight:600;color:${C.text};white-space:nowrap">${row.ctrl}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid ${C.border};font-size:12px;color:${C.text}">${name}${badges}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid ${C.border};font-size:11px;color:#0891B2;font-weight:500">${row.type}</td>
              <td style="padding:8px 10px;border-bottom:.5px solid ${C.border};font-size:11px;color:${C.muted}">${row.vendors}</td>
            </tr>`;
        }).join('');

        const domainFilters = ['all','Governance','Defense','Resilience','External Parties','Technical Systems'].map(d => {
            const label = d === 'all' ? t('filter_all') : d;
            const col   = d === 'all' ? C.accent : (DOMAIN_META[d]?.colour || C.accent);
            const active = (activeDomain === d.toLowerCase().replace(/ /g,'-')) || (d === 'all' && activeDomain === 'all');
            const key   = d === 'all' ? 'all' : d.toLowerCase().replace(/ /g,'-');
            return `<button onclick="window.__grcFilterDomain('${key}')" style="padding:4px 11px;border-radius:5px;border:.5px solid ${active?col:C.border};background:${active?col:'transparent'};color:${active?'#fff':C.muted};cursor:pointer;font-size:11px;transition:all .15s">${label}</button>`;
        }).join('');

        const domainBars = byDomain.map(bd => {
            const col = DOMAIN_META[bd.main_domain]?.colour || C.accent;
            const pct = bd.total ? Math.round(bd.compliant / bd.total * 100) : 0;
            return `<div style="margin-bottom:9px">
              <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px">
                <span style="color:${C.text}">${bd.main_domain}</span>
                <span style="color:${col};font-weight:600">${bd.compliant}/${bd.total} · ${pct}%</span>
              </div>
              <div style="height:5px;border-radius:3px;background:#f1f5f9;overflow:hidden">
                <div style="height:100%;width:${pct}%;background:${col};border-radius:3px"></div>
              </div>
            </div>`;
        }).join('');

        const recentCards = recent.map(a => {
            const col = CRIT_META[a.asset_criticality] || C.muted;
            const tm  = TYPE_META[a.asset_type] || { icon:'📁', colour: C.accent };
            return `<a href="/app/grc-asset-inventory/${a.name}" style="text-decoration:none">
              <div style="background:${C.card};border:.5px solid ${C.border};border-radius:10px;padding:12px;border-left:3px solid ${col};transition:box-shadow .2s"
                   onmouseover="this.style.boxShadow='0 3px 12px rgba(0,0,0,.07)'" onmouseout="this.style.boxShadow='none'">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span style="font-size:18px">${tm.icon}</span>
                  <div style="font-size:12px;font-weight:600;color:${C.text};overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${a.asset_name}</div>
                </div>
                <div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:5px">
                  <span style="background:#f1f5f9;color:#475569;padding:1px 6px;border-radius:3px;font-size:10px">${a.asset_type||'—'}</span>
                  <span style="background:${col}20;color:${col};padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700">${a.asset_criticality||'—'}</span>
                  ${a.contains_personal_data ? `<span style="background:#7C3AED20;color:#7C3AED;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700">PDPL</span>` : ''}
                </div>
                <div style="font-size:10px;color:${C.muted}">
                  C: <strong>${(a.confidentiality||'—').charAt(0)}</strong> &nbsp;
                  I: <strong>${(a.integrity||'—').charAt(0)}</strong> &nbsp;
                  A: <strong>${(a.availability||'—').charAt(0)}</strong>
                  ${a.nca_ecc_domain ? `&nbsp;· <span style="color:${DOMAIN_META[a.nca_ecc_domain]?.colour||C.accent}">${a.nca_ecc_domain}</span>` : ''}
                </div>
              </div>
            </a>`;
        }).join('');

        const html = `
<div id="ad-root" style="direction:${dir};font-family:'Segoe UI',Tahoma,system-ui,sans-serif;background:${C.bg};min-height:100vh">

  <!-- HEADER -->
  <div style="background:${C.nav};color:#fff;padding:14px 22px;border-bottom:3px solid ${C.accent}">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
      <div>
        <div style="font-size:17px;font-weight:600;letter-spacing:.01em">${t('title')}</div>
        <div style="font-size:11px;opacity:.6;margin-top:2px">${t('subtitle')}</div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <a href="/app/grc-asset-inventory/new" style="padding:6px 14px;border-radius:6px;background:${C.accent};color:#fff;font-size:12px;font-weight:600;text-decoration:none">+ ${t('btn_add')}</a>
        <a href="/app/grc-asset-inventory" style="padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;font-size:12px;text-decoration:none">${t('btn_all')}</a>
        <button id="ad-lang" style="padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;cursor:pointer;font-size:12px">${t('btn_lang')}</button>
        <button id="ad-refresh" style="padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.1);color:#fff;cursor:pointer;font-size:12px">${t('btn_refresh')}</button>
      </div>
    </div>
  </div>

  <div style="padding:18px;display:flex;flex-direction:column;gap:16px">

    <!-- KPI STRIP -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px">
      ${kpi(total,    t('kpi_total'),    C.accent)}
      ${kpi(critical, t('kpi_critical'), C.critical)}
      ${kpi(high,     t('kpi_high'),     C.high)}
      ${kpi(pdpl,     t('kpi_pdpl'),     '#7C3AED')}
      ${kpi(eol,      t('kpi_eol'),      C.medium)}
      ${kpi(overdue,  t('kpi_overdue'),  '#EF4444')}
    </div>

    <!-- ROW 2: Charts + NCA Status -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px">

      <div class="grc-card">
        <div class="grc-card-title">${t('sec_type')}</div>
        <div style="position:relative;height:210px;background:#ffffff;border-radius:6px"><canvas id="ad-type" role="img" aria-label="${t('sec_type')}">Asset types</canvas></div>
        <div id="ad-type-leg" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;font-size:10px"></div>
      </div>

      <div class="grc-card">
        <div class="grc-card-title">${t('sec_crit')}</div>
        <div style="position:relative;height:210px;background:#ffffff;border-radius:6px"><canvas id="ad-crit" role="img" aria-label="${t('sec_crit')}">Criticality</canvas></div>
        <div id="ad-crit-leg" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;font-size:10px"></div>
      </div>

      <div class="grc-card">
        <div class="grc-card-title">${t('sec_nca_status')}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
          ${ncaMini(ncaCompliant, t('nca_compliant'), C.ok)}
          ${ncaMini(ncaPartial,   t('nca_partial'),   C.medium)}
          ${ncaMini(ncaNon,       t('nca_non'),       C.critical)}
          ${ncaMini(ncaNotAssess, t('nca_assessed'),  C.muted)}
        </div>
        <div style="text-align:center;margin-bottom:14px">
          <div style="font-size:28px;font-weight:700;color:${C.accent}">${ncaScore}%</div>
          <div style="font-size:10px;color:${C.muted};margin-top:2px">${t('score')}</div>
        </div>
        ${domainBars || '<div style="font-size:11px;color:'+C.muted+';text-align:center;padding:8px">No domain data yet</div>'}
      </div>
    </div>

    <!-- ROW 3: Pillars -->
    <div class="grc-card">
      <div class="grc-card-title">${t('sec_pillars')}</div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
        ${PILLARS_DEF.map(p => {
            const cnt = bp[p.key] || 0;
            const lbl = lang === 'ar' ? p.ar : p.en;
            return `<div style="background:${p.colour}10;border:.5px solid ${p.colour}40;border-radius:10px;padding:14px;text-align:center;border-top:3px solid ${p.colour}">
              <div style="font-size:24px;font-weight:700;color:${p.colour};line-height:1">${cnt}</div>
              <div style="font-size:10px;color:${C.muted};margin-top:5px;line-height:1.4">${lbl}</div>
              <div style="font-size:9px;color:${C.muted};opacity:.7;margin-top:2px">${t('controls_mapped')}</div>
            </div>`;
        }).join('')}
      </div>
    </div>

    <!-- ROW 4: NCA ECC Technology Map -->
    <div class="grc-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
        <div class="grc-card-title" style="margin:0">${t('sec_nca_map')}</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">${domainFilters}</div>
      </div>
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px;min-width:650px">
          <thead><tr style="background:#f8fafc">
            <th style="padding:8px 10px;text-align:${flip};font-size:10px;color:${C.muted};font-weight:600;border-bottom:1px solid ${C.border};white-space:nowrap;width:16%">${t('col_domain')}</th>
            <th style="padding:8px 10px;text-align:center;font-size:10px;color:${C.muted};font-weight:600;border-bottom:1px solid ${C.border};width:7%">${t('col_ctrl')}</th>
            <th style="padding:8px 10px;text-align:${flip};font-size:10px;color:${C.muted};font-weight:600;border-bottom:1px solid ${C.border};width:30%">${t('col_name')}</th>
            <th style="padding:8px 10px;text-align:${flip};font-size:10px;color:${C.muted};font-weight:600;border-bottom:1px solid ${C.border};width:22%">${t('col_tech')}</th>
            <th style="padding:8px 10px;text-align:${flip};font-size:10px;color:${C.muted};font-weight:600;border-bottom:1px solid ${C.border};width:25%">${t('col_vendors')}</th>
          </tr></thead>
          <tbody>${ncaRows}</tbody>
        </table>
      </div>
    </div>

    <!-- ROW 5: Recent assets -->
    ${recent.length ? `
    <div class="grc-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div class="grc-card-title" style="margin:0">${t('sec_recent')}</div>
        <a href="/app/grc-asset-inventory" style="font-size:11px;color:${C.accent};text-decoration:none">${t('btn_all')} →</a>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px">
        ${recentCards}
      </div>
    </div>` : ''}

  </div>
</div>
<style>
.grc-card{background:${C.card};border:.5px solid ${C.border};border-radius:12px;padding:14px}
.grc-card-title{font-size:13px;font-weight:600;margin-bottom:12px;color:${C.text}}
</style>`;

        $(page.body).html(html);

        // Buttons
        $('#ad-lang').on('click', () => { lang = lang === 'en' ? 'ar' : 'en'; render(); drawCharts(); });
        $('#ad-refresh').on('click', () => {
            $(page.body).html(`<div style="padding:60px;text-align:center;color:${C.muted}">${t('loading')}</div>`);
            fetchAll(() => { render(); drawCharts(); });
        });

        // Domain filter
        window.__grcFilterDomain = key => { activeDomain = key; render(); drawCharts(); };

        drawCharts();
    }

    function kpi(val, label, colour) {
        return `<div style="background:${C.card};border:.5px solid ${C.border};border-radius:10px;padding:12px 14px;border-top:3px solid ${colour}">
          <div style="font-size:26px;font-weight:700;color:${colour};line-height:1">${val}</div>
          <div style="font-size:10px;color:${C.muted};text-transform:uppercase;letter-spacing:.05em;margin-top:4px">${label}</div>
        </div>`;
    }
    function ncaMini(val, label, colour) {
        return `<div style="background:#f8fafc;border-radius:8px;padding:10px;text-align:center">
          <div style="font-size:20px;font-weight:700;color:${colour}">${val}</div>
          <div style="font-size:9px;color:${C.muted};margin-top:2px;line-height:1.3">${label}</div>
        </div>`;
    }

    // ── Charts ─────────────────────────────────────────────────────────
    function drawCharts() {
        if (!window.Chart) return;
        if (typeChart) { try { typeChart.destroy(); } catch(e){} }
        if (critChart) { try { critChart.destroy(); } catch(e){} }

        const d = DATA || {};
        const byType = d.by_type || Object.entries({
            'Software':3,'Network Device':2,'Server':3,'Laptop':2,'Desktop':2,'Media / Portable Device':2,'Cloud Service':1
        }).map(([k,v]) => ({asset_type:k,count:v}));

        const typeLabels = byType.map(x => {
            const tm = TYPE_META[x.asset_type] || {};
            return lang === 'ar' ? (tm.ar || x.asset_type) : x.asset_type;
        });
        const typeVals = byType.map(x => x.count || 0);
        const typeCols = byType.map(x => (TYPE_META[x.asset_type] || {colour: C.accent}).colour);

        const typeEl = document.getElementById('ad-type');
        if (typeEl) {
            typeChart = new Chart(typeEl, {
                type: 'doughnut',
                data: { labels: typeLabels, datasets: [{ data: typeVals, backgroundColor: typeCols, borderWidth: 2, hoverOffset: 6 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '56%', plugins: { legend: { display: false } } }
            });
            document.getElementById('ad-type-leg').innerHTML = typeLabels.map((l, i) =>
                `<span style="display:flex;align-items:center;gap:3px;color:${C.muted}">
                  <span style="width:9px;height:9px;border-radius:50%;background:${typeCols[i]};flex-shrink:0"></span>${l} (${typeVals[i]})</span>`
            ).join('');
        }

        const byCrit = d.by_criticality || [
            {asset_criticality:'Critical',count:4},{asset_criticality:'High',count:5},
            {asset_criticality:'Medium',count:4},{asset_criticality:'Low',count:2}
        ];
        const critOrder = ['Critical','High','Medium','Low','Very Low'];
        const sortedCrit = [...byCrit].sort((a,b) => critOrder.indexOf(a.asset_criticality) - critOrder.indexOf(b.asset_criticality));
        const critLabels = sortedCrit.map(x => x.asset_criticality);
        const critVals   = sortedCrit.map(x => x.count || 0);
        const critCols   = sortedCrit.map(x => CRIT_META[x.asset_criticality] || C.muted);

        const critEl = document.getElementById('ad-crit');
        if (critEl) {
            critChart = new Chart(critEl, {
                type: 'bar',
                data: { labels: critLabels, datasets: [{ data: critVals, backgroundColor: critCols, borderRadius: 6, borderSkipped: false }] },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font:{size:10}, color: '#64748B' }, grid: { display: false } },
                        y: { ticks: { font:{size:10}, color: '#64748B', precision: 0 }, beginAtZero: true, grid: { color: 'rgba(0,0,0,.04)' } }
                    }
                }
            });
            document.getElementById('ad-crit-leg').innerHTML = critLabels.map((l, i) =>
                `<span style="display:flex;align-items:center;gap:3px;color:${C.muted}">
                  <span style="width:9px;height:9px;border-radius:2px;background:${critCols[i]};flex-shrink:0"></span>${l} (${critVals[i]})</span>`
            ).join('');
        }
    }

    // ── Bootstrap ──────────────────────────────────────────────────────
    $(page.body).html(`<div style="padding:60px;text-align:center;color:#64748b;font-family:sans-serif">
        <div style="font-size:14px;margin-bottom:8px">Loading Asset Inventory & NCA ECC Dashboard...</div>
        <div style="font-size:11px;opacity:.6">AlphaX GRC v1.2.0</div>
    </div>`);

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
        fetchAll(() => { render(); drawCharts(); });
    });
};
