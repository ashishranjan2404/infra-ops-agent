#!/usr/bin/env python3
"""Validate the A3 outreach artifacts.

Checks:
  T1  intake_example.json validates against intake_schema.json
  T2  a copy with a required field removed FAILS (proves the check bites)
  T3  tracking_sheet.csv parses; header + status/track enums valid
  T4  example category is in the real-spec category set

Uses `jsonschema` if importable; otherwise a minimal stdlib validator that
checks required fields + enums + types. Exit 0 on success, non-zero otherwise.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "intake_schema.json"
EXAMPLE = HERE / "intake_example.json"
CSV_FILE = HERE / "tracking_sheet.csv"

STATUS_ENUM = {
    "not_started", "contacted", "replied", "negotiating",
    "received", "declined", "no_response",
}
TRACK_ENUM = {"community_warm", "dua_nonpublic"}
REAL_SPEC_CATEGORIES = {
    "saturation", "network_fault", "config_error", "dependency_failure",
    "bad_deploy", "resource_exhaustion", "node_failure", "data_quality",
}


def _load(p):
    with open(p) as f:
        return json.load(f)


def _minimal_validate(instance, schema):
    """Tiny stdlib validator: required, enum, type (str/bool/int/object/array)."""
    errors = []
    req = schema.get("required", [])
    props = schema.get("properties", {})
    for r in req:
        if r not in instance:
            errors.append(f"missing required field: {r}")
    type_map = {
        "string": str, "boolean": bool, "integer": int,
        "object": dict, "array": list, "null": type(None),
    }
    for k, v in instance.items():
        if k not in props:
            continue
        spec = props[k]
        t = spec.get("type")
        types = t if isinstance(t, list) else ([t] if t else [])
        if types:
            py = tuple(type_map[x] for x in types if x in type_map)
            # bool is subclass of int; guard integer fields
            if py and not isinstance(v, py):
                errors.append(f"field {k}: wrong type")
            if "integer" in types and isinstance(v, bool):
                errors.append(f"field {k}: bool is not integer")
        if "enum" in spec and v not in spec["enum"]:
            errors.append(f"field {k}: {v!r} not in enum {spec['enum']}")
        # validate nested 'consent' object
        if spec.get("type") == "object" and isinstance(v, dict):
            errs = _minimal_validate(v, spec)
            errors.extend(f"{k}.{e}" for e in errs)
    return errors


def validate(instance, schema):
    """Return list of error strings ([] == valid)."""
    try:
        import jsonschema  # type: ignore
    except Exception:
        return _minimal_validate(instance, schema)
    v = jsonschema.Draft7Validator(schema)
    return [e.message for e in v.iter_errors(instance)]


def main():
    schema = _load(SCHEMA)
    example = _load(EXAMPLE)
    failures = []

    # T1
    errs = validate(example, schema)
    if errs:
        failures.append(f"T1 example should validate but didn't: {errs}")
    else:
        print("T1 PASS: intake_example.json validates against schema")

    # T2 negative test
    broken = dict(example)
    broken.pop("root_cause", None)
    errs = validate(broken, schema)
    if not errs:
        failures.append("T2 broken example (no root_cause) should FAIL but passed")
    else:
        print("T2 PASS: missing required field correctly rejected")

    # T3 CSV
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    expected_header = {
        "target", "track", "channel", "owner", "status", "first_contact",
        "last_touch", "next_action", "provenance_expected", "incident_id", "notes",
    }
    if set(reader.fieldnames) != expected_header:
        failures.append(f"T3 CSV header mismatch: {reader.fieldnames}")
    bad_status = [r["status"] for r in rows if r["status"] not in STATUS_ENUM]
    bad_track = [r["track"] for r in rows if r["track"] not in TRACK_ENUM]
    if bad_status:
        failures.append(f"T3 bad status values: {bad_status}")
    if bad_track:
        failures.append(f"T3 bad track values: {bad_track}")
    if not bad_status and not bad_track and set(reader.fieldnames) == expected_header:
        print(f"T3 PASS: tracking_sheet.csv parses ({len(rows)} rows), enums valid")

    # T4 category in real-spec set
    if example["category"] not in REAL_SPEC_CATEGORIES:
        failures.append(f"T4 category {example['category']} not in real-spec set")
    else:
        print(f"T4 PASS: category '{example['category']}' is a valid real-spec category")

    if failures:
        print("\nFAILURES:")
        for fmsg in failures:
            print("  -", fmsg)
        sys.exit(1)
    print("\nALL CHECKS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
