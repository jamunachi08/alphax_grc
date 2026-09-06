// Copyright (c) 2026, Neotec Integrated Solutions
// GRC Pathway Console — a working surface, not a dashboard. Every stage
// exposes the transactions available right now, gated on what came before.

frappe.pages["grc-pathway-console"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("GRC Pathway Console"),
		single_column: true,
	});

	const console_view = new GRCPathwayConsole(page);
	wrapper.grc_console = console_view;
};

frappe.pages["grc-pathway-console"].on_page_show = function (wrapper) {
	if (wrapper.grc_console) wrapper.grc_console.load();
};

const GP_THEMES = {
	ocean: ["#0ea5e9", "#2563eb", "#6366f1", "#0891b2", "#0d9488"],
	sunset: ["#f97316", "#ef4444", "#ec4899", "#f59e0b", "#d946ef"],
	forest: ["#16a34a", "#059669", "#65a30d", "#0d9488", "#4d7c0f"],
	royal: ["#7c3aed", "#a21caf", "#4f46e5", "#9333ea", "#c026d3"],
	desert: ["#b45309", "#a16207", "#ca8a04", "#92400e", "#78716c"],
	mono: ["#6b7280", "#6b7280", "#6b7280", "#6b7280", "#6b7280"],
	contrast: ["#000000", "#000000", "#000000", "#000000", "#000000"],
};

const GP_THEME_LABELS = {
	Ocean: "ocean",
	Sunset: "sunset",
	Forest: "forest",
	Royal: "royal",
	Desert: "desert",
	"Monochrome (No Colour)": "mono",
	"High Contrast": "contrast",
};

const GP_STATE = {
	done: { label: __("Done"), tone: "green" },
	progress: { label: __("In progress"), tone: "blue" },
	ready: { label: __("Ready"), tone: "orange" },
	blocked: { label: __("Blocked"), tone: "gray" },
};

class GRCPathwayConsole {
	constructor(page) {
		this.page = page;
		this.client = localStorage.getItem("grc_pathway_client") || "";
		this.theme = localStorage.getItem("grc_pathway_theme") || "ocean";
		this.view = "journey";
		this.build_shell();
		this.load();
	}

	build_shell() {
		this.$body = $(`
			<div class="grc-console" data-theme="${this.theme}">
				<div class="gpc-bar">
					<div class="gpc-client"></div>
					<div class="gpc-right">
						<div class="gpc-tabs">
							<button class="gpc-tab active" data-view="journey">${__("Journey")}</button>
							<button class="gpc-tab" data-view="map">${__("Domain map")}</button>
							<button class="gpc-tab" data-view="sama">${__("SAMA CSF")}</button>
						</div>
						<select class="gpc-theme"></select>
					</div>
				</div>
				<div class="gpc-progress"></div>
				<div class="gpc-content"></div>
			</div>
		`).appendTo(this.page.main);

		this.inject_styles();

		this.client_control = frappe.ui.form.make_control({
			parent: this.$body.find(".gpc-client"),
			df: {
				fieldtype: "Link",
				options: "GRC Client Profile",
				fieldname: "client",
				placeholder: __("All clients"),
				only_input: true,
				change: () => {
					const value = this.client_control.get_value() || "";
					if (value === this.client) return;
					this.client = value;
					localStorage.setItem("grc_pathway_client", value);
					this.load();
				},
			},
			render_input: true,
		});
		if (this.client) this.client_control.set_value(this.client);

		const $theme = this.$body.find(".gpc-theme");
		Object.keys(GP_THEME_LABELS).forEach((label) => {
			$theme.append(`<option value="${GP_THEME_LABELS[label]}">${label}</option>`);
		});
		$theme.val(this.theme).on("change", () => {
			this.theme = $theme.val();
			localStorage.setItem("grc_pathway_theme", this.theme);
			this.$body.attr("data-theme", this.theme);
			this.render();
		});

		this.$body.on("click", ".gpc-tab", (e) => {
			this.view = $(e.currentTarget).data("view");
			this.$body.find(".gpc-tab").removeClass("active");
			$(e.currentTarget).addClass("active");
			this.render();
		});

		this.page.set_primary_action(__("Refresh"), () => this.load(), "refresh");

		this.page.add_menu_item(__("Run Diagnostics"), () => this.run_diagnostics());

		this.page.add_menu_item(__("Report Studio"), () => frappe.set_route("grc-report-studio"));
	}

