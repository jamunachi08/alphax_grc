"""v2.14.0 governance tests: workflows installed, legacy DSR blocked,
DSR migration idempotent. Run with:
    bench --site <site> run-tests --module alphax_grc.tests.test_v2_14_governance
"""

import frappe
from frappe.tests.utils import FrappeTestCase

NEW_WORKFLOWS = [
    ("GRC Risk Acceptance Workflow", "GRC Risk Acceptance"),
    ("GRC SAMA Waiver Workflow", "GRC SAMA Waiver"),
    ("GRC DPIA Workflow", "GRC DPIA Record"),
]


class TestGovernanceWorkflows(FrappeTestCase):
    def test_workflows_installed(self):
        from alphax_grc.install import install_workflows
        install_workflows()
        for name, doctype in NEW_WORKFLOWS:
            self.assertTrue(frappe.db.exists("Workflow", name),
                f"{name} should exist after install")
            wf = frappe.get_doc("Workflow", name)
            self.assertEqual(wf.document_type, doctype)
            self.assertTrue(wf.is_active)
            self.assertGreaterEqual(len(wf.states), 4)
            self.assertGreaterEqual(len(wf.transitions), 4)

    def test_install_is_idempotent(self):
        from alphax_grc.install import install_workflows
        install_workflows()
        install_workflows()  # second run must not raise or duplicate
        for name, _ in NEW_WORKFLOWS:
            self.assertEqual(
                frappe.db.count("Workflow", {"workflow_name": name}), 1)


class TestLegacyDSRDeprecation(FrappeTestCase):
    def test_new_legacy_records_blocked(self):
        doc = frappe.new_doc("GRC Data Subject Request")
        doc.request_type = doc.meta.get_field("request_type").options.split("\n")[0] \
            if doc.meta.has_field("request_type") else None
        with self.assertRaises(frappe.ValidationError):
            doc.insert(ignore_permissions=True)

    def test_migration_is_idempotent(self):
        from alphax_grc.patches.v2_14_0_governance import migrate_legacy_dsr
        before = frappe.db.count("GRC DSAR Request")
        migrate_legacy_dsr()
        after_first = frappe.db.count("GRC DSAR Request")
        migrate_legacy_dsr()
        after_second = frappe.db.count("GRC DSAR Request")
        self.assertEqual(after_first, after_second,
            "second migration run must not create duplicates")
        self.assertGreaterEqual(after_first, before)
