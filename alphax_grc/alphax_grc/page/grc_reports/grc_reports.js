frappe.pages['grc-reports'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Grc Reports',
        single_column: true
    });
    $(page.body).html(`<div class="grc-page-wrap"><div class="text-muted">Reports page lists management, audit, maturity, vendor, and privacy reports.</div></div>`);
};
