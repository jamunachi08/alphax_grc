frappe.pages['grc-help'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Grc Help',
        single_column: true
    });
    $(page.body).html(`<div class="grc-page-wrap"><div class="text-muted">Help page links user, process, technical manuals, and policy samples.</div></div>`);
};
