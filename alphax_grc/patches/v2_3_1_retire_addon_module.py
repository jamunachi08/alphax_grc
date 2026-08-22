# Copyright (c) 2026, Neotec Integrated Solutions
"""v2.3.1 — reclaim Module Def rows still pointing at the retired add-on app.

Runs pre_model_sync: doctype sync itself is what fails when the module still
resolves to alphax_grc_evidence_automation, so this has to land first.
"""

from alphax_grc.install import retire_legacy_module_defs


def execute():
	retire_legacy_module_defs()
