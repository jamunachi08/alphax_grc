// Copyright (c) 2026, Neotec Integrated Solutions
// Report Studio: pick a report, see chart + drill-down, export CSV, and
// build new reports from the front end without code.

frappe.pages["grc-report-studio"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("GRC Report Studio"),
		single_column: true,
	});
	wrapper.studio = new GRCReportStudio(page);
};

const RS_THEMES = {
	ocean: ["#0ea5e9", "#2563eb", "#6366f1", "#0891b2", "#0d9488", "#38bdf8", "#818cf8"],
	sunset: ["#f97316", "#ef4444", "#ec4899", "#f59e0b", "#d946ef", "#fb923c", "#f472b6"],
	forest: ["#16a34a", "#059669", "#65a30d", "#0d9488", "#4d7c0f", "#4ade80", "#2dd4bf"],
	royal: ["#7c3aed", "#a21caf", "#4f46e5", "#9333ea", "#c026d3", "#a78bfa", "#e879f9"],
	desert: ["#b45309", "#a16207", "#ca8a04", "#92400e", "#78716c", "#d97706", "#a8a29e"],
	mono: ["#374151", "#4b5563", "#6b7280", "#9ca3af", "#d1d5db", "#54606f", "#7d8794"],
	contrast: ["#000", "#333", "#555", "#777", "#999", "#222", "#444"],
};

class GRCReportStudio {
	constructor(page) {
		this.page = page;
		this.theme = localStorage.getItem("grc_pathway_theme") || "ocean";
		this.build();
		this.load_list();
	}

	build() {
		this.$body = $(`
			<div class="rs-wrap">
				<div class="rs-side">
					<div class="rs-side-head">${__("Reports")}</div>
					<div class="rs-list"></div>
				</div>
				<div class="rs-main">
					<div class="rs-head">
						<div>
							<div class="rs-title">${__("Pick a report")}</div>
							<div class="rs-desc"></div>
						</div>
						<div class="rs-btns">
							<button class="rs-btn" data-csv>${__("Export CSV")}</button>
							<button class="rs-btn" data-refresh>${__("Refresh")}</button>
						</div>
					</div>
					<div class="rs-chart"></div>
					<div class="rs-tablewrap"><table class="rs-table"></table></div>
				</div>
			</div>
		`).appendTo(this.page.main);
		this.styles();

		this.page.set_primary_action(__("New Report"), () => this.new_report_dialog(), "add");
		this.$body.on("click", "[data-refresh]", () => this.current && this.run(this.current));
		this.$body.on("click", "[data-csv]", () => this.export_csv());
	}

	load_list(select) {
		frappe.call({ method: "alphax_grc.pathway.reports.list_definitions" }).then((r) => {
			const defs = (r && r.message) || [];
			const $list = this.$body.find(".rs-list").empty();
			if (!defs.length) {
				$list.html(`<div class="rs-empty">${__("No reports yet. Create one.")}</div>`);
				return;
			}
			let category = null;
			defs.forEach((d) => {
				if (d.category !== category) {
					category = d.category;
					$list.append(`<div class="rs-cat">${frappe.utils.escape_html(category || "General")}</div>`);
				}
				$(`<button class="rs-item" data-name="${frappe.utils.escape_html(d.name)}">
						${frappe.utils.escape_html(d.report_title)}
						<span class="rs-kind">${d.definition_type === "Built-in" ? "&#9733;" : ""}</span>
				   </button>`)
					.on("click", () => this.run(d.name))
					.appendTo($list);
			});
			this.run(select || defs[0].name);
		});
	}

