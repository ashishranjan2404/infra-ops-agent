#!/usr/bin/env python3
"""Validate G6 sources/claims artifacts. Exit 0 + 'VALIDATE PASS' on success.

Checks (from 04_spec + 05_ouroboros):
  1. sources.json parses; every url is https; ids unique and match ^S\\d+$.
  2. claims_table.csv parses; no empty claim/source_id.
  3. every claim.source_id resolves to a sources.json id (HARD fail on dangling).
  4. type enum enforced; >=1 each of capability and quant; >=1 of the limit/gap types.
  5. required repo file paths referenced as differentiators actually exist.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # -> /Users/mei/rl
SOURCES = os.path.join(HERE, "sources.json")
CLAIMS = os.path.join(HERE, "claims_table.csv")

ALLOWED_TYPES = {"capability", "quant", "acknowledged_limit", "not_disclosed", "structural"}
GAP_TYPES = {"acknowledged_limit", "not_disclosed", "structural"}
REQUIRED_REPO_FILES = ["rex/scoring.py", "rex/escalate.py", "rex/loop.py",
                       "sim/engine.py", "ARCHITECTURE.md", "agent/llm.py"]


def load_sources(path: str) -> dict[str, dict]:
    with open(path) as f:
        data = json.load(f)
    out: dict[str, dict] = {}
    for s in data["sources"]:
        sid = s["id"]
        assert re.match(r"^S\d+$", sid), f"bad source id: {sid}"
        assert sid not in out, f"duplicate source id: {sid}"
        assert s["url"].startswith("https://"), f"non-https url: {s['url']}"
        out[sid] = s
    return out


def load_claims(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def validate() -> int:
    errors: list[str] = []
    sources = load_sources(SOURCES)
    claims = load_claims(CLAIMS)

    types_seen: set[str] = set()
    for i, row in enumerate(claims, 1):
        if not (row.get("claim") or "").strip():
            errors.append(f"row {i}: empty claim")
        sid = (row.get("source_id") or "").strip()
        if not sid:
            errors.append(f"row {i}: empty source_id")
        elif sid not in sources:
            errors.append(f"row {i}: dangling source_id {sid!r}")
        t = (row.get("type") or "").strip()
        if t not in ALLOWED_TYPES:
            errors.append(f"row {i}: bad type {t!r}")
        types_seen.add(t)

    if "capability" not in types_seen:
        errors.append("no 'capability' claim present")
    if "quant" not in types_seen:
        errors.append("no 'quant' claim present")
    if not (types_seen & GAP_TYPES):
        errors.append("no gap/limit claim present")

    for rel in REQUIRED_REPO_FILES:
        if not os.path.exists(os.path.join(REPO, rel)):
            errors.append(f"differentiator cites missing repo file: {rel}")

    if errors:
        print("VALIDATE FAIL")
        for e in errors:
            print("  -", e)
        return 1
    print(f"VALIDATE PASS  ({len(sources)} sources, {len(claims)} claims, "
          f"types={sorted(types_seen)})")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
