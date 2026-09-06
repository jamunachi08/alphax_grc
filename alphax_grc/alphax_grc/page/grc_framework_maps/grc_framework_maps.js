// AlphaX GRC — Framework Process Maps
// Index of every process flow + one clickable swimlane map per framework.
// Config-driven: each framework defines lanes, nodes and edges; one shared
// renderer draws them all. Navigate with the in-page hash (#fw=nca).

frappe.pages["grc-framework-maps"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Framework Process Maps"),
		single_column: true,
	});
	page.set_secondary_action(__("All frameworks"), () => go(""));
	page.add_menu_item(__("General Process Map"), () => frappe.set_route("grc-process-map"));
	page.add_menu_item(__("Lifecycle wheel"), () => frappe.set_route("grc-lifecycle"));
	wrapper.__fw_page = page;
	route(page);
	$(window).off("hashchange.fwm").on("hashchange.fwm", () => {
		if (frappe.get_route()[0] === "grc-framework-maps") route(page);
	});
};

function go(key) {
	location.hash = key ? "fw=" + key : "";
}

function current_key() {
	const m = location.hash.match(/fw=([a-z0-9_]+)/);
	return m ? m[1] : "";
}

function route(page) {
	const key = current_key();
	if (key && FRAMEWORKS[key]) render_flow(page, key);
	else render_index(page);
}

// ---------------------------------------------------------------------------
// Framework configurations. Lane sets are per-framework (4 lanes each).
// Node: {id, lane, row, kind, num, title, desc, gate, links:[[label, DocType]]}
// Edge: [from, to, {label, route: v|elbow|loop, dashed}]
// ---------------------------------------------------------------------------
const L4 = (a, b, c, d) => [
	{ key: 1, label: a, tint: "#eaf2fb", border: "#3b6fb5" },
	{ key: 2, label: b, tint: "#eaf6ec", border: "#3d7a4a" },
	{ key: 3, label: c, tint: "#fdf6e3", border: "#c98a2d" },
	{ key: 4, label: d, tint: "#fdeeee", border: "#b04a4a" },
];

