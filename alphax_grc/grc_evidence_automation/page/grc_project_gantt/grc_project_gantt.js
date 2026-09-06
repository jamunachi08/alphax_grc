// Copyright (c) 2026, Neotec Integrated Solutions
// Gantt for GRC Project Plan. Bars are rendered from dates the server already
// computed, so the chart never disagrees with the plan document.

frappe.pages["grc-project-gantt"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("GRC Project Gantt"),
		single_column: true,
	});
	wrapper.gantt = new GRCGantt(page);
};

frappe.pages["grc-project-gantt"].on_page_show = function (wrapper) {
	if (!wrapper.gantt) return;
	const plan = frappe.get_route_options && frappe.get_route_options().plan;
	if (plan) wrapper.gantt.select_plan(plan);
	else wrapper.gantt.load_plans();
};

const GG_THEMES = {
	ocean: ["#0ea5e9", "#2563eb", "#6366f1", "#0891b2", "#0d9488"],
	sunset: ["#f97316", "#ef4444", "#ec4899", "#f59e0b", "#d946ef"],
	forest: ["#16a34a", "#059669", "#65a30d", "#0d9488", "#4d7c0f"],
	royal: ["#7c3aed", "#a21caf", "#4f46e5", "#9333ea", "#c026d3"],
	desert: ["#b45309", "#a16207", "#ca8a04", "#92400e", "#78716c"],
	mono: ["#6b7280", "#6b7280", "#6b7280", "#6b7280", "#6b7280"],
	contrast: ["#000000", "#000000", "#000000", "#000000", "#000000"],
};
const GG_THEME_KEYS = {
	Ocean: "ocean", Sunset: "sunset", Forest: "forest", Royal: "royal",
	Desert: "desert", "Monochrome (No Colour)": "mono", "High Contrast": "contrast",
};

const DAY = 86400000;
const ROW_H = 26;
const LABEL_W = 300;

class GRCGantt {
	constructor(page) {
		this.page = page;
		this.theme = localStorage.getItem("grc_pathway_theme") || "ocean";
		this.zoom = 18; // px per day
		this.build();
		this.load_plans();
	}

	build() {
		this.$body = $(`
			<div class="gg-wrap">
				<div class="gg-bar">
					<div class="gg-plan"></div>
					<div class="gg-right">
						<button class="gg-btn" data-zoom="out" title="${__("Zoom out")}">&minus;</button>
						<button class="gg-btn" data-zoom="in" title="${__("Zoom in")}">+</button>
						<select class="gg-theme"></select>
						<button class="gg-btn" data-open>${__("Open Plan")}</button>
					</div>
				</div>
				<div class="gg-meta"></div>
				<div class="gg-scroll"><div class="gg-chart"></div></div>
				<div class="gg-legend"></div>
			</div>
		`).appendTo(this.page.main);

		this.styles();

		this.plan_control = frappe.ui.form.make_control({
			parent: this.$body.find(".gg-plan"),
			df: {
				fieldtype: "Link",
				options: "GRC Project Plan",
				fieldname: "plan",
				placeholder: __("Select a plan"),
				only_input: true,
				change: () => {
					const v = this.plan_control.get_value();
					if (v && v !== this.plan_name) this.select_plan(v);
				},
			},
			render_input: true,
		});

		const $t = this.$body.find(".gg-theme");
		Object.keys(GG_THEME_KEYS).forEach((label) =>
			$t.append(`<option value="${GG_THEME_KEYS[label]}">${label}</option>`)
		);
		$t.val(this.theme).on("change", () => {
			this.theme = $t.val();
			localStorage.setItem("grc_pathway_theme", this.theme);
			this.render();
		});

		this.$body.on("click", "[data-zoom]", (e) => {
			const dir = $(e.currentTarget).data("zoom");
			this.zoom = Math.max(6, Math.min(48, this.zoom + (dir === "in" ? 6 : -6)));
			this.render();
		});
		this.$body.on("click", "[data-open]", () => {
			if (this.plan_name) frappe.set_route("Form", "GRC Project Plan", this.plan_name);
		});

		this.page.set_secondary_action(__("Refresh"), () => this.select_plan(this.plan_name));
	}

	load_plans() {
		frappe.call({ method: "alphax_grc.pathway.api.list_plans" }).then((r) => {
			const plans = (r && r.message) || [];
			if (!this.plan_name && plans.length) this.select_plan(plans[0].name);
			else if (!plans.length) {
				this.$body.find(".gg-chart").html(
					`<div class="gg-empty">${__("No project plans yet. Create one from a plan template.")}</div>`
				);
			}
		});
	}

