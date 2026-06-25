#!/usr/bin/env python3
"""Validate resolve_ai_watchlist.yaml against the G7 spec.

Exit 0 + prints OK on success; raises SystemExit(1) with the offending id/key on failure.
Usage: python3 validate_watchlist.py [path/to/watchlist.yaml]
"""
import sys
import os

try:
    import yaml
except ImportError:
    sys.exit("FAIL: pyyaml not installed (pip install pyyaml)")

REQUIRED_ITEM_KEYS = {"id", "what", "where", "signal", "cadence", "verifiability", "why_it_matters"}
CADENCES = {"daily", "weekly", "monthly", "on-event"}
VERIF = {"high", "medium", "low"}


def fail(msg: str):
    raise SystemExit(f"FAIL: {msg}")


def main(path: str) -> int:
    if not os.path.exists(path):
        fail(f"file not found: {path}")
    with open(path) as f:
        doc = yaml.safe_load(f)

    if not isinstance(doc, dict):
        fail("top-level YAML is not a mapping")

    meta = doc.get("meta")
    if not isinstance(meta, dict):
        fail("missing 'meta' mapping")
    for k in ("target", "as_of", "review_cadence"):
        if not meta.get(k):
            fail(f"meta missing required key: {k}")

    items = doc.get("watch_items")
    if not isinstance(items, list) or len(items) < 7:
        fail(f"watch_items must be a list of length >= 7 (got {len(items) if isinstance(items, list) else type(items)})")

    seen_ids = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"watch_items[{i}] is not a mapping")
        iid = item.get("id", f"<index {i}>")
        missing = REQUIRED_ITEM_KEYS - set(item.keys())
        if missing:
            fail(f"item '{iid}' missing keys: {sorted(missing)}")
        if iid in seen_ids:
            fail(f"duplicate item id: {iid}")
        seen_ids.add(iid)
        if not isinstance(item["where"], list) or not item["where"]:
            fail(f"item '{iid}': 'where' must be a non-empty list")
        if item["cadence"] not in CADENCES:
            fail(f"item '{iid}': cadence '{item['cadence']}' not in {sorted(CADENCES)}")
        if item["verifiability"] not in VERIF:
            fail(f"item '{iid}': verifiability '{item['verifiability']}' not in {sorted(VERIF)}")

    npk = doc.get("not_publicly_knowable")
    if not isinstance(npk, list) or not npk:
        fail("'not_publicly_knowable' must be a non-empty list")

    print(f"OK: {len(items)} watch items, schema valid; {len(npk)} not-knowable entries.")
    return 0


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "resolve_ai_watchlist.yaml")
    sys.exit(main(p))
