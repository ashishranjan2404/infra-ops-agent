#!/usr/bin/env python3
"""A12 — Curriculum ordering (easy -> hard) for the CIDG incident set.

Reads the generated scenario YAMLs + registry under scenarios/cidg/generated/
and produces a deterministic easy->hard ordering. The difficulty signal is a
composite scalar derived ENTIRELY from static structural fields already present
in each scenario spec (no model rollouts needed), so the ordering is reproducible
and cheap. Every component is documented and emitted per-incident so a downstream
curriculum-learning experiment can swap weights or use a single component.

Difficulty components (each normalized into the score):
  topology_size   : len(nodes) + len(edges)            -- bigger graph = harder
  hidden_root     : root_cause.hidden                  -- cause not directly alerting
  cascades        : assertions.cascades                -- failure propagates
  loud_not_cause  : assertions.loudest_alert_not_cause -- loud alert is a victim
  buried_gun      : assertions.buried_gun_exists       -- evidence buried in noise
  buried_depth    : max smoking_guns[].buried_under    -- how deep the evidence sits
  hysteresis      : assertions.hysteresis              -- naive fix is sticky/worsens
  mon_degrades    : assertions.monitoring_degrades     -- observability itself fails
  n_red_herrings  : len(registry.red_herrings)         -- distractor count
  n_slo           : len(slo)                            -- breadth of impact
  multi_fix       : len(canonical_fix.steps) > 1       -- multi-step remediation

Usage:
    python3 build_curriculum.py            # writes curriculum_order.json next to this file
    python3 build_curriculum.py --print    # also print the table to stdout
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
# repo root is .../rl ; this file lives at rl/experiments/ralph_outputs/A12/artifacts/
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
GEN = os.path.join(REPO, "scenarios", "cidg", "generated")
OUT = os.path.join(HERE, "curriculum_order.json")

# Weights for the composite difficulty signal. Boolean "trap" properties that
# make naive RCA fail dominate; raw size is a gentle tiebreaker.
W = {
    "topology_size": 0.6,   # per (node+edge) unit, scaled below
    "hidden_root": 2.0,
    "cascades": 1.5,
    "loud_not_cause": 2.5,
    "buried_gun": 1.5,
    "buried_depth": 0.04,   # per unit of buried_under
    "hysteresis": 2.0,
    "mon_degrades": 1.5,
    "n_red_herrings": 0.4,  # per herring
    "n_slo": 0.3,           # per SLO
    "multi_fix": 1.0,
}


def _load_registry() -> dict:
    with open(os.path.join(GEN, "registry.json")) as f:
        reg = json.load(f)
    # index registry by yaml basename for joining red_herrings/family
    by_path = {}
    for key, v in reg.items():
        by_path[os.path.basename(v["path"])] = (key, v)
    return by_path


def _features(spec: dict, reg_entry: tuple | None) -> dict:
    topo = spec.get("topology", {}) or {}
    nodes = topo.get("nodes", []) or []
    edges = topo.get("edges", []) or []
    rc = spec.get("root_cause", {}) or {}
    asrt = spec.get("assertions", {}) or {}
    obs = spec.get("observation", {}) or {}
    slo = spec.get("slo", []) or []
    fix = (spec.get("canonical_fix", {}) or {}).get("steps", []) or []
    guns = obs.get("smoking_guns", []) or []
    buried_depth = max([g.get("buried_under", 0) for g in guns], default=0)
    n_herrings = 0
    if reg_entry is not None:
        n_herrings = len(reg_entry[1].get("red_herrings", []) or [])
    return {
        "topology_size": len(nodes) + len(edges),
        "hidden_root": int(bool(rc.get("hidden"))),
        "cascades": int(bool(asrt.get("cascades"))),
        "loud_not_cause": int(bool(asrt.get("loudest_alert_not_cause"))),
        "buried_gun": int(bool(asrt.get("buried_gun_exists"))),
        "buried_depth": buried_depth,
        "hysteresis": int(bool(asrt.get("hysteresis"))),
        "mon_degrades": int(bool(asrt.get("monitoring_degrades"))),
        "n_red_herrings": n_herrings,
        "n_slo": len(slo),
        "multi_fix": int(len(fix) > 1),
    }


def _score(feat: dict) -> float:
    s = 0.0
    for k, w in W.items():
        s += w * feat[k]
    return round(s, 4)


def build() -> dict:
    by_path = _load_registry()
    rows = []
    for fn in sorted(os.listdir(GEN)):
        if not fn.endswith(".yaml"):
            continue
        with open(os.path.join(GEN, fn)) as f:
            spec = yaml.safe_load(f)
        reg_entry = by_path.get(fn)
        meta = spec.get("meta", {}) or {}
        # canonical incident id: registry key if present, else meta.id
        inc_id = reg_entry[0] if reg_entry else meta.get("id", fn[:-5])
        family = reg_entry[1].get("family") if reg_entry else "unknown"
        feat = _features(spec, reg_entry)
        rows.append({
            "id": inc_id,
            "yaml": fn,
            "title": meta.get("title", ""),
            "family": family,
            "failure_class": meta.get("failure_class", ""),
            "difficulty": _score(feat),
            "features": feat,
        })
    # easy -> hard; stable tiebreak on id for determinism
    rows.sort(key=lambda r: (r["difficulty"], r["id"]))
    for i, r in enumerate(rows):
        r["rank"] = i
    return {
        "signal": "composite static-structural difficulty score (see weights)",
        "weights": W,
        "order_easy_to_hard": [r["id"] for r in rows],
        "n": len(rows),
        "incidents": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true", dest="show")
    args = ap.parse_args()
    data = build()
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT}  ({data['n']} incidents)")
    if args.show:
        print(f"\n{'rank':>4} {'diff':>6}  {'family':10} id")
        for r in data["incidents"]:
            print(f"{r['rank']:>4} {r['difficulty']:>6.2f}  {r['family']:10} {r['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
