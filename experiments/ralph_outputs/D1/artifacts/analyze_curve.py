#!/usr/bin/env python3
"""D1 — RFT training-curve analyzer.

Reads a per-step JSONL emitted by train_rft.py / train_rft_v2.py
(each line: {"step", "mean_reward", "reward_std"?, "n", ...}) and reports:
  - first/last mean_reward and the delta
  - OLS slope per step + extrapolation to a target horizon
  - whether the trend is "continuing", "flat", or "reversed" vs a threshold

Pure stdlib; no HUD/network. Used to judge if the +0.037 trend holds at 50 steps.

  python3 analyze_curve.py ../../../../opensre-traj/runs/train_qwen3-8b_v2.jsonl --horizon 50
"""
from __future__ import annotations
import argparse, json, sys


def ols_slope(xs, ys):
    n = len(xs)
    xm = sum(xs) / n
    ym = sum(ys) / n
    denom = sum((x - xm) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / denom


def analyze(path: str, horizon: int, flat_eps: float = 0.005):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if len(rows) < 2:
        raise SystemExit(f"need >=2 steps, got {len(rows)} in {path}")
    rows.sort(key=lambda r: r["step"])
    m = [float(r["mean_reward"]) for r in rows]
    xs = [int(r["step"]) for r in rows]
    delta = m[-1] - m[0]
    slope = ols_slope(xs, m)
    proj = m[0] + slope * horizon
    k = min(5, len(m) // 2 or 1)
    early = sum(m[:k]) / k
    late = sum(m[-k:]) / k
    if slope > flat_eps:
        verdict = "continuing-up"
    elif slope < -flat_eps:
        verdict = "reversed-down"
    else:
        verdict = "flat"
    return {
        "path": path, "n_steps": len(rows),
        "step0": round(m[0], 4), "stepN": round(m[-1], 4),
        "delta": round(delta, 4),
        "ols_slope_per_step": round(slope, 5),
        "early_mean": round(early, 4), "late_mean": round(late, 4),
        "projected_at_horizon": {"horizon": horizon, "value": round(proj, 4)},
        "verdict": verdict,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--horizon", type=int, default=50)
    ap.add_argument("--flat-eps", type=float, default=0.005)
    args = ap.parse_args()
    out = analyze(args.jsonl, args.horizon, args.flat_eps)
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
