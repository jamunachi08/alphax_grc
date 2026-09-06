# AlphaX GRC Technical Manual

## Package Structure
- `alphax_grc/install.py` seeds safe baseline records.
- `alphax_grc/alphax_grc/doctype/*` contains standard DocTypes.
- `alphax_grc/alphax_grc/page/*` contains Desk pages.
- `alphax_grc/manuals/*` contains markdown manuals bundled with the app.

## Stability Principles
- Only valid select-option values are seeded.
- Optional seed-data failures are logged and do not stop install.
- Pages use simple fallback HTML/JS so Desk routes can render even without advanced front-end builds.

## Site Validation Checklist
1. Confirm app installs without validation errors.
2. Open module **AlphaX GRC** from Desk.
3. Verify key DocTypes: Framework, Risk, Policy, Evidence, Assessment, Audit Plan, Vendor, Vendor Assessment.
4. Verify child tables: Vendor Question Item, Control Mapping Item, Pack Framework Item.
5. Test Desk routes: `/app/grc-command-center`, `/app/grc-reports`, `/app/grc-help`, `/app/grc-v04-help`, `/app/grc-neo-hub`.
