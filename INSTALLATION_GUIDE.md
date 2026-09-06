# AlphaX GRC v1.2.0 — Installation & Troubleshooting Guide

**Publisher:** IRSAA Business Solutions | support@irsaa.com  
**Platform:** Frappe v15/v16, Python 3.10–3.12, MariaDB 10.6+

---

## Quick Install

```bash
# 1. Get the app into your bench
cd /home/frappe/frappe-bench
bench get-app alphax_grc /path/to/alphax_grc_v1_2_0/

# 2. Install on your site
bench --site your-site.localhost install-app alphax_grc

# 3. Run migrations (creates all DocTypes and pages)
bench --site your-site.localhost migrate

# 4. Build assets (registers CSS/JS for pages)
bench build --app alphax_grc

# 5. Restart services
bench restart
```

---

## If Pages Show "Page Not Found" (404)

Run these commands:

```bash
# Re-run migration (ensures pages are registered)
bench --site your-site.localhost migrate

# Re-build assets
bench build --app alphax_grc

# Clear server cache
bench --site your-site.localhost clear-cache

# Restart
bench restart
```

Then navigate to: `http://your-site.localhost/app/grc-neo-hub`

---

## If Charts Show Black Background

This is a Chart.js canvas rendering issue. v1.2.0 includes the fix.  
If you still see it after upgrading:

```bash
bench build --app alphax_grc
bench --site your-site.localhost clear-cache
bench restart
```

Then hard-refresh the browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

---

## Manual Page Registration (Emergency Fix)

If pages still show 404 after migrate, run in the Frappe console:

```bash
bench --site your-site.localhost console
```

```python
import frappe

pages = [
    ("grc-command-center", "GRC Command Centre"),
    ("grc-neo-hub", "GRC Neo Hub"),
    ("grc-itgc-program", "ITGC Audit Programme"),
    ("grc-asset-dashboard", "Asset Inventory Dashboard"),
    ("grc-reports", "GRC Reports"),
    ("grc-help", "GRC Help"),
]

for route, title in pages:
    if not frappe.db.exists("Page", route):
        doc = frappe.get_doc({
            "doctype": "Page",
            "name": route,
            "page_name": route,
            "title": title,
            "module": "AlphaX GRC",
            "standard": "Yes",
        })
        doc.insert(ignore_permissions=True)
        print(f"Created: {route}")
    else:
        print(f"Already exists: {route}")

frappe.db.commit()
print("Done!")
```

---

## All App Pages

| Page | URL | Description |
|------|-----|-------------|
| GRC Neo Hub | `/app/grc-neo-hub` | Main launch hub — 15 module cards |
| GRC Command Centre | `/app/grc-command-center` | Full dashboard with heatmap & charts |
| ITGC Audit Programme | `/app/grc-itgc-program` | 145 IT General Controls tracker |
| Asset Inventory Dashboard | `/app/grc-asset-dashboard` | ISO 27001 assets + NCA ECC mapping |
| GRC Reports | `/app/grc-reports` | Reports listing |
| GRC Help | `/app/grc-help` | Help documentation |

---

## DocType List Routes

| DocType | URL |
|---------|-----|
| Risk Register | `/app/grc-risk-register` |
| ITGC Audit Items | `/app/grc-itgc-audit-item` |
| Asset Inventory | `/app/grc-asset-inventory` |
| NCA ECC Controls | `/app/grc-nca-ecc-control` |
| ISO 27001 Documents | `/app/grc-iso27001-document` |
| Audit Findings | `/app/grc-audit-finding` |
| Policies | `/app/grc-policy` |
| KRIs | `/app/grc-kri` |
| Incidents | `/app/grc-incident` |
| Vendors | `/app/grc-vendor` |

---

## Seed Data

On first install, `after_install` and `after_migrate` both run `bootstrap_grc()` which seeds:

- **9 Roles** (GRC Executive, GRC Admin, Compliance Officer, etc.)
- **8 Frameworks** (NCA ECC, SAMA CSF, PDPL, ISO 27001, etc.)
- **14 Sample Policies** (Information Security, Access Control, etc.)
- **145 ITGC Audit Items** (7 domains from Shahidul Islam's programme)
- **15 Asset Inventory Records** (all 6 ISO 27001 asset types)
- **15 NCA ECC-2:2024 Controls** (full technology mapping)
- **19 ISO 27001:2022 Documents** (mandatory document checklist)
- Theme settings, DR plans, problem records, assessment templates

---

## Support

Email: support@irsaa.com  
Version: 1.2.0 | April 2026