	run(name) {
		this.current = name;
		this.$body.find(".rs-item").removeClass("active");
		this.$body.find(`.rs-item[data-name="${CSS.escape(name)}"]`).addClass("active");
		this.$body.find(".rs-chart").html(`<div class="rs-empty">${__("Running...")}</div>`);
		this.$body.find(".rs-table").empty();

		frappe
			.call({ method: "alphax_grc.pathway.reports.run_definition", args: { name } })
			.then((r) => {
				if (!r || !r.message) return;
				this.data = r.message;
				this.render();
			})
			.catch(() => {
				this.$body.find(".rs-chart").html(
					`<div class="rs-empty">${__("This report failed to run — open its definition to fix it.")}</div>`
				);
			});
	}

	render() {
		const d = this.data;
		this.$body.find(".rs-title").text(d.title);
		this.$body.find(".rs-desc").text(d.description || "");
		const $chart = this.$body.find(".rs-chart").empty();

		if (d.chart_type === "Number" || (d.number !== undefined && d.number !== null)) {
			$chart.html(`<div class="rs-number">${d.number ?? (d.series[0] && d.series[0][0]) ?? 0}<span>${d.suffix || ""}</span></div>`);
		} else if (d.chart_type === "Donut") {
			$chart.html(this.donut(d));
		} else if (d.chart_type !== "Table only") {
			$chart.html(this.bars(d));
		}
		this.table(d);
	}

	bars(d) {
		const colours = RS_THEMES[this.theme];
		const labels = d.labels || [];
		if (!labels.length) return `<div class="rs-empty">${__("No data.")}</div>`;
		const seriesCount = d.series.length;
		const max = Math.max(1, ...d.series.flat());
		const rowH = 26, groupH = rowH * seriesCount + 10;
		const H = labels.length * groupH + 24;
		const W = 720, labelW = 210;

		let svg = `<svg viewBox="0 0 ${W} ${H}" class="rs-svg" role="img">`;
		const legend = (d.series_labels || [])
			.map((l, si) => `<span class="rs-key"><i style="background:${colours[si % colours.length]}"></i>${frappe.utils.escape_html(l)}</span>`)
			.join("");

		labels.forEach((label, i) => {
			const y0 = 12 + i * groupH;
			svg += `<text x="${labelW - 8}" y="${y0 + groupH / 2}" text-anchor="end" class="rs-label">${frappe.utils.escape_html(String(label).slice(0, 34))}</text>`;
			d.series.forEach((series, si) => {
				const v = series[i] || 0;
				const w = Math.max(2, (v / max) * (W - labelW - 70));
				const y = y0 + si * rowH;
				svg += `<rect x="${labelW}" y="${y}" width="${w}" height="${rowH - 8}" rx="4"
							fill="${colours[si % colours.length]}" opacity="${si ? 0.55 : 0.95}"><title>${v}</title></rect>
						<text x="${labelW + w + 6}" y="${y + rowH - 15}" class="rs-val">${v}</text>`;
			});
		});
		svg += "</svg>";
		return `<div class="rs-legend">${legend}</div>${svg}`;
	}