	load() {
		this.$body.find(".gpc-content").html(`<div class="gpc-loading">${__("Loading pathway...")}</div>`);
		frappe
			.call({
				method: "alphax_grc.pathway.console.get_console_state",
				args: { client: this.client },
			})
			.then((r) => {
				if (!r || !r.message) return;
				this.state = r.message;
				if (!localStorage.getItem("grc_pathway_theme") && this.state.theme) {
					this.theme = GP_THEME_LABELS[this.state.theme] || "ocean";
					this.$body.attr("data-theme", this.theme).find(".gpc-theme").val(this.theme);
				}
				this.$body.find(".gpc-theme").prop("disabled", !this.state.allow_user_override);
				this.render();
			})
			.catch(() => {
				this.$body
					.find(".gpc-content")
					.html(`<div class="gpc-loading">${__("Could not load the pathway.")}</div>`);
			});
	}

	render() {
		if (!this.state) return;
		this.render_progress();
		if (this.view === "journey") this.render_journey();
		else if (this.view === "sama") this.render_sama();
		else this.render_map();
	}

	render_progress() {
		const p = this.state.progress;
		const colours = GP_THEMES[this.theme];
		const st = this.state.stages;
		const done = st.filter((x) => x.state === "done").length;
		const active = st.filter((x) => x.state === "progress").length;
		const ready = st.filter((x) => x.state === "ready").length;
		const blocked = st.filter((x) => x.state === "blocked").length;
		const attention = st.reduce((n, x) => n + (x.attention || 0), 0);
		const client = this.state.client
			? frappe.utils.escape_html(this.state.client)
			: __("All clients");
		const next = p.next ? frappe.utils.escape_html(p.next) : __("All stages complete");
		const mono = this.theme === "mono" || this.theme === "contrast";
		const heroBg = mono
			? "linear-gradient(135deg, #374151, #111827)"
			: `linear-gradient(135deg, ${colours[1]}, ${colours[2]} 55%, ${colours[4]})`;

		this.$body.find(".gpc-progress").html(`
			<div class="gpc-hero" style="background:${heroBg}">
				<div class="gpc-hero-left">
					<div class="gpc-hero-eyebrow">${__("GRC Pathway")} &middot; ${client}</div>
					<div class="gpc-hero-title">${p.pct}<span class="gpc-hero-pct">%</span></div>
					<div class="gpc-hero-sub">${p.done} ${__("of")} ${p.total} ${__("stages complete")} &middot; ${__("next")}: <b>${next}</b></div>
					<div class="gpc-hero-rail"><div class="gpc-hero-fill" style="width:${p.pct}%"></div></div>
				</div>
				<div class="gpc-hero-tiles">
					<div class="gpc-tile"><b>${done}</b><span>${__("done")}</span></div>
					<div class="gpc-tile"><b>${active}</b><span>${__("in progress")}</span></div>
					<div class="gpc-tile"><b>${ready}</b><span>${__("ready to start")}</span></div>
					<div class="gpc-tile"><b>${blocked}</b><span>${__("blocked")}</span></div>
					<div class="gpc-tile ${attention ? "hot" : ""}"><b>${attention}</b><span>${__("need attention")}</span></div>
				</div>
			</div>
			<div class="gpc-pillars">
				${this.pillar_strip()}
			</div>
		`);
	}

	pillar_strip() {
		// Risk anticipates -> Audit validates -> Compliance enforces.
		const colours = GP_THEMES[this.theme];
		const st = this.state.stages;
		const by = (k) => st.find((x) => x.key === k) || {};
		const pillars = [
			{ label: __("Governance"), sub: __("Direct and oversee"), keys: ["client", "engagement", "policy"], colour: colours[1] },
			{ label: __("Risk"), sub: __("Anticipate threats"), keys: ["risk", "vendor"], colour: colours[0] },
			// v2.10.0 — Resilience stage added to the console; colours[2] was
			// the one slot in the 5-colour theme palette not yet used here.
			{ label: __("Resilience"), sub: __("Prepare and recover"), keys: ["resilience"], colour: colours[2] },
			{ label: __("Compliance"), sub: __("Enforce the rules"), keys: ["framework", "control", "evidence"], colour: colours[4] },
			{ label: __("Audit"), sub: __("Validate controls"), keys: ["finding", "report"], colour: colours[3] },
		];
		return pillars
			.map((pl) => {
				const stages = pl.keys.map(by).filter((x) => x.key);
				const total = stages.reduce((n, x) => n + (x.count || 0), 0);
				const doneN = stages.filter((x) => x.state === "done").length;
				const pct = stages.length ? Math.round((doneN / stages.length) * 100) : 0;
				return `
				<div class="gpc-pillar-chip" style="--pc:${pl.colour}">
					<div class="gpc-pc-top"><span class="gpc-pc-dot"></span><b>${pl.label}</b><span class="gpc-pc-pct">${pct}%</span></div>
					<div class="gpc-pc-sub">${pl.sub}</div>
					<div class="gpc-pc-bar"><div style="width:${pct}%"></div></div>
					<div class="gpc-pc-meta">${total} ${__("records")} &middot; ${doneN}/${stages.length} ${__("stages done")}</div>
				</div>`;
			})
			.join("");
	}

