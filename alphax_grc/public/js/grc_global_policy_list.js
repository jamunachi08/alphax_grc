// Copyright (c) 2026, Neotec Integrated Solutions
frappe.listview_settings["GRC Global Policy"] = {
	add_fields: ["is_mandatory", "is_active", "category", "source"],

	get_indicator(doc) {
		if (!doc.is_active) return [__("Inactive"), "gray", "is_active,=,0"];
		if (doc.is_mandatory) return [__("Baseline"), "blue", "is_mandatory,=,1"];
		return [__("Optional"), "green", "is_mandatory,=,0"];
	},

	onload(listview) {
		listview.page.add_inner_button(__("Adopt for Client"), () => {
			const selected = listview.get_checked_items(true) || [];

			const d = new frappe.ui.Dialog({
				title: __("Adopt Policies for a Client"),
				fields: [
					{
						fieldname: "client",
						fieldtype: "Link",
						options: "GRC Client Profile",
						label: __("Client"),
						reqd: 1,
					},
					{
						fieldname: "scope_html",
						fieldtype: "HTML",
						options: selected.length
							? `<p class="text-muted small">${__("Adopting {0} selected policies.", [
									selected.length,
							  ])}</p>`
							: `<p class="text-muted small">${__(
									"Nothing selected — the whole active library will be adopted."
							  )}</p>`,
					},
					{
						fieldname: "only_mandatory",
						fieldtype: "Check",
						label: __("Baseline (mandatory) policies only"),
						depends_on: `eval:${selected.length === 0}`,
					},
				],
				primary_action_label: __("Adopt"),
				primary_action(values) {
					d.hide();
					frappe.dom.freeze(__("Creating policies..."));
					frappe
						.call({
							method: "alphax_grc.pathway.api.adopt_policies",
							args: {
								client: values.client,
								policies: selected,
								only_mandatory: values.only_mandatory ? 1 : 0,
							},
						})
						.then((r) => {
							frappe.dom.unfreeze();
							if (!r || !r.message) return;
							frappe.msgprint({
								title: __("Policies Adopted"),
								indicator: r.message.failed.length ? "orange" : "green",
								message: r.message.message,
							});
						})
						.catch(() => frappe.dom.unfreeze());
				},
			});
			d.show();
		});
	},
};
