// Copyright (c) 2026, Neotec Integrated Solutions
frappe.ui.form.on("GRC Evidence Fetcher", {
	refresh(frm) {
		if (frm.is_new() || !frm.doc.enabled) return;

		frm.add_custom_button(__("Run Now"), () => {
			frappe.dom.freeze(__("Running evidence fetcher..."));
			frappe
				.call({
					method: "alphax_grc.pathway.api.run_fetcher_now",
					args: { fetcher: frm.doc.name },
				})
				.then((r) => {
					frappe.dom.unfreeze();
					if (!r || !r.message) return;
					frappe.show_alert({
						message: __("Result: {0}", [r.message.result || __("Unknown")]),
						indicator: r.message.result === "Pass" ? "green" : "orange",
					});
					frm.reload_doc();
				})
				.catch(() => frappe.dom.unfreeze());
		});

		frm.add_custom_button(__("View Runs"), () => {
			frappe.set_route("List", "GRC Evidence Run", { fetcher: frm.doc.name });
		});
	},
});