	render_journey() {
		const colours = GP_THEMES[this.theme];
		const $content = this.$body.find(".gpc-content").empty();

		if (!this.state.stages.length) {
			$content.html(`<div class="gpc-loading">${__("No AlphaX GRC doctypes are readable for your roles.")}</div>`);
			return;
		}

		const ICON = {
			client: "&#128100;", engagement: "&#128188;", framework: "&#128209;", control: "&#128737;",
			risk: "&#9888;", evidence: "&#128206;", finding: "&#128269;", policy: "&#128220;",
			vendor: "&#129309;", report: "&#128200;",
		};

		const $grid = $('<div class="gpc-grid"></div>').appendTo($content);

		this.state.stages.forEach((stage, i) => {
			const colour = colours[i % 5];
			const meta = GP_STATE[stage.state];
			const blocked = stage.state === "blocked";
			const done = stage.state === "done";

			const metrics = (stage.metrics || [])
				.map((m) => `<span class="gpc-metric ${m.warn ? "warn" : ""}">${m.value} ${frappe.utils.escape_html(m.label)}</span>`)
				.join("");

			const actions = (stage.actions || [])
				.map((a, ai) => `<button class="gpc-act ${ai === 0 ? "primary" : ""}" data-stage="${stage.key}" data-idx="${ai}"${blocked ? " disabled" : ""}>${frappe.utils.escape_html(a.label)}</button>`)
				.join("");

			const blockers = blocked
				? `<div class="gpc-blocked">&#128274; ${__("Waiting on")}: ${stage.blockers.map((b) => frappe.utils.escape_html(b)).join(", ")}</div>`
				: "";

			$(`
				<div class="gpc-card2 ${stage.state}" style="--stage-c:${colour}">
					<div class="gpc-card2-head">
						<span class="gpc-num">${done ? "&#10003;" : i + 1}</span>
						<span class="gpc-icon">${ICON[stage.key] || "&#9679;"}</span>
						<span class="gpc-chip ${meta.tone}">${meta.label}</span>
					</div>
					<div class="gpc-card2-body">
						<div class="gpc-name">${frappe.utils.escape_html(stage.label)}</div>
						<div class="gpc-count-row"><span class="gpc-count">${stage.count}</span><span class="gpc-count-cap">${__("records")}</span></div>
						<p class="gpc-blurb">${frappe.utils.escape_html(stage.blurb)}</p>
						${metrics ? `<div class="gpc-metrics">${metrics}</div>` : ""}
						${blockers}
					</div>
					<div class="gpc-acts">${actions}</div>
					${i < this.state.stages.length - 1 ? '<span class="gpc-arrow">&#10140;</span>' : ""}
				</div>
			`).appendTo($grid);
		});

		$grid.find(".gpc-act").on("click", (e) => {
			const $b = $(e.currentTarget);
			const stage = this.state.stages.find((s) => s.key === $b.data("stage"));
			this.run_action(stage, stage.actions[$b.data("idx")]);
		});
	}

	render_sama() {
		const $content = this.$body.find(".gpc-content").empty();
		$content.html(`<div class="gpc-loading">${__("Loading SAMA position...")}</div>`);

		frappe
			.call({
				method: "alphax_grc.pathway.api.get_sama_dashboard",
				args: { client: this.client },
			})
			.then((r) => {
				if (!r || !r.message) return;
				this.draw_sama(r.message, $content);
			})
			.catch(() => {
				$content.html(`<div class="gpc-loading">${__("Could not load the SAMA dashboard.")}</div>`);
			});
	}

