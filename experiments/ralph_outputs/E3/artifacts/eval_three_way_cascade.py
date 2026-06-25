#!/usr/bin/env python3
"""E3 — 3-way cascade comparison: Fireball-trained vs OpenSRE-trained vs zero-shot.

Goal (Ralph task E3): on the 14 hardest CASCADE incidents, compare three policies:

  1. zero-shot          — the BASE open model, untrained (Qwen/Qwen3-8B), apples-to-apples
                          control for the trained arms.
  2. opensre_trained    — the SAME base model after OpenSRE GRPO/RFT training
                          (forked Tinker slug `opensre-qwen3-8b-1e439a`), served on the
                          HUD OpenAI-compatible inference gateway.
  3. fireball_trained   — BLOCKED. No Fireball training data / model exists yet
                          (see experiments/ralph_outputs/E2 and D8 — both empty: the
                          upstream Fireball pipeline never produced a dataset or a forked
                          model). We DO NOT fabricate numbers for this arm; it is recorded
                          as status="blocked" with a documented reason.

Why a separate harness (not rex.eval_pass_at_k --frontier): the OpenSRE-trained and the
base-Qwen models are reached by their gateway *slug*, which is NOT in agent/models.ROSTER.
Per the Ralph real-artifact rules we must NOT edit shared core files (agent/models.py,
agent/llm.py, rex/*). So this harness registers the two extra slugs into a LOCAL copy of
the roster at runtime (ROSTER.setdefault), then reuses the repo's real machinery:

    rex.harness.load_scenario / run_plan / scenarios_by_family   (the sim)
    rex.loop.build_prompt / parse_plan                           (prompt + parse)
    rex.scoring.score_plan / failed_checks                       (P0 DETERMINISTIC judge)
    experiments.compute_pass_at_k.pass_at_k / wilson_ci          (stats)

Reward is the deterministic judge (reproducible, no LLM judge). PASS = reward >= 0.8
(SLO restored + root cleared + no trap), same threshold as rex.eval_pass_at_k.

Usage:
    set -a; source ~/.zshrc; set +a       # exports HUD_API_KEY (gateway), etc.
    python3 experiments/ralph_outputs/E3/artifacts/eval_three_way_cascade.py \
        --seeds 3 --n-incidents 14 \
        --out experiments/ralph_outputs/E3/artifacts/result_three_way.json

    # dry run — select incidents + check arm reachability, NO model calls:
    python3 .../eval_three_way_cascade.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from compute_pass_at_k import pass_at_k, wilson_ci, binary_pass  # noqa: E402
from agent.models import ROSTER  # noqa: E402
from agent.llm import call  # noqa: E402
from rex.harness import load_scenario, run_plan, scenarios_by_family  # noqa: E402
from rex.loop import build_prompt, parse_plan  # noqa: E402
from rex.scoring import failed_checks, score_plan  # noqa: E402

THRESHOLD = 0.8

# --- the three arms ---------------------------------------------------------
# Each arm names a roster KEY we resolve via agent.llm.call. The two open-model
# slugs are added to a LOCAL copy of the roster (we never write agent/models.py).
EXTRA_ROSTER = {
    # base open model, untrained -> the zero-shot control
    "qwen3-8b-base": {
        "provider": "gateway", "model": "Qwen/Qwen3-8B",
        "anchor": "weak", "no_temperature": False,
    },
    # SAME base model after OpenSRE GRPO/RFT (forked Tinker slug, served on the gateway)
    "opensre-qwen3-8b": {
        "provider": "gateway", "model": "opensre-qwen3-8b-1e439a",
        "anchor": "weak", "no_temperature": False,
    },
}

ARMS = {
    "zero_shot": {
        "roster_key": "qwen3-8b-base",
        "status": "runnable",
        "note": "base Qwen/Qwen3-8B, untrained (apples-to-apples control)",
    },
    "opensre_trained": {
        "roster_key": "opensre-qwen3-8b",
        "status": "runnable",
        "note": "Qwen3-8B after OpenSRE GRPO/RFT (forked slug opensre-qwen3-8b-1e439a)",
    },
    "fireball_trained": {
        "roster_key": None,
        "status": "blocked",
        "note": ("No Fireball training data or forked model exists. Upstream Fireball "
                 "pipeline (tasks E2/D8) produced no dataset and no model; nothing to "
                 "evaluate. Numbers intentionally NOT fabricated."),
    },
}


def register_extra_models() -> None:
    for k, v in EXTRA_ROSTER.items():
        ROSTER.setdefault(k, v)


# --- incident selection: 14 cascade incidents, deterministic ----------------
def select_cascade_incidents(n: int = 14) -> list[str]:
    fam = scenarios_by_family()
    cascade = sorted(fam.get("cascade", []))
    if len(cascade) < n:
        raise RuntimeError(f"only {len(cascade)} cascade incidents available, need {n}")
    return cascade[:n]


# --- one episode: zero-shot single proposal scored by the deterministic judge ---
def make_proposer(roster_key: str, temp: float = 0.7, max_tokens: int = 1400):
    def _propose(scenario):
        last = None
        for _ in range(2):  # one retry on a transient transport error
            try:
                txt = call(roster_key, build_prompt(scenario, None),
                           max_tokens=max_tokens, temperature=temp)
                return parse_plan(txt)
            except Exception as e:  # noqa: BLE001
                last = e
        raise last
    return _propose


def score_episode(roster_key: str, scenario) -> float:
    plan = make_proposer(roster_key)(scenario)
    sim = run_plan(plan, scenario)
    score, _ = score_plan(plan, scenario, sim)  # P0 deterministic judge
    return float(score)


def summarize(rewards: list) -> dict:
    n = len(rewards)
    if not n:
        return {"n": 0, "passes": 0, "pass@1": 0.0, "ci95": [0.0, 0.0],
                "pass@2": 0.0, "mean_reward": 0.0, "reward_std": 0.0}
    c = sum(binary_pass(r, THRESHOLD) for r in rewards)
    p1 = c / n
    lo, hi = wilson_ci(p1, n)
    return {
        "n": n, "passes": c, "pass@1": round(p1, 4), "ci95": [round(lo, 4), round(hi, 4)],
        "pass@2": round(pass_at_k(n, c, 2), 4),
        "mean_reward": round(st.mean(rewards), 4),
        "reward_std": round(st.pstdev(rewards), 4) if n > 1 else 0.0,
    }


def reachable(roster_key: str) -> tuple[bool, str]:
    try:
        r = call(roster_key, "Reply with the single word OK.", max_tokens=8, temperature=0)
        return True, repr((r or "")[:40])
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:120]}"


def run(seeds: int, incidents: list[str], arms_to_run: list[str],
        max_workers: int = 8) -> dict:
    scenarios = {n: load_scenario(n) for n in incidents}
    raw: dict[str, dict[str, list]] = {a: {n: [] for n in incidents} for a in arms_to_run}

    jobs = [(a, n, s) for a in arms_to_run for n in incidents for s in range(seeds)]

    def work(job):
        arm, name, _s = job
        key = ARMS[arm]["roster_key"]
        try:
            return job, score_episode(key, scenarios[name]), None
        except Exception as e:  # noqa: BLE001
            return job, None, f"{type(e).__name__}: {str(e)[:90]}"

    errors, t0, done = [], time.time(), 0
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for job, r, err in ex.map(work, jobs):
            arm, name, _s = job
            if err:
                errors.append({"job": list(job), "err": err})
            else:
                raw[arm][name].append(r)
            done += 1
            if done % 20 == 0 or done == len(jobs):
                print(f"  [progress] {done}/{len(jobs)} episodes "
                      f"({time.time()-t0:.0f}s, {len(errors)} errors)", flush=True)

    out = {"threshold": THRESHOLD, "seeds": seeds, "n_incidents": len(incidents),
           "incidents": incidents, "elapsed_s": round(time.time() - t0, 1),
           "n_errors": len(errors), "errors": errors[:20], "by_arm": {}}
    for arm in arms_to_run:
        rewards = [r for n in incidents for r in raw[arm][n]]
        out["by_arm"][arm] = {
            "roster_key": ARMS[arm]["roster_key"], "note": ARMS[arm]["note"],
            "overall": summarize(rewards),
            "per_incident_mean": {n: (round(st.mean(raw[arm][n]), 3) if raw[arm][n] else None)
                                  for n in incidents},
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--n-incidents", type=int, default=14)
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true",
                    help="select incidents + probe arm reachability; NO scoring calls")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__),
                    "result_three_way.json"))
    args = ap.parse_args()

    register_extra_models()
    incidents = select_cascade_incidents(args.n_incidents)
    print(f"selected {len(incidents)} cascade incidents:\n  " + "\n  ".join(incidents))

    # reachability / blocker report for all three arms
    arm_status = {}
    for arm, spec in ARMS.items():
        if spec["status"] == "blocked":
            arm_status[arm] = {"runnable": False, "reason": spec["note"]}
            print(f"arm {arm}: BLOCKED — {spec['note']}")
            continue
        ok, detail = reachable(spec["roster_key"])
        arm_status[arm] = {"runnable": ok, "roster_key": spec["roster_key"], "probe": detail}
        print(f"arm {arm}: {'REACHABLE' if ok else 'UNREACHABLE'} "
              f"({spec['roster_key']}) {detail}")

    runnable_arms = [a for a, s in arm_status.items()
                     if s["runnable"] and ARMS[a]["status"] != "blocked"]

    report = {"task_id": "E3", "threshold": THRESHOLD,
              "incident_family": "cascade", "n_incidents": len(incidents),
              "incidents": incidents, "arm_status": arm_status,
              "blocked_arms": [a for a in ARMS if ARMS[a]["status"] == "blocked"],
              "runnable_arms": runnable_arms}

    if args.dry_run:
        report["mode"] = "dry-run"
        json.dump(report, open(args.out, "w"), indent=2)
        print(f"\n[dry-run] -> {args.out}")
        return

    if not runnable_arms:
        report["mode"] = "no-runnable-arms"
        json.dump(report, open(args.out, "w"), indent=2)
        print(f"\nNO runnable arms (all blocked/unreachable) -> {args.out}")
        return

    print(f"\nrunning arms: {runnable_arms}  seeds={args.seeds}")
    results = run(args.seeds, incidents, runnable_arms, args.max_workers)
    report["mode"] = "eval"
    report.update(results)

    # tidy comparison table
    print(f"\n{'='*72}\n3-way cascade comparison (threshold={THRESHOLD})\n{'='*72}")
    print(f"{'arm':<18}{'pass@1':>8}{'95% CI':>16}{'mean':>8}{'std':>7}{'n':>5}")
    print("-" * 72)
    for arm in ARMS:
        if arm in results["by_arm"]:
            o = results["by_arm"][arm]["overall"]
            ci = f"[{o['ci95'][0]:.2f},{o['ci95'][1]:.2f}]"
            print(f"{arm:<18}{o['pass@1']:>8.3f}{ci:>16}{o['mean_reward']:>8.3f}"
                  f"{o['reward_std']:>7.3f}{o['n']:>5}")
        else:
            print(f"{arm:<18}{'BLOCKED':>8}   {ARMS[arm]['note'][:42]}")

    json.dump(report, open(args.out, "w"), indent=2)
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
