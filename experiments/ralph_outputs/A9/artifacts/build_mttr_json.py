#!/usr/bin/env python3
"""Build mttr_labels.json sidecar from mttr_labels.csv (CSV is source of truth).

Usage:
    python3 build_mttr_json.py [--check]

--check  validates the CSV (schema, value ranges, confidence enum) and exits
         non-zero on any problem WITHOUT writing the JSON.

Task A9 (SRE-Degrees): label each incident with real-world MTTR from its source
postmortem for downstream correlation analysis. Unknown MTTR is preserved as
null (never invented).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "mttr_labels.csv")
JSON_PATH = os.path.join(HERE, "mttr_labels.json")

VALID_CONFIDENCE = {"high", "medium", "low", "unknown", "not_applicable"}
EXPECTED_COLS = [
    "incident_id", "yaml_file", "title", "is_real_incident",
    "mttr_minutes", "mttr_basis", "source_citation", "confidence", "notes",
]


def _parse_bool(s: str) -> bool:
    return str(s).strip().lower() in ("true", "1", "yes")


def _parse_mttr(s: str):
    s = (s or "").strip()
    if s == "":
        return None
    return float(s)


def load_rows():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLS:
            raise ValueError(
                f"CSV header mismatch.\n  got: {reader.fieldnames}\n  exp: {EXPECTED_COLS}"
            )
        return list(reader)


def to_records(rows):
    out = []
    for r in rows:
        out.append({
            "incident_id": r["incident_id"].strip(),
            "yaml_file": r["yaml_file"].strip(),
            "title": r["title"].strip(),
            "is_real_incident": _parse_bool(r["is_real_incident"]),
            "mttr_minutes": _parse_mttr(r["mttr_minutes"]),
            "mttr_basis": r["mttr_basis"].strip(),
            "source_citation": r["source_citation"].strip(),
            "confidence": r["confidence"].strip(),
            "notes": r["notes"].strip(),
        })
    return out


def validate(records):
    errors = []
    seen = set()
    for rec in records:
        iid = rec["incident_id"]
        if not iid:
            errors.append("empty incident_id")
        if iid in seen:
            errors.append(f"duplicate incident_id: {iid}")
        seen.add(iid)
        if rec["confidence"] not in VALID_CONFIDENCE:
            errors.append(f"{iid}: bad confidence '{rec['confidence']}'")
        m = rec["mttr_minutes"]
        if m is not None and (m <= 0 or m > 100000):
            errors.append(f"{iid}: mttr_minutes out of range: {m}")
        # invariant: a known MTTR must carry a non-'unknown'/'na' confidence
        if m is not None and rec["confidence"] in ("unknown", "not_applicable"):
            errors.append(f"{iid}: has MTTR but confidence={rec['confidence']}")
        # invariant: not_applicable rows are the non-real ones
        if rec["confidence"] == "not_applicable" and rec["is_real_incident"]:
            errors.append(f"{iid}: not_applicable but flagged real")
    return errors


def summarize(records):
    n = len(records)
    real = [r for r in records if r["is_real_incident"]]
    labeled = [r for r in records if r["mttr_minutes"] is not None]
    unknown_real = [r for r in real if r["mttr_minutes"] is None]
    return {
        "total_incidents": n,
        "real_incidents": len(real),
        "synthetic_incidents": n - len(real),
        "mttr_labeled": len(labeled),
        "real_but_unknown_mttr": len(unknown_real),
        "coverage_of_real_pct": round(100.0 * len(labeled) / max(1, len(real)), 1),
    }


def main():
    check = "--check" in sys.argv
    records = to_records(load_rows())
    errors = validate(records)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    summary = summarize(records)
    if check:
        print("VALIDATION OK")
        print(json.dumps(summary, indent=2))
        return
    payload = {
        "schema_version": 1,
        "task": "A9-mttr-labels",
        "description": "Real-world MTTR labels for CIDG incidents (correlation analysis).",
        "summary": summary,
        "incidents": records,
    }
    with open(JSON_PATH, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"wrote {JSON_PATH}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
