// AlphaX GRC Neo Hub v1.0.0 — Bilingual launch hub, LTR/RTL
frappe.pages['grc-neo-hub'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, title: 'GRC Neo Hub', single_column: true });

    const lang = (frappe.boot.lang === 'ar') ? 'ar' : 'en';

    const MODULES = [
        { key:'risk', icon:'⚡', en:'Risk Management', ar:'إدارة المخاطر', en_desc:'Risk register, KRIs, heat maps, acceptance', ar_desc:'سجل المخاطر، المؤشرات، الخرائط الحرارية', link:'/app/grc-risk-register', color:'#DC2626' },
        { key:'audit', icon:'🔍', en:'Audit & Findings', ar:'التدقيق والملاحظات', en_desc:'Audit plans, workpapers, findings, remediation', ar_desc:'خطط التدقيق، الأوراق، الملاحظات', link:'/app/grc-audit-finding', color:'#2563EB' },
        { key:'compliance', icon:'✅', en:'Compliance', ar:'الامتثال', en_desc:'Frameworks, controls, assessments, maturity', ar_desc:'الأطر والضوابط والتقييمات', link:'/app/grc-regulatory-obligation', color:'#10B981' },
        { key:'policy', icon:'📋', en:'Policy Management', ar:'إدارة السياسات', en_desc:'Policy lifecycle, approval, acknowledgement', ar_desc:'دورة حياة السياسة والاعتماد', link:'/app/grc-policy', color:'#D97706' },
        { key:'vendor', icon:'🏢', en:'Vendor Risk', ar:'مخاطر الموردين', en_desc:'Vendor assessments, questionnaires, Aramco TP', ar_desc:'تقييمات الموردين وأرامكو', link:'/app/grc-vendor', color:'#7C3AED' },
        { key:'privacy', icon:'🔒', en:'Privacy & PDPL', ar:'الخصوصية ونظام PDPL', en_desc:'Data subjects, processing activities, DSRs', ar_desc:'موضوعات البيانات وأنشطة المعالجة', link:'/app/grc-privacy-processing-activity', color:'#0EA5E4' },
        { key:'incident', icon:'🚨', en:'Incident Management', ar:'إدارة الحوادث', en_desc:'Incidents, SLA tracking, notifications', ar_desc:'الحوادث وتتبع SLA والإشعارات', link:'/app/grc-incident', color:'#EF4444' },
        { key:'problem', icon:'🔧', en:'Problem Management', ar:'إدارة المشاكل', en_desc:'RCA, known errors, permanent fixes', ar_desc:'تحليل السبب الجذري والحلول الدائمة', link:'/app/grc-problem-record', color:'#F59E0B' },
        { key:'dr', icon:'🛡️', en:'DR Plans', ar:'خطط الاسترداد', en_desc:'DR plans, RTO/RPO, test schedules', ar_desc:'خطط الاسترداد، RTO/RPO، جدولة الاختبار', link:'/app/grc-dr-plan', color:'#6366F1' },
        { key:'action', icon:'📌', en:'Action Plans', ar:'خطط العمل', en_desc:'Risk response tasks, progress, completion', ar_desc:'مهام الاستجابة للمخاطر والتقدم', link:'/app/grc-action-plan', color:'#8B5CF6' },
        { key:'itgc', icon:'💻', en:'IT General Controls (ITGC)', ar:'ضوابط تقنية المعلومات (ITGC)', en_desc:'145 controls — GLBA, DLP, Patch, Vendor, Network, InfoSec, Incident', ar_desc:'145 ضابطاً — GLBA، DLP، التصحيح، الموردون، الشبكات', link:'/app/grc-itgc-program', color:'#059669' },
        { key:'asset', icon:'📦', en:'Asset Inventory (ISO 27001)', ar:'جرد الأصول (ISO 27001)', en_desc:'6 asset types, CIA rating, NCA ECC mapping, PDPL flag', ar_desc:'6 أنواع أصول، تصنيف CIA، ربط NCA ECC وPDPL', link:'/app/grc-asset-dashboard', color:'#0891B2' },
        { key:'dashboard', icon:'📊', en:'Command Centre', ar:'مركز القيادة', en_desc:'Full GRC dashboard with heatmap & charts', ar_desc:'لوحة القيادة مع الخرائط والمخططات', link:'/app/grc-command-center', color:'#0B132B' },
        { key:'board', icon:'📈', en:'Board Reports', ar:'تقارير مجلس الإدارة', en_desc:'Executive KPIs for board-level governance', ar_desc:'مؤشرات الأداء التنفيذية لمجلس الإدارة', link:'/app/grc-board-report', color:'#1D4ED8' },
        { key:'theme', icon:'🎨', en:'Theme Settings', ar:'إعدادات المظهر', en_desc:'5 presets + 38 custom colour fields', ar_desc:'5 تصميمات مسبقة + 38 حقل لوني', link:'/app/grc-theme-settings', color:'#EC4899' },
    ];

    const dir = lang === 'ar' ? 'rtl' : 'ltr';
    const title_text = lang === 'ar' ? 'مركز AlphaX GRC' : 'AlphaX GRC Neo Hub';
    const sub_text = lang === 'ar' ? 'منصة الحوكمة والمخاطر والامتثال المتكاملة | v1.0.0' : 'Integrated Governance, Risk & Compliance Platform | v1.0.0';

    const cards = MODULES.map(m => {
        const name = lang === 'ar' ? m.ar : m.en;
        const desc = lang === 'ar' ? m.ar_desc : m.en_desc;
        return `<a href="${m.link}" style="text-decoration:none">
          <div style="background:#fff;border:.5px solid #e2e8f0;border-radius:12px;padding:16px;cursor:pointer;transition:box-shadow .2s;border-top:3px solid ${m.color}"
               onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,.08)'" onmouseout="this.style.boxShadow='none'">
            <div style="font-size:22px;margin-bottom:8px">${m.icon}</div>
            <div style="font-size:13px;font-weight:600;color:#1E293B;margin-bottom:4px">${name}</div>
            <div style="font-size:11px;color:#64748B;line-height:1.5">${desc}</div>
          </div>
        </a>`;
    }).join('');

    const html = `
<div style="direction:${dir};font-family:'Segoe UI',Tahoma,system-ui,sans-serif;background:linear-gradient(135deg,#0B132B 0%,#1C2541 50%,#3A506B 100%);min-height:100vh;padding:0">
  <div style="text-align:center;padding:40px 24px 24px;color:#fff">
    <div style="font-size:28px;font-weight:800;letter-spacing:.02em;margin-bottom:8px">🛡️ ${title_text}</div>
    <div style="font-size:13px;opacity:.7">${sub_text}</div>
    <div style="display:flex;gap:8px;justify-content:center;margin-top:16px;flex-wrap:wrap">
      <span style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:11px;color:#fff">NCA ECC 2:2024</span>
      <span style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:11px;color:#fff">SAMA CSF</span>
      <span style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:11px;color:#fff">PDPL</span>
      <span style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:11px;color:#fff">ISO 27001:2022</span>
      <span style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:4px 12px;border-radius:20px;font-size:11px;color:#fff">Aramco TP</span>
    </div>
  </div>
  <div style="background:#F8FAFC;border-radius:20px 20px 0 0;padding:24px;min-height:70vh">
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px">
      ${cards}
    </div>
    <div style="margin-top:24px;text-align:center;color:#94A3B8;font-size:11px">
      AlphaX GRC v1.0.0 | IRSAA Business Solutions | support@irsaa.com
    </div>
  </div>
</div>`;

    $(page.body).html(html);
};
