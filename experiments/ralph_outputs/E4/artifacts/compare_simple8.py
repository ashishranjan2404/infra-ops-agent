#!/usr/bin/env python3
"""E4 — Fireball-trained vs OpenSRE-trained on 8 simple incidents: "does it hurt?"

THESIS UNDER TEST
-----------------
A policy specialised on the *source* domain (FIREBALL D&D transfer corpus) and a
policy specialised on the *target* domain (OpenSRE incidents) should both handle
EASY incidents. The worry is regression: does domain-specialisation training
*hurt* on the simple cases that a generalist already solves? This harness measures
the per-incident pass delta between two policies on the 8 simplest incidents.

WHAT THIS HARNESS IS
--------------------
A self-contained, task-namespaced comparison driver. It is deliberately additive:
it imports the frozen REx evaluation primitives (load_scenario / run_plan /
build_prompt / parse_plan / score_plan) and the P0 DETERMINISTIC judge, and does
NOT edit any shared core file. Given any two roster model slugs it:
  1. runs each model `--seeds` times on each of the 8 simple incidents (zero-shot),
  2. grades every episode with the deterministic judge (binary pass at THRESHOLD),
  3. reports pass@1 per incident for each policy + the per-incident delta,
  4. flags any incident where policy B regresses below policy A ("HURTS").

BLOCKER (documented, not faked)
-------------------------------
The two *actual* trained policies do not exist in this repo:
  - No FIREBALL-trained slug (no fireball training corpus, no forked slug on HUD;
    see experiments/results/P7_fireball_status.md).
  - No OpenSRE-GRPO-trained Qwen slug pushed (opensre-traj/train_rft.py is the
    trainer, but Wenji's GRPO run was never pushed — see CLAIMS_EVIDENCE.md).
So the trained-vs-trained comparison CANNOT be run tonight. The harness is the
deliverable; it is run with available FROZEN frontier models as labelled
STAND-IN policies to prove the pipeline end-to-end and produce real numbers. The
moment the two trained slugs land, pass:
    --model-a <fireball-slug> --label-a fireball \
    --model-b <opensre-slug>  --label-b opensre
and the same harness yields the real answer.

USAGE
    set -a; source ~/.zshrc; set +a
    python3 compare_simple8.py --model-a glm-5p2 --model-b minimax-m3 --seeds 3
    python3 compare_simple8.py --model-a <fireball> --model-b <opensre> --seeds 5 \
        --label-a fireball --label-b opensre --out result.json
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# import the frozen REx primitives (read-only use; nothing is mutated)
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from agent.llm import call                                    # noqa: E402
from compute_pass_at_k import binary_pass, pass_at_k, wilson_ci  # noqa: E402
from rex.harness import load_scenario, run_plan, scenarios_by_family  # noqa: E402
from rex.loop import build_prompt, parse_plan                 # noqa: E402
from rex.scoring import score_plan                            # noqa: E402

THRESHOLD = 0.8

# The 8 simple incidents under test. Pinned (not "first 8 of a dict") so the run is
# reproducible and the same 8 are used for both policies and across re-runs.
SIMPLE_8 = [
    "cpu_saturation_leaf",
    "oom_kill",
    "bad_deploy_leaf",
    "redis_cache_flush",
    "auth_cert_expiry",
    "billing_disk_fill",
    "singleton_node_notready",
    "ingest_fd_exhaust",
]


def validate_incidents(names: list[str]) -> None:
    """Fail fast if a pinned incident is not actually in the `simple` family."""
    simple = set(scenarios_by_family().get("simple", []))
    missing = [n for n in names if n not in simple]
    if missing:
        raise SystemExit(f"pinned incidents not in 'simple' family: {missing}")


def propose(model: str, scenario, temp: float = 0.7, max_tokens: int = 1400) -> dict:
    """One zero-shot plan from `model`, with a single retry on a transient error."""
    last = None
    for _ in range(2):
        try:
            txt = call(model, build_prompt(scenario, None),
                       max_tokens=max_tokens, temperature=temp)
            return parse_plan(txt)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def episode_reward(model: str, scenario) -> float:
    plan = propose(model, scenario)
    sim = run_plan(plan, scenario)
    score, _ = score_plan(plan, scenario, sim)   # P0 deterministic judge
    return float(score)


def summarize(rewards: list[float]) -> dict:
    n = len(rewards)
    c = sum(binary_pass(r, THRESHOLD) for r in rewards)
    p1 = c / n if n else 0.0
    lo, hi = wilson_ci(p1, n)
    return {
        "n": n, "passes": c, "pass@1": round(p1, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "pass@2": round(pass_at_k(n, c, 2), 4) if n >= 2 else None,
        "mean_reward": round(st.mean(rewards), 4) if rewards else 0.0,
        "reward_std": round(st.pstdev(rewards), 4) if len(rewards) > 1 else 0.0,
    }


def run(model_a, model_b, label_a, label_b, seeds, incidents, max_workers=8) -> dict:
    validate_incidents(incidents)
    scenarios = {n: load_scenario(n) for n in incidents}
    policies = {label_a: model_a, label_b: model_b}

    # one job = (policy_label, incident, seed_index)
    jobs = [(lab, name, s)
            for lab in policies for name in incidents for s in range(seeds)]
    raw = {lab: {name: [] for name in incidents} for lab in policies}
    errors = []

    def work(job):
        lab, name, _i = job
        try:
            return job, episode_reward(policies[lab], scenarios[name]), None
        except Exception as e:  # noqa: BLE001
            return job, None, f"{type(e).__name__}: {str(e)[:80]}"

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for job, r, err in ex.map(work, jobs):
            lab, name, _i = job
            if err:
                errors.append({"job": list(job), "err": err})
            else:
                raw[lab][name].append(r)

    # per-incident summaries + the per-incident regression check
    per_incident = []
    for name in incidents:
        sa = summarize(raw[label_a][name])
        sb = summarize(raw[label_b][name])
        delta = round(sb["pass@1"] - sa["pass@1"], 4)
        per_incident.append({
            "incident": name,
            f"{label_a}_pass@1": sa["pass@1"], f"{label_b}_pass@1": sb["pass@1"],
            "delta_b_minus_a": delta,
            "hurts": delta < 0,   # B regresses vs A on this simple incident
            f"{label_a}_mean": sa["mean_reward"], f"{label_b}_mean": sb["mean_reward"],
        })

    flat_a = [r for name in incidents for r in raw[label_a][name]]
    flat_b = [r for name in incidents for r in raw[label_b][name]]
    n_hurts = sum(p["hurts"] for p in per_incident)
    mean_delta = round(st.mean([p["delta_b_minus_a"] for p in per_incident]), 4)

    return {
        "task_id": "E4", "threshold": THRESHOLD, "seeds": seeds,
        "incidents": incidents, "n_incidents": len(incidents),
        "policy_a": {"label": label_a, "model": model_a},
        "policy_b": {"label": label_b, "model": model_b},
        "overall": {label_a: summarize(flat_a), label_b: summarize(flat_b)},
        "per_incident": per_incident,
        "regression": {
            "n_incidents_b_hurts_vs_a": n_hurts,
            "mean_delta_b_minus_a": mean_delta,
            # the headline answer to "does it hurt?": positive/zero => no net harm
            "verdict": ("B_HELPS" if mean_delta > 0
                        else "NO_NET_CHANGE" if mean_delta == 0 else "B_HURTS"),
        },
        "elapsed_s": round(time.time() - t0, 1),
        "n_errors": len(errors), "errors": errors[:20],
        "note": ("STAND-IN policies (frozen frontier models) — neither the FIREBALL-"
                 "trained nor the OpenSRE-GRPO-trained slug exists in this repo; see "
                 "experiments/results/P7_fireball_status.md. Re-run with the real "
                 "slugs when they land."),
    }


def print_report(out: dict) -> None:
    a, b = out["policy_a"]["label"], out["policy_b"]["label"]
    print(f"\n{'='*72}\nE4 simple-8: {a} (A) vs {b} (B)  seeds={out['seeds']}  "
          f"thr={out['threshold']}  ({out['elapsed_s']}s, {out['n_errors']} err)\n{'='*72}")
    print(f"{'incident':<26}{a+' p@1':>14}{b+' p@1':>14}{'delta':>9}{'  hurts?':>9}")
    print("-" * 72)
    for p in out["per_incident"]:
        print(f"{p['incident']:<26}{p[a+'_pass@1']:>14.3f}{p[b+'_pass@1']:>14.3f}"
              f"{p['delta_b_minus_a']:>9.3f}{('  YES' if p['hurts'] else '  no'):>9}")
    oa, ob = out["overall"][a], out["overall"][b]
    print("-" * 72)
    print(f"{'OVERALL':<26}{oa['pass@1']:>14.3f}{ob['pass@1']:>14.3f}"
          f"{out['regression']['mean_delta_b_minus_a']:>9.3f}")
    r = out["regression"]
    print(f"\nverdict: {r['verdict']}  (mean delta {r['mean_delta_b_minus_a']:+.3f}, "
          f"{r['n_incidents_b_hurts_vs_a']}/{out['n_incidents']} incidents B hurts)")
    print(f"note: {out['note']}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-a", required=True, help="policy A slug (e.g. fireball-trained)")
    ap.add_argument("--model-b", required=True, help="policy B slug (e.g. opensre-trained)")
    ap.add_argument("--label-a", default=None)
    ap.add_argument("--label-b", default=None)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out = run(args.model_a, args.model_b,
              args.label_a or args.model_a, args.label_b or args.model_b,
              args.seeds, SIMPLE_8, args.max_workers)
    print_report(out)
    if args.out:
        json.dump(out, open(args.out, "w"), indent=2)
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
