# Copyright (c) 2026, Neotec Integrated Solutions
"""
The graphical pathway board rendered at /app/grc-pathway.

Shipped as a Frappe **Custom HTML Block** and injected as the first content
block of the GRC Pathway workspace. Seeding is idempotent and self-healing:
`bench migrate` re-imports the workspace JSON from disk, then `after_migrate`
puts the board block back at the top.

If the running Frappe build has no Custom HTML Block doctype, the block is
removed from the workspace instead of left behind as a blank gap.
"""

from __future__ import annotations

import json

import frappe

BLOCK_NAME = "GRC Pathway Board"
WORKSPACE = "GRC Pathway"

# --------------------------------------------------------------------------
# Markup
# --------------------------------------------------------------------------

BOARD_HTML = """
<div class="grc-pathway" data-grc-pathway data-theme="ocean" data-colour="on">
	<div class="gp-head">
		<div class="gp-title">
			<span class="gp-dot"></span>
			<div>
				<h3>Engagement Pathway</h3>
				<p class="gp-sub">Client onboarding through to audit-ready reporting</p>
			</div>
		</div>
		<button class="gp-btn gp-cta" data-gp-console>Open console &rarr;</button>
		<div class="gp-controls">
			<select class="gp-select" data-gp-client aria-label="Filter by client">
				<option value="">All clients</option>
			</select>
			<select class="gp-select" data-gp-theme aria-label="Colour theme">
				<option value="ocean">Ocean</option>
				<option value="sunset">Sunset</option>
				<option value="forest">Forest</option>
				<option value="royal">Royal</option>
				<option value="desert">Desert</option>
				<option value="mono">Monochrome (no colour)</option>
				<option value="contrast">High contrast</option>
			</select>
			<button class="gp-btn" data-gp-refresh title="Refresh counts" aria-label="Refresh">&#8635;</button>
		</div>
	</div>

	<div class="gp-rail" data-gp-rail>
		<div class="gp-rail-fill" data-gp-rail-fill></div>
		<span class="gp-rail-label" data-gp-rail-label>Loading&hellip;</span>
	</div>

	<div class="gp-grid" data-gp-grid>
		<div class="gp-skeleton"></div>
		<div class="gp-skeleton"></div>
		<div class="gp-skeleton"></div>
		<div class="gp-skeleton"></div>
		<div class="gp-skeleton"></div>
	</div>

	<div class="gp-foot">
		<span data-gp-foot>Counts refresh on load. Click any stage to open its list.</span>
	</div>
</div>
"""

# --------------------------------------------------------------------------
# Styling — every colour comes from a theme variable so "no colour" is a
# first-class option rather than a stylesheet hack.
# --------------------------------------------------------------------------

