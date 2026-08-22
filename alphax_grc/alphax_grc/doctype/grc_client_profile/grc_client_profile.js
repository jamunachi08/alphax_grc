// AlphaX GRC v1.3.0 — Client Profile form controller
// When country or sector changes, suggest the matching framework list.

frappe.ui.form.on('GRC Client Profile', {
    country: function(frm) { suggest_frameworks(frm); },
    sector:  function(frm) { suggest_frameworks(frm); },
});

function suggest_frameworks(frm) {
    if (!frm.doc.country || !frm.doc.sector) return;
    if (frm.doc.applicable_frameworks &&
        frm.doc.applicable_frameworks.trim().length > 0) {
        // Don't overwrite an existing override silently
        return;
    }
    frappe.call({
        method: 'alphax_grc.alphax_grc.doctype.grc_client_profile.grc_client_profile.get_suggested_frameworks',
        args: { country: frm.doc.country, sector: frm.doc.sector },
        callback: (r) => {
            if (r && r.message && r.message.length) {
                frm.set_value('applicable_frameworks', r.message.join('\n'));
            }
        },
    });
}
