#!/usr/bin/env python3
"""A7 — Incident difficulty scoring (sidecar, non-mutating).

Reads scenarios/cidg/generated/*.yaml and computes two difficulty metadata
fields per incident WITHOUT modifying the source YAMLs:

  * trap_complexity   in [0,1] — how hard it is to AVOID the wrong move and
                       FIND the real root cause (structural trap density).
  * expected_pass_rate in [0,1] — model-agnostic prior probability that an
                       agent resolves the incident on a single attempt.

Emits a difficulty_scores.json (full breakdown) and difficulty_scores.csv
(flat table) into this artifacts dir. Pure stdlib + pyyaml. Deterministic.

The mapping is a transparent, hand-justified heuristic (no hidden weights):
each contributing signal is documented in COMPONENTS below so a reviewer can
audit exactly why an incident scored as it did.
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SCEN_GLOB = os.path.join(REPO, "scenarios", "cidg", "generated", "*.yaml")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def trap_complexity(d: dict) -> tuple[float, dict]:
    """Structural trap density: bigger/cascading/hidden/buried -> harder.

    Each term is normalized to roughly [0,1] then weight-averaged. Returns the
    score plus the per-component breakdown for auditability.
    """
    topo = d.get("topology", {}) or {}
    nodes = topo.get("nodes", []) or []
    edges = topo.get("edges", []) or []
    rc = d.get("root_cause", {}) or {}
    obs = d.get("observation", {}) or {}
    asrt = d.get("assertions", {}) or {}
    traps = d.get("trap_actions", []) or []
    guns = obs.get("smoking_guns", []) or []

    # buried depth: how far the real evidence is hidden under noise (0 if none)
    max_buried = max((g.get("buried_under", 0) or 0) for g in guns) if guns else 0

    c = {
        # topology surface: more nodes/edges => more places to look / mislead
        "topology": clamp((len(nodes) - 1) / 6.0) * 0.18,
        "fanout": clamp(len(edges) / 6.0) * 0.10,
        # the classic traps from the assertions block
        "cascades": (0.16 if asrt.get("cascades") else 0.0),
        "loudest_not_cause": (0.16 if asrt.get("loudest_alert_not_cause") else 0.0),
        "hidden_root": (0.12 if rc.get("hidden") else 0.0),
        "buried_gun": clamp(max_buried / 50.0) * 0.12,
        "hysteresis": (0.06 if asrt.get("hysteresis") else 0.0),
        "monitoring_degrades": (0.06 if asrt.get("monitoring_degrades") else 0.0),
        # explicit wrong-move bait + severity of the fault
        "trap_actions": clamp(len(traps) / 3.0) * 0.06,
        "severity": clamp(float(rc.get("severity", 0.0))) * 0.06,
    }
    score = clamp(sum(c.values()))
    return round(score, 4), {k: round(v, 4) for k, v in c.items()}


def expected_pass_rate(d: dict, tc: float) -> tuple[float, dict]:
    """Prior single-attempt success probability.

    Anchored at a high base for a trivial incident, then penalized by trap
    complexity and additional execution-difficulty signals (multi-step fixes,
    flappy dynamics, multiple SLOs to satisfy at once).
    """
    cf = d.get("canonical_fix", {}) or {}
    steps = cf.get("steps", []) or []
    chance = d.get("chance", {}) or {}
    slos = d.get("slo", []) or []

    base = 0.92  # a clean, single-service, single-step incident
    pen = {
        # the dominant penalty: structural trap complexity
        "trap_complexity": tc * 0.55,
        # multi-step / ordered fixes are harder to land correctly
        "fix_steps": clamp((len(steps) - 1) / 4.0) * 0.10,
        # noisy dynamics make signals/fixes unreliable
        "flap": clamp(float(chance.get("flap_prob", 0.0)) / 0.2) * 0.05,
        "partial_recovery": clamp(float(chance.get("partial_recovery_prob", 0.0))) * 0.06,
        # more simultaneous SLOs to clear => harder to fully resolve
        "multi_slo": clamp((len(slos) - 1) / 3.0) * 0.06,
    }
    score = clamp(base - sum(pen.values()))
    return round(score, 4), {k: round(v, 4) for k, v in pen.items()}


def bucket(epr: float) -> str:
    if epr >= 0.70:
        return "easy"
    if epr >= 0.45:
        return "medium"
    return "hard"


def main() -> int:
    paths = sorted(glob.glob(SCEN_GLOB))
    if not paths:
        sys.exit(f"no scenarios found at {SCEN_GLOB}")

    rows = []
    for p in paths:
        with open(p) as fh:
            d = yaml.safe_load(fh)
        meta = d.get("meta", {}) or {}
        tc, tc_break = trap_complexity(d)
        epr, epr_break = expected_pass_rate(d, tc)
        rows.append({
            "file": os.path.basename(p),
            "id": meta.get("id", ""),
            "failure_class": meta.get("failure_class", ""),
            "title": meta.get("title", ""),
            "trap_complexity": tc,
            "expected_pass_rate": epr,
            "difficulty_bucket": bucket(epr),
            "trap_breakdown": tc_break,
            "pass_rate_penalties": epr_break,
        })

    rows.sort(key=lambda r: r["expected_pass_rate"])

    json_path = os.path.join(OUT_DIR, "difficulty_scores.json")
    with open(json_path, "w") as fh:
        json.dump({
            "schema": {
                "trap_complexity": "0..1 structural trap density (higher=trappier)",
                "expected_pass_rate": "0..1 prior single-attempt resolve probability",
                "difficulty_bucket": "easy>=0.70 | medium>=0.45 | hard<0.45 on expected_pass_rate",
            },
            "count": len(rows),
            "scores": rows,
        }, fh, indent=2)

    csv_path = os.path.join(OUT_DIR, "difficulty_scores.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "id", "failure_class", "trap_complexity",
                    "expected_pass_rate", "difficulty_bucket"])
        for r in rows:
            w.writerow([r["file"], r["id"], r["failure_class"],
                        r["trap_complexity"], r["expected_pass_rate"],
                        r["difficulty_bucket"]])

    # console summary
    n = len(rows)
    eprs = [r["expected_pass_rate"] for r in rows]
    tcs = [r["trap_complexity"] for r in rows]
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for r in rows:
        counts[r["difficulty_bucket"]] += 1
    print(f"scored {n} incidents")
    print(f"  expected_pass_rate: min={min(eprs):.3f} mean={sum(eprs)/n:.3f} max={max(eprs):.3f}")
    print(f"  trap_complexity:    min={min(tcs):.3f} mean={sum(tcs)/n:.3f} max={max(tcs):.3f}")
    print(f"  buckets: easy={counts['easy']} medium={counts['medium']} hard={counts['hard']}")
    print("  hardest 5:")
    for r in rows[:5]:
        print(f"    {r['id']:<28} epr={r['expected_pass_rate']:.3f} tc={r['trap_complexity']:.3f} [{r['failure_class']}]")
    print("  easiest 5:")
    for r in rows[-5:]:
        print(f"    {r['id']:<28} epr={r['expected_pass_rate']:.3f} tc={r['trap_complexity']:.3f} [{r['failure_class']}]")
    print(f"wrote {json_path}")
    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
