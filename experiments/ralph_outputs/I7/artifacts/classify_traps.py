#!/usr/bin/env python3
"""I7 artifact: classify each scenario's trap action into a named trap taxonomy.

Read-only over the repo. For every generated scenario YAML that declares
`trap_actions`, map the trap *tool* onto one of four taxonomy categories:

    scale-trap     — adding replicas / capacity to a fault that capacity cannot fix
    restart-trap   — bouncing a process/pod/service without removing the root cause
    rollback-trap  — reverting a deployment when the active deploy is NOT the cause
    failover-trap  — flipping to a standby/secondary that shares the same fault

A fifth bucket, `other-trap`, catches any trap tool we have not mapped yet, so the
classifier degrades honestly instead of silently dropping rows.

The category map is GROUNDED in rex/scoring.py:
  - `_traps_in()` defines a trap purely by (tool, target) match against the
    scenario's declared `trap_actions` — so the *tool* is the load-bearing signal,
    which is exactly what we classify on.
  - the `why`-table in `format_feedback()` names `scale_deployment`,
    `restart_service` and `clear_cache` explicitly; we reuse those penalties' intent.

If G4's `trap_taxonomy.json` is present we reuse its per-scenario records as the input
set (so we agree on which files have traps); otherwise we re-scan the YAMLs directly.

Usage:
    python3 classify_traps.py [REPO_ROOT] [OUT_JSON]
Defaults: REPO_ROOT=/Users/mei/rl  OUT=<this dir>/trap_classification.json
Exit code 0 on success; 2 if no traps were found at all.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

import yaml

DEFAULT_REPO = "/Users/mei/rl"
_HERE = os.path.dirname(os.path.abspath(__file__))

# Tool -> taxonomy category. The four categories the task asks for, plus a catch-all.
TOOL_TO_CATEGORY = {
    "scale_deployment": "scale-trap",
    "restart_service": "restart-trap",
    "restart_pod": "restart-trap",
    "rollback_deployment": "rollback-trap",
    # failover-class tools (none present in the current corpus, but mapped so the
    # taxonomy is complete and future scenarios classify without code changes):
    "failover": "failover-trap",
    "promote_replica": "failover-trap",
    "switch_to_standby": "failover-trap",
    "drain_node": "failover-trap",
}

CATEGORIES = ["scale-trap", "restart-trap", "rollback-trap", "failover-trap", "other-trap"]


def classify_tool(tool: str) -> str:
    return TOOL_TO_CATEGORY.get(tool, "other-trap")


def _records_from_g4(repo: str):
    """Reuse G4's extracted records if present: [(file, scenario_id, fault_node, tool, target)]."""
    g4 = os.path.join(repo, "experiments/ralph_outputs/G4/artifacts/trap_taxonomy.json")
    if not os.path.exists(g4):
        return None
    try:
        data = json.load(open(g4))
    except (OSError, ValueError):
        return None
    out = []
    for r in data.get("records", []):
        trap = r.get("trap") or {}
        out.append({
            "file": r.get("file"),
            "scenario_id": r.get("scenario_id"),
            "fault_node": r.get("fault_node"),
            "tool": trap.get("tool"),
            "target": trap.get("target"),
        })
    return out or None


def _records_from_yaml(repo: str):
    """Fallback: scan generated YAMLs directly for declared trap_actions."""
    out = []
    pat = os.path.join(repo, "scenarios/cidg/generated/*.yaml")
    for path in sorted(glob.glob(pat)):
        try:
            doc = yaml.safe_load(open(path)) or {}
        except (OSError, yaml.YAMLError):
            continue
        traps = doc.get("trap_actions") or []
        if not traps:
            continue
        meta = doc.get("meta") or {}
        rc = doc.get("root_cause") or {}
        # first declared trap is the canonical one for this scenario
        t = traps[0] or {}
        out.append({
            "file": os.path.basename(path),
            "scenario_id": meta.get("id"),
            "fault_node": rc.get("location"),
            "tool": (t.get("tool")),
            "target": (t.get("args") or {}).get("target"),
        })
    return out


def build(repo: str) -> dict:
    records = _records_from_g4(repo)
    source = "G4/trap_taxonomy.json"
    if records is None:
        records = _records_from_yaml(repo)
        source = "scenarios/cidg/generated/*.yaml (direct scan)"

    counts = collections.Counter()
    by_class = collections.defaultdict(lambda: collections.Counter())
    classified = []
    for r in records:
        cat = classify_tool(r["tool"])
        counts[cat] += 1
        if r.get("scenario_id"):
            # failure_class isn't in G4 minimal record; derive from file tail is noisy,
            # so we only cross-tab when present. Keep simple: tally per category only.
            pass
        classified.append({**r, "category": cat})

    # ensure all categories appear (even at 0) so the distribution is honest about gaps
    dist = {c: counts.get(c, 0) for c in CATEGORIES}
    total = sum(dist.values())
    skew = (max(dist.values()) / total) if total else 0.0
    dominant = max(dist, key=dist.get) if total else None

    return {
        "input_source": source,
        "n_scenarios_with_trap": total,
        "categories": CATEGORIES,
        "tool_to_category": TOOL_TO_CATEGORY,
        "distribution": dist,
        "dominant_category": dominant,
        "skew_fraction": round(skew, 4),
        "empty_categories": [c for c, n in dist.items() if n == 0],
        "records": classified,
    }


def main(argv):
    repo = argv[1] if len(argv) > 1 else DEFAULT_REPO
    out = argv[2] if len(argv) > 2 else os.path.join(_HERE, "trap_classification.json")
    result = build(repo)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)

    d = result["distribution"]
    print(f"input: {result['input_source']}")
    print(f"scenarios with a trap: {result['n_scenarios_with_trap']}")
    print("counts per category:")
    for c in CATEGORIES:
        bar = "#" * d[c]
        print(f"  {c:14s} {d[c]:3d}  {bar}")
    print(f"dominant: {result['dominant_category']} "
          f"({result['skew_fraction']*100:.1f}% of all traps)")
    if result["empty_categories"]:
        print(f"EMPTY (no coverage): {', '.join(result['empty_categories'])}")
    print(f"wrote {out}")
    return 0 if result["n_scenarios_with_trap"] else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