	draw_sama(d, $content) {
		if (!d.available) {
			$content.html(`<div class="gpc-loading">${frappe.utils.escape_html(d.reason || "")}</div>`);
			return;
		}
		const colours = GP_THEMES[this.theme];
		const esc = (v) => frappe.utils.escape_html(String(v == null ? "" : v));

		const a = d.assessment;
		const ring = (value, max, colour, label, sub) => {
			const r = 34, c = 2 * Math.PI * r;
			const pct = Math.max(0, Math.min(1, value / max));
			return `
			<div class="sama-ring">
				<svg viewBox="0 0 84 84" width="84" height="84">
					<circle cx="42" cy="42" r="${r}" stroke="var(--gray-200)" stroke-width="9" fill="none"/>
					<circle cx="42" cy="42" r="${r}" stroke="${colour}" stroke-width="9" fill="none"
						stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct)}"
						transform="rotate(-90 42 42)" style="transition:stroke-dashoffset .6s ease"/>
					<text x="42" y="47" text-anchor="middle" font-size="18" font-weight="800" fill="var(--text-color)">${label}</text>
				</svg>
				<div class="sama-ring-cap">${sub}</div>
			</div>`;
		};
		const matColour = a && a.overall_maturity >= d.target_level ? "var(--green-500)"
			: a && a.overall_maturity >= d.target_level - 1 ? "var(--orange-500)" : "var(--red-500)";
		const headline = a
			? `<div class="sama-head">
					${ring(a.overall_maturity, 5, matColour, a.overall_maturity, __("maturity / 5 &middot; target {0}", [d.target_level]))}
					${ring(a.pct_at_target || 0, 100, colours[1], (a.pct_at_target || 0) + "%", __("sub-domains at level 3+"))}
					${ring(d.deliverables.complete, Math.max(1, d.deliverables.total), colours[4], d.deliverables.complete + "/" + d.deliverables.total, __("deliverables filed"))}
					<div class="sama-score${d.incidents.not_yet_notified ? " warn" : ""}">
						<span class="sama-big">${d.incidents.not_yet_notified}</span>
						<div class="sama-cap">${__("reportable incidents not yet notified")}</div>
					</div>
			   </div>`
			: `<div class="sama-empty">
					${__("No SAMA assessment for this client yet.")}
					<button class="gpc-act primary" data-sama-new>${__("Start assessment")}</button>
			   </div>`;

		const bars = d.domains
			.map((dom, i) => {
				const colour = colours[i % 5];
				const pct = Math.round((dom.level / 5) * 100);
				const targetPct = (d.target_level / 5) * 100;
				return `
				<div class="sama-dom">
					<div class="sama-dom-head">
						<span>${esc(dom.code)} ${esc(dom.title)}</span>
						<b>${dom.level || 0}</b>
					</div>
					<div class="sama-track">
						<div class="sama-fill" style="width:${pct}%;background:${colour}"></div>
						<div class="sama-target" style="left:${targetPct}%" title="${__("SAMA target level 3")}"></div>
					</div>
					<div class="sama-dom-meta">${dom.at_target} / ${dom.total} ${__("sub-domains at target")}</div>
				</div>`;
			})
			.join("");

		const gaps = (d.weakest || []).length
			? `<table class="sama-gaps"><tbody>${d.weakest
					.map(
						(g) => `<tr>
							<td class="sama-code">${esc(g.code)}</td>
							<td>${esc(g.title)}</td>
							<td class="sama-lvl">${__("level")} ${g.level}</td>
							<td class="sama-gap">${esc(g.gap)}</td>
						</tr>`
					)
					.join("")}</tbody></table>`
			: `<p class="gpc-blurb">${__("No sub-domains below target.")}</p>`;

		$content.html(`
			${headline}
			<div class="sama-grid">
				<div class="sama-panel">
					<div class="sama-title">${__("Maturity by domain")}</div>
					${bars}
				</div>
				<div class="sama-panel">
					<div class="sama-title">${__("Furthest below target")}</div>
					${gaps}
				</div>
			</div>
			<div class="sama-actions">
				<button class="gpc-act primary" data-sama-new>${__("New assessment")}</button>
				<button class="gpc-act" data-sama-list="GRC SAMA Assessment">${__("Assessments")}</button>
				<button class="gpc-act" data-sama-list="GRC SAMA Deliverable">${__("Deliverables")} (${d.deliverables.total})</button>
				<button class="gpc-act" data-sama-list="GRC SAMA Waiver">${__("Waivers")} (${d.waivers.open} ${__("open")})</button>
				<button class="gpc-act" data-sama-list="GRC SAMA Subdomain">${__("Sub-domain catalogue")} (${d.catalogue_size})</button>
			</div>
		`);

		$content.find("[data-sama-list]").on("click", (e) => {
			const dt = $(e.currentTarget).data("sama-list");
			const f = this.client && dt !== "GRC SAMA Subdomain" ? { client: this.client } : {};
			frappe.set_route("List", dt, f);
		});
		$content.find("[data-sama-new]").on("click", () => {
			if (!this.client) {
				frappe.msgprint({
					title: __("Pick a client first"),
					message: __("A SAMA assessment is scoped to one member organisation."),
					indicator: "orange",
				});
				return;
			}
			frappe.new_doc("GRC SAMA Assessment", { client: this.client });
		});
	}

