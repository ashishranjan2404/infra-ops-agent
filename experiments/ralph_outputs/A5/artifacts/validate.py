#!/usr/bin/env python3
"""Validate the A5 outreach package: tracking.csv + anonymization_schema.json.

Stdlib only. Exits 0 + 'OK: ...' on success; exits 1 + reason on any violation.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

EXPECTED_HEADER = [
    "company", "contact_role", "channel", "status",
    "probability", "last_touch", "next_action", "notes",
]
ALLOWED_STATUS = {"not_started", "drafted", "sent", "replied", "agreed", "declined"}
ALLOWED_PROB = {"high", "medium", "low"}
SCHEMA_FIELDS = {
    "incident_id", "disclosed_publicly", "failure_class",
    "timeline", "alert_shapes", "remediation_steps", "provenance",
}


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        fail("tracking.csv is empty")
    header, data = rows[0], rows[1:]
    if header != EXPECTED_HEADER:
        fail(f"header mismatch: {header}")
    out = []
    for i, r in enumerate(data, start=2):
        if len(r) != len(EXPECTED_HEADER):
            fail(f"row {i} has {len(r)} cols, expected {len(EXPECTED_HEADER)}")
        d = dict(zip(EXPECTED_HEADER, r))
        if d["status"] not in ALLOWED_STATUS:
            fail(f"row {i} bad status {d['status']!r}")
        if d["probability"] not in ALLOWED_PROB:
            fail(f"row {i} bad probability {d['probability']!r}")
        out.append(d)
    return out


def load_schema(path: Path):
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"schema not valid JSON: {e}")
    if "$schema" not in schema:
        fail("schema missing $schema")
    props = set(schema.get("properties", {}))
    missing = SCHEMA_FIELDS - props
    if missing:
        fail(f"schema missing fields: {sorted(missing)}")
    return schema


def main() -> int:
    rows = load_csv(HERE / "tracking.csv")
    schema = load_schema(HERE / "anonymization_schema.json")
    companies = sorted({r["company"] for r in rows})
    expected_companies = {"CircleCI", "incident.io", "Cloudflare"}
    if set(companies) != expected_companies:
        fail(f"companies {companies} != {sorted(expected_companies)}")
    print(f"OK: {len(companies)} companies, "
          f"{len(rows)} contact rows, "
          f"schema fields={len(schema.get('properties', {}))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