	donut(d) {
		const colours = RS_THEMES[this.theme];
		const values = d.series[0] || [];
		const total = values.reduce((a, b) => a + b, 0) || 1;
		const r = 74, cx = 105, cy = 105, circ = 2 * Math.PI * r;
		let offset = 0;
		let rings = "";
		values.forEach((v, i) => {
			const frac = v / total;
			rings += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${colours[i % colours.length]}"
				stroke-width="30" stroke-dasharray="${frac * circ} ${circ}" stroke-dashoffset="${-offset * circ}"
				transform="rotate(-90 ${cx} ${cy})"><title>${d.labels[i]}: ${v}</title></circle>`;
			offset += frac;
		});
		const legend = (d.labels || [])
			.map((l, i) => `<span class="rs-key"><i style="background:${colours[i % colours.length]}"></i>${frappe.utils.escape_html(String(l))} <b>${values[i]}</b></span>`)
			.join("");
		return `
			<div class="rs-donutwrap">
				<svg viewBox="0 0 210 210" width="190" height="190">${rings}
					<text x="${cx}" y="${cy + 6}" text-anchor="middle" class="rs-donut-total">${total}</text>
				</svg>
				<div class="rs-legend rs-legend-col">${legend}</div>
			</div>`;
	}

	table(d) {
		const $t = this.$body.find(".rs-table").empty();
		if (!d.columns || !d.columns.length || !d.rows || !d.rows.length) return;
		const head = d.columns
			.map((c) => `<th>${frappe.utils.escape_html(frappe.unscrub ? frappe.unscrub(c) : c)}</th>`)
			.join("");
		const body = d.rows
			.map((row) => {
				const cells = d.columns
					.map((c) => {
						let v = row[c];
						if (v === null || v === undefined) v = "";
						if (c === "name" && d.source_doctype && v) {
							return `<td><a href="/app/${frappe.router.slug(d.source_doctype)}/${encodeURIComponent(v)}">${frappe.utils.escape_html(String(v))}</a></td>`;
						}
						return `<td>${frappe.utils.escape_html(String(v))}</td>`;
					})
					.join("");
				return `<tr>${cells}</tr>`;
			})
			.join("");
		$t.html(`<thead><tr>${head}</tr></thead><tbody>${body}</tbody>`);
	}

	export_csv() {
		const d = this.data;
		if (!d || !d.rows || !d.rows.length) return;
		const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
		const lines = [d.columns.map(esc).join(",")];
		d.rows.forEach((row) => lines.push(d.columns.map((c) => esc(row[c])).join(",")));
		const blob = new Blob(["\ufeff" + lines.join("\n")], { type: "text/csv;charset=utf-8" });
		const a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = `${(d.title || "report").replace(/[^\w-]+/g, "_")}.csv`;
		a.click();
		URL.revokeObjectURL(a.href);
	}

	new_report_dialog() {
		const dlg = new frappe.ui.Dialog({
			title: __("New Report"),
			fields: [
				{ fieldname: "report_title", fieldtype: "Data", label: __("Report Title"), reqd: 1 },
				{
					fieldname: "source_doctype", fieldtype: "Link", options: "DocType",
					label: __("Source DocType"), reqd: 1,
					get_query: () => ({
						filters: { module: ["in", ["AlphaX GRC", "GRC Evidence Automation"]], istable: 0 },
					}),
					change: () => this.load_fields(dlg),
				},
				{ fieldname: "cb1", fieldtype: "Column Break" },
				{
					fieldname: "category", fieldtype: "Select", label: __("Category"), default: "General",
					options: "Privacy\nRisk\nCompliance\nSAMA\nIncidents\nAssets\nPolicies\nVendors\nDelivery\nGeneral",
				},
				{ fieldname: "chart_type", fieldtype: "Select", label: __("Chart"),
				  options: "Bar\nDonut\nNumber\nTable only", default: "Bar" },
				{ fieldname: "sec1", fieldtype: "Section Break", label: __("Shape") },
				{ fieldname: "group_by", fieldtype: "Select", label: __("Group By"), options: "" },
				{ fieldname: "cb2", fieldtype: "Column Break" },
				{ fieldname: "aggregate", fieldtype: "Select", label: __("Aggregate"),
				  options: "Count\nSum\nAverage", default: "Count" },
				{ fieldname: "aggregate_field", fieldtype: "Select", label: __("Aggregate Field"),
				  options: "", depends_on: "eval:doc.aggregate!='Count'" },
				{ fieldname: "sec2", fieldtype: "Section Break", label: __("Filter (optional)") },
				{ fieldname: "filters_json", fieldtype: "Small Text", label: __("Filters (JSON)"),
				  description: __('e.g. [["status","in",["Open","Monitoring"]]]') },
			],
			primary_action_label: __("Create & Run"),
			primary_action: (v) => {
				frappe
					.call({ method: "alphax_grc.pathway.reports.create_definition", args: v })
					.then((r) => {
						dlg.hide();
						frappe.show_alert({ message: __("Report created"), indicator: "green" });
						this.load_list(r.message);
					});
			},
		});
		dlg.show();
	}

	load_fields(dlg) {
		const dt = dlg.get_value("source_doctype");
		if (!dt) return;
		frappe
			.call({ method: "alphax_grc.pathway.reports.field_options", args: { doctype: dt } })
			.then((r) => {
				if (!r || !r.message) return;
				const opts = r.message;
				dlg.set_df_property("group_by", "options",
					[""].concat(opts.groupable.map((f) => f.fieldname)).join("\n"));
				dlg.set_df_property("aggregate_field", "options",
					[""].concat(opts.numeric.map((f) => f.fieldname)).join("\n"));
			});
	}

	styles() {
		if (document.getElementById("rs-styles")) return;
		$("<style id='rs-styles'></style>").text(`
.rs-wrap { display:flex; gap:16px; padding-bottom:40px; align-items:flex-start; }
.rs-side { flex:0 0 240px; border:1px solid var(--border-color); border-radius:10px; background:var(--card-bg); overflow:hidden; position:sticky; top:70px; max-height:80vh; display:flex; flex-direction:column; }
.rs-side-head { padding:10px 12px; font-size:12px; font-weight:700; border-bottom:1px solid var(--border-color); }
.rs-list { overflow-y:auto; padding:6px; }
.rs-cat { font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--text-muted); padding:8px 8px 3px; }
.rs-item { display:block; width:100%; text-align:left; font-size:12px; padding:7px 9px; border:0; border-radius:7px; background:transparent; color:var(--text-color); cursor:pointer; }
.rs-item:hover { background:var(--gray-100); }
.rs-item.active { background:var(--gray-200); font-weight:600; }
.rs-kind { float:right; color:var(--yellow-500); font-size:10px; }
.rs-main { flex:1; min-width:0; }
.rs-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px; }
.rs-title { font-size:16px; font-weight:700; }
.rs-desc { font-size:11px; color:var(--text-muted); max-width:520px; }
.rs-btn { font-size:12px; padding:5px 11px; border-radius:7px; border:1px solid var(--border-color); background:var(--card-bg); color:var(--text-color); cursor:pointer; }
.rs-chart { border:1px solid var(--border-color); border-radius:10px; background:var(--card-bg); padding:14px; margin-bottom:12px; overflow-x:auto; }
.rs-svg { width:100%; max-width:760px; display:block; }
.rs-label { font-size:11px; fill:var(--text-color); }
.rs-val { font-size:10px; fill:var(--text-muted); }
.rs-legend { display:flex; gap:14px; flex-wrap:wrap; font-size:11px; color:var(--text-muted); margin-bottom:8px; }
.rs-legend-col { flex-direction:column; gap:6px; margin:0; }
.rs-key { display:flex; align-items:center; gap:6px; }
.rs-key i { width:10px; height:10px; border-radius:3px; display:inline-block; }
.rs-donutwrap { display:flex; gap:26px; align-items:center; flex-wrap:wrap; }
.rs-donut-total { font-size:22px; font-weight:800; fill:var(--text-color); }
.rs-number { font-size:52px; font-weight:800; padding:12px 6px; }
.rs-number span { font-size:24px; color:var(--text-muted); margin-left:4px; }
.rs-tablewrap { border:1px solid var(--border-color); border-radius:10px; overflow:auto; max-height:420px; background:var(--card-bg); }
.rs-table { width:100%; font-size:11.5px; border-collapse:collapse; }
.rs-table th { position:sticky; top:0; background:var(--gray-100); text-align:left; padding:7px 9px; font-weight:600; border-bottom:1px solid var(--border-color); white-space:nowrap; }
.rs-table td { padding:6px 9px; border-bottom:1px solid var(--border-color); }
.rs-empty { padding:26px; text-align:center; color:var(--text-muted); font-size:12px; }
@media (max-width:860px){ .rs-wrap { flex-direction:column; } .rs-side { position:static; width:100%; flex:none; } }
`).appendTo(document.head);
	}
}
