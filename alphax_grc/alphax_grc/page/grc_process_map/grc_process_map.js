// AlphaX GRC — Process Map: end-to-end swimlane flow with clickable
// transactions, decision loops and gate tooltips. Companion to the
// GRC Lifecycle wheel: same eight-stage vocabulary, laid out as a pathway.

frappe.pages["grc-process-map"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("GRC Process Map"),
		single_column: true,
	});
	page.set_secondary_action(__("Refresh"), () => render(page));
	page.add_menu_item(__("Open Lifecycle wheel"),
		() => frappe.set_route("grc-lifecycle"));
	page.add_menu_item(__("Framework maps"),
		() => frappe.set_route("grc-framework-maps"));
	render(page);
};

const LANES = [
	{ key: 1, label: "Client & Engagement", tint: "#eaf2fb", border: "#3b6fb5" },
	{ key: 2, label: "Risk & Assessment", tint: "#eaf6ec", border: "#3d7a4a" },
	{ key: 3, label: "Controls, Policies & Evidence", tint: "#fdf6e3", border: "#c98a2d" },
	{ key: 4, label: "Audit & Remediation", tint: "#f1ecfa", border: "#6f4fb0" },
	{ key: 5, label: "Governance & Reporting", tint: "#fdeeee", border: "#b04a4a" },
];