	select_plan(name) {
		if (!name) return;
		this.plan_name = name;
		if (this.plan_control.get_value() !== name) this.plan_control.set_value(name);
		frappe
			.call({ method: "alphax_grc.pathway.api.get_gantt", args: { plan: name } })
			.then((r) => {
				if (!r || !r.message) return;
				this.data = r.message;
				if (!localStorage.getItem("grc_pathway_theme") && this.data.theme) {
					this.theme = GG_THEME_KEYS[this.data.theme] || "ocean";
					this.$body.find(".gg-theme").val(this.theme);
				}
				this.render();
			});
	}

	render() {
		if (!this.data) return;
		const d = this.data;
		const colours = GG_THEMES[this.theme];
		const tasks = d.tasks.filter((t) => t.start && t.end);

		this.$body.find(".gg-meta").html(`
			<b>${frappe.utils.escape_html(d.title || d.plan)}</b>
			<span class="gg-sep">&middot;</span>${frappe.utils.escape_html(d.client || "")}
			<span class="gg-sep">&middot;</span>${d.start || "?"} &rarr; ${d.end || "?"}
			<span class="gg-sep">&middot;</span>${d.total_working_days} ${__("working days")}
			<span class="gg-sep">&middot;</span>${d.pct_complete}% ${__("complete")}
		`);

		if (!tasks.length) {
			this.$body.find(".gg-chart").html(
				`<div class="gg-empty">${__("This plan has no dated tasks yet.")}</div>`
			);
			return;
		}

		const min = new Date(d.start || tasks[0].start);
		const max = new Date(d.end || tasks[tasks.length - 1].end);
		min.setHours(0, 0, 0, 0);
		max.setHours(0, 0, 0, 0);
		const span = Math.max(1, Math.round((max - min) / DAY) + 2);
		const W = LABEL_W + span * this.zoom;
		const H = (tasks.length + 2) * ROW_H;
		const x = (iso) => LABEL_W + (Math.round((new Date(iso) - min) / DAY) * this.zoom);

		// month ruler
		let ruler = "";
		let cursor = new Date(min);
		while (cursor <= max) {
			const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
			const label = cursor.toLocaleDateString(undefined, { month: "short", year: "2-digit" });
			const px = LABEL_W + Math.max(0, Math.round((first - min) / DAY)) * this.zoom;
			ruler +=
				`<line x1="${px}" y1="0" x2="${px}" y2="${H}" stroke="var(--border-color)" stroke-width="1"/>` +
				`<text x="${px + 4}" y="14" class="gg-month">${label}</text>`;
			cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
		}

		const today = new Date();
		today.setHours(0, 0, 0, 0);
		let todayLine = "";
		if (today >= min && today <= max) {
			const tx = x(today.toISOString().slice(0, 10));
			todayLine =
				`<line x1="${tx}" y1="18" x2="${tx}" y2="${H}" stroke="var(--red-500)" stroke-width="1.5" stroke-dasharray="3 3"/>` +
				`<text x="${tx + 4}" y="30" class="gg-today">${__("today")}</text>`;
		}

		const phases = [...new Set(tasks.map((t) => t.phase).filter(Boolean))];
		const bars = tasks
			.map((t, i) => {
				const y = 24 + i * ROW_H;
				const colour = colours[Math.max(0, phases.indexOf(t.phase)) % 5];
				const x1 = x(t.start);
				const x2 = x(t.end) + this.zoom;
				const w = Math.max(this.zoom * 0.6, x2 - x1);
				const indent = 6 + t.depth * 10;
				const label = frappe.utils.escape_html(
					t.title.length > 42 ? t.title.slice(0, 40) + "\u2026" : t.title
				);

				const shape = t.milestone
					? `<polygon points="${x1},${y + 9} ${x1 + 8},${y + 1} ${x1 + 16},${y + 9} ${x1 + 8},${y + 17}"
							fill="${colour}" class="gg-ms"/>`
					: `<rect x="${x1}" y="${y + 3}" width="${w}" height="14" rx="3" fill="${colour}"
							opacity="${t.status === "Cancelled" ? 0.3 : 0.85}"/>` +
					  (t.pct
							? `<rect x="${x1}" y="${y + 3}" width="${(w * t.pct) / 100}" height="14" rx="3"
									fill="${colour}"/>`
							: "");

				return (
					`<g class="gg-row" data-idx="${t.idx}">` +
					`<rect x="0" y="${y}" width="${W}" height="${ROW_H - 4}" class="gg-band"/>` +
					`<text x="${indent}" y="${y + 14}" class="gg-label${t.depth === 0 ? " gg-summary" : ""}">` +
					`${frappe.utils.escape_html(t.wbs)}  ${label}</text>` +
					`<text x="${LABEL_W - 34}" y="${y + 14}" class="gg-days">${t.milestone ? "" : t.days + "d"}</text>` +
					(t.locked ? `<text x="${LABEL_W - 12}" y="${y + 14}" class="gg-lock">&#128274;</text>` : "") +
					shape +
					`<title>${frappe.utils.escape_html(t.title)}\n${t.start} → ${t.end}` +
					`\n${t.days}d · ${t.pct}% · ${t.status}${t.role ? " · " + t.role : ""}</title>` +
					`</g>`
				);
			})
			.join("");

		this.$body.find(".gg-chart").html(
			`<svg width="${W}" height="${H}" class="gg-svg">${ruler}${bars}${todayLine}</svg>`
		);

		this.$body.find(".gg-legend").html(
			phases
				.map(
					(p, i) =>
						`<span class="gg-key"><i style="background:${colours[i % 5]}"></i>${frappe.utils.escape_html(p)}</span>`
				)
				.join("") +
				`<span class="gg-key gg-hint">${__("Click a bar to edit its dates")}</span>`
		);

		this.$body.find(".gg-row").on("click", (e) => {
			this.edit_task($(e.currentTarget).data("idx"));
		});
	}

