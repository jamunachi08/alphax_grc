# AlphaX GRC v2.13.0

## Added
- **Framework Process Maps** desk page (`/app/grc-framework-maps`):
  - Index of every process flow: three overview cards (General Process Map,
    Lifecycle Wheel, Command Centre) plus nine framework flow cards, each
    showing step/decision counts with "Open flow" and direct dashboard links.
  - Nine framework-specific swimlane flows, each with numbered steps,
    decision diamonds, loop-backs, ⚠ gate tooltips and clickable
    list / ＋ new transaction chips (55 DocType links, all verified):
    NCA ECC-2:2024 · SAMA CSF · Aramco CCC (SACS-002) · ISO/IEC 27001 ·
    ISO 22301 BCMS · NIST CSF 2.0 · PDPL & GDPR · ISO/IEC 42001 · ITGC.
  - In-page hash navigation (#fw=nca) with an "All frameworks" back action.
- Workspace: "🧭 Framework Maps" shortcut next to the Process Map.
- General Process Map: menu cross-link to Framework Maps.

## Notes
- Standard pages; sync on `bench migrate`. Run `bench build` and hard-refresh.
  No schema changes.
