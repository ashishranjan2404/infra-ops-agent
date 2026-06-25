#!/usr/bin/env python3
"""D9 — Curriculum-vs-random comparison harness.

Compares three training-data orderings (curriculum easy->hard, random shuffle,
anti-curriculum hard->easy) on the A12 CIDG incident set.

REAL training is blocked here (no GPU / frozen-LLM project), so this harness
runs a TRANSPARENT, DETERMINISTIC learning-curve SIMULATION rather than
fabricating model reward numbers. The simulation is a standard competence-vs-
difficulty model from the curriculum-learning literature (Bengio 2009; Graves
2017 ATPG): a learner has a scalar competence `c` that rises when it trains on
incidents near its current frontier and barely moves when incidents are far too
hard (gradient too noisy) or far too easy (no signal). Per-incident learnability
is a Gaussian band around the current competence:

    learn_gain(diff) = lr * exp(-((diff - c) / sigma)^2)
    p_solve(diff)    = sigmoid(k * (c - diff))      # eval reward proxy

This is a MODEL, not measured rewards — it exists to show the *mechanism* by
which easy->hard ordering helps (it keeps incidents inside the learnable band)
and to give the downstream real-training run a falsifiable hypothesis + the
exact metric/plot code to reuse. The blocker is documented; numbers are clearly
labeled "simulated".

The harness is structured so that swapping `simulate_run` for a real eval call
(rex.scoring.score_plan over actual model rollouts per stage) is a one-function
change — the schedule, metrics, and reporting are reused verbatim.

Usage:
    python3 curriculum_vs_random.py            # writes comparison.json + prints
    python3 curriculum_vs_random.py --seeds 8  # average over 8 random seeds
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics as st

from curriculum_schedule import build_schedule, load_order

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "comparison.json")

# Simulation hyperparameters (the "learner"). Fixed + documented for repro.
LR = 0.18          # base competence gain per training touch
SIGMA = 3.5        # width of the learnable difficulty band around competence
K = 0.9            # sharpness of the solve-probability sigmoid
C0 = 0.5           # initial competence (below the easiest incident's difficulty)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def simulate_run(order: str, n_stages: int, diff: dict, seed: int,
                 rehearsal: float = 0.3) -> dict:
    """Run the competence simulation for one ordering. Returns per-stage eval.

    Eval is ALWAYS over the full incident set (held-out style), so all orderings
    are scored on the same yardstick regardless of what they trained on.
    """
    sched = build_schedule(order, n_stages, rehearsal=rehearsal, seed=seed)
    c = C0
    all_ids = list(diff.keys())
    stage_eval = []
    for stg in sched["stages"]:
        # train: each active incident nudges competence by its learnability,
        # weighted by the schedule sampling weight.
        for a in stg["active_incidents"]:
            d = diff[a["id"]]
            gain = LR * a["weight"] * math.exp(-(((d - c) / SIGMA) ** 2))
            c += gain
        # eval over the WHOLE set -> mean solve probability (reward proxy in 0..1)
        mean_reward = st.mean(_sigmoid(K * (c - diff[i])) for i in all_ids)
        stage_eval.append({
            "stage": stg["stage"],
            "competence": round(c, 4),
            "mean_reward": round(mean_reward, 4),
        })
    return {
        "order": order,
        "final_competence": round(c, 4),
        "final_mean_reward": stage_eval[-1]["mean_reward"],
        "auc": round(st.mean(s["mean_reward"] for s in stage_eval), 4),  # area under learning curve
        "stage_eval": stage_eval,
    }


def compare(n_stages: int = 6, seeds: int = 5, rehearsal: float = 0.3) -> dict:
    data = load_order()
    diff = {r["id"]: r["difficulty"] for r in data["incidents"]}

    results = {}
    for order in ("curriculum", "random", "anti"):
        if order == "random":
            runs = [simulate_run(order, n_stages, diff, seed=s, rehearsal=rehearsal)
                    for s in range(seeds)]
            results[order] = {
                "order": order,
                "final_mean_reward": round(st.mean(r["final_mean_reward"] for r in runs), 4),
                "final_mean_reward_std": round(st.pstdev(r["final_mean_reward"] for r in runs), 4),
                "auc": round(st.mean(r["auc"] for r in runs), 4),
                "n_seeds": seeds,
                # representative single curve (seed 0) for plotting
                "stage_eval": runs[0]["stage_eval"],
            }
        else:
            r = simulate_run(order, n_stages, diff, seed=0, rehearsal=rehearsal)
            results[order] = {
                "order": order,
                "final_mean_reward": r["final_mean_reward"],
                "final_mean_reward_std": 0.0,
                "auc": r["auc"],
                "n_seeds": 1,
                "stage_eval": r["stage_eval"],
            }

    cur = results["curriculum"]
    rnd = results["random"]
    verdict = {
        "curriculum_auc": cur["auc"],
        "random_auc": rnd["auc"],
        "auc_delta": round(cur["auc"] - rnd["auc"], 4),
        "curriculum_beats_random": cur["auc"] > rnd["auc"],
        "final_delta": round(cur["final_mean_reward"] - rnd["final_mean_reward"], 4),
    }
    return {
        "kind": "SIMULATED learning-curve comparison (training blocked: no GPU)",
        "model_note": "competence-vs-difficulty proxy, NOT measured model reward",
        "n_incidents": len(diff),
        "n_stages": n_stages,
        "rehearsal": rehearsal,
        "sim_params": {"LR": LR, "SIGMA": SIGMA, "K": K, "C0": C0},
        "results": results,
        "verdict": verdict,
    }


def _ascii_curve(label: str, curve: list) -> str:
    cells = []
    for s in curve:
        v = s["mean_reward"]
        cells.append(f"{v:.2f}")
    return f"  {label:11} " + " -> ".join(cells)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", type=int, default=6)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--rehearsal", type=float, default=0.3)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    rep = compare(args.stages, args.seeds, args.rehearsal)
    with open(args.out, "w") as f:
        json.dump(rep, f, indent=2)

    print(f"wrote {args.out}")
    print(f"\n[SIMULATED — training blocked] mean_reward per stage "
          f"(eval over all {rep['n_incidents']} incidents):")
    for order in ("curriculum", "random", "anti"):
        print(_ascii_curve(order, rep["results"][order]["stage_eval"]))
    v = rep["verdict"]
    print(f"\n  curriculum AUC={v['curriculum_auc']}  random AUC={v['random_auc']}  "
          f"delta={v['auc_delta']}  curriculum_wins={v['curriculum_beats_random']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
