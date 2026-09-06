# Copyright (c) 2026, Neotec Integrated Solutions
"""v2.10.0 — immutable policy version history.

GRC Policy is a single mutable record — the right place to edit a policy day
to day, but it means there's no way to answer "what did this policy actually
say on the date it was in effect, and can we prove it hasn't been touched
since?" That question comes up in almost every audit and regulator review.

This module doesn't change how GRC Policy works. It listens for the moment a
policy's publication_status becomes "Published" and takes an immutable,
hash-chained snapshot (GRC Policy Version) of the fields that matter for
proving what was published. Editing the live GRC Policy record afterwards is
still allowed — that's normal operation — but the version history it already
published is never retroactively rewritten.
"""

from __future__ import annotations

import frappe

from alphax_grc.integrity import canonical_json, compute_chain_hash, get_last_hash, verify_chain

SNAPSHOT_FIELDS = [
	"policy_title", "policy_category", "policy_owner", "version_no",
	"status", "effective_date", "review_due_date", "summary",
]


def snapshot_if_published(doc, method: str | None = None) -> None:
	if doc.publication_status != "Published":
		return

	# Only snapshot once per distinct version_no - a policy being saved
	# again with the same version shouldn't create a duplicate version
	# record every time someone touches an unrelated field.
	already_versioned = frappe.db.exists(
		"GRC Policy Version", {"policy": doc.name, "version_label": doc.version_no or ""}
	)
	if already_versioned:
		return

	snapshot = {field: doc.get(field) for field in SNAPSHOT_FIELDS}
	version_label = doc.version_no or frappe.utils.now_datetime().strftime("%Y%m%d-%H%M%S")

	prev_hash = get_last_hash("GRC Policy Version", {"policy": doc.name})
	snapshot_hash = compute_chain_hash(prev_hash, doc.name, version_label, canonical_json(snapshot))

	version = frappe.new_doc("GRC Policy Version")
	version.update({
		"policy": doc.name,
		"version_label": version_label,
		"published_on": frappe.utils.now_datetime(),
		"published_by": frappe.session.user,
		"snapshot_json": canonical_json(snapshot),
		"prev_hash": prev_hash,
		"snapshot_hash": snapshot_hash,
	})
	# No role holds "create" on GRC Policy Version by design (see its
	# doctype JSON) - this function is the one sanctioned path in.
	version.insert(ignore_permissions=True)


@frappe.whitelist()
def verify_policy_chain(policy: str) -> dict:
	"""Re-walk a policy's full version history and confirm no snapshot was
	altered after the fact. Intended to be surfaced as a button on the
	GRC Policy form."""
	return verify_chain(
		"GRC Policy Version",
		{"policy": policy},
		part_fields=["policy", "version_label", "snapshot_json"],
	)
