# AlphaX GRC v2.12.0

## Added
- **GRC Process Map** desk page (`/app/grc-process-map`): end-to-end swimlane
  flow chart across five lanes — Client & Engagement, Risk & Assessment,
  Controls/Policies/Evidence, Audit & Remediation, Governance & Reporting.
  - 17 numbered steps from Client Profile through the continuous-review cycle,
    with three decision diamonds (risk appetite, control effectiveness,
    open findings) and dashed loop-backs (strengthen controls, re-test
    evidence, exceptions path, review-reopens-register).
  - Every step carries direct chips to open the transaction list or create a
    new record (25 DocTypes linked, all verified against the app).
  - ⚠ gate badges with hover/keyboard tooltips explaining each step's
    prerequisite (e.g., evidence attaches to mapped controls).
  - Menu link to the existing Lifecycle wheel; same 8-stage vocabulary.
- Workspace: "🗺 Process Map (start here)" shortcut and intro hint at the top
  of the AlphaX GRC workspace.

## Notes
- Page is standard and syncs on `bench migrate`; run `bench build` and
  hard-refresh after update. No schema changes.