const FRAMEWORKS = {
	nca: {
		title: "NCA ECC-2:2024", tag: "Saudi Essential Cybersecurity Controls",
		icon: "🇸🇦", dashboards: [["ECC-2 Dashboard", "grc-ecc2-dashboard"],
			["NCA Templates", "grc-nca-templates"]],
		lanes: L4("Scope & Catalog", "Controls & Documents", "Assess", "Remediate & Review"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Engagement & Scope",
				desc: "Client, sector, applicability",
				links: [["Engagement", "GRC Engagement"], ["Client Profile", "GRC Client Profile"]] },
			{ id: "n2", lane: 1, row: 3, kind: "step", num: 2, title: "ECC Catalog Baseline",
				desc: "Seeded control catalog per scope",
				gate: "The catalog seeds sector-appropriate controls — set scope before implementing.",
				links: [["ECC-2 Catalog", "GRC NCA ECC2 Catalog"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "Implement ECC Controls",
				desc: "Ownership, status, maturity per control",
				links: [["ECC Control", "GRC NCA ECC Control"]] },
			{ id: "n4", lane: 2, row: 5, kind: "step", num: 4, title: "Policies & Templates",
				desc: "Author from the NCA libraries",
				links: [["Policy Library", "GRC NCA Policy Library"],
					["Procedures", "GRC NCA Procedure Library"],
					["Standards", "GRC NCA Standard Library"],
					["Forms", "GRC NCA Form Library"]] },
			{ id: "n5", lane: 2, row: 6, kind: "step", num: 5, title: "Control Documents & Evidence",
				desc: "Attach implementation evidence",
				gate: "Each control needs its supporting document/evidence before assessment scores it.",
				links: [["ECC Document", "GRC NCA ECC Document"]] },
			{ id: "n6", lane: 2, row: 7, kind: "step", num: 6, title: "Tool Mapping",
				desc: "Map controls to deployed tools",
				links: [["Tool Mapping", "GRC NCA ECC Tool Mapping"]] },
			{ id: "n7", lane: 3, row: 8, kind: "step", num: 7, title: "Compliance Assessment",
				desc: "Run and score against ECC-2",
				links: [["Assessment Run", "GRC Assessment Run"]] },
			{ id: "d1", lane: 3, row: 9, kind: "decision", title: "Compliant?" },
			{ id: "n8", lane: 4, row: 10, kind: "step", num: 8, title: "Remediation",
				desc: "Close gaps, re-implement",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n9", lane: 4, row: 11, kind: "step", num: 9, title: "Periodic Review",
				desc: "Calendar-driven re-assessment",
				links: [["Review Calendar", "GRC NCA ECC Review Calendar"]] },
			{ id: "end", lane: 4, row: 12, kind: "end", title: "Maintained" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", {}], ["n2", "n3", { route: "elbow" }],
			["n3", "n4", {}], ["n4", "n5", {}],
			["n5", "n6", { label: "map tools", dashed: 1 }],
			["n5", "n7", { route: "elbow" }], ["n7", "d1", {}],
			["d1", "n8", { label: "No — gaps", route: "elbow" }],
			["n8", "n3", { label: "re-implement", route: "loop", dashed: 1 }],
			["d1", "n9", { label: "Yes", route: "elbow" }],
			["n9", "n7", { label: "periodic", route: "loop", dashed: 1 }],
			["n9", "end", {}],
		],
	},

	sama: {
		title: "SAMA CSF", tag: "Saudi Central Bank Cybersecurity Framework",
		icon: "🏦", dashboards: [],
		lanes: L4("Scope", "Assess & Score", "Deliverables", "Report"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Engagement & Scope",
				desc: "Entity, domains in scope",
				links: [["Engagement", "GRC Engagement"]] },
			{ id: "n2", lane: 2, row: 3, kind: "step", num: 2, title: "SAMA Assessment",
				desc: "Score maturity per subdomain",
				gate: "Every in-scope subdomain must be scored with rationale before deliverables.",
				links: [["SAMA Assessment", "GRC SAMA Assessment"],
					["Subdomains", "GRC SAMA Subdomain"]] },
			{ id: "d1", lane: 2, row: 4, kind: "decision", title: "Below target\nmaturity?" },
			{ id: "n3", lane: 2, row: 5, kind: "step", num: 3, title: "Remediation",
				desc: "Uplift actions to target level",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n4", lane: 2, row: 6, kind: "step", num: 4, title: "Waivers",
				desc: "Where compliance is not feasible",
				gate: "Waivers are time-bound and approved — never open-ended.",
				links: [["SAMA Waiver", "GRC SAMA Waiver"]] },
			{ id: "n5", lane: 3, row: 7, kind: "step", num: 5, title: "Deliverables Pack",
				desc: "Evidence and submission set",
				links: [["Deliverable", "GRC SAMA Deliverable"]] },
			{ id: "n6", lane: 4, row: 8, kind: "step", num: 6, title: "Board & Regulator Report",
				desc: "Maturity position and plan",
				links: [["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 9, kind: "end", title: "Submitted" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", { route: "elbow" }], ["n2", "d1", {}],
			["d1", "n3", { label: "Yes — uplift" }],
			["n3", "n2", { label: "re-score", route: "loop", dashed: 1 }],
			["d1", "n4", { label: "cannot comply", route: "loop", dashed: 1 }],
			["d1", "n5", { label: "No — at target", route: "elbow" }],
			["n3", "n5", { route: "elbow" }], ["n4", "n5", { route: "elbow", dashed: 1 }],
			["n5", "n6", { route: "elbow" }], ["n6", "end", {}],
		],
	},

	aramco: {
		title: "Aramco CCC (SACS-002)", tag: "Third-party cybersecurity certification",
		icon: "🛢", dashboards: [["Aramco CCC Dashboard", "grc-aramco-ccc"]],
		lanes: L4("Third Party & Engagement", "Controls", "Assess & Audit", "Certify & Notify"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Third-Party Profile",
				desc: "Classification drives applicable controls",
				links: [["Third Party Profile", "GRC Aramco Third Party Profile"]] },
			{ id: "n2", lane: 1, row: 3, kind: "step", num: 2, title: "CCC Engagement",
				desc: "Scope and timeline",
				links: [["CCC Engagement", "GRC Aramco CCC Engagement"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "SACS-002 Controls",
				desc: "Implement per classification",
				links: [["SACS-002 Control", "GRC Aramco SACS002 Control"]] },
			{ id: "n4", lane: 3, row: 5, kind: "step", num: 4, title: "Control Assessment",
				desc: "Self-assess with evidence",
				links: [["Control Assessment", "GRC Aramco Control Assessment"]] },
			{ id: "d1", lane: 3, row: 6, kind: "decision", title: "All controls\npass?" },
			{ id: "n5", lane: 3, row: 7, kind: "step", num: 5, title: "Authorized Audit Firm",
				desc: "Independent verification",
				gate: "Certification requires an Aramco-authorized audit firm's verification.",
				links: [["Audit Firm", "GRC Aramco Audit Firm"]] },
			{ id: "n6", lane: 4, row: 8, kind: "step", num: 6, title: "Certificate",
				desc: "Track number and expiry",
				gate: "Certificates expire — renewal restarts the assessment before the expiry date.",
				links: [["Certificate", "GRC Aramco Certificate"]] },
			{ id: "n7", lane: 4, row: 9, kind: "step", num: 7, title: "Incident Notification",
				desc: "Ongoing obligation while certified",
				links: [["Incident Notification", "GRC Aramco Incident Notification"]] },
			{ id: "end", lane: 4, row: 10, kind: "end", title: "Certified" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", {}], ["n2", "n3", { route: "elbow" }],
			["n3", "n4", { route: "elbow" }], ["n4", "d1", {}],
			["d1", "n3", { label: "No — remediate", route: "loop", dashed: 1 }],
			["d1", "n5", { label: "Yes" }], ["n5", "n6", { route: "elbow" }],
			["n6", "n7", { label: "ongoing", dashed: 1 }], ["n6", "end", { route: "elbow" }],
		],
	},

	iso27001: {
		title: "ISO/IEC 27001", tag: "Information Security Management System",
		icon: "🔐", dashboards: [],
		lanes: L4("Scope & SoA", "Controls & Documents", "Audit", "Certify"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Engagement & ISMS Scope",
				desc: "Boundaries and interested parties",
				links: [["Engagement", "GRC Engagement"]] },
			{ id: "n2", lane: 1, row: 3, kind: "step", num: 2, title: "Statement of Applicability",
				desc: "Include / exclude with justification",
				gate: "Every Annex A control needs an applicability decision with justification.",
				links: [["SoA", "GRC ISO27001 SOA"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "Controls",
				desc: "Implement applicable controls",
				links: [["Control", "GRC Control"], ["Control Library", "GRC Control Library"]] },
			{ id: "n4", lane: 2, row: 5, kind: "step", num: 4, title: "ISMS Documents & Policies",
				desc: "Mandatory documentation set",
				links: [["ISMS Document", "GRC ISO27001 Document"], ["Policy", "GRC Policy"]] },
			{ id: "n5", lane: 2, row: 6, kind: "step", num: 5, title: "Evidence",
				desc: "Operating-effectiveness evidence",
				links: [["Evidence Run", "GRC Evidence Run"]] },
			{ id: "n6", lane: 3, row: 7, kind: "step", num: 6, title: "Internal Audit",
				desc: "Plan, execute, raise findings",
				links: [["Audit Plan", "GRC Audit Plan"], ["Audit Finding", "GRC Audit Finding"]] },
			{ id: "d1", lane: 3, row: 8, kind: "decision", title: "Nonconformities?" },
			{ id: "n7", lane: 4, row: 9, kind: "step", num: 7, title: "Corrective Actions",
				desc: "Close NCs before certification",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n8", lane: 4, row: 10, kind: "step", num: 8, title: "Certification Readiness",
				desc: "Maturity check for Stage 1/2",
				links: [["Maturity Assessment", "GRC Maturity Assessment"]] },
			{ id: "end", lane: 4, row: 11, kind: "end", title: "Certified ISMS" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", {}], ["n2", "n3", { route: "elbow" }],
			["n3", "n4", {}], ["n4", "n5", {}], ["n5", "n6", { route: "elbow" }],
			["n6", "d1", {}],
			["d1", "n7", { label: "Yes", route: "elbow" }],
			["n7", "n3", { label: "correct & re-audit", route: "loop", dashed: 1 }],
			["d1", "n8", { label: "No", route: "elbow" }], ["n8", "end", {}],
		],
	},

	iso22301: {
		title: "ISO 22301 BCMS", tag: "Business continuity management",
		icon: "🔄", dashboards: [["BCMS Dashboard", "grc-iso22301-dashboard"]],
		lanes: L4("Analyse", "Plan & Control", "Exercise", "Review"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Business Impact Analysis",
				desc: "Critical processes, RTO/RPO, dependencies",
				links: [["BIA", "GRC Business Impact Analysis"]] },
			{ id: "n2", lane: 1, row: 3, kind: "step", num: 2, title: "Continuity Risks",
				desc: "Register continuity-specific risks",
				links: [["Risk Register", "GRC Risk Register"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "BC Controls",
				desc: "ISO 22301 control implementation",
				links: [["ISO22301 Control", "GRC ISO22301 Control"]] },
			{ id: "n4", lane: 2, row: 5, kind: "step", num: 4, title: "DR / BC Plans",
				desc: "Recovery strategies and runbooks",
				gate: "Every critical process from the BIA needs a plan covering its RTO/RPO.",
				links: [["DR Plan", "GRC DR Plan"]] },
			{ id: "n5", lane: 3, row: 6, kind: "step", num: 5, title: "Exercise & Test",
				desc: "Tabletop / failover exercises",
				links: [["DR Plan", "GRC DR Plan"]] },
			{ id: "d1", lane: 3, row: 7, kind: "decision", title: "RTO / RPO\nmet?" },
			{ id: "n6", lane: 4, row: 8, kind: "step", num: 6, title: "Improve Plans",
				desc: "Fix gaps found in exercises",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n7", lane: 4, row: 9, kind: "step", num: 7, title: "Management Review",
				desc: "Report readiness to the board",
				links: [["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 10, kind: "end", title: "Resilient" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", {}], ["n2", "n3", { route: "elbow" }],
			["n3", "n4", {}], ["n4", "n5", { route: "elbow" }], ["n5", "d1", {}],
			["d1", "n6", { label: "No — gaps", route: "elbow" }],
			["n6", "n4", { label: "update & re-test", route: "loop", dashed: 1 }],
			["d1", "n7", { label: "Yes", route: "elbow" }], ["n7", "end", {}],
			["n7", "n1", { label: "annual cycle", route: "loop", dashed: 1 }],
		],
	},

	nist: {
		title: "NIST CSF 2.0", tag: "Cybersecurity framework profile",
		icon: "🧩", dashboards: [["NIST CSF Dashboard", "grc-nist-csf-dashboard"]],
		lanes: L4("Profile", "Implement", "Assess", "Report"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Catalog & Target Profile",
				desc: "Functions, categories, target tiers",
				links: [["CSF Catalog", "GRC NIST CSF Catalog"]] },
			{ id: "n2", lane: 2, row: 3, kind: "step", num: 2, title: "Implement Controls",
				desc: "Current profile per subcategory",
				links: [["CSF Control", "GRC NIST CSF Control"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "Detection Coverage",
				desc: "Map detective capability",
				links: [["Detection Coverage", "GRC Detection Coverage"]] },
			{ id: "n4", lane: 3, row: 5, kind: "step", num: 4, title: "Assessment",
				desc: "Score current vs target profile",
				links: [["Assessment Run", "GRC Assessment Run"]] },
			{ id: "d1", lane: 3, row: 6, kind: "decision", title: "Target profile\nmet?" },
			{ id: "n5", lane: 4, row: 7, kind: "step", num: 5, title: "Close Gaps",
				desc: "Prioritized uplift actions",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n6", lane: 4, row: 8, kind: "step", num: 6, title: "KPIs & Report",
				desc: "Profile position to leadership",
				links: [["KPI", "GRC KPI"], ["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 9, kind: "end", title: "At target" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", { route: "elbow" }], ["n2", "n3", {}],
			["n3", "n4", { route: "elbow" }], ["n4", "d1", {}],
			["d1", "n5", { label: "No", route: "elbow" }],
			["n5", "n2", { label: "uplift", route: "loop", dashed: 1 }],
			["d1", "n6", { label: "Yes", route: "elbow" }], ["n6", "end", {}],
		],
	},

	pdpl: {
		title: "PDPL & GDPR", tag: "KSA and EU privacy compliance",
		icon: "🛡", dashboards: [["PDPL Dashboard", "grc-pdpl-dashboard"],
			["GDPR Dashboard", "grc-gdpr-dashboard"]],
		lanes: L4("Records", "Controls & DPIA", "Rights & Incidents", "Review"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "Processing Activities (RoPA)",
				desc: "What data, why, where, how long",
				links: [["Processing Activity", "GRC Privacy Processing Activity"]] },
			{ id: "n2", lane: 2, row: 3, kind: "step", num: 2, title: "Privacy Controls",
				desc: "PDPL control implementation",
				links: [["PDPL Control", "GRC PDPL Control"], ["PDPL Catalog", "GRC PDPL Catalog"]] },
			{ id: "n3", lane: 2, row: 4, kind: "step", num: 3, title: "DPIA",
				desc: "Impact assessment for high-risk processing",
				gate: "High-risk processing activities require a DPIA before go-live.",
				links: [["DPIA Record", "GRC DPIA Record"]] },
			{ id: "d1", lane: 2, row: 5, kind: "decision", title: "High residual\nrisk?" },
			{ id: "n4", lane: 2, row: 6, kind: "step", num: 4, title: "Mitigation",
				desc: "Reduce risk before processing",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n5", lane: 3, row: 7, kind: "step", num: 5, title: "Data Subject Requests",
				desc: "Access, deletion, correction — on SLA",
				gate: "DSARs run on statutory clocks — track received date and due date on every request.",
				links: [["DSAR Request", "GRC DSAR Request"]] },
			{ id: "n6", lane: 3, row: 8, kind: "step", num: 6, title: "Breaches & Problems",
				desc: "Record, assess, notify where required",
				links: [["Problem Record", "GRC Problem Record"]] },
			{ id: "n7", lane: 4, row: 9, kind: "step", num: 7, title: "Review & Report",
				desc: "Privacy posture to leadership",
				links: [["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 10, kind: "end", title: "Compliant" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", { route: "elbow" }], ["n2", "n3", {}],
			["n3", "d1", {}],
			["d1", "n4", { label: "Yes — mitigate" }],
			["n4", "n3", { label: "reassess", route: "loop", dashed: 1 }],
			["d1", "n5", { label: "No — proceed", route: "elbow" }],
			["n5", "n6", { label: "if incident", dashed: 1 }],
			["n5", "n7", { route: "elbow" }], ["n6", "n7", { route: "elbow", dashed: 1 }],
			["n7", "n1", { label: "keep RoPA current", route: "loop", dashed: 1 }],
			["n7", "end", {}],
		],
	},

	iso42001: {
		title: "ISO/IEC 42001", tag: "AI management system",
		icon: "🤖", dashboards: [["AI MS Dashboard", "grc-iso42001-dashboard"]],
		lanes: L4("Catalog", "Implement", "Assess", "Report"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "AI Controls Catalog",
				desc: "Applicable AI governance controls",
				links: [["ISO42001 Catalog", "GRC ISO42001 Catalog"]] },
			{ id: "n2", lane: 2, row: 3, kind: "step", num: 2, title: "Implement AI Controls",
				desc: "Ownership and status per control",
				links: [["ISO42001 Control", "GRC ISO42001 Control"]] },
			{ id: "n3", lane: 3, row: 4, kind: "step", num: 3, title: "Assessment",
				desc: "Score implementation",
				links: [["Assessment Run", "GRC Assessment Run"]] },
			{ id: "d1", lane: 3, row: 5, kind: "decision", title: "Gaps?" },
			{ id: "n4", lane: 4, row: 6, kind: "step", num: 4, title: "Close Gaps",
				desc: "Remediation to target",
				links: [["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n5", lane: 4, row: 7, kind: "step", num: 5, title: "Report",
				desc: "AI governance posture",
				links: [["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 8, kind: "end", title: "Governed" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", { route: "elbow" }],
			["n2", "n3", { route: "elbow" }], ["n3", "d1", {}],
			["d1", "n4", { label: "Yes", route: "elbow" }],
			["n4", "n2", { label: "uplift", route: "loop", dashed: 1 }],
			["d1", "n5", { label: "No", route: "elbow" }], ["n5", "end", {}],
		],
	},

	itgc: {
		title: "ITGC Programme", tag: "IT general controls audit",
		icon: "🖥", dashboards: [["ITGC Programme", "grc-itgc-program"]],
		lanes: L4("Programme", "Scope Items", "Test", "Remediate & Report"),
		nodes: [
			{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
			{ id: "n1", lane: 1, row: 2, kind: "step", num: 1, title: "IT Audit Program",
				desc: "Annual programme and scope",
				links: [["IT Audit Program", "GRC IT Audit Program"]] },
			{ id: "n2", lane: 2, row: 3, kind: "step", num: 2, title: "ITGC Scope Items",
				desc: "Access, change, operations, backup…",
				links: [["ITGC Item", "GRC ITGC Audit Item"]] },
			{ id: "n3", lane: 3, row: 4, kind: "step", num: 3, title: "Control Testing",
				desc: "Design + operating effectiveness",
				gate: "Testing needs sampled evidence per control — document it in the workpaper.",
				links: [["Control Item", "GRC IT Audit Control Item"],
					["Workpaper", "GRC Audit Workpaper"]] },
			{ id: "d1", lane: 3, row: 5, kind: "decision", title: "Deficiencies?" },
			{ id: "n4", lane: 4, row: 6, kind: "step", num: 4, title: "Findings & Remediation",
				desc: "Raise, own, fix, verify",
				links: [["Audit Finding", "GRC Audit Finding"],
					["Remediation Action", "GRC Remediation Action"]] },
			{ id: "n5", lane: 4, row: 7, kind: "step", num: 5, title: "Report",
				desc: "ITGC conclusion",
				links: [["Board Report", "GRC Board Report"]] },
			{ id: "end", lane: 4, row: 8, kind: "end", title: "Concluded" },
		],
		edges: [
			["start", "n1", {}], ["n1", "n2", { route: "elbow" }],
			["n2", "n3", { route: "elbow" }], ["n3", "d1", {}],
			["d1", "n4", { label: "Yes", route: "elbow" }],
			["n4", "n3", { label: "re-test", route: "loop", dashed: 1 }],
			["d1", "n5", { label: "No", route: "elbow" }],
			["n4", "n5", { route: "elbow" }], ["n5", "end", {}],
		],
	},
};

const OVERVIEWS = [
	["🗺", "General Process Map", "The full end-to-end GRC flow across all functions", "grc-process-map"],
	["🎡", "Lifecycle Wheel", "Live 8-stage journey per client", "grc-lifecycle"],
	["🎛", "Command Centre", "Firm-wide operational overview", "grc-command-center"],
];

// ---------------------------------------------------------------------------
// Index view
// ---------------------------------------------------------------------------
function render_index(page) {
	page.set_title(__("Framework Process Maps"));
	const fw_cards = Object.entries(FRAMEWORKS).map(([key, f]) => {
		const steps = f.nodes.filter(n => n.kind === "step").length;
		const dash = (f.dashboards || []).map(([label, route]) =>
			`<a class="fwm-btn fwm-btn-light" href="/app/${route}">${frappe.utils.escape_html(__(label))}</a>`).join("");
		return `<div class="fwm-card">
			<div class="fwm-card-head"><span class="fwm-icon">${f.icon}</span>
				<div><div class="fwm-card-title">${frappe.utils.escape_html(__(f.title))}</div>
				<div class="fwm-card-tag">${frappe.utils.escape_html(__(f.tag))}</div></div></div>
			<div class="fwm-card-meta">${steps} ${__("steps")} · ${f.nodes.filter(n => n.kind === "decision").length} ${__("decisions")}</div>
			<div class="fwm-card-actions">
				<a class="fwm-btn fwm-btn-primary" href="#fw=${key}">${__("Open flow")} →</a>
				${dash}
			</div></div>`;
	}).join("");
	const ov_cards = OVERVIEWS.map(([icon, title, desc, route]) =>
		`<div class="fwm-card fwm-card-ov">
			<div class="fwm-card-head"><span class="fwm-icon">${icon}</span>
				<div><div class="fwm-card-title">${frappe.utils.escape_html(__(title))}</div>
				<div class="fwm-card-tag">${frappe.utils.escape_html(__(desc))}</div></div></div>
			<div class="fwm-card-actions">
				<a class="fwm-btn fwm-btn-primary" href="/app/${route}">${__("Open")} →</a>
			</div></div>`).join("");

	$(page.body).html(`
		${index_css()}
		<div class="fwm-wrap">
			<div class="fwm-section">${__("Overviews — the whole process at a glance")}</div>
			<div class="fwm-grid">${ov_cards}</div>
			<div class="fwm-section">${__("Framework flows — step-by-step with transactions")}</div>
			<div class="fwm-grid">${fw_cards}</div>
		</div>`);
}

function index_css() {
	return `<style>
		.fwm-wrap { padding: 8px 4px 40px; }
		.fwm-section { font-weight: 700; font-size: 14px; margin: 14px 2px 10px;
			color: var(--heading-color); }
		.fwm-grid { display: grid; gap: 12px;
			grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); }
		.fwm-card { border: 1px solid var(--border-color); border-radius: 12px;
			padding: 14px; background: var(--card-bg);
			box-shadow: 0 1px 3px rgba(0,0,0,.06); display: flex;
			flex-direction: column; gap: 8px; }
		.fwm-card-ov { background: var(--subtle-fg, #f8fafc); }
		.fwm-card-head { display: flex; gap: 10px; align-items: center; }
		.fwm-icon { font-size: 26px; line-height: 1; }
		.fwm-card-title { font-weight: 700; font-size: 14px; }
		.fwm-card-tag { font-size: 11.5px; color: var(--text-muted); }
		.fwm-card-meta { font-size: 11px; color: var(--text-muted); }
		.fwm-card-actions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; }
		.fwm-btn { font-size: 12px; padding: 4px 12px; border-radius: 999px;
			text-decoration: none; border: 1px solid transparent; }
		.fwm-btn-primary { background: var(--primary, #2490ef); color: #fff; }
		.fwm-btn-primary:hover { filter: brightness(.95); color: #fff; }
		.fwm-btn-light { background: var(--gray-100); color: var(--text-color);
			border-color: var(--gray-300); }
		.fwm-btn-light:hover { background: var(--gray-200); }
	</style>`;
}

// ---------------------------------------------------------------------------
// Flow view (shared renderer)
// ---------------------------------------------------------------------------
function slug(dt) { return frappe.router.slug(dt); }

function render_flow(page, key) {
	const f = FRAMEWORKS[key];
	page.set_title(__(f.title) + " — " + __("Process Flow"));
	const maxrow = Math.max(...f.nodes.map(n => n.row)) + 1;
	const ncols = f.lanes.length;

	const lanes_head = f.lanes.map(l =>
		`<div class="fwf-lane-head" style="background:${l.tint};border-top:4px solid ${l.border}">
			${frappe.utils.escape_html(__(l.label))}</div>`).join("");
	const lane_bgs = f.lanes.map(l =>
		`<div class="fwf-lane-bg" style="grid-column:${l.key};grid-row:1 / ${maxrow};background:${l.tint}55"></div>`).join("");
	const nodes = f.nodes.map(n => flow_node(n, f.lanes[n.lane - 1])).join("");

	$(page.body).html(`
		${flow_css(ncols)}
		<div class="fwf-wrap">
			<div class="fwf-top">
				<a class="fwm-btn fwm-btn-light" href="#">← ${__("All frameworks")}</a>
				<span class="fwf-legend">${__("Click a name to open the list, ＋ to create. Hover ⚠ for gates. Dashed arrows are loops / alternate paths.")}</span>
			</div>
			<div class="fwf-heads">${lanes_head}</div>
			<div class="fwf-grid" id="fwf-grid">
				${lane_bgs}
				<svg class="fwf-svg" id="fwf-svg">
					<defs><marker id="fwf-arrow" viewBox="0 0 10 10" refX="9" refY="5"
						markerWidth="7" markerHeight="7" orient="auto-start-reverse">
						<path d="M 0 0 L 10 5 L 0 10 z" fill="#4a5568"></path>
					</marker></defs>
				</svg>
				${nodes}
			</div>
		</div>`);

	const draw = () => draw_edges(f);
	setTimeout(draw, 60);
	$(window).off("resize.fwf").on("resize.fwf", frappe.utils.debounce(draw, 150));
}

function flow_node(n, lane) {
	if (n.kind === "start" || n.kind === "end") {
		const bg = n.kind === "start" ? "#2e7d4f" : "#b04a4a";
		return `<div class="fwf-node fwf-pill" id="fwf-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row};background:${bg}">${frappe.utils.escape_html(__(n.title))}</div>`;
	}
	if (n.kind === "decision") {
		return `<div class="fwf-node fwf-decision-wrap" id="fwf-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row}">
			<div class="fwf-decision" style="border-color:${lane.border}">
				<span>${frappe.utils.escape_html(__(n.title)).replace(/\n/g, "<br>")}</span>
			</div></div>`;
	}
	const links = (n.links || []).map(([label, dt]) => {
		const s = slug(dt);
		return `<span class="fwf-chip">
			<a href="/app/${s}" title="${__("Open list")}">${frappe.utils.escape_html(__(label))}</a>
			<a class="fwf-new" href="/app/${s}/new" title="${__("Create new")}">＋</a>
		</span>`;
	}).join("");
	const gate = n.gate
		? `<span class="fwf-gate" tabindex="0">⚠<span class="fwf-tip">${frappe.utils.escape_html(__(n.gate))}</span></span>`
		: "";
	return `<div class="fwf-node fwf-step" id="fwf-${n.id}"
		style="grid-column:${n.lane};grid-row:${n.row};border-color:${lane.border};background:#fff">
		<div class="fwf-step-title">
			<span class="fwf-num" style="background:${lane.border}">${n.num}</span>
			${frappe.utils.escape_html(__(n.title))}${gate}
		</div>
		<div class="fwf-step-desc">${frappe.utils.escape_html(__(n.desc || ""))}</div>
		<div class="fwf-links">${links}</div>
	</div>`;
}

function flow_css(ncols) {
	return `<style>
		.fwf-wrap { padding: 8px 4px 40px; overflow-x: auto; }
		.fwf-top { display: flex; gap: 12px; align-items: center; margin-bottom: 10px; }
		.fwf-legend { font-size: 12px; color: var(--text-muted); }
		.fwm-btn { font-size: 12px; padding: 4px 12px; border-radius: 999px;
			text-decoration: none; }
		.fwm-btn-light { background: var(--gray-100); color: var(--text-color);
			border: 1px solid var(--gray-300); }
		.fwm-btn-light:hover { background: var(--gray-200); }
		.fwf-heads, .fwf-grid { display: grid;
			grid-template-columns: repeat(${ncols}, minmax(225px, 1fr)); gap: 0 14px;
			min-width: ${ncols * 240}px; }
		.fwf-lane-head { padding: 10px 8px; text-align: center; font-weight: 700;
			border-radius: 8px 8px 0 0; font-size: 13px; position: sticky; top: 0; z-index: 3; }
		.fwf-grid { position: relative; grid-auto-rows: minmax(56px, auto);
			row-gap: 32px; padding: 26px 0 10px; }
		.fwf-lane-bg { border-radius: 0 0 8px 8px; }
		.fwf-node { position: relative; z-index: 2; align-self: center;
			justify-self: center; width: 92%; }
		.fwf-step { border: 2px solid; border-radius: 10px; padding: 8px 10px;
			box-shadow: 0 1px 3px rgba(0,0,0,.08); }
		.fwf-step-title { font-weight: 700; font-size: 12.5px; display: flex;
			gap: 6px; align-items: center; flex-wrap: wrap; }
		.fwf-num { color: #fff; border-radius: 50%; min-width: 20px; height: 20px;
			display: inline-flex; align-items: center; justify-content: center;
			font-size: 11px; }
		.fwf-step-desc { font-size: 11px; color: var(--text-muted); margin: 4px 0 6px; }
		.fwf-links { display: flex; flex-wrap: wrap; gap: 4px; }
		.fwf-chip { display: inline-flex; border: 1px solid var(--gray-300);
			border-radius: 999px; overflow: hidden; font-size: 11px;
			background: var(--gray-50); }
		.fwf-chip a { padding: 2px 8px; text-decoration: none; }
		.fwf-chip a.fwf-new { border-left: 1px solid var(--gray-300); font-weight: 700; }
		.fwf-chip a:hover { background: var(--gray-200); }
		.fwf-pill { color: #fff; font-weight: 700; text-align: center;
			border-radius: 999px; padding: 8px 0; width: 150px; }
		.fwf-decision-wrap { display: flex; justify-content: center; }
		.fwf-decision { width: 118px; height: 118px; background: #fff; border: 2px solid;
			transform: rotate(45deg); border-radius: 12px; display: flex;
			align-items: center; justify-content: center;
			box-shadow: 0 1px 3px rgba(0,0,0,.08); }
		.fwf-decision span { transform: rotate(-45deg); font-size: 11px;
			font-weight: 700; text-align: center; line-height: 1.25; }
		.fwf-svg { position: absolute; inset: 0; width: 100%; height: 100%;
			z-index: 1; pointer-events: none; }
		.fwf-edge-label { font-size: 10px; font-weight: 700; fill: #555;
			paint-order: stroke; stroke: #fff; stroke-width: 3px; }
		.fwf-gate { cursor: help; position: relative; outline: none; font-size: 12px; }
		.fwf-tip { display: none; position: absolute; left: 50%;
			bottom: calc(100% + 8px); transform: translateX(-50%); width: 240px;
			background: #1f2937; color: #fff; font-size: 11px; font-weight: 400;
			line-height: 1.45; padding: 8px 10px; border-radius: 8px;
			box-shadow: 0 4px 14px rgba(0,0,0,.25); z-index: 50;
			white-space: normal; text-align: left; pointer-events: none; }
		.fwf-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
			transform: translateX(-50%); border: 6px solid transparent;
			border-top-color: #1f2937; }
		.fwf-gate:hover .fwf-tip, .fwf-gate:focus .fwf-tip { display: block; }
	</style>`;
}

function draw_edges(f) {
	const grid = document.getElementById("fwf-grid");
	const svg = document.getElementById("fwf-svg");
	if (!grid || !svg) return;
	const gb = grid.getBoundingClientRect();
	svg.setAttribute("width", grid.scrollWidth);
	svg.setAttribute("height", grid.scrollHeight);
	[...svg.querySelectorAll("path,text")].forEach(el => el.remove());

	const box = id => {
		const el = document.getElementById("fwf-" + id);
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
		p.setAttribute("marker-end", "url(#fwf-arrow)");
		svg.appendChild(p);
	};
	const T = (x, y, text) => {
		const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
		t.setAttribute("x", x); t.setAttribute("y", y);
		t.setAttribute("class", "fwf-edge-label");
		t.textContent = text;
		svg.appendChild(t);
	};

	f.edges.forEach(([from, to, opt]) => {
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
