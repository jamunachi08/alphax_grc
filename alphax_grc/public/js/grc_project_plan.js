// Copyright (c) 2026, Neotec Integrated Solutions
frappe.ui.form.on("GRC Project Plan", {
	setup(frm) {
		// Only offer templates that fit the engagement being planned.
		frm.set_query("template", () => {
			if (!frm.doc.engagement || !frm._engagement_type) return { filters: { is_active: 1 } };
			return { filters: { is_active: 1, engagement_type: frm._engagement_type } };
		});
	},

	engagement(frm) {
		frm._engagement_type = null;
		if (!frm.doc.engagement) return;

		frappe
			.call({
				method: "alphax_grc.pathway.api.suggest_templates",
				args: { engagement: frm.doc.engagement, client: frm.doc.client },
			})
			.then((r) => {
				if (!r || !r.message) return;
				const d = r.message;
				frm._engagement_type = d.engagement_type;

				if (!d.matches.length) {
					frm.dashboard.clear_headline();
					if (d.engagement_type) {
						frm.dashboard.set_headline(
							__("No plan template is tagged for a {0}. Any active template can still be picked.", [
								d.engagement_type,
							])
						);
					}
					return;
				}

				// One clean match: fill it in rather than making them hunt.
				if (d.matches.length === 1 && !frm.doc.template) {
					const m = d.matches[0];
					frm.set_value("template", m.name);
					frappe.show_alert({
						message: __("Template set to {0} ({1} tasks, ~{2} working days)", [
							m.template_name, m.task_count, m.indicative_duration_days,
						]),
						indicator: "blue",
					});
					return;
				}

				frm.dashboard.set_headline(
					__("{0} plan templates match a {1}.", [d.matches.length, d.engagement_type])
				);
			});
	},

	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Gantt Chart"), () => {
				frappe.set_route("grc-project-gantt");
				frappe.route_options = { plan: frm.doc.name };
				setTimeout(() => frappe.set_route("grc-project-gantt"), 50);
			}).addClass("btn-primary");
		}

		if (frm.doc.template) {
			frm.add_custom_button(__("Load Template Tasks"), () => {
				const has_tasks = (frm.doc.tasks || []).length > 0;
				const run = (overwrite) =>
					frm
						.call({ doc: frm.doc, method: "load_template", args: { overwrite } })
						.then((r) => {
							frm.refresh_field("tasks");
							frappe.show_alert({
								message: __("{0} tasks loaded", [r.message]),
								indicator: "green",
							});
						});

				if (!has_tasks) return run(0);
				frappe.confirm(
					__("This plan already has {0} tasks. Replace them with the template?", [
						frm.doc.tasks.length,
					]),
					() => run(1)
				);
			});
		}

		if ((frm.doc.tasks || []).some((t) => t.locked)) {
			frm.dashboard.set_headline(
				__("{0} task(s) are locked and keep their dates when the schedule shifts.", [
					frm.doc.tasks.filter((t) => t.locked).length,
				])
			);
		}
	},

	start_date(frm) {
		if (frm.doc.tasks && frm.doc.tasks.length) {
			frappe.show_alert(__("Unlocked tasks will reschedule on save."));
		}
	},
});

frappe.ui.form.on("GRC Plan Template", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(__("Create Project Plan"), () => {
			const d = new frappe.ui.Dialog({
				title: __("Create Plan from {0}", [frm.doc.template_name]),
				fields: [
					{ fieldname: "client", fieldtype: "Link", options: "GRC Client Profile",
					  label: __("Client"), reqd: 1 },
					{ fieldname: "engagement", fieldtype: "Link", options: "GRC Engagement",
					  label: __("Engagement") },
					{ fieldname: "start_date", fieldtype: "Date", label: __("Start Date"),
					  default: frappe.datetime.get_today(), reqd: 1 },
					{ fieldname: "info", fieldtype: "HTML",
					  options: `<p class="text-muted small">${__(
							"{0} tasks, roughly {1} working days on a {2} week.",
							[frm.doc.task_count, frm.doc.indicative_duration_days,
							 frm.doc.default_working_days || "Sun-Thu (KSA)"]
					  )}</p>` },
				],
				primary_action_label: __("Create"),
				primary_action: (v) => {
					d.hide();
					frappe.dom.freeze(__("Building the schedule..."));
					frm.call({ doc: frm.doc, method: "create_plan", args: v })
						.then((r) => {
							frappe.dom.unfreeze();
							if (r.message) frappe.set_route("Form", "GRC Project Plan", r.message);
						})
						.catch(() => frappe.dom.unfreeze());
				},
			});
			d.show();
		}).addClass("btn-primary");

		if (frm.doc.task_count) {
			frm.dashboard.set_headline(
				__("{0} tasks across {1} phases · {2} working days end to end", [
					frm.doc.task_count, frm.doc.phase_count, frm.doc.indicative_duration_days,
				])
			);
		}
	},
});
