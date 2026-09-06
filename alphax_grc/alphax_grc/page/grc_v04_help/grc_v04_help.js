frappe.pages['grc-v04-help'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Grc V04 Help',
        single_column: true
    });
    $(page.body).html(`<div class="grc-page-wrap"><div class="text-muted">Legacy help page for v0.4 users with migration notes.</div></div>`);
};