BOARD_STYLE = """
.grc-pathway {
	--gp-radius: 12px;
	--gp-gap: 12px;
	--gp-card-bg: var(--card-bg, #fff);
	--gp-text: var(--text-color, #1f272e);
	--gp-muted: var(--text-muted, #7a8896);
	--gp-border: var(--border-color, #e2e6ea);
	font-family: var(--font-stack, inherit);
	color: var(--gp-text);
	padding: 4px 0 8px;
}

/* ---- themes ---- */
.grc-pathway[data-theme="ocean"]   { --c1:#0ea5e9; --c2:#2563eb; --c3:#6366f1; --c4:#0891b2; --c5:#0d9488; --accent:#2563eb; }
.grc-pathway[data-theme="sunset"]  { --c1:#f97316; --c2:#ef4444; --c3:#ec4899; --c4:#f59e0b; --c5:#d946ef; --accent:#ef4444; }
.grc-pathway[data-theme="forest"]  { --c1:#16a34a; --c2:#059669; --c3:#65a30d; --c4:#0d9488; --c5:#4d7c0f; --accent:#059669; }
.grc-pathway[data-theme="royal"]   { --c1:#7c3aed; --c2:#a21caf; --c3:#4f46e5; --c4:#9333ea; --c5:#c026d3; --accent:#7c3aed; }
.grc-pathway[data-theme="desert"]  { --c1:#b45309; --c2:#a16207; --c3:#ca8a04; --c4:#92400e; --c5:#78716c; --accent:#b45309; }
.grc-pathway[data-theme="mono"]    { --c1:#6b7280; --c2:#6b7280; --c3:#6b7280; --c4:#6b7280; --c5:#6b7280; --accent:#4b5563; }
.grc-pathway[data-theme="contrast"]{ --c1:#000; --c2:#000; --c3:#000; --c4:#000; --c5:#000; --accent:#000; }

.grc-pathway[data-theme="mono"] .gp-card,
.grc-pathway[data-colour="off"] .gp-card { background: var(--gp-card-bg); }
.grc-pathway[data-theme="contrast"] .gp-card { border-width: 2px; }

/* ---- header ---- */
.grc-pathway .gp-head {
	display: flex; align-items: flex-start; justify-content: space-between;
	gap: 12px; flex-wrap: wrap; margin-bottom: 14px;
}
.grc-pathway .gp-title { display: flex; align-items: center; gap: 10px; }
.grc-pathway .gp-title h3 { margin: 0; font-size: 15px; font-weight: 600; letter-spacing: -0.01em; }
.grc-pathway .gp-sub { margin: 2px 0 0; font-size: 12px; color: var(--gp-muted); }
.grc-pathway .gp-dot {
	width: 10px; height: 10px; border-radius: 50%; flex: none;
	background: linear-gradient(135deg, var(--c1), var(--c3));
	box-shadow: 0 0 0 4px color-mix(in srgb, var(--c1) 18%, transparent);
}
.grc-pathway .gp-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.grc-pathway .gp-select, .grc-pathway .gp-btn {
	font-size: 12px; padding: 5px 9px; border-radius: 7px;
	border: 1px solid var(--gp-border); background: var(--gp-card-bg);
	color: var(--gp-text); cursor: pointer; line-height: 1.4;
}
.grc-pathway .gp-btn { padding: 5px 10px; font-size: 14px; }
.grc-pathway .gp-select:focus, .grc-pathway .gp-btn:focus {
	outline: 2px solid var(--accent); outline-offset: 1px;
}

/* ---- progress rail ---- */
.grc-pathway .gp-rail {
	position: relative; height: 22px; border-radius: 11px; margin-bottom: 16px;
	background: color-mix(in srgb, var(--gp-border) 55%, transparent); overflow: hidden;
}
.grc-pathway .gp-rail-fill {
	height: 100%; width: 0%; border-radius: 11px;
	background: linear-gradient(90deg, var(--c1), var(--c2) 45%, var(--c3));
	transition: width .5s ease;
}
.grc-pathway[data-theme="mono"] .gp-rail-fill,
.grc-pathway[data-colour="off"] .gp-rail-fill { background: var(--c1); }
.grc-pathway .gp-rail-label {
	position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
	font-size: 11px; font-weight: 600; letter-spacing: .02em;
	color: var(--gp-text); mix-blend-mode: normal;
}

/* ---- stage grid ---- */
.grc-pathway .gp-grid {
	display: grid; gap: var(--gp-gap);
	grid-template-columns: repeat(5, minmax(0, 1fr));
}
@media (max-width: 1100px) { .grc-pathway .gp-grid { grid-template-columns: repeat(3, minmax(0,1fr)); } }
@media (max-width: 700px)  { .grc-pathway .gp-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }

.grc-pathway .gp-card {
	position: relative; display: block; width: 100%; text-align: left;
	border: 1px solid var(--gp-border); border-radius: var(--gp-radius);
	background: var(--gp-card-bg); padding: 12px 12px 11px; cursor: pointer;
	transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
	overflow: hidden;
}
.grc-pathway .gp-card::before {
	content: ""; position: absolute; inset: 0 0 auto 0; height: 5px;
	background: linear-gradient(90deg, var(--stage-c, var(--c1)), color-mix(in srgb, var(--stage-c, var(--c1)) 55%, #fff));
}
.grc-pathway[data-theme="mono"] .gp-card::before,
.grc-pathway[data-theme="contrast"] .gp-card::before { background: var(--stage-c, var(--c1)); }
.grc-pathway .gp-cta {
	background: linear-gradient(135deg, var(--c1), var(--c3)); color: #fff; border: 0; font-weight: 600;
}
.grc-pathway[data-theme="mono"] .gp-cta, .grc-pathway[data-theme="contrast"] .gp-cta { background: var(--c1); }
.grc-pathway .gp-count { color: var(--stage-c, var(--c1)); }
.grc-pathway .gp-step { box-shadow: 0 3px 8px color-mix(in srgb, var(--stage-c, var(--c1)) 40%, transparent); }
.grc-pathway .gp-card:hover {
	transform: translateY(-2px);
	border-color: color-mix(in srgb, var(--stage-c, var(--c1)) 45%, var(--gp-border));
	box-shadow: 0 6px 16px color-mix(in srgb, var(--stage-c, var(--c1)) 16%, transparent);
}
.grc-pathway .gp-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.grc-pathway .gp-step {
	display: inline-flex; align-items: center; justify-content: center;
	width: 20px; height: 20px; border-radius: 50%; font-size: 10px; font-weight: 700;
	color: #fff; background: var(--stage-c, var(--c1)); margin-bottom: 8px;
}
.grc-pathway[data-theme="contrast"] .gp-step { background: #000; }
.grc-pathway .gp-name { font-size: 12px; font-weight: 600; margin: 0 0 6px; line-height: 1.3; }
.grc-pathway .gp-count { font-size: 22px; font-weight: 700; line-height: 1; letter-spacing: -0.02em; }
.grc-pathway .gp-meta { font-size: 11px; color: var(--gp-muted); margin-top: 5px; min-height: 15px; }
.grc-pathway .gp-flag {
	display: inline-block; font-size: 10px; font-weight: 600; padding: 1px 6px;
	border-radius: 20px; margin-top: 6px;
	background: color-mix(in srgb, var(--stage-c, var(--c1)) 14%, transparent);
	color: var(--stage-c, var(--c1));
}
.grc-pathway[data-theme="contrast"] .gp-flag { background: #000; color: #fff; }
.grc-pathway .gp-card[data-empty="1"] { opacity: .62; }
.grc-pathway .gp-card[data-empty="1"] .gp-count { color: var(--gp-muted); }

.grc-pathway .gp-skeleton {
	height: 104px; border-radius: var(--gp-radius);
	background: linear-gradient(90deg,
		color-mix(in srgb, var(--gp-border) 40%, transparent),
		color-mix(in srgb, var(--gp-border) 75%, transparent),
		color-mix(in srgb, var(--gp-border) 40%, transparent));
	background-size: 200% 100%; animation: gp-shimmer 1.2s linear infinite;
}
@keyframes gp-shimmer { to { background-position: -200% 0; } }

.grc-pathway .gp-foot { margin-top: 12px; font-size: 11px; color: var(--gp-muted); }
.grc-pathway .gp-err { color: #b91c1c; font-size: 12px; padding: 10px 0; }
"""