	render_map() {
		const colours = GP_THEMES[this.theme];
		const $content = this.$body.find(".gpc-content").empty();
		const $grid = $('<div class="gpc-map"></div>').appendTo($content);

		this.state.pillars.forEach((group, i) => {
			const colour = colours[i % 5];
			const items = group.items
				.map(
					(item) => `
					<button class="gpc-map-item" data-doctype="${frappe.utils.escape_html(item.doctype)}" data-scoped="${item.scoped}">
						<span>${frappe.utils.escape_html(item.label)}</span>
						<span class="gpc-map-count">${item.count}</span>
					</button>`
				)
				.join("");

			$(`
				<div class="gpc-pillar" style="--stage-c:${colour}">
					<div class="gpc-pillar-head">
						<span class="gpc-pillar-name">${frappe.utils.escape_html(group.pillar)}</span>
						<span class="gpc-pillar-cap">${frappe.utils.escape_html(group.caption)}</span>
					</div>
					<div class="gpc-pillar-items">${items}</div>
				</div>
			`).appendTo($grid);
		});

		$grid.find(".gpc-map-item").on("click", (e) => {
			const $b = $(e.currentTarget);
			const filters = $b.data("scoped") && this.client ? { client: this.client } : {};
			frappe.set_route("List", $b.data("doctype"), filters);
		});
	}

	run_action(stage, action) {
		if (!action) return;

		if (action.type === "report") {
			const route = { name: action.target };
			frappe.set_route("query-report", action.target);
			return;
		}

		if (action.type === "list") {
			const filters =
				this.client && stage.client_field && action.target === stage.doctype
					? { [stage.client_field]: this.client }
					: {};
			frappe.set_route("List", action.target, filters);
			return;
		}

		if (action.type === "adopt") {
			this.adopt_policies();
			return;
		}

		// type === "new" — create the record with the client already filled in,
		// so the console actually drives the transaction rather than pointing at it.
		const defaults = {};
		if (this.client && stage.client_field) defaults[stage.client_field] = this.client;
		if (this.client && action.target !== stage.doctype) defaults.client = this.client;

		frappe.new_doc(action.target, defaults);
	}

	run_diagnostics() {
		frappe.dom.freeze(__("Checking this site..."));
		frappe
			.call({ method: "alphax_grc.diagnostics.run_diagnostics" })
			.then((r) => {
				frappe.dom.unfreeze();
				if (!r || !r.message) return;
				const d = r.message;
				const icon = { BLOCKER: "&#10005;", WARNING: "!", OK: "&#10003;" };
				const colour = {
					BLOCKER: "var(--red-600)",
					WARNING: "var(--orange-600)",
					OK: "var(--green-600)",
				};
				const rows = d.results
					.map(
						(x) => `
						<tr>
							<td style="color:${colour[x.level]};font-weight:600;width:22px">${icon[x.level]}</td>
							<td style="width:150px">${frappe.utils.escape_html(x.check)}</td>
							<td>${frappe.utils.escape_html(x.detail)}
								${x.fix && x.level !== "OK"
									? `<div class="text-muted small" style="margin-top:3px">${frappe.utils.escape_html(x.fix)}</div>`
									: ""}
							</td>
						</tr>`
					)
					.join("");

				const headline = d.stopper
					? `<div style="padding:10px 12px;border-left:3px solid var(--red-600);background:var(--red-50);margin-bottom:12px">
							<b>${__("Stopper")}:</b> ${frappe.utils.escape_html(d.stopper.detail)}
							<div class="small" style="margin-top:4px">${frappe.utils.escape_html(d.stopper.fix)}</div>
					   </div>`
					: `<div style="padding:10px 12px;border-left:3px solid var(--green-600);background:var(--green-50);margin-bottom:12px">
							${__("No blockers found.")} ${d.warnings} ${__("warning(s).")}
					   </div>`;

				frappe.msgprint({
					title: __("AlphaX GRC Diagnostics") + ` — v${d.version}`,
					wide: true,
					message: headline +
						`<table class="table table-sm" style="font-size:12px">${rows}</table>`,
				});
			})
			.catch(() => frappe.dom.unfreeze());
	}