// gate: shown as a ⚠ badge with a hover/focus tooltip
const NODES = [
	{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
	{ id: "s1", lane: 1, row: 2, kind: "step", num: 1, title: "Client Profile",
		desc: "Country, sector and frameworks — seeds the right control catalogs",
		links: [["Client Profile", "GRC Client Profile"]] },
	{ id: "s2", lane: 1, row: 3, kind: "step", num: 2, title: "Engagement",
		desc: "Scope, phase checklist, decision log",
		links: [["Engagement", "GRC Engagement"]] },
	{ id: "s3", lane: 1, row: 4, kind: "step", num: 3, title: "Project Plan",
		desc: "Generate tasks from a plan template",
		gate: "Needs an active Engagement — plans and tasks hang off it.",
		links: [["Project Plan", "GRC Project Plan"], ["Plan Template", "GRC Plan Template"]] },
	{ id: "s4", lane: 2, row: 5, kind: "step", num: 4, title: "Asset Inventory",
		desc: "Classify assets, assign owners",
		links: [["Asset Inventory", "GRC Asset Inventory"]] },
	{ id: "s5", lane: 2, row: 6, kind: "step", num: 5, title: "Risk Register",
		desc: "Identify, score, assign risk owners",
		gate: "Link risks to inventoried assets so exposure and coverage roll up correctly.",
		links: [["Risk Register", "GRC Risk Register"]] },
	{ id: "d1", lane: 2, row: 7, kind: "decision", title: "Above risk\nappetite?" },
	{ id: "s6", lane: 2, row: 8, kind: "step", num: 6, title: "Risk Treatment",
		desc: "Treatment actions and plans until residual risk is acceptable",
		gate: "Every above-appetite risk needs a treatment action with an owner and due date.",
		links: [["Treatment Action", "GRC Risk Treatment Action"],
			["Action Plan", "GRC Action Plan"]] },
	{ id: "s7", lane: 2, row: 9, kind: "step", num: 7, title: "Assessments & Gap Analysis",
		desc: "Framework maturity runs, weighted scoring",
		links: [["Assessment Run", "GRC Assessment Run"],
			["Maturity Assessment", "GRC Maturity Assessment"]] },
	{ id: "s8", lane: 3, row: 10, kind: "step", num: 8, title: "Controls & Policies",
		desc: "Map gaps to controls; author and publish policies",
		links: [["Control", "GRC Control"], ["Policy", "GRC Policy"]] },
	{ id: "s9", lane: 3, row: 11, kind: "step", num: 9, title: "Evidence Collection",
		desc: "Manual upload or automated fetch via connectors",
		gate: "Evidence attaches to mapped controls — map controls first (step 8).",
		links: [["Evidence Run", "GRC Evidence Run"],
			["Evidence Connector", "GRC Evidence Connector"]] },
	{ id: "d2", lane: 3, row: 12, kind: "decision", title: "Control effective,\nevidence sufficient?" },
	{ id: "s10", lane: 4, row: 13, kind: "step", num: 10, title: "Audit Plan",
		desc: "Annual programme, scope and schedule",
		links: [["Audit Plan", "GRC Audit Plan"]] },
	{ id: "s11", lane: 4, row: 14, kind: "step", num: 11, title: "Audit Execution",
		desc: "Workpapers, ITGC and IT audit programs",
		links: [["Workpaper", "GRC Audit Workpaper"],
			["IT Audit Program", "GRC IT Audit Program"]] },
	{ id: "s12", lane: 4, row: 15, kind: "step", num: 12, title: "Audit Findings",
		desc: "Workflow-controlled from draft to closure",
		gate: "Findings arise from executed workpapers and carry their own approval workflow.",
		links: [["Audit Finding", "GRC Audit Finding"]] },
	{ id: "d3", lane: 4, row: 16, kind: "decision", title: "Open\nfindings?" },
	{ id: "s13", lane: 4, row: 17, kind: "step", num: 13, title: "Remediation",
		desc: "Track due dates, escalation and verification",
		gate: "Every finding needs an owner and a due date; closure requires verification.",
		links: [["Remediation Action", "GRC Remediation Action"]] },
	{ id: "s14", lane: 4, row: 18, kind: "step", num: 14, title: "Exceptions & Acceptance",
		desc: "Where remediation is not feasible — time-bound and approved",
		gate: "Exceptions follow their own approval workflow and must carry an expiry.",
		links: [["Exception", "GRC Exception"],
			["Risk Acceptance", "GRC Risk Acceptance"]] },
	{ id: "s15", lane: 5, row: 19, kind: "step", num: 15, title: "KPIs & KRIs",
		desc: "Measure programme health and risk indicators",
		links: [["KPI", "GRC KPI"], ["KRI", "GRC KRI"]] },
	{ id: "s16", lane: 5, row: 20, kind: "step", num: 16, title: "Board & Regulator Reporting",
		desc: "Compliance score, KRI status, board pack",
		gate: "Pulls live KPI/KRI values and assessment scores — keep steps 7 and 15 current.",
		links: [["Board Report", "GRC Board Report"]] },
	{ id: "s17", lane: 5, row: 21, kind: "step", num: 17, title: "Periodic Review",
		desc: "Calendar-driven reviews reopen register items",
		links: [["Review Calendar", "GRC NCA ECC Review Calendar"]] },
	{ id: "end", lane: 5, row: 22, kind: "end", title: "Continuous cycle" },
];

const EDGES = [
	["start", "s1", {}],
	["s1", "s2", {}],
	["s2", "s3", {}],
	["s3", "s4", { route: "elbow" }],
	["s4", "s5", {}],
	["s5", "d1", {}],
	["d1", "s6", { label: "Yes — treat" }],
	["d1", "s7", { label: "No — monitor", route: "loop", dashed: 1 }],
	["s6", "s7", {}],
	["s7", "s8", { route: "elbow" }],
	["s8", "s9", {}],
	["s9", "d2", {}],
	["d2", "s8", { label: "No — strengthen", route: "loop", dashed: 1 }],
	["d2", "s10", { label: "Yes", route: "elbow" }],
	["s10", "s11", {}],
	["s11", "s12", {}],
	["s12", "d3", {}],
	["d3", "s13", { label: "Yes" }],
	["d3", "s15", { label: "No", route: "elbow" }],
	["s13", "s9", { label: "re-test evidence", route: "loop", dashed: 1 }],
	["d3", "s14", { label: "cannot remediate", route: "loop", dashed: 1 }],
	["s13", "s15", { route: "elbow" }],
	["s15", "s16", {}],
	["s16", "s17", {}],
	["s17", "s5", { label: "review reopens register", route: "loop", dashed: 1 }],
	["s17", "end", {}],
];

function slug(dt) {
	return frappe.router.slug(dt);
}

function node_html(n, lane) {
	if (n.kind === "start" || n.kind === "end") {
		const bg = n.kind === "start" ? "#2e7d4f" : "#b04a4a";
		return `<div class="gpm-node gpm-pill" id="gpm-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row};background:${bg}">${frappe.utils.escape_html(__(n.title))}</div>`;
	}
	if (n.kind === "decision") {
		return `<div class="gpm-node gpm-decision-wrap" id="gpm-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row}">
			<div class="gpm-decision" style="border-color:${lane.border}">
				<span>${frappe.utils.escape_html(__(n.title)).replace(/\n/g, "<br>")}</span>
			</div></div>`;
	}
	const links = (n.links || []).map(([label, dt]) => {
		const s = slug(dt);
		return `<span class="gpm-chip">
			<a class="gpm-open" href="/app/${s}" title="${__("Open list")}">${frappe.utils.escape_html(__(label))}</a>
			<a class="gpm-new" href="/app/${s}/new" title="${__("Create new")}">＋</a>
		</span>`;
	}).join("");
	const gate = n.gate
		? `<span class="gpm-gate" tabindex="0">⚠<span class="gpm-tip">${frappe.utils.escape_html(__(n.gate))}</span></span>`
		: "";
	return `<div class="gpm-node gpm-step" id="gpm-${n.id}"
		style="grid-column:${n.lane};grid-row:${n.row};border-color:${lane.border};background:#fff">
		<div class="gpm-step-title">
			<span class="gpm-num" style="background:${lane.border}">${n.num}</span>
			${frappe.utils.escape_html(__(n.title))}${gate}
		</div>
		<div class="gpm-step-desc">${frappe.utils.escape_html(__(n.desc || ""))}</div>
		<div class="gpm-links">${links}</div>
	</div>`;
}

function render(page) {
	const lanes_head = LANES.map(l =>
		`<div class="gpm-lane-head" style="background:${l.tint};border-top:4px solid ${l.border}">
			${frappe.utils.escape_html(__(l.label))}</div>`).join("");
	const nodes = NODES.map(n => node_html(n, LANES[n.lane - 1])).join("");
	const lane_bgs = LANES.map(l =>
		`<div class="gpm-lane-bg" style="grid-column:${l.key};background:${l.tint}55"></div>`).join("");

	$(page.body).html(`
		<style>
			.gpm-wrap { padding: 8px 4px 40px; overflow-x: auto; }
			.gpm-heads, .gpm-grid { display: grid;
				grid-template-columns: repeat(5, minmax(215px, 1fr)); gap: 0 14px;
				min-width: 1150px; }
			.gpm-lane-head { padding: 10px 8px; text-align: center; font-weight: 700;
				border-radius: 8px 8px 0 0; font-size: 13px; position: sticky; top: 0; z-index: 3; }
			.gpm-grid { position: relative; grid-auto-rows: minmax(56px, auto);
				row-gap: 32px; padding: 26px 0 10px; }
			.gpm-lane-bg { grid-row: 1 / 23; border-radius: 0 0 8px 8px; }
			.gpm-node { position: relative; z-index: 2; align-self: center;
				justify-self: center; width: 92%; }
			.gpm-step { border: 2px solid; border-radius: 10px; padding: 8px 10px;
				box-shadow: 0 1px 3px rgba(0,0,0,.08); }
			.gpm-step-title { font-weight: 700; font-size: 12.5px; display: flex;
				gap: 6px; align-items: center; flex-wrap: wrap; }
			.gpm-num { color: #fff; border-radius: 50%; min-width: 20px; height: 20px;
				display: inline-flex; align-items: center; justify-content: center;
				font-size: 11px; }
			.gpm-step-desc { font-size: 11px; color: var(--text-muted); margin: 4px 0 6px; }
			.gpm-links { display: flex; flex-wrap: wrap; gap: 4px; }
			.gpm-chip { display: inline-flex; border: 1px solid var(--gray-300);
				border-radius: 999px; overflow: hidden; font-size: 11px;
				background: var(--gray-50); }
			.gpm-chip a { padding: 2px 8px; text-decoration: none; }
			.gpm-chip a.gpm-new { border-left: 1px solid var(--gray-300); font-weight: 700; }
			.gpm-chip a:hover { background: var(--gray-200); }
			.gpm-pill { color: #fff; font-weight: 700; text-align: center;
				border-radius: 999px; padding: 8px 0; width: 150px; }
			.gpm-decision-wrap { display: flex; justify-content: center; }
			.gpm-decision { width: 122px; height: 122px; background: #fff; border: 2px solid;
				transform: rotate(45deg); border-radius: 12px; display: flex;
				align-items: center; justify-content: center;
				box-shadow: 0 1px 3px rgba(0,0,0,.08); }
			.gpm-decision span { transform: rotate(-45deg); font-size: 11px;
				font-weight: 700; text-align: center; line-height: 1.25; }
			.gpm-svg { position: absolute; inset: 0; width: 100%; height: 100%;
				z-index: 1; pointer-events: none; }
			.gpm-edge-label { font-size: 10px; font-weight: 700; fill: #555;
				paint-order: stroke; stroke: #fff; stroke-width: 3px; }
			.gpm-legend { font-size: 12px; color: var(--text-muted); margin: 6px 2px 12px; }
			.gpm-gate { cursor: help; position: relative; outline: none; font-size: 12px; }
			.gpm-tip { display: none; position: absolute; left: 50%;
				bottom: calc(100% + 8px); transform: translateX(-50%); width: 240px;
				background: #1f2937; color: #fff; font-size: 11px; font-weight: 400;
				line-height: 1.45; padding: 8px 10px; border-radius: 8px;
				box-shadow: 0 4px 14px rgba(0,0,0,.25); z-index: 50;
				white-space: normal; text-align: left; pointer-events: none; }
			.gpm-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
				transform: translateX(-50%); border: 6px solid transparent;
				border-top-color: #1f2937; }
			.gpm-gate:hover .gpm-tip, .gpm-gate:focus .gpm-tip { display: block; }
		</style>
		<div class="gpm-wrap">
			<div class="gpm-legend">${__("Follow the arrows top to bottom. On any step: click the name to open the list, or ＋ to create the transaction. Hover ⚠ for the gate that applies. Dashed arrows are loops / alternate paths.")}</div>
			<div class="gpm-heads">${lanes_head}</div>
			<div class="gpm-grid" id="gpm-grid">
				${lane_bgs}
				<svg class="gpm-svg" id="gpm-svg">
					<defs><marker id="gpm-arrow" viewBox="0 0 10 10" refX="9" refY="5"
						markerWidth="7" markerHeight="7" orient="auto-start-reverse">
						<path d="M 0 0 L 10 5 L 0 10 z" fill="#4a5568"></path>
					</marker></defs>
				</svg>
				${nodes}
			</div>
		</div>`);

	const draw = () => draw_edges();
	setTimeout(draw, 60);
	$(window).off("resize.gpm").on("resize.gpm", frappe.utils.debounce(draw, 150));
}

function draw_edges() {
	const grid = document.getElementById("gpm-grid");
	const svg = document.getElementById("gpm-svg");
	if (!grid || !svg) return;
	const gb = grid.getBoundingClientRect();
	svg.setAttribute("width", grid.scrollWidth);
	svg.setAttribute("height", grid.scrollHeight);
	[...svg.querySelectorAll("path,text")].forEach(el => el.remove());

	const box = id => {
		const el = document.getElementById("gpm-" + id);
		if (!el) return null;
		const r = el.getBoundingClientRect();
		return { l: r.left - gb.left, t: r.top - gb.top, w: r.width, h: r.height,
			cx: r.left - gb.left + r.width / 2, cy: r.top - gb.top + r.height / 2 };
	};
	const P = (d, dashed) => {
		const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
		p.setAttribute("d", d);
		p.setAttribute("fill", "none");
		p.setAttribute("stroke", "#4a5568");
		p.setAttribute("stroke-width", "2");
		if (dashed) p.setAttribute("stroke-dasharray", "6 4");
		p.setAttribute("marker-end", "url(#gpm-arrow)");
		svg.appendChild(p);
	};
	const T = (x, y, text) => {
		const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
		t.setAttribute("x", x); t.setAttribute("y", y);
		t.setAttribute("class", "gpm-edge-label");
		t.textContent = text;
		svg.appendChild(t);
	};

	EDGES.forEach(([from, to, opt]) => {
		const a = box(from), b = box(to);
		if (!a || !b) return;
		const o = opt || {};
		let d, lx, ly;
		if (o.route === "loop") {
			const gx = Math.min(a.l, b.l) - 22;
			d = `M ${a.l} ${a.cy} H ${gx} V ${b.cy} H ${b.l}`;
			lx = gx + 6; ly = Math.min(a.cy, b.cy) - 8;
		} else if (o.route === "elbow" || Math.abs(a.cx - b.cx) > 40) {
			if (b.t > a.t + a.h) {
				const midy = a.t + a.h + Math.max(14, (b.t - a.t - a.h) / 2);
				d = `M ${a.cx} ${a.t + a.h} V ${midy} H ${b.cx} V ${b.t}`;
				lx = a.cx + 8; ly = a.t + a.h + 14;
			} else {
				const fromx = b.cx > a.cx ? a.l + a.w : a.l;
				const tox = b.cx > a.cx ? b.l : b.l + b.w;
				d = `M ${fromx} ${a.cy} H ${(fromx + tox) / 2} V ${b.cy} H ${tox}`;
				lx = (fromx + tox) / 2 + 6; ly = a.cy - 6;
			}
		} else {
			d = `M ${a.cx} ${a.t + a.h} V ${b.t}`;
			lx = a.cx + 8; ly = a.t + a.h + 14;
		}
		P(d, o.dashed);
		if (o.label) T(lx, ly, __(o.label));
	});
}
