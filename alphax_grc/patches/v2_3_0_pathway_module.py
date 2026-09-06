# Copyright (c) 2026, Neotec Integrated Solutions
"""v2.3.0 — GRC Evidence Automation module merged in from the separate add-on.

Idempotent: re-seeds the policy library, pathway board, and role grants over
whatever the standalone alphax_grc_evidence_automation app may have created.
"""

from alphax_grc.install import run_pathway_setup


def execute():
	run_pathway_setup()
