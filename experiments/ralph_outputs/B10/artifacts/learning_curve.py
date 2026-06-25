#!/usr/bin/env python3
"""B10 — RFT learning curve: pass@1 vs training step.

Grounded in opensre-traj/train_rft.py / train_rft_v2.py, which append one JSONL
line per GRPO step. Each line carries a per-rollout ``rewards`` array (continuous
weighted grader score in [0,1] from hud_env_static / hud_env_v2). There is no
binary pass/fail in the log, so pass@1 is DERIVED from the reward array with the
repo-canonical success threshold.

pass@1 definition (matches rex/eval_pass_at_k.py + experiments/compute_pass_at_k.py):
  THRESHOLD = 0.8  (incident 'resolved': SLO restored + root cleared + no trap)
  A rollout PASSES iff reward >= THRESHOLD.
  pass@1(step) = (# rollouts with reward >= THRESHOLD) / (# rollouts at that step)
                = mean over the step's `rewards` of [reward >= THRESHOLD]
  This is the standard single-sample pass rate; each GRPO rollout is one i.i.d.
  attempt, so the empirical mean of the per-rollout indicator IS the pass@1 estimate.

Log format contract (one JSON object per line):
  {"step": int, "mean_reward": float, "rewards": [float, ...], "n": int,
   "reward_std"?: float, "loss"?: float|null}
Only `step` and `rewards` are required by this script. Lines missing either are
skipped with a warning. mean_reward (if present) is plotted as a secondary line
for context.

Usage:
  python3 learning_curve.py --log <path.jsonl> [--log <path2.jsonl> ...] \
      [--threshold 0.8] [--out curve.png] [--csv curve.csv] [--title "..."]
  # default: auto-discover opensre-traj/runs/*.jsonl
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import sys

THRESHOLD = 0.8           # repo-canonical (rex/eval_pass_at_k.py:43)
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_DEFAULT_RUNS = os.path.join(_REPO_ROOT, "opensre-traj", "runs")


def wilson_ci(p: float, n: int, z: float = 1.96):
    """Wilson score 95% CI for a binomial proportion (mirrors compute_pass_at_k.wilson_ci)."""
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, center - spread), min(1.0, center + spread))


def parse_log(path: str, threshold: float = THRESHOLD):
    """Parse one RFT JSONL log -> sorted list of per-step dicts.

    Returns: [{"step","n","passes","pass1","ci_lo","ci_hi","mean_reward"}, ...]
    Robust to: blank lines, malformed JSON, missing keys.
    """
    rows = []
    with open(path) as fh:
        for ln, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"  [warn] {os.path.basename(path)}:{ln} bad JSON ({e}); skipped",
                      file=sys.stderr)
                continue
            if "step" not in rec or "rewards" not in rec:
                print(f"  [warn] {os.path.basename(path)}:{ln} missing step/rewards; skipped",
                      file=sys.stderr)
                continue
            rewards = [float(x) for x in rec["rewards"]]
            n = len(rewards)
            if n == 0:
                print(f"  [warn] {os.path.basename(path)}:{ln} empty rewards; skipped",
                      file=sys.stderr)
                continue
            passes = sum(1 for r in rewards if r >= threshold)
            p1 = passes / n
            lo, hi = wilson_ci(p1, n)
            rows.append({
                "step": int(rec["step"]), "n": n, "passes": passes,
                "pass1": p1, "ci_lo": lo, "ci_hi": hi,
                "mean_reward": rec.get("mean_reward",
                                       sum(rewards) / n if n else 0.0),
            })
    rows.sort(key=lambda r: r["step"])
    return rows


def write_csv(series: dict, path: str):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["run", "step", "n", "passes", "pass1", "ci_lo", "ci_hi", "mean_reward"])
        for label, rows in series.items():
            for r in rows:
                w.writerow([label, r["step"], r["n"], r["passes"],
                            f"{r['pass1']:.4f}", f"{r['ci_lo']:.4f}",
                            f"{r['ci_hi']:.4f}", f"{r['mean_reward']:.4f}"])


def plot(series: dict, out: str, threshold: float, title: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for i, (label, rows) in enumerate(series.items()):
        if not rows:
            continue
        c = colors[i % len(colors)]
        steps = [r["step"] for r in rows]
        p1 = [r["pass1"] for r in rows]
        lo = [r["ci_lo"] for r in rows]
        hi = [r["ci_hi"] for r in rows]
        ax.plot(steps, p1, marker="o", ms=4, color=c, label=f"{label}  pass@1")
        ax.fill_between(steps, lo, hi, color=c, alpha=0.15)
        # mean reward as a faint dashed reference line
        ax.plot(steps, [r["mean_reward"] for r in rows], ls="--", lw=1,
                color=c, alpha=0.5, label=f"{label}  mean_reward")

    ax.axhline(threshold, color="grey", ls=":", lw=1,
               label=f"pass threshold = {threshold}")
    ax.set_xlabel("GRPO training step")
    ax.set_ylabel(f"pass@1 (reward ≥ {threshold})  /  mean reward")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc="best", ncol=1)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"wrote {out}")


def label_for(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", action="append", default=[],
                    help="RFT JSONL log path (repeatable). Default: auto-discover runs/*.jsonl")
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "learning_curve.png"))
    ap.add_argument("--csv", default=os.path.join(os.path.dirname(__file__), "learning_curve.csv"))
    ap.add_argument("--title", default="opensre RFT (GRPO) learning curve — pass@1 vs step")
    args = ap.parse_args()

    logs = args.log
    if not logs:
        logs = sorted(glob.glob(os.path.join(_DEFAULT_RUNS, "*.jsonl")))
        if not logs:
            print(f"BLOCKER: no --log given and no JSONL logs under {_DEFAULT_RUNS}",
                  file=sys.stderr)
            return 2
        print(f"auto-discovered {len(logs)} log(s) under {_DEFAULT_RUNS}")

    series = {}
    for p in logs:
        if not os.path.exists(p):
            print(f"  [warn] missing log: {p}", file=sys.stderr)
            continue
        rows = parse_log(p, args.threshold)
        if rows:
            series[label_for(p)] = rows
            print(f"  {label_for(p)}: {len(rows)} steps, "
                  f"pass@1 {rows[0]['pass1']:.3f} -> {rows[-1]['pass1']:.3f} "
                  f"(n={rows[0]['n']}/step, threshold={args.threshold})")

    if not series:
        print("BLOCKER: no parseable steps in any log", file=sys.stderr)
        return 2

    write_csv(series, args.csv)
    print(f"wrote {args.csv}")
    plot(series, args.out, args.threshold, args.title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
