// AlphaX GRC Command Centre v1.0.0 — Full multilingual (EN/AR) with RTL, Chart.js, live data
frappe.pages['grc-command-center'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, title: 'GRC Command Centre', single_column: true });

    const T = {
        en: { title:'GRC Command Centre', subtitle:'AlphaX GRC v1.0.0 | Saudi-First GRC Platform',
              critical_risks:'Critical Risks', open_findings:'Open Findings',
              compliance:'Compliance Score', overdue:'Overdue Actions',
              risk_heatmap:'Risk Heatmap — 5×5 Matrix', top_risks:'Top Open Risks',
              by_category:'Risks by Category', by_severity:'Findings by Severity',
              kri_status:'KRI Status', fw_progress:'Framework Compliance',
              new_in_v1:'What\'s New in v1.0', loading:'Loading...', refresh:'Refresh',
              lang_btn:'العربية', score_gte:'Score ≥ 15', not_closed:'Not closed',
              avg_across:'Avg across frameworks', past_due:'Past due date',
              risk:'Risk', score:'Score', rating:'Rating',
              likelihood:'Likelihood', catastrophic:'Catastrophic', major:'Major',
              moderate:'Moderate', minor:'Minor', negligible:'Negligible',
              very_high:'Very High', high:'High', medium:'Medium', low:'Low', very_low:'Very Low',
              critical:'Critical', ok:'OK', alert:'Alert', warn:'Warn', breach:'Breach' },
        ar: { title:'مركز القيادة GRC', subtitle:'AlphaX GRC v1.0.0 | منصة الحوكمة والمخاطر والامتثال',
              critical_risks:'المخاطر الحرجة', open_findings:'الملاحظات المفتوحة',
              compliance:'درجة الامتثال', overdue:'الإجراءات المتأخرة',
              risk_heatmap:'خريطة المخاطر الحرارية — 5×5', top_risks:'أعلى المخاطر المفتوحة',
              by_category:'المخاطر حسب الفئة', by_severity:'الملاحظات حسب الشدة',
              kri_status:'مؤشرات المخاطر', fw_progress:'امتثال الأطر',
              new_in_v1:'الجديد في v1.0', loading:'جارٍ التحميل...', refresh:'تحديث',
              lang_btn:'English', score_gte:'الدرجة ≥ 15', not_closed:'غير مغلقة',
              avg_across:'متوسط الأطر', past_due:'تجاوز الموعد',
              risk:'المخاطرة', score:'الدرجة', rating:'التقييم',
              likelihood:'الاحتمالية', catastrophic:'كارثية', major:'كبيرة',
              moderate:'متوسطة', minor:'طفيفة', negligible:'هامشية',
              very_high:'عالية جداً', high:'عالية', medium:'متوسطة', low:'منخفضة', very_low:'منخفضة جداً',
              critical:'حرج', ok:'موافق', alert:'تنبيه', warn:'تحذير', breach:'اختراق' }
    };
    let lang = (frappe.boot.lang === 'ar') ? 'ar' : 'en';
    const t = k => T[lang][k] || T.en[k] || k;

    let THEME = { primary:'#0B132B', accent:'#2563EB', bg:'#F8FAFC', card:'#FFFFFF',
        text:'#1E293B', muted:'#64748B', critical:'#DC2626', high:'#D97706',
        medium:'#F59E0B', low:'#16A34A', ok:'#10B981', info:'#0EA5E4',
        h1:'#3B82F6', h2:'#0EA5E4', h3:'#10B981', h4:'#F59E0B', h5:'#EF4444',
        hml:'#DCFCE7', hmm:'#FEF3C7', hmh:'#FEE2E2', hmc:'#991B1B' };

    let DATA = null;
    let catChart = null, sevChart = null;

    function loadScript(src, cb) {
        if (window.Chart) { cb(); return; }
        const s = document.createElement('script'); s.src = src; s.onload = cb;
        document.head.appendChild(s);
    }

    function fetchTheme(cb) {
        frappe.call({
            method: 'alphax_grc.alphax_grc.doctype.grc_theme_settings.grc_theme_settings.get_theme',
            callback(r) {
                if (r && r.message) {
                    const m = r.message;
                    THEME.primary = m['--grc-primary'] || THEME.primary;
                    THEME.accent  = m['--grc-accent']  || THEME.accent;
                    THEME.bg      = m['--grc-bg']       || THEME.bg;
                    THEME.card    = m['--grc-card-bg']  || THEME.card;
                    THEME.text    = m['--grc-text']     || THEME.text;
                    THEME.muted   = m['--grc-muted']    || THEME.muted;
                    THEME.critical= m['--grc-critical'] || THEME.critical;
                    THEME.high    = m['--grc-high']     || THEME.high;
                    THEME.medium  = m['--grc-medium']   || THEME.medium;
                    THEME.low     = m['--grc-low']      || THEME.low;
                    THEME.ok      = m['--grc-ok']       || THEME.ok;
                    THEME.info    = m['--grc-info']     || THEME.info;
                    THEME.h1 = m['--grc-chart-1'] || THEME.h1;
                    THEME.h2 = m['--grc-chart-2'] || THEME.h2;
                    THEME.h3 = m['--grc-chart-3'] || THEME.h3;
                    THEME.h4 = m['--grc-chart-4'] || THEME.h4;
                    THEME.h5 = m['--grc-chart-5'] || THEME.h5;
                    THEME.hml = m['--grc-heatmap-low']  || THEME.hml;
                    THEME.hmm = m['--grc-heatmap-med']  || THEME.hmm;
                    THEME.hmh = m['--grc-heatmap-high'] || THEME.hmh;
                    THEME.hmc = m['--grc-heatmap-crit'] || THEME.hmc;
                }
                cb();
            }, error: cb
        });
    }

    function fetchData(cb) {
        frappe.call({
            method: 'alphax_grc.api.get_command_center_data',
            callback(r) { DATA = (r && r.message) || null; cb(); },
            error() { DATA = null; cb(); }
        });
    }

    function hmColour(s) {
        if (s >= 15) return THEME.hmc;
        if (s >= 10) return THEME.hmh;
        if (s >= 5)  return THEME.hmm;
        return THEME.hml;
    }
    function textOn(bg) {
        try {
            const h = bg.replace('#','');
            const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16);
            return (r*299+g*587+b*114)/1000 > 128 ? '#1E293B' : '#FFFFFF';
        } catch(e) { return '#1E293B'; }
    }
    function rColour(r) {
        return {Critical:THEME.critical,High:THEME.high,Medium:THEME.medium,Low:THEME.low}[r]||THEME.muted;
    }
    function kriColour(s) {
        return {Breach:THEME.critical,Warn:THEME.high,Alert:THEME.medium,OK:THEME.ok}[s]||THEME.muted;
    }

    const HM_SCORES = [[2,4,6,8,10],[3,6,9,12,15],[4,8,12,16,20],[5,10,15,20,25],[6,12,18,24,30]];
    const HM_COUNTS_DEFAULT = [[0,1,0,0,0],[0,2,0,1,0],[1,0,2,0,1],[0,1,0,3,0],[1,0,0,0,4]];
    const DEFAULT_RISKS = [
        {title:'Regulatory non-compliance',title_ar:'عدم الامتثال التنظيمي',score:20,rating:'Critical'},
        {title:'Third-party dependency',title_ar:'الاعتماد على طرف ثالث',score:12,rating:'High'},
        {title:'Contract dispute',title_ar:'نزاع تعاقدي',score:12,rating:'High'},
        {title:'System outage risk',title_ar:'خطر انقطاع النظام',score:10,rating:'High'},
        {title:'Data privacy breach',title_ar:'اختراق خصوصية البيانات',score:6,rating:'Medium'},
        {title:'Inventory stockout',title_ar:'نفاد المخزون',score:2,rating:'Low'}
    ];
    const DEFAULT_KRIS = [
        {name:'Phishing click rate',name_ar:'معدل النقر على التصيد',current:'8%',threshold:'5%',status:'Breach'},
        {name:'Patch compliance',name_ar:'امتثال التصحيح',current:'88%',threshold:'90%',status:'Warn'},
        {name:'Access review completion',name_ar:'إتمام مراجعة الوصول',current:'95%',threshold:'90%',status:'OK'},
        {name:'Vendor assessment overdue',name_ar:'تقييم المورد المتأخر',current:'3',threshold:'5',status:'Alert'},
        {name:'Incident SLA breaches',name_ar:'اختراقات SLA للحوادث',current:'1',threshold:'3',status:'OK'}
    ];
    const DEFAULT_FW = [
        {name:'NCA ECC',score:72},{name:'SAMA CSF',score:58},{name:'PDPL',score:65},
        {name:'ISO 27001',score:81},{name:'Aramco TP',score:44}
    ];
    const DEFAULT_CAT = [
        {category:'Strategic',count:8},{category:'Operational',count:3},
        {'Supply Chain':7,category:'Supply Chain',count:7},{category:'Financial',count:3},
        {category:'Legal',count:4},{category:'Technology',count:6}
    ];
    const DEFAULT_SEV = [
        {severity:'Critical',count:2},{severity:'High',count:3},
        {severity:'Medium',count:4},{severity:'Low',count:2}
    ];

    function newItems() {
        const items = lang === 'ar' ? [
            ['سجل التدقيق العام لتقنية المعلومات (GLBA، DLP، التصحيح، المورد، الشبكة)', 'ITGC', '#2563EB'],
            ['تعيين تقنيات NCA ECC-2:2024', 'NCA MAP', '#10B981'],
            ['قائمة وثائق ISO 27001:2022 الإلزامية (93 وثيقة)', 'ISO 27001', '#D97706'],
            ['جرد الأصول مع تصنيف المخاطر', 'ASSETS', '#7C3AED'],
            ['دعم ثنائي اللغة (EN/AR) مع تخطيط RTL', 'i18n RTL', '#EF4444'],
            ['لوحة ألوان عالمية وفردية قابلة للتخصيص', 'THEME', '#0EA5E4'],
            ['إصلاح صفحات Frappe — كانت جميعها 404', 'BUG FIX', '#DC2626']
        ] : [
            ['IT General Controls Audit Program (GLBA, DLP, Patch Mgmt, Vendor, Network, InfoSec, Incident — 95+ controls)', 'ITGC', '#2563EB'],
            ['NCA ECC-2:2024 Cybersecurity Technology Mapping (15 control domains)', 'NCA MAP', '#10B981'],
            ['ISO 27001:2022 Mandatory Document Checklist (93 document requirements)', 'ISO 27001', '#D97706'],
            ['Asset Inventory DocType with CIA classification & risk linkage', 'ASSETS', '#7C3AED'],
            ['Full bilingual support EN/AR with RTL layout switching', 'i18n RTL', '#EF4444'],
            ['Global & per-component colour theming — 5 presets + custom', 'THEME', '#0EA5E4'],
            ['Fixed all Frappe page 404 errors — page JSON definitions added', 'BUG FIX', '#DC2626']
        ];
        return items.map(([d,tag,c]) =>
            `<div style="padding:5px 0;border-bottom:.5px solid #f1f5f9;display:flex;align-items:flex-start;gap:8px">
              <span style="background:${c}22;color:${c};padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;white-space:nowrap;flex-shrink:0">${tag}</span>
              <span style="color:${THEME.text};font-size:12px">${d}</span>
            </div>`).join('');
    }

    function render() {
        const dir = lang === 'ar' ? 'rtl' : 'ltr';
        const ta  = lang === 'ar' ? 'right' : 'left';

        const fwColours = [THEME.h1,THEME.h2,THEME.h3,THEME.h4,THEME.h5];
        const d = DATA || {};

        // KPI values
        const kpiCrit = d.critical_risks !== undefined ? d.critical_risks : 0;
        const kpiFind = d.open_findings  !== undefined ? d.open_findings  : 0;
        const kpiComp = d.compliance_score !== undefined ? d.compliance_score+'%' : '—';
        const kpiOver = d.overdue_actions !== undefined ? d.overdue_actions : 0;

        // Heatmap
        const hmCounts = (d.heatmap_counts && d.heatmap_counts.length) ? d.heatmap_counts : [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]];
        const rowLabels_en = [t('very_high'),t('high'),t('medium'),t('low'),t('very_low')];
        const colLabels_en = [t('negligible'),t('minor'),t('moderate'),t('major'),t('catastrophic')];

        let hmHtml = `<div style="display:grid;grid-template-columns:52px repeat(5,1fr);gap:3px;font-size:9px">
          <div></div>`;
        colLabels_en.forEach(c => { hmHtml += `<div style="text-align:center;color:${THEME.muted};padding-bottom:2px">${c.slice(0,4)}</div>`; });
        HM_SCORES.forEach((row,ri) => {
            hmHtml += `<div style="display:flex;align-items:center;justify-content:flex-end;padding-right:4px;color:${THEME.muted}">${rowLabels_en[ri].slice(0,6)}</div>`;
            row.forEach((s,ci) => {
                const bg = hmColour(s); const tc = textOn(bg);
                const cnt = (hmCounts[ri] && hmCounts[ri][ci]) || '';
                hmHtml += `<div style="background:${bg};color:${tc};border-radius:4px;height:30px;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:11px">${cnt}</div>`;
            });
        });
        hmHtml += '</div>';

        // Risk table
        const risks = (d.top_risks && d.top_risks.length) ? d.top_risks : DEFAULT_RISKS;
        const riskRows = risks.slice(0,6).map(r => {
            const title = (lang==='ar' && r.title_ar) ? r.title_ar : (r.risk_description||r.title||r.name||'');
            const s = r.risk_score||r.score||'—'; const rt = r.risk_rating||r.rating||'—';
            const c = rColour(rt);
            return `<tr>
              <td style="padding:6px 8px;border-bottom:.5px solid #f1f5f9;text-align:${ta};max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${title}</td>
              <td style="padding:6px 8px;border-bottom:.5px solid #f1f5f9;text-align:center;font-weight:600">${s}</td>
              <td style="padding:6px 8px;border-bottom:.5px solid #f1f5f9;text-align:center">
                <span style="background:${c}22;color:${c};padding:2px 8px;border-radius:999px;font-size:10px;font-weight:600">${rt}</span>
              </td></tr>`;
        }).join('');

        // KRI list
        const kris = (d.kri_status && d.kri_status.length) ? d.kri_status : DEFAULT_KRIS;
        const kriLabels_ar = {Breach:'اختراق',Warn:'تحذير',Alert:'تنبيه',OK:'موافق'};
        const kriHtml = kris.map(k => {
            const name = (lang==='ar' && k.name_ar) ? k.name_ar : (k.indicator_name||k.kri_name||k.name||'');
            const c = kriColour(k.status); const sl = lang==='ar' ? (kriLabels_ar[k.status]||k.status) : k.status;
            return `<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:.5px solid #f1f5f9">
              <div style="flex:1;font-size:12px;color:${THEME.text}">${name}</div>
              <div style="font-size:10px;color:${THEME.muted};margin:0 8px">${k.current_value||k.current||''} / ${k.threshold_value||k.threshold||''}</div>
              <span style="background:${c}22;color:${c};padding:2px 7px;border-radius:4px;font-size:10px;font-weight:600">${sl}</span>
            </div>`;
        }).join('');

        // Framework progress
        const fws = (d.compliance_by_framework && d.compliance_by_framework.length) ? d.compliance_by_framework : DEFAULT_FW;
        const fwHtml = fws.slice(0,6).map((f,i) => {
            const s = f.compliance_score||f.score||0; const c = fwColours[i%5];
            return `<div style="margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
                <span>${f.framework_name||f.name||''}</span><span style="color:${c};font-weight:600">${s}%</span>
              </div>
              <div style="height:6px;border-radius:999px;background:#f1f5f9;overflow:hidden">
                <div style="height:100%;width:${s}%;background:${c};border-radius:999px"></div>
              </div></div>`;
        }).join('');

        const html = `
<div id="grc-cc" style="direction:${dir};font-family:'Segoe UI',Tahoma,system-ui,sans-serif;background:${THEME.bg};min-height:100vh">
  <!-- HEADER -->
  <div style="background:${THEME.primary};color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid ${THEME.accent}">
    <div>
      <div style="font-size:19px;font-weight:700">${t('title')}</div>
      <div style="font-size:11px;opacity:.6;margin-top:2px">${t('subtitle')}</div>
    </div>
    <div style="display:flex;gap:8px">
      <button id="cc-lang" style="padding:5px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font-size:12px">${t('lang_btn')}</button>
      <button id="cc-refresh" style="padding:5px 12px;border-radius:6px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font-size:12px">${t('refresh')}</button>
    </div>
  </div>

  <div style="padding:18px;display:flex;flex-direction:column;gap:14px">

    <!-- KPI ROW -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
      ${kpi(kpiCrit,t('critical_risks'),t('score_gte'),THEME.critical)}
      ${kpi(kpiFind,t('open_findings'),t('not_closed'),THEME.high)}
      ${kpi(kpiComp,t('compliance'),t('avg_across'),THEME.accent)}
      ${kpi(kpiOver,t('overdue'),t('past_due'),THEME.ok)}
    </div>

    <!-- ROW 2: Heatmap + Top Risks -->
    <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:14px">
      <div class="gc">${card_title(t('risk_heatmap'))}${hmHtml}</div>
      <div class="gc">${card_title(t('top_risks'))}
        <table style="width:100%;border-collapse:collapse;font-size:12px">
          <thead><tr>
            <th style="text-align:${ta};padding:6px 8px;border-bottom:1px solid #e2e8f0;color:${THEME.muted};font-size:10px;text-transform:uppercase;font-weight:600">${t('risk')}</th>
            <th style="text-align:center;padding:6px 8px;border-bottom:1px solid #e2e8f0;color:${THEME.muted};font-size:10px;text-transform:uppercase;font-weight:600">${t('score')}</th>
            <th style="text-align:center;padding:6px 8px;border-bottom:1px solid #e2e8f0;color:${THEME.muted};font-size:10px;text-transform:uppercase;font-weight:600">${t('rating')}</th>
          </tr></thead>
          <tbody>${riskRows}</tbody>
        </table>
      </div>
    </div>

    <!-- ROW 3: Charts + KRI -->
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px">
      <div class="gc">${card_title(t('by_category'))}
        <div style="position:relative;height:180px;background:#ffffff;border-radius:6px"><canvas id="cc-cat"></canvas></div>
        <div id="cc-cat-leg" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;font-size:10px"></div>
      </div>
      <div class="gc">${card_title(t('by_severity'))}
        <div style="position:relative;height:180px;background:#ffffff;border-radius:6px"><canvas id="cc-sev"></canvas></div>
        <div id="cc-sev-leg" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;font-size:10px"></div>
      </div>
      <div class="gc">${card_title(t('kri_status'))}<div id="cc-kri">${kriHtml}</div></div>
    </div>

    <!-- ROW 4: Frameworks + What's New -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
      <div class="gc">${card_title(t('fw_progress'))}${fwHtml}</div>
      <div class="gc">${card_title(t('new_in_v1'))}${newItems()}</div>
    </div>

  </div>
</div>
<style>
.gc{background:${THEME.card};border:.5px solid #e2e8f0;border-radius:12px;padding:14px}
.gct{font-size:13px;font-weight:600;margin-bottom:12px;color:${THEME.text}}
</style>`;

        $(page.body).html(html);
        $('#cc-lang').on('click', () => { lang = (lang === 'en') ? 'ar' : 'en'; render(); drawCharts(); });
        $('#cc-refresh').on('click', () => { fetchData(() => { render(); drawCharts(); }); });
        drawCharts();
    }

    function kpi(val, label, sub, colour) {
        return `<div style="background:${THEME.card};border:.5px solid #e2e8f0;border-radius:10px;padding:14px 16px">
          <div style="font-size:28px;font-weight:700;color:${colour};line-height:1">${val}</div>
          <div style="font-size:10px;color:${THEME.muted};text-transform:uppercase;letter-spacing:.06em;margin-top:4px">${label}</div>
          <div style="font-size:10px;color:${THEME.muted};margin-top:2px">${sub}</div>
        </div>`;
    }
    function card_title(t) { return `<div class="gct">${t}</div>`; }

    function drawCharts() {
        if (!window.Chart) return;
        if (catChart) { try{catChart.destroy();}catch(e){} }
        if (sevChart) { try{sevChart.destroy();}catch(e){} }

        const d = DATA || {};
        const catData = (d.risks_by_category && d.risks_by_category.length) ? d.risks_by_category : DEFAULT_CAT;
        const catAr = {Strategic:'استراتيجية',Operational:'تشغيلية','Supply Chain':'سلسلة التوريد',Financial:'مالية',Legal:'قانونية',Technology:'تقنية'};
        const catLabels = catData.map(c => (lang==='ar'&&catAr[c.category])?catAr[c.category]:c.category);
        const catVals = catData.map(c => c.count||c.total||0);
        const chartCols = [THEME.h1,THEME.h2,THEME.h3,THEME.h4,THEME.h5,THEME.accent];

        const catEl = document.getElementById('cc-cat');
        if (catEl) {
            catChart = new Chart(catEl, {
                type:'bar', data:{ labels:catLabels, datasets:[{ data:catVals, backgroundColor:chartCols.slice(0,catLabels.length), borderRadius:4 }]},
                options:{ responsive:true, maintainAspectRatio:false,
                    plugins:{legend:{display:false},
                             beforeDraw:(chart)=>{const ctx=chart.ctx;ctx.save();ctx.globalCompositeOperation='destination-over';ctx.fillStyle='#ffffff';ctx.fillRect(0,0,chart.width,chart.height);ctx.restore();}},
                    scales:{x:{ticks:{font:{size:9},color:'#64748B',maxRotation:45,autoSkip:false},grid:{display:false},border:{color:'#e2e8f0'}},
                            y:{ticks:{font:{size:9},color:'#64748B',precision:0},grid:{color:'rgba(0,0,0,.05)'},border:{color:'#e2e8f0'},beginAtZero:true}}}
            });
            document.getElementById('cc-cat-leg').innerHTML = catLabels.map((l,i)=>
                `<span style="display:flex;align-items:center;gap:3px"><span style="width:9px;height:9px;border-radius:2px;background:${chartCols[i]}"></span><span style="color:${THEME.muted}">${l}</span></span>`
            ).join('');
        }

        const sevData = (d.findings_by_severity && d.findings_by_severity.length) ? d.findings_by_severity : DEFAULT_SEV;
        const sevAr = {Critical:'حرج',High:'عالي',Medium:'متوسط',Low:'منخفض'};
        const sevLabels = sevData.map(s => (lang==='ar'&&sevAr[s.severity])?sevAr[s.severity]:s.severity);
        const sevVals = sevData.map(s => s.count||0);
        const sevCols = sevData.map(s => ({Critical:THEME.critical,High:THEME.high,Medium:THEME.medium,Low:THEME.low}[s.severity]||THEME.muted));

        const sevEl = document.getElementById('cc-sev');
        if (sevEl) {
            sevChart = new Chart(sevEl, {
                type:'doughnut', data:{labels:sevLabels,datasets:[{data:sevVals,backgroundColor:sevCols,borderWidth:2}]},
                options:{responsive:true,maintainAspectRatio:false,cutout:'62%',
                plugins:{legend:{display:false},
                         beforeDraw:(chart)=>{const ctx=chart.ctx;ctx.save();ctx.globalCompositeOperation='destination-over';ctx.fillStyle='#ffffff';ctx.fillRect(0,0,chart.width,chart.height);ctx.restore();}}}
            });
            document.getElementById('cc-sev-leg').innerHTML = sevLabels.map((l,i)=>
                `<span style="display:flex;align-items:center;gap:3px"><span style="width:9px;height:9px;border-radius:2px;background:${sevCols[i]}"></span><span style="color:${THEME.muted}">${l} (${sevVals[i]})</span></span>`
            ).join('');
        }
    }

    // ── INIT ───────────────────────────────────────────────────────────
    $(page.body).html('<div style="padding:40px;text-align:center;color:#64748b">Loading AlphaX GRC...</div>');
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js', () => {
        // Register canvas white background plugin (prevents black bg in Frappe)
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
        fetchTheme(() => {
            // Initial render with empty state, then start live polling
            const $indicator = frappe.alphaxGRC.makeIndicator();
            page.page_actions.prepend($indicator);

            const live = frappe.alphaxGRC.live({
                endpoint: 'alphax_grc.api.get_command_center_data',
                getArgs: () => ({}),
                invalidateOnAnyClient: true,
                indicatorEl: $indicator,
                refreshSeconds: 30,
                onData: (payload) => {
                    DATA = payload || null;
                    render();
                    drawCharts();
                },
            });
            live.start();
            // Manual-refresh button hooks into live module
            $('#cc-refresh').off('click').on('click', () => live.refreshNow());
        });
    });
};
