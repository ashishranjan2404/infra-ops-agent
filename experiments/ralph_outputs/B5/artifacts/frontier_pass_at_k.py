#!/usr/bin/env python3
"""B5 — Frontier sweep with pass@k (not just mean reward).

`rex/frontier.py` runs baseline-vs-REx across N frontier models but its headline is
ONLY a mean-reward-per-model table. Mean reward conflates "barely passed" with
"crushed it" and gives no notion of reliability-under-resampling. This script adds the
pass@k frontier: for each (model, condition) it runs every incident `seeds` times,
converts each graded reward to a BINARY pass (reward >= THRESHOLD = SLO restored +
root cleared + no trap), and reports pass@1 / pass@2 / pass@5 with Wilson 95% CIs, for
both the zero-shot baseline and REx — so the headline is now "how reliably does this
frozen model resolve incidents, and how much does REx lift that reliability".

It deliberately reuses the SAME grading path as rex/frontier.py:
  - propose:  parse_plan(call(model, build_prompt(scenario, prior_feedback)))
  - baseline: model answers once  -> deterministic reward
  - rex:      rex_tree(scenario, budget, propose_fn) -> best node's reward
and the SAME estimators as rex/eval_pass_at_k.py (experiments/compute_pass_at_k.py:
unbiased pass@k + Wilson CI), so this is purely an *aggregation* upgrade — no change to
the substrate, the judge, or REx itself. Grading uses the P0 DETERMINISTIC judge
(judge_fn=None propagated; score_plan with no LLM judge) for reproducibility.

This file is a self-contained, task-namespaced copy under experiments/ralph_outputs/B5/
— it does NOT edit rex/frontier.py. To upstream it, drop the pass@k headline into
rex/frontier.py's main() or call this module directly.

Usage:
    set -a; source ~/.zshrc; set +a            # HUD_API_KEY for gateway models
    python3 experiments/ralph_outputs/B5/artifacts/frontier_pass_at_k.py \
        --models gemini-3.1-pro,deepseek-v4-pro --scenarios oom_kill,gcp_service_control \
        --seeds 3 --budget 3 --out .../frontier_pass_at_k_result.json
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from compute_pass_at_k import pass_at_k, wilson_ci, binary_pass  # noqa: E402

from agent.llm import call  # noqa: E402
from rex.harness import load_scenario, run_plan  # noqa: E402
from rex.loop import build_prompt, parse_plan  # noqa: E402
from rex.scoring import score_plan  # noqa: E402
from rex.tree import rex_tree  # noqa: E402

# Defaults mirror rex/frontier.py.
DEFAULT_MODELS = ["claude-haiku-4-5", "claude-opus-4-8",
                  "gpt-5.5", "gemini-3.1-pro", "deepseek-v4-pro"]
DEFAULT_SCENARIOS = ["oom_kill", "cpu_saturation_leaf", "bad_deploy_leaf",
                     "gcp_service_control", "singleton_node_notready"]
THRESHOLD = 0.8
MAX_TOKENS = 4000


def _propose(model):
    def fn(scenario, prior_feedback):
        return parse_plan(call(model, build_prompt(scenario, prior_feedback),
                               max_tokens=MAX_TOKENS))
    return fn


def _grade(plan, scenario) -> float:
    sim = run_plan(plan, scenario)
    score, _ = score_plan(plan, scenario, sim, judge_fn=None)   # deterministic judge
    return score


def summarize(rewards: list, threshold: float = THRESHOLD) -> dict:
    """reward list -> pass@1/2/5 + Wilson CI + mean + within-group std (trainability)."""
    n = len(rewards)
    c = sum(binary_pass(r, threshold) for r in rewards)
    p1 = c / n if n else 0.0
    lo, hi = wilson_ci(p1, n)
    return {
        "n": n, "passes": c,
        "pass@1": round(p1, 4), "ci95": [round(lo, 4), round(hi, 4)],
        "pass@2": round(pass_at_k(n, c, 2), 4), "pass@5": round(pass_at_k(n, c, 5), 4),
        "mean_reward": round(st.mean(rewards), 4) if rewards else 0.0,
        "reward_std": round(st.pstdev(rewards), 4) if len(rewards) > 1 else 0.0,
    }


def run_model(model: str, scenarios: list, seeds: int, budget: int,
              threshold: float = THRESHOLD, log=print) -> dict:
    """For one frozen model: baseline & REx rewards over (scenario x seed); pass@k each."""
    base_rewards, rex_rewards = [], []
    base_by_inc = {n: [] for n in scenarios}
    rex_by_inc = {n: [] for n in scenarios}
    errors = []
    propose = _propose(model)
    for name in scenarios:
        sc = load_scenario(name)
        for s in range(seeds):
            try:
                b = _grade(propose(sc, None), sc)
                base_rewards.append(b); base_by_inc[name].append(round(b, 3))
            except Exception as e:  # noqa: BLE001
                errors.append({"cond": "baseline", "scenario": name, "seed": s,
                               "err": f"{type(e).__name__}: {str(e)[:80]}"})
            try:
                r = rex_tree(sc, budget=budget, propose_fn=propose, seed=s)["best_score"]
                rex_rewards.append(r); rex_by_inc[name].append(round(r, 3))
            except Exception as e:  # noqa: BLE001
                errors.append({"cond": "rex", "scenario": name, "seed": s,
                               "err": f"{type(e).__name__}: {str(e)[:80]}"})
        bm = st.mean(base_by_inc[name]) if base_by_inc[name] else float("nan")
        rm = st.mean(rex_by_inc[name]) if rex_by_inc[name] else float("nan")
        log(f"  [{model}] {name:24} baseline_mean={bm:.3f}  rex_mean={rm:.3f}  (seeds={seeds})")
    base_sum = summarize(base_rewards, threshold)
    rex_sum = summarize(rex_rewards, threshold)
    return {
        "model": model, "seeds": seeds, "budget": budget, "threshold": threshold,
        "baseline": base_sum, "rex": rex_sum,
        "pass1_lift": round(rex_sum["pass@1"] - base_sum["pass@1"], 4),
        "mean_lift": round(rex_sum["mean_reward"] - base_sum["mean_reward"], 4),
        "baseline_per_incident": base_by_inc, "rex_per_incident": rex_by_inc,
        "errors": errors, "n_errors": len(errors),
    }


def print_report(rows: list, scenarios: list):
    print("\n" + "=" * 92)
    print("FRONTIER pass@k — baseline vs REx  (threshold = SLO restored + root cleared + no trap)")
    print("=" * 92)
    hdr = (f"{'model':<18}{'cond':<10}{'pass@1':>8}{'95% CI':>16}"
           f"{'pass@2':>8}{'pass@5':>8}{'mean':>7}{'std':>7}{'n':>5}")
    print(hdr); print("-" * 92)
    for r in rows:
        for cond in ("baseline", "rex"):
            d = r[cond]
            ci = f"[{d['ci95'][0]:.2f},{d['ci95'][1]:.2f}]"
            print(f"{r['model']:<18}{cond:<10}{d['pass@1']:>8.3f}{ci:>16}"
                  f"{d['pass@2']:>8.3f}{d['pass@5']:>8.3f}"
                  f"{d['mean_reward']:>7.2f}{d['reward_std']:>7.2f}{d['n']:>5}")
    print("-" * 92)
    print(f"{'model':<18}{'pass@1 lift (REx-base)':>26}{'mean lift':>14}")
    print("-" * 92)
    for r in rows:
        print(f"{r['model']:<18}{r['pass1_lift']:>+26.3f}{r['mean_lift']:>+14.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--scenarios", default=",".join(DEFAULT_SCENARIOS))
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--budget", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--time-budget-s", type=float, default=None,
                    help="stop starting new models once this wall-clock budget is exceeded")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__),
                                                  "frontier_pass_at_k_result.json"))
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    print(f"=== Frontier pass@k — {len(models)} models x {len(scenarios)} incidents x "
          f"{args.seeds} seeds, REx budget {args.budget}, threshold {args.threshold} ===\n")

    rows = []
    t0 = time.time()
    for m in models:
        if args.time_budget_s is not None and time.time() - t0 > args.time_budget_s:
            print(f"--- skipping {m}: wall budget {args.time_budget_s}s exceeded "
                  f"({time.time()-t0:.0f}s elapsed) ---")
            continue
        print(f"--- {m} ---")
        rows.append(run_model(m, scenarios, args.seeds, args.budget, args.threshold))
        print()

    out = {"threshold": args.threshold, "seeds": args.seeds, "budget": args.budget,
           "scenarios": scenarios, "models_requested": models,
           "elapsed_s": round(time.time() - t0, 1), "models": rows}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print_report(rows, scenarios)
    print(f"\n-> {args.out}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
