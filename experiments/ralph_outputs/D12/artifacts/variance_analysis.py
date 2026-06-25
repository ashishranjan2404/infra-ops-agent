#!/usr/bin/env python3
"""D12 — expected variance reduction from RFT group size 4 -> 8.

GROUNDING: reads the REAL baseline log opensre-traj/runs/train_qwen3-8b_v2.jsonl
(10 tasks x group=4 = 40 rollouts/step, 15 steps) and derives the within-group
reward sigma empirically, then projects the GRPO baseline-estimator error for G=8.

GRPO mechanics (train_rft_v2.py: trainer.step(..., group_size=G)):
  advantage_i = r_i - mean_g(r)         # group mean is the variance-reduction baseline
  the baseline mean_g is estimated from G samples, so its sampling error is sigma/sqrt(G).
  Doubling G (4->8) shrinks that error by 1/sqrt(2) = 0.707 (a 29.3% reduction) and
  halves the variance of the gradient's baseline term.

Run:  python3 variance_analysis.py
      python3 variance_analysis.py --log /abs/path/to/train_qwen3-8b_v2.jsonl
"""
from __future__ import annotations
import argparse, json, os, statistics as st

DEFAULT_LOG = os.path.join(os.path.dirname(__file__),
                           "../../../../opensre-traj/runs/train_qwen3-8b_v2.jsonl")
BASE_G = 4          # baseline group size in the logged run
N_TASKS = 10        # rollouts are task-major: BASE_G consecutive entries == one task's group


def within_group_sigma(log_path: str, base_g: int = BASE_G):
    sigmas, steps = [], 0
    with open(log_path) as fh:
        for line in fh:
            d = json.loads(line)
            r = d.get("rewards") or []
            steps += 1
            for t in range(0, len(r), base_g):
                g = r[t:t + base_g]
                if len(g) > 1:
                    sigmas.append(st.pstdev(g))
    if not sigmas:
        raise SystemExit("no grouped rewards found in log")
    return sigmas, steps


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=DEFAULT_LOG)
    args = ap.parse_args()
    log = os.path.abspath(args.log)
    if not os.path.exists(log):
        raise SystemExit(f"baseline log not found: {log}")

    sigmas, steps = within_group_sigma(log)
    sigma = st.mean(sigmas)

    print(f"baseline log         : {log}")
    print(f"steps                : {steps}   groups sampled: {len(sigmas)}")
    print(f"within-group sigma   : mean={sigma:.4f}  median={st.median(sigmas):.4f}"
          f"  (per-task reward spread that GRPO advantage rides on)")
    print()
    print("GRPO baseline-estimator standard error  SEM = sigma / sqrt(G):")
    sem = {}
    for G in (4, 8):
        sem[G] = sigma / (G ** 0.5)
        print(f"  G={G}:  rollouts/step={N_TASKS*G:>3}   SEM(group-mean)={sem[G]:.4f}"
              f"   Var={sem[G]**2:.5f}")
    print()
    red_sd = 1 - sem[8] / sem[4]
    print(f"4 -> 8 effect:")
    print(f"  baseline-mean std error : -{red_sd:.1%}  (exactly 1 - 1/sqrt(2) = 29.3%)")
    print(f"  baseline-mean variance  : -{1 - (sem[8]**2/sem[4]**2):.1%}  (halved)")
    print(f"  rollout compute / step  : +100%  ({N_TASKS*4} -> {N_TASKS*8} rollouts)")
    print()
    print("Interpretation: the v2 baseline was flat NOT because of baseline-mean noise")
    print(f"(SEM was already ~{sem[4]:.3f}, small vs sigma~{sigma:.3f}); the flatness was")
    print("the diagnosed lack of learnable headroom + few tasks. So group 4->8 buys a")
    print("cleaner advantage estimate (a real but second-order win) at 2x rollout cost,")
    print("not a fix for the flat-reward root cause. Spend compute on tasks/headroom first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
