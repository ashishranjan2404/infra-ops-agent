#!/usr/bin/env python3
"""Minimal stdlib-only validator for IncidentRecord against incident_ingest_schema.json.

Supports the subset of JSON-Schema draft-07 we use: required, type, enum, pattern,
minimum/maximum, minItems, properties, items, plus our x-conditional rule
(classification == 'cascade' => why_misleading required). Warns (does not fail) on
tools outside x-recommended-tools.

Usage:
    python3 validate_schema.py incident_ingest_schema.json example_record.json
Exit 0 = valid, non-zero = invalid (with a readable message).
"""
import json
import re
import sys

_TYPES = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool,
}


def _type_ok(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate(node, schema, path, errors):
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} not in enum {schema['enum']}")
        return
    t = schema.get("type")
    if t and not _type_ok(node, t):
        errors.append(f"{path}: expected type {t}, got {type(node).__name__}")
        return
    if t == "string":
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{path}: {node!r} does not match /{schema['pattern']}/")
    if t in ("number", "integer"):
        if "minimum" in schema and node < schema["minimum"]:
            errors.append(f"{path}: {node} < minimum {schema['minimum']}")
        if "maximum" in schema and node > schema["maximum"]:
            errors.append(f"{path}: {node} > maximum {schema['maximum']}")
    if t == "array":
        if "minItems" in schema and len(node) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(node):
                validate(item, item_schema, f"{path}[{i}]", errors)
    if t == "object":
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{path}: missing required key '{req}'")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in node:
                validate(node[key], sub, f"{path}.{key}", errors)


def main():
    if len(sys.argv) != 3:
        print("usage: validate_schema.py <schema.json> <record.json>", file=sys.stderr)
        return 2
    schema = json.load(open(sys.argv[1]))
    record = json.load(open(sys.argv[2]))
    errors = []
    validate(record, schema, "$", errors)

    # x-conditional: cascade requires why_misleading
    if record.get("classification") == "cascade" and not record.get("why_misleading"):
        errors.append("$: classification 'cascade' requires non-empty 'why_misleading'")

    # warn (do not fail) on tools outside recommended vocab
    rec_tools = set(schema.get("x-recommended-tools", []))
    used = []
    for a in record.get("trap_actions", []):
        used.append(a.get("tool"))
    for s in record.get("canonical_fix", {}).get("steps", []):
        used.append(s.get("tool"))
    for tool in used:
        if tool and rec_tools and tool not in rec_tools:
            print(f"WARN: tool '{tool}' not in recommended vocabulary (will need a simulator binding)", file=sys.stderr)

    if errors:
        print(f"INVALID ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1
    print(f"VALID: {record.get('incident_id')} conforms to {schema.get('title')} "
          f"v{record.get('schema_version')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