	adopt_policies() {
		if (!this.client) {
			frappe.msgprint({
				title: __("Pick a client first"),
				message: __("Policies are adopted for a specific client. Choose one above."),
				indicator: "orange",
			});
			return;
		}

		const d = new frappe.ui.Dialog({
			title: __("Adopt Policies for {0}", [this.client]),
			fields: [
				{
					fieldname: "scope",
					fieldtype: "Select",
					label: __("Which policies"),
					options: [
						{ label: __("Baseline (mandatory) only"), value: "baseline" },
						{ label: __("Entire active library"), value: "all" },
					],
					default: "baseline",
					reqd: 1,
				},
				{
					fieldname: "note",
					fieldtype: "HTML",
					options: `<p class="text-muted small">${__(
						"Policies already held by this client are skipped, so this is safe to re-run."
					)}</p>`,
				},
			],
			primary_action_label: __("Adopt"),
			primary_action: (values) => {
				d.hide();
				frappe.dom.freeze(__("Creating policies..."));
				frappe
					.call({
						method: "alphax_grc.pathway.api.adopt_policies",
						args: {
							client: this.client,
							only_mandatory: values.scope === "baseline" ? 1 : 0,
						},
					})
					.then((r) => {
						frappe.dom.unfreeze();
						if (r && r.message) {
							frappe.show_alert({ message: r.message.message, indicator: "green" });
						}
						this.load();
					})
					.catch(() => frappe.dom.unfreeze());
			},
		});
		d.show();
	}

