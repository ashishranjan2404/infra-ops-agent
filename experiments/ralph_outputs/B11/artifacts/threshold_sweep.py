#!/usr/bin/env python3
"""B11 — pass-threshold robustness sweep.

Grounds in rex/scoring.py (graded reward in [0,1]) and the pass-cutoff used in
rex/eval_pass_at_k.py / experiments/compute_pass_at_k.py:

    binary_pass(reward, threshold) := 1 if reward >= threshold else 0  (THRESHOLD=0.8 default)

The headline ablation ("REx lifts every model") binarises a continuous reward at a
SINGLE cutoff of 0.80. A reviewer's obvious attack: "you tuned the threshold to make
REx win." This script answers that by re-binarising the SAME real per-attempt reward
data at multiple thresholds {0.70, 0.80, 0.86, 0.90} and reporting the per-arm
pass-rate + the REx-vs-best-control GAP at every cutoff. If the ordering (and the gap)
is stable across thresholds, the result is robust to the (arbitrary) choice of 0.80.

INPUT  (real data, not synthetic): rex/runs/ablation.json
  per_incident[arm][incident] = [reward_seed0, reward_seed1, ...]  (graded, in [0,1])
  Produced by `python3 -m rex.ablation` — claude-haiku-4-5, N=4, 3 seeds, 5 hard
  cascades, scored with the deterministic P0 judge.

This script DOES NOT edit any shared core file. It only re-reads ablation.json and
re-applies the threshold; the reward generation is untouched.

Usage:
    python3 threshold_sweep.py \
        --in /Users/mei/rl/rex/runs/ablation.json \
        --out /Users/mei/rl/experiments/ralph_outputs/B11/artifacts/robustness.json \
        --thresholds 0.7 0.8 0.86 0.9
"""
from __future__ import annotations

import argparse
import json
import math
import os


# -- estimators copied (NOT imported) so the artifact is self-contained & doesn't
#    touch shared modules. Identical math to experiments/compute_pass_at_k.py.
def binary_pass(reward: float, threshold: float) -> int:
    """Graded reward -> binary pass. Mirrors rex/eval_pass_at_k.binary_pass."""
    return 1 if reward >= threshold else 0


def wilson_ci(p: float, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (round(max(0.0, center - spread), 4), round(min(1.0, center + spread), 4))


def arm_rewards(per_incident: dict) -> dict:
    """Flatten {arm: {incident: [rewards]}} -> {arm: [all rewards]}."""
    return {arm: [v for lst in inc.values() for v in lst]
            for arm, inc in per_incident.items()}


def sweep(per_incident: dict, thresholds: list) -> dict:
    # defensive shape check (05_ouroboros, Engineer A): {arm: {incident: [floats]}}
    assert isinstance(per_incident, dict) and per_incident, "per_incident empty/not a dict"
    for arm, inc in per_incident.items():
        assert isinstance(inc, dict) and inc, f"arm {arm!r} not a dict of incidents"
        for k, lst in inc.items():
            assert isinstance(lst, list) and lst, f"{arm}/{k} not a non-empty list"
    rewards = arm_rewards(per_incident)
    arms = list(rewards.keys())
    # the "best control" = best non-rex arm (the fair-control claim is rex vs these)
    controls = [a for a in arms if not a.startswith("rex")]

    rows = {}
    for thr in thresholds:
        per_arm = {}
        for arm, rs in rewards.items():
            n = len(rs)
            c = sum(binary_pass(r, thr) for r in rs)
            p = c / n if n else 0.0
            lo, hi = wilson_ci(p, n)
            per_arm[arm] = {"n": n, "passes": c, "pass_rate": round(p, 4),
                            "wilson95": [lo, hi]}
        best_ctrl = max(controls, key=lambda a: per_arm[a]["pass_rate"]) if controls else None
        rex_pr = per_arm.get("rex", {}).get("pass_rate", 0.0)
        ctrl_pr = per_arm[best_ctrl]["pass_rate"] if best_ctrl else 0.0
        rows[f"{thr:.2f}"] = {
            "per_arm": per_arm,
            "best_control": best_ctrl,
            "rex_pass_rate": round(rex_pr, 4),
            "best_control_pass_rate": round(ctrl_pr, 4),
            "rex_minus_best_control": round(rex_pr - ctrl_pr, 4),
            "rex_wins": rex_pr > ctrl_pr,
        }
    return rows


def render_table(rows: dict, arms: list) -> str:
    thrs = list(rows.keys())
    w = 16
    head = "arm".ljust(w) + "".join(f"thr={t}".rjust(12) for t in thrs)
    lines = [head, "-" * len(head)]
    for arm in arms:
        line = arm.ljust(w)
        for t in thrs:
            pr = rows[t]["per_arm"][arm]["pass_rate"]
            line += f"{pr:.2f}".rjust(12)
        lines.append(line)
    lines.append("-" * len(head))
    gap = "REx - best ctrl".ljust(w) + "".join(
        f"{rows[t]['rex_minus_best_control']:+.2f}".rjust(12) for t in thrs)
    lines.append(gap)
    wins = "REx wins?".ljust(w) + "".join(
        ("yes" if rows[t]["rex_wins"] else "NO").rjust(12) for t in thrs)
    lines.append(wins)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default="/Users/mei/rl/rex/runs/ablation.json")
    ap.add_argument("--out", dest="out",
                    default="/Users/mei/rl/experiments/ralph_outputs/B11/artifacts/robustness.json")
    ap.add_argument("--thresholds", nargs="+", type=float,
                    default=[0.7, 0.8, 0.86, 0.9])
    args = ap.parse_args()

    with open(args.inp) as f:
        data = json.load(f)
    per_incident = data["per_incident"]
    arms = list(per_incident.keys())

    rows = sweep(per_incident, args.thresholds)
    table = render_table(rows, arms)

    out = {
        "_source": os.path.relpath(args.inp, "/Users/mei/rl"),
        "model": data.get("model"),
        "seeds": data.get("seeds"),
        "N": data.get("N"),
        "incidents": data.get("incidents"),
        "n_attempts_per_arm": len(arm_rewards(per_incident)[arms[0]]),
        "thresholds": args.thresholds,
        "arms": arms,
        "rows": rows,
        "robust": all(r["rex_wins"] for r in rows.values()),
        "table": table,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(table)
    print()
    print(f"robust (REx wins at every threshold): {out['robust']}")
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
