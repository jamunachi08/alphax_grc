import frappe
from frappe.model.document import Document


# Country + sector → applicable frameworks mapping.
# This is the heart of the multi-tenant model: when a consultant creates a
# new client, the right framework set is suggested automatically.
COUNTRY_SECTOR_FRAMEWORKS = {
    ("Saudi Arabia", "Government"):
        ["NCA ECC-2:2024", "NCA CSCC", "NCA Data Cybersecurity Controls",
         "Saudi PDPL", "SDAIA AI Ethics Principles"],
    ("Saudi Arabia", "Banking & Finance"):
        ["SAMA Cyber Security Framework 1.0", "SAMA CTI Principles",
         "Saudi PDPL", "NCA ECC-2:2024 (where applicable)"],
    ("Saudi Arabia", "Aramco Supply Chain"):
        ["Aramco TPCSP", "Aramco SACS-002",
         "NCA ECC-2:2024 (subset)", "Saudi PDPL"],
    ("Saudi Arabia", "Healthcare"):
        ["MoH Cybersecurity Directives", "Saudi PDPL",
         "NCA ECC-2:2024 (CNI)"],
    ("Saudi Arabia", "Energy & Utilities"):
        ["NCA ECC-2:2024 (CNI)", "NCA OTCC", "Saudi PDPL"],
    ("Saudi Arabia", "Telecom"):
        ["CITC Cybersecurity Regulatory Framework",
         "NCA ECC-2:2024 (CNI)", "Saudi PDPL"],
    ("Saudi Arabia", "General Private"):
        ["Saudi PDPL", "NCA ECC-2:2024 (voluntary)"],

    ("UAE", "Government"):
        ["UAE Information Assurance Standards",
         "TDRA Cybersecurity Framework", "UAE PDPL"],
    ("UAE", "Banking & Finance"):
        ["DIFC Data Protection Law", "DFSA Cyber Risk Management",
         "ADGM Data Protection Regs", "UAE PDPL"],
    ("UAE", "Healthcare"):
        ["DHA Cybersecurity Standard",
         "Department of Health Abu Dhabi Cybersecurity",
         "UAE PDPL"],

    ("Bahrain", "Banking & Finance"):
        ["CBB Cyber Security Module", "Bahrain PDPL"],
    ("Bahrain", "Government"):
        ["NCSC Cybersecurity Guidance", "Bahrain PDPL"],

    ("Qatar", "Government"):
        ["Qatar NIA Policy", "NCSA Standards"],
    ("Qatar", "Banking & Finance"):
        ["QFC Data Protection", "QFC Cyber Standards"],

    ("Kuwait", "Government"):
        ["CITRA Information Security Framework"],

    ("Oman", "Government"):
        ["OCERT Guidance", "NCSI Standards"],
}


def derive_frameworks(country, sector):
    """Return the framework list for a country+sector combination.
    Falls back to a reasonable generic list if the combination isn't mapped."""
    key = (country, sector)
    if key in COUNTRY_SECTOR_FRAMEWORKS:
        return COUNTRY_SECTOR_FRAMEWORKS[key]
    # Country fallback: any sector for that country
    country_only = [v for (c, _), v in COUNTRY_SECTOR_FRAMEWORKS.items() if c == country]
    if country_only:
        merged = []
        for fwlist in country_only:
            for fw in fwlist:
                if fw not in merged:
                    merged.append(fw)
        return merged
    return ["ISO/IEC 27001", "NIST Cybersecurity Framework"]