	inject_styles() {
		if (document.getElementById("gpc-styles")) return;
		const css = `
.grc-console { --c1:#0ea5e9; --c2:#2563eb; --c3:#6366f1; padding: 4px 0 40px; }
.grc-console[data-theme="mono"] .gpc-chip, .grc-console[data-theme="contrast"] .gpc-chip { background: var(--gray-100); color: var(--text-color); }
.gpc-bar { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:14px; }
.gpc-client { min-width: 240px; }
.gpc-right { display:flex; align-items:center; gap:8px; }
.gpc-tabs { display:flex; border:1px solid var(--border-color); border-radius:8px; overflow:hidden; }
.gpc-tab { border:0; background:var(--card-bg); padding:6px 14px; font-size:12px; cursor:pointer; color:var(--text-muted); }
.gpc-tab.active { background:var(--gray-100); color:var(--text-color); font-weight:500; }
.gpc-theme { font-size:12px; padding:6px 8px; border-radius:8px; border:1px solid var(--border-color); background:var(--card-bg); color:var(--text-color); }
.gpc-rail { height:8px; border-radius:6px; background:var(--gray-200); overflow:hidden; }
.gpc-rail-fill { height:100%; border-radius:6px; transition:width .45s ease; }
.gpc-rail-meta { display:flex; justify-content:space-between; font-size:11px; color:var(--text-muted); margin:6px 0 18px; }
.gpc-loading { padding:32px 0; text-align:center; color:var(--text-muted); font-size:13px; }
.gpc-stage { display:flex; gap:14px; }
.gpc-spine { display:flex; flex-direction:column; align-items:center; width:28px; flex:none; }
.gpc-node { width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:600; color:#fff; background:var(--stage-c); flex:none; }
.gpc-stage.blocked .gpc-node { background:var(--gray-400); }
.gpc-line { flex:1; width:2px; background:var(--border-color); margin:4px 0; min-height:14px; }
.gpc-card { flex:1; border:1px solid var(--border-color); border-left:3px solid var(--stage-c); border-radius:0 8px 8px 0; background:var(--card-bg); padding:12px 14px; margin-bottom:10px; }
.gpc-stage.blocked .gpc-card { border-left-color:var(--gray-400); opacity:.72; }
.gpc-stage.done .gpc-card { background:var(--gray-50); }
.gpc-card-head { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.gpc-name { font-size:13px; font-weight:600; margin-right:8px; }
.gpc-count { font-size:20px; font-weight:700; line-height:1; }
.gpc-chip { font-size:10px; font-weight:600; padding:2px 8px; border-radius:20px; background:var(--gray-100); color:var(--text-muted); }
.gpc-chip.green { background:var(--green-100); color:var(--green-700); }
.gpc-chip.blue { background:var(--blue-100); color:var(--blue-700); }
.gpc-chip.orange { background:var(--orange-100); color:var(--orange-700); }
.gpc-blurb { font-size:12px; color:var(--text-muted); margin:6px 0 0; }
.gpc-metrics { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
.gpc-metric { font-size:11px; padding:2px 8px; border-radius:6px; background:var(--gray-100); color:var(--text-muted); }
.gpc-metric.warn { background:var(--orange-100); color:var(--orange-700); }
.gpc-blocked { font-size:11px; color:var(--text-muted); margin-top:8px; font-style:italic; }
.gpc-acts { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
.gpc-act { font-size:12px; padding:5px 12px; border-radius:6px; border:1px solid var(--border-color); background:var(--card-bg); color:var(--text-color); cursor:pointer; }
.gpc-act.primary { border-color:var(--stage-c); color:var(--stage-c); font-weight:500; }
.gpc-act:disabled { opacity:.45; cursor:not-allowed; }
.gpc-act:hover:not(:disabled) { background:var(--gray-100); }
.gpc-map { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }
.gpc-pillar { border:1px solid var(--border-color); border-top:3px solid var(--stage-c); border-radius:0 0 8px 8px; background:var(--card-bg); padding:12px 14px; }
.gpc-pillar-head { margin-bottom:10px; }
.gpc-pillar-name { display:block; font-size:13px; font-weight:600; }
.gpc-pillar-cap { font-size:11px; color:var(--text-muted); }
.gpc-pillar-items { display:flex; flex-direction:column; gap:6px; }
.gpc-map-item { display:flex; justify-content:space-between; align-items:center; gap:8px; width:100%; font-size:12px; padding:7px 10px; border:1px solid var(--border-color); border-radius:6px; background:var(--card-bg); color:var(--text-color); cursor:pointer; }
.gpc-map-item:hover { border-color:var(--stage-c); }
.gpc-map-count { font-weight:600; font-size:12px; }

/* ---- hero ---- */
.gpc-hero { display:flex; gap:20px; align-items:stretch; flex-wrap:wrap; border-radius:14px; padding:20px 22px; color:#fff; margin-bottom:12px; box-shadow:0 8px 24px rgba(0,0,0,.12); }
.gpc-hero-left { flex:1 1 280px; min-width:240px; }
.gpc-hero-eyebrow { font-size:11px; letter-spacing:.08em; text-transform:uppercase; opacity:.85; }
.gpc-hero-title { font-size:46px; font-weight:800; line-height:1; margin:6px 0 4px; letter-spacing:-.02em; }
.gpc-hero-pct { font-size:22px; font-weight:600; opacity:.85; margin-left:2px; }
.gpc-hero-sub { font-size:12px; opacity:.92; }
.gpc-hero-rail { height:8px; border-radius:6px; background:rgba(255,255,255,.28); margin-top:12px; overflow:hidden; }
.gpc-hero-fill { height:100%; background:#fff; border-radius:6px; transition:width .5s ease; }
.gpc-hero-tiles { display:grid; grid-template-columns:repeat(5,minmax(78px,1fr)); gap:8px; align-content:center; flex:0 0 auto; }
.gpc-tile { background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.28); border-radius:10px; padding:10px 8px; text-align:center; backdrop-filter:blur(2px); }
.gpc-tile b { display:block; font-size:22px; font-weight:800; line-height:1; }
.gpc-tile span { display:block; font-size:10px; opacity:.9; margin-top:4px; letter-spacing:.02em; }
.gpc-tile.hot { background:rgba(255,255,255,.92); color:var(--red-600); border-color:#fff; }
.gpc-tile.hot span { color:var(--red-600); }
@media (max-width:900px){ .gpc-hero-tiles { grid-template-columns:repeat(3,1fr); width:100%; } }

/* ---- pillar strip ---- */
.gpc-pillars { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin-bottom:18px; }
@media (max-width:1100px){ .gpc-pillars { grid-template-columns:repeat(3,1fr); } }
@media (max-width:900px){ .gpc-pillars { grid-template-columns:repeat(2,1fr); } }
.gpc-pillar-chip { border:1px solid var(--border-color); border-top:4px solid var(--pc); border-radius:10px; padding:10px 12px; background:var(--card-bg); }
.gpc-pc-top { display:flex; align-items:center; gap:7px; font-size:12px; }
.gpc-pc-dot { width:9px; height:9px; border-radius:50%; background:var(--pc); }
.gpc-pc-pct { margin-left:auto; font-weight:700; color:var(--pc); }
.gpc-pc-sub { font-size:11px; color:var(--text-muted); margin:2px 0 6px; }
.gpc-pc-bar { height:5px; border-radius:3px; background:var(--gray-200); overflow:hidden; }
.gpc-pc-bar div { height:100%; background:var(--pc); border-radius:3px; }
.gpc-pc-meta { font-size:10px; color:var(--text-muted); margin-top:5px; }

/* ---- journey grid ---- */
.gpc-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:14px; }
.gpc-card2 { position:relative; display:flex; flex-direction:column; border:1px solid var(--border-color); border-radius:12px; background:var(--card-bg); overflow:hidden; transition:transform .15s ease, box-shadow .15s ease; }
.gpc-card2:hover { transform:translateY(-3px); box-shadow:0 10px 24px color-mix(in srgb, var(--stage-c) 22%, transparent); }
.gpc-card2::before { content:""; position:absolute; inset:0 0 auto 0; height:6px; background:var(--stage-c); }
.gpc-card2.blocked { opacity:.7; }
.gpc-card2.blocked::before { background:var(--gray-400); }
.gpc-card2.done { background:linear-gradient(180deg, color-mix(in srgb, var(--stage-c) 10%, var(--card-bg)), var(--card-bg) 60%); }
.gpc-card2-head { display:flex; align-items:center; gap:8px; padding:14px 12px 4px; }
.gpc-num { width:30px; height:30px; border-radius:50%; background:var(--stage-c); color:#fff; font-weight:800; font-size:13px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px color-mix(in srgb, var(--stage-c) 40%, transparent); }
.gpc-card2.blocked .gpc-num { background:var(--gray-400); box-shadow:none; }
.gpc-icon { font-size:18px; opacity:.85; }
.gpc-card2-head .gpc-chip { margin-left:auto; }
.gpc-card2-body { padding:4px 12px 8px; flex:1; }
.gpc-card2 .gpc-name { font-size:13px; font-weight:700; margin:0 0 4px; }
.gpc-count-row { display:flex; align-items:baseline; gap:6px; margin-bottom:6px; }
.gpc-card2 .gpc-count { font-size:26px; font-weight:800; line-height:1; color:var(--stage-c); }
.gpc-card2.blocked .gpc-count { color:var(--text-muted); }
.gpc-count-cap { font-size:11px; color:var(--text-muted); }
.gpc-card2 .gpc-blurb { font-size:11px; line-height:1.4; }
.gpc-card2 .gpc-acts { padding:8px 12px 12px; border-top:1px solid var(--border-color); margin-top:auto; }
.gpc-arrow { position:absolute; right:-11px; top:50%; transform:translateY(-50%); font-size:16px; color:var(--stage-c); background:var(--card-bg); border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; z-index:2; border:1px solid var(--border-color); }
@media (max-width:700px){ .gpc-arrow { display:none; } }
.grc-console[data-theme="mono"] .gpc-arrow, .grc-console[data-theme="contrast"] .gpc-arrow { display:none; }
.sama-head { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:16px; align-items:stretch; }
.sama-ring { flex:1; min-width:150px; border:1px solid var(--border-color); border-radius:12px; padding:12px; background:var(--card-bg); display:flex; flex-direction:column; align-items:center; }
.sama-ring-cap { font-size:11px; color:var(--text-muted); margin-top:6px; text-align:center; }
.sama-score { flex:1; min-width:150px; border:1px solid var(--border-color); border-radius:8px; padding:12px 14px; background:var(--card-bg); }
.sama-score.warn { border-color: var(--orange-400); }
.sama-big { font-size:26px; font-weight:700; line-height:1; }
.sama-of { font-size:13px; color:var(--text-muted); margin-left:2px; }
.sama-cap { font-size:11px; color:var(--text-muted); margin-top:6px; }
.sama-empty { padding:22px; text-align:center; border:1px dashed var(--border-color); border-radius:8px; margin-bottom:16px; font-size:13px; color:var(--text-muted); }
.sama-empty .gpc-act { margin-left:10px; }
.sama-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:12px; }
.sama-panel { border:1px solid var(--border-color); border-radius:8px; padding:14px; background:var(--card-bg); }
.sama-title { font-size:12px; font-weight:600; margin-bottom:12px; }
.sama-dom { margin-bottom:14px; }
.sama-dom-head { display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px; }
.sama-track { position:relative; height:10px; border-radius:5px; background:var(--gray-200); overflow:visible; }
.sama-fill { height:100%; border-radius:5px; transition:width .4s ease; }
.sama-target { position:absolute; top:-3px; width:2px; height:16px; background:var(--text-color); opacity:.55; }
.sama-dom-meta { font-size:11px; color:var(--text-muted); margin-top:4px; }
.sama-gaps { width:100%; font-size:11px; border-collapse:collapse; }
.sama-gaps td { padding:5px 6px; border-bottom:1px solid var(--border-color); vertical-align:top; }
.sama-code { font-weight:600; white-space:nowrap; }
.sama-lvl { white-space:nowrap; color:var(--orange-600); }
.sama-gap { color:var(--text-muted); }
.sama-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:14px; }
`;
		$("<style id='gpc-styles'></style>").text(css).appendTo(document.head);
	}
}
