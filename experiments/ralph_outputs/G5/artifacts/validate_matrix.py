#!/usr/bin/env python3
"""Structural validator for the G5 positioning matrix.

Scope (honest): this proves CITATION HYGIENE + vendor-flag discipline, NOT factual accuracy.
- Every competitor data cell carries >=1 [Sn] tag.
- Every [Sn] tag used resolves to a source in sources.json.
- Every source has the 5 required fields and a non-empty url.
- Commercial vendor columns (Komodor, Datadog) cite >=1 source flagged 'vendor-stated'.

Usage:
  python3 validate_matrix.py            # validate sibling positioning_matrix.md + sources.json
  python3 validate_matrix.py --selftest # run T1..T4 on inline fixtures
Exit 0 = pass, 1 = fail.
"""
import json
import os
import re
import sys

TAG_RE = re.compile(r"\[S\d+\]")
DIMENSIONS = ["Open benchmark", "Trap-action safety", "Training method",
              "Deployment posture", "Evaluation rigor"]
REQUIRED_FIELDS = ["url", "who", "claim", "verification", "as_of"]
# column index (after leading empty) -> competitor key
COLS = {1: "us", 2: "sregym", 3: "komodor", 4: "datadog"}
VENDOR_COLS = {"komodor": "Komodor", "datadog": "Datadog Bits AI"}


def load_sources(path):
    with open(path) as f:
        return json.load(f).get("sources", {})


def extract_tags(text):
    return set(t.strip("[]") for t in TAG_RE.findall(text))


def parse_matrix(md):
    """Return list of dim-row dicts from the one 5-dimension table."""
    rows = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        name = cells[0].strip("* ")
        if name in DIMENSIONS:
            if len(cells) != 5:
                raise ValueError(f"row '{name}' has {len(cells)} cells, expected 5: {line}")
            rows.append({"dimension": name, "cells": cells})
    return rows


def validate(md_path, src_path):
    errors = []
    with open(md_path) as f:
        md = f.read()
    sources = load_sources(src_path)

    # C4: source integrity
    for sid, s in sources.items():
        for fld in REQUIRED_FIELDS:
            if not s.get(fld):
                errors.append(f"source {sid} missing/empty field '{fld}'")

    # C1: structure
    try:
        rows = parse_matrix(md)
    except ValueError as e:
        return [str(e)]
    if len(rows) != 5:
        errors.append(f"expected 5 dimension rows, found {len(rows)}")

    # C2 + C3: per competitor cell tags resolve
    for r in rows:
        for idx, col in COLS.items():
            cell = r["cells"][idx]
            tags = extract_tags(cell)
            if not tags:
                errors.append(f"cell [{r['dimension']} / {col}] has no [Sn] citation")
            for t in tags:
                if t not in sources:
                    errors.append(f"unresolved tag {t} in [{r['dimension']} / {col}]")

    # C5: vendor honesty guard
    for r in rows:
        for col_key, label in VENDOR_COLS.items():
            idx = [k for k, v in COLS.items() if v == col_key][0]
            for t in extract_tags(r["cells"][idx]):
                if t in sources and sources[t].get("verification") == "vendor-stated":
                    VENDOR_COLS_SEEN.add(col_key)
    for col_key, label in VENDOR_COLS.items():
        if col_key not in VENDOR_COLS_SEEN:
            errors.append(f"vendor column '{label}' never cites a 'vendor-stated' source")

    return errors


VENDOR_COLS_SEEN = set()


def _selftest():
    good_src = {"sources": {
        "S1": {"url": "x", "who": "us", "claim": "c", "verification": "self-reported", "as_of": "2026-06"},
        "S5": {"url": "x", "who": "Komodor", "claim": "c", "verification": "vendor-stated", "as_of": "2025-11"},
        "S8": {"url": "x", "who": "Datadog", "claim": "c", "verification": "vendor-stated", "as_of": "2025-12"},
    }}
    base = ("| Dimension | us | SREGym | Komodor | Datadog Bits AI |\n"
            "|---|---|---|---|---|\n")
    rows = "".join(
        f"| **{d}** | a [S1] | b [S1] | c [S5] | d [S8] |\n" for d in DIMENSIONS)
    import tempfile
    failures = []

    def run(md_text, src_obj, label, expect_ok):
        global VENDOR_COLS_SEEN
        VENDOR_COLS_SEEN = set()
        with tempfile.TemporaryDirectory() as d:
            mp = os.path.join(d, "m.md"); sp = os.path.join(d, "s.json")
            open(mp, "w").write(md_text); json.dump(src_obj, open(sp, "w"))
            errs = validate(mp, sp)
            ok = (len(errs) == 0)
            status = "PASS" if ok == expect_ok else "FAIL"
            print(f"  [{status}] {label}: errors={errs[:2]}")
            if ok != expect_ok:
                failures.append(label)

    run(base + rows, good_src, "T1 happy path -> clean", True)
    bad = base + "| **Open benchmark** | a | b [S1] | c [S5] | d [S8] |\n" + \
        "".join(f"| **{d}** | a [S1] | b [S1] | c [S5] | d [S8] |\n" for d in DIMENSIONS[1:])
    run(bad, good_src, "T2 missing tag -> fail", False)
    bad3 = base + "".join(
        f"| **{d}** | a [S99] | b [S1] | c [S5] | d [S8] |\n" for d in DIMENSIONS)
    run(bad3, good_src, "T3 unresolved tag -> fail", False)
    bad_src = json.loads(json.dumps(good_src)); bad_src["sources"]["S1"]["url"] = ""
    run(base + rows, bad_src, "T4 source missing url -> fail", False)
    return failures


def main():
    if "--selftest" in sys.argv:
        print("selftest:")
        fails = _selftest()
        sys.exit(1 if fails else 0)
    here = os.path.dirname(os.path.abspath(__file__))
    md = os.path.join(here, "positioning_matrix.md")
    src = os.path.join(here, "sources.json")
    errs = validate(md, src)
    if errs:
        print("VALIDATION FAILED:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print("VALIDATION PASSED: 5 dimensions x 4 columns, all cells cited, all tags resolve, "
          "both vendor columns carry a 'vendor-stated' flag.")
    sys.exit(0)


if __name__ == "__main__":
    main()
