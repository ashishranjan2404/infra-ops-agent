#!/usr/bin/env python3
"""A8 — Standalone overlap guard.

Reads heldout_manifest.json (produced by build_heldout_split.py) and the raw
training corpora, then independently re-derives the training incident set and
asserts that NO held-out incident overlaps training under the Tier 1/Tier 2
criteria. This is a *separate* check from the builder so a reviewer can run it
against any manifest, including a hand-edited one.

Exit 0 = clean. Exit 1 = contamination found (prints the offending pairs).
Run:  python3 assert_no_overlap.py [path/to/heldout_manifest.json]
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
TRAIN_FILES = [
    REPO / "opensre-traj/out/trajectories.jsonl",
    REPO / "opensre-traj/out/hud_trajectories.jsonl",
]
COMPANIES = {
    "github", "cloudflare", "slack", "aws", "datadog", "circleci",
    "incidentio", "launchdarkly", "facebook", "knight", "azure", "firefox",
    "gke", "kafka", "redis", "consul", "mysql", "proxysql", "kinesis",
    "dynamodb",
}
STOP = {
    "cache", "cold", "stale", "leak", "cert", "expiry", "expire", "disk",
    "fill", "rollout", "limit", "exhaustion", "exhaust", "starve", "pool",
    "flush", "spike", "delay", "error", "errors", "node", "cpu", "fd",
    "the", "and", "via", "with",
}


def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
def toks(s): return {t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t}
def meaningful(s): return {t for t in toks(s) if t not in STOP}


def train_incidents():
    inc = set()
    for f in TRAIN_FILES:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                d = json.loads(line)
                if d.get("incident"):
                    inc.add(d["incident"])
    return inc


def main():
    mpath = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "heldout_manifest.json"
    manifest = json.loads(mpath.read_text())
    held = manifest["held_out"]
    inc = train_incidents()
    train_norm = {norm(i) for i in inc}
    train_companies = {t for i in inc for t in toks(i) if t in COMPANIES}

    violations = []
    for k in held:
        if norm(k) in train_norm:
            violations.append((k, "exact-id", k))
        for i in inc:
            if len(meaningful(k) & meaningful(i)) >= 2:
                violations.append((k, "pair-overlap", i))
        for c in (toks(k) & COMPANIES):
            if c in train_companies:
                violations.append((k, "company-axis", c))

    print(f"checked {len(held)} held-out incidents against {len(inc)} training incidents")
    if violations:
        print(f"FAIL: {len(violations)} overlap(s):")
        for v in violations:
            print("   ", v)
        return 1
    print("PASS: zero overlap. Held-out set is strictly novel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