# --------------------------------------------------------------------------
# Behaviour
# --------------------------------------------------------------------------

BOARD_SCRIPT = """
(function () {
	const root =
		(typeof root_element !== "undefined" && root_element) ||
		document.querySelector("[data-grc-pathway]");
	if (!root) return;

	const wrap = root.matches && root.matches("[data-grc-pathway]")
		? root
		: root.querySelector("[data-grc-pathway]");
	if (!wrap) return;

	const grid = wrap.querySelector("[data-gp-grid]");
	const railFill = wrap.querySelector("[data-gp-rail-fill]");
	const railLabel = wrap.querySelector("[data-gp-rail-label]");
	const themeSel = wrap.querySelector("[data-gp-theme]");
	const clientSel = wrap.querySelector("[data-gp-client]");
	const foot = wrap.querySelector("[data-gp-foot]");
	const LS_THEME = "grc_pathway_theme";
	const LS_CLIENT = "grc_pathway_client";

	const THEME_KEYS = {
		"Ocean": "ocean", "Sunset": "sunset", "Forest": "forest", "Royal": "royal",
		"Desert": "desert", "Monochrome (No Colour)": "mono", "High Contrast": "contrast"
	};

	let settings = { allow_user_override: 1, show_counts: 1, show_progress_rail: 1, compact_mode: 0 };

	function applyTheme(key) {
		wrap.setAttribute("data-theme", key);
		wrap.setAttribute("data-colour", key === "mono" ? "off" : "on");
		if (themeSel) themeSel.value = key;
	}

	function esc(s) {
		return String(s == null ? "" : s).replace(/[&<>"']/g,
			c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
	}

	function render(data) {
		const stages = data.stages || [];
		if (!stages.length) {
			grid.innerHTML = '<div class="gp-err">No pathway stages available. Is AlphaX GRC installed?</div>';
			return;
		}
		grid.innerHTML = stages.map((s, i) => {
			const colour = "var(--c" + ((i % 5) + 1) + ")";
			const count = settings.show_counts ? esc(s.count) : "&mdash;";
			const meta = s.meta ? '<div class="gp-meta">' + esc(s.meta) + "</div>" : '<div class="gp-meta"></div>';
			const flag = s.flag ? '<span class="gp-flag">' + esc(s.flag) + "</span>" : "";
			return (
				'<button class="gp-card" style="--stage-c:' + colour + '"' +
				' data-empty="' + (s.count ? 0 : 1) + '"' +
				' data-route="' + esc(s.route_type) + '" data-target="' + esc(s.route_to) + '"' +
				' title="' + esc(s.hint || s.label) + '">' +
				'<span class="gp-step">' + (i + 1) + "</span>" +
				'<p class="gp-name">' + esc(s.label) + "</p>" +
				'<div class="gp-count">' + count + "</div>" +
				meta + flag +
				"</button>"
			);
		}).join("");

		grid.querySelectorAll(".gp-card").forEach(card => {
			card.addEventListener("click", () => {
				const type = card.getAttribute("data-route");
				const target = card.getAttribute("data-target");
				if (!target) return;
				const client = clientSel && clientSel.value;
				if (type === "report") {
					frappe.set_route("query-report", target);
				} else if (client) {
					frappe.set_route("List", target, { client: client });
				} else {
					frappe.set_route("List", target);
				}
			});
		});

		if (settings.show_progress_rail) {
			const done = stages.filter(s => s.count > 0).length;
			const pct = Math.round((done / stages.length) * 100);
			railFill.style.width = pct + "%";
			railLabel.textContent = done + " of " + stages.length + " stages started \\u00b7 " + pct + "%";
			wrap.querySelector("[data-gp-rail]").style.display = "";
		} else {
			wrap.querySelector("[data-gp-rail]").style.display = "none";
		}

		if (foot && data.as_of) {
			foot.textContent = "Counts as of " + data.as_of + " \\u00b7 click any stage to open its list";
		}
	}

	function load() {
		grid.innerHTML = '<div class="gp-skeleton"></div>'.repeat(5);
		frappe.call({
			method: "alphax_grc.pathway.api.get_pathway_stats",
			args: { client: (clientSel && clientSel.value) || "" },
			callback: r => {
				if (!r || !r.message) return;
				const data = r.message;
				settings = Object.assign(settings, data.settings || {});
				if (clientSel && !clientSel.dataset.filled) {
					(data.clients || []).forEach(c => {
						const o = document.createElement("option");
						o.value = c.value; o.textContent = c.label;
						clientSel.appendChild(o);
					});
					clientSel.dataset.filled = "1";
					const saved = localStorage.getItem(LS_CLIENT);
					if (saved) clientSel.value = saved;
					else if (data.default_client) clientSel.value = data.default_client;
				}
				const stored = settings.allow_user_override ? localStorage.getItem(LS_THEME) : null;
				applyTheme(stored || THEME_KEYS[data.theme] || "ocean");
				if (themeSel) themeSel.disabled = !settings.allow_user_override;
				render(data);
			},
			error: () => {
				grid.innerHTML = '<div class="gp-err">Could not load pathway counts. Check the error log.</div>';
			}
		});
	}

	if (themeSel) {
		themeSel.addEventListener("change", () => {
			applyTheme(themeSel.value);
			try { localStorage.setItem(LS_THEME, themeSel.value); } catch (e) { /* private mode */ }
		});
	}
	if (clientSel) {
		clientSel.addEventListener("change", () => {
			try { localStorage.setItem(LS_CLIENT, clientSel.value); } catch (e) { /* private mode */ }
			load();
		});
	}
	const refresh = wrap.querySelector("[data-gp-refresh]");
	if (refresh) refresh.addEventListener("click", load);
	const cta = wrap.querySelector("[data-gp-console]");
	if (cta) cta.addEventListener("click", () => frappe.set_route("grc-pathway-console"));

	load();
})();
"""