	edit_task(idx) {
		const t = this.data.tasks.find((x) => x.idx === idx);
		if (!t) return;

		const d = new frappe.ui.Dialog({
			title: `${t.wbs} ${t.title}`,
			fields: [
				{ fieldname: "start_date", fieldtype: "Date", label: __("Start"), default: t.start },
				{
					fieldname: "duration_days", fieldtype: "Int", label: __("Duration (working days)"),
					default: t.days, depends_on: `eval:${!t.milestone}`,
				},
				{ fieldname: "cb", fieldtype: "Column Break" },
				{ fieldname: "pct_complete", fieldtype: "Percent", label: __("% Complete"), default: t.pct },
				{
					fieldname: "lock", fieldtype: "Check", label: __("Lock these dates"), default: 1,
					description: __("Locked tasks keep their dates when the plan start moves."),
				},
			],
			primary_action_label: __("Apply"),
			primary_action: (v) => {
				d.hide();
				frappe.dom.freeze(__("Rescheduling..."));
				frappe
					.call({
						method: "alphax_grc.pathway.api.update_task_dates",
						args: {
							plan: this.plan_name, idx: idx, start_date: v.start_date,
							duration_days: v.duration_days, pct_complete: v.pct_complete,
							lock: v.lock ? 1 : 0,
						},
					})
					.then((r) => {
						frappe.dom.unfreeze();
						if (r && r.message) {
							this.data = r.message;
							this.render();
						}
					})
					.catch(() => frappe.dom.unfreeze());
			},
		});
		d.show();
	}

	styles() {
		if (document.getElementById("gg-styles")) return;
		$("<style id='gg-styles'></style>").text(`
.gg-wrap { padding: 4px 0 40px; }
.gg-bar { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:10px; }
.gg-plan { min-width: 280px; }
.gg-right { display:flex; gap:6px; align-items:center; }
.gg-btn, .gg-theme { font-size:12px; padding:5px 10px; border-radius:7px; border:1px solid var(--border-color); background:var(--card-bg); color:var(--text-color); cursor:pointer; }
.gg-meta { font-size:12px; color:var(--text-muted); margin-bottom:10px; }
.gg-meta b { color: var(--text-color); font-size:13px; }
.gg-sep { margin:0 8px; opacity:.5; }
.gg-scroll { overflow-x:auto; border:1px solid var(--border-color); border-radius:8px; background:var(--card-bg); }
.gg-svg { display:block; font-family: var(--font-stack, inherit); }
.gg-band { fill: transparent; }
.gg-row:hover .gg-band { fill: var(--gray-100); }
.gg-row { cursor: pointer; }
.gg-label { font-size:11px; fill: var(--text-color); }
.gg-summary { font-weight:600; }
.gg-days, .gg-lock { font-size:10px; fill: var(--text-muted); }
.gg-month { font-size:10px; fill: var(--text-muted); }
.gg-today { font-size:10px; fill: var(--red-500); }
.gg-empty { padding:40px; text-align:center; color:var(--text-muted); font-size:13px; }
.gg-legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:11px; color:var(--text-muted); }
.gg-key { display:flex; align-items:center; gap:5px; }
.gg-key i { width:10px; height:10px; border-radius:2px; display:inline-block; }
.gg-hint { margin-left:auto; font-style:italic; }
`).appendTo(document.head);
	}
}
