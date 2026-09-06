# Copyright (c) 2026, Neotec Integrated Solutions
from alphax_grc.grc_evidence_automation.engine.evidence_runner import (
	run_due_fetchers,
)


def run_due_evidence_fetchers():
	run_due_fetchers(schedule="Hourly")


def run_due_daily_evidence_fetchers():
	run_due_fetchers(schedule="Daily")


def run_due_weekly_evidence_fetchers():
	run_due_fetchers(schedule="Weekly")


def run_due_monthly_evidence_fetchers():
	run_due_fetchers(schedule="Monthly")
