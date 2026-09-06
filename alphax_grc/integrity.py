# Copyright (c) 2026, Neotec Integrated Solutions
"""v2.10.0 — shared tamper-evidence utility.

A small, dependency-free hash-chaining helper used anywhere in the app that
needs to prove a record wasn't silently altered after it was written:
GRC Evidence Rule Evaluation results and GRC Policy Version snapshots today,
and any future doctype that needs the same property.

The pattern: each new record's hash is computed over its own content plus the
hash of the previous record in the same chain (scoped by whatever key the
caller chooses — a rule name, a policy name, etc.). Re-walking the chain and
recomputing every hash will only match what's stored if nothing was edited
out from under it.
"""

from __future__ import annotations

import hashlib
import json

import frappe

GENESIS = "GENESIS"


def compute_chain_hash(prev_hash: str, *parts: str) -> str:
	"""Deterministic hash over the previous link plus an ordered list of
	content parts. Callers are responsible for passing parts in a stable,
	consistent order every time."""
	material = "|".join([prev_hash or GENESIS, *[str(p) for p in parts]])
	return hashlib.sha256(material.encode("utf-8")).hexdigest()


def get_last_hash(doctype: str, scope_filters: dict, hash_field: str = "snapshot_hash",
                   order_by: str = "creation desc") -> str:
	"""Fetch the most recent hash in a chain, or GENESIS if this is the
	first record for the given scope (e.g. the first evaluation of a rule,
	or the first version of a policy)."""
	value = frappe.db.get_value(doctype, scope_filters, hash_field, order_by=order_by)
	return value or GENESIS


def verify_chain(doctype: str, scope_filters: dict, part_fields: list[str],
                  hash_field: str = "snapshot_hash", prev_field: str = "prev_hash",
                  order_by: str = "creation asc") -> dict:
	"""Walk every record in a chain (oldest first) and confirm each stored
	hash is consistent with its own content and the previous record's hash.
	Returns the first broken link, if any, so a reviewer can see exactly
	where a chain stopped being trustworthy rather than just "invalid"."""
	rows = frappe.get_all(
		doctype,
		filters=scope_filters,
		fields=["name", prev_field, hash_field, *part_fields],
		order_by=order_by,
	)

	expected_prev = GENESIS
	for row in rows:
		if row.get(prev_field) != expected_prev:
			return {"valid": False, "broken_at": row["name"], "reason": "prev_hash mismatch"}

		parts = [row.get(f) for f in part_fields]
		recomputed = compute_chain_hash(expected_prev, *parts)
		if recomputed != row.get(hash_field):
			return {"valid": False, "broken_at": row["name"], "reason": "content hash mismatch — record may have been altered"}

		expected_prev = row.get(hash_field)

	return {"valid": True, "chain_length": len(rows), "head_hash": expected_prev}


def canonical_json(value) -> str:
	"""Stable JSON serialization so the same logical content always hashes
	the same way regardless of dict key ordering."""
	return json.dumps(value, sort_keys=True, default=str)