class GRCClientProfile(Document):
    def validate(self):
        if not self.applicable_frameworks:
            self.applicable_frameworks = "\n".join(
                derive_frameworks(self.country, self.sector)
            )
        # Refresh live summary fields
        self._refresh_summary()

    def on_update(self):
        # v1.4.1 — auto-adopt NCA library after save (not in validate, so the
        # client record exists when adopt_template_for_client looks it up)
        self._auto_adopt_nca_library()

    def _auto_adopt_nca_library(self):
        """If any auto_adopt_* checkbox is set AND no records of that kind
        exist for this client yet, bulk-create from the NCA library."""
        if not (self.auto_adopt_nca_policies
                or self.auto_adopt_nca_procedures
                or self.auto_adopt_nca_forms):
            return

        # Avoid recursion: don't re-trigger on the writes we make below
        if frappe.flags.get("alphax_grc_auto_adopting"):
            return
        frappe.flags.alphax_grc_auto_adopting = True
        results = []
        try:
            from alphax_grc.alphax_grc.page.grc_nca_templates.grc_nca_templates \
                import adopt_template_for_client

            jobs = []
            if self.auto_adopt_nca_policies:
                jobs.append(("Policy", "GRC NCA Policy Library",
                             "GRC Policy", "client"))
            if self.auto_adopt_nca_procedures:
                jobs.append(("Procedure", "GRC NCA Procedure Library",
                             "GRC ISMS Document Register", "client"))
            if self.auto_adopt_nca_forms:
                jobs.append(("Form", "GRC NCA Form Library",
                             "GRC ISMS Document Register", "client"))

            for kind, lib_doctype, target_doctype, scope_field in jobs:
                if not frappe.db.exists("DocType", lib_doctype):
                    continue
                if not frappe.db.exists("DocType", target_doctype):
                    continue
                # Already adopted? Skip.
                existing = frappe.db.count(
                    target_doctype, {scope_field: self.name}) or 0
                if existing > 0:
                    results.append(f"{kind}: skipped ({existing} already exist)")
                    continue
                templates = frappe.get_all(
                    lib_doctype, filters={"is_active": 1},
                    fields=["template_code"],
                )
                created = 0
                for t in templates:
                    try:
                        adopt_template_for_client(self.name, kind, t.template_code)
                        created += 1
                    except Exception:
                        try:
                            frappe.log_error(frappe.get_traceback(),
                                f"Auto-adopt failed: {t.template_code} for {self.name}")
                        except Exception:
                            pass
                results.append(f"{kind}: {created} adopted")
                # Reset the checkbox so it doesn't re-trigger on next save
                if kind == "Policy":
                    frappe.db.set_value("GRC Client Profile", self.name,
                                        "auto_adopt_nca_policies", 0)
                elif kind == "Procedure":
                    frappe.db.set_value("GRC Client Profile", self.name,
                                        "auto_adopt_nca_procedures", 0)
                elif kind == "Form":
                    frappe.db.set_value("GRC Client Profile", self.name,
                                        "auto_adopt_nca_forms", 0)

            if results:
                summary = " | ".join(results)
                frappe.db.set_value("GRC Client Profile", self.name,
                                    "adoption_status", summary)
        except Exception:
            try:
                frappe.log_error(frappe.get_traceback(),
                                 f"_auto_adopt_nca_library failed: {self.name}")
            except Exception:
                pass
        finally:
            frappe.flags.alphax_grc_auto_adopting = False

    def _refresh_summary(self):
        # Open risks
        if frappe.db.exists("DocType", "GRC Risk Register"):
            self.open_risks = frappe.db.count(
                "GRC Risk Register",
                {"client": self.name, "status": ["!=", "Closed"]},
            ) or 0
        # Open findings
        if frappe.db.exists("DocType", "GRC Audit Finding"):
            self.open_findings = frappe.db.count(
                "GRC Audit Finding",
                {"client": self.name,
                 "status": ["not in", ["Closed", "Verified"]]},
            ) or 0
        # Compliance score: average of GRC Assessment.compliance_score for
        # assessments on this client's frameworks. (GRC Framework itself has
        # no compliance_score column.)
        if (frappe.db.exists("DocType", "GRC Framework")
                and frappe.db.exists("DocType", "GRC Assessment")):
            framework_names = [
                fw.name for fw in frappe.get_all(
                    "GRC Framework",
                    filters={"client": self.name},
                    fields=["name"],
                )
            ]
            if framework_names:
                rows = frappe.db.sql(
                    """SELECT AVG(compliance_score) AS avg_score
                       FROM `tabGRC Assessment`
                       WHERE client = %s
                         AND framework IN %s""",
                    (self.name, tuple(framework_names)),
                    as_dict=True,
                )
                if rows and rows[0].avg_score is not None:
                    self.compliance_score = rows[0].avg_score
                else:
                    self.compliance_score = 0
            else:
                self.compliance_score = 0


@frappe.whitelist()
def get_suggested_frameworks(country, sector):
    """Whitelisted endpoint used by the Client Profile form to suggest the
    framework list based on the chosen country + sector."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    return derive_frameworks(country, sector)


@frappe.whitelist()
def get_active_clients():
    """Return the list of active clients the current user can read.
    Used by the client picker UI in the lifecycle dashboard."""
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required.", frappe.PermissionError)
    return frappe.get_list(
        "GRC Client Profile",
        filters={"is_active": 1},
        fields=["name", "client_name", "country", "sector",
                "compliance_score", "open_risks", "open_findings",
                "lead_consultant", "engagement_type"],
        order_by="modified desc",
        limit=200,
    )