def _log_title(text: str) -> str:
	return text[:140]


def seed_pathway_board():
	"""Create/refresh the Custom HTML Block, then wire it into the workspace."""
	supported = bool(frappe.db.exists("DocType", "Custom HTML Block"))

	if supported:
		try:
			_upsert_block()
		except Exception:
			supported = False
			frappe.log_error(
				title=_log_title("GRC Pathway board: block creation failed"),
				message=frappe.get_traceback(),
			)

	_wire_workspace(include=supported)


def _upsert_block():
	if frappe.db.exists("Custom HTML Block", BLOCK_NAME):
		block = frappe.get_doc("Custom HTML Block", BLOCK_NAME)
	else:
		block = frappe.new_doc("Custom HTML Block")
		block.name = BLOCK_NAME
		block.flags.name_set = True

	meta = frappe.get_meta("Custom HTML Block")
	values = {"html": BOARD_HTML, "style": BOARD_STYLE, "script": BOARD_SCRIPT, "public": 1}
	for fieldname, value in values.items():
		if meta.get_field(fieldname):
			block.set(fieldname, value)

	block.flags.ignore_permissions = True
	block.flags.ignore_mandatory = True
	if block.is_new():
		block.insert(ignore_permissions=True)
	else:
		block.save(ignore_permissions=True)


def _wire_workspace(include: bool):
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	ws = frappe.get_doc("Workspace", WORKSPACE)
	try:
		content = json.loads(ws.content or "[]")
	except Exception:
		return

	content = [
		b for b in content
		if not (b.get("type") == "custom_block"
				and (b.get("data") or {}).get("custom_block_name") == BLOCK_NAME)
	]

	if include:
		block = {
			"id": "grcPathwayBoard",
			"type": "custom_block",
			"data": {"custom_block_name": BLOCK_NAME, "col": 12},
		}
		# Sits directly under the page header, above the onboarding walkthrough.
		insert_at = 1 if content and content[0].get("type") == "header" else 0
		content.insert(insert_at, block)

	new_content = json.dumps(content)
	if new_content != (ws.content or ""):
		ws.db_set("content", new_content, update_modified=False)
