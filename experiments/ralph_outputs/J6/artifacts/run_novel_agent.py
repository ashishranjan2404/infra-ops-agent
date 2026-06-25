#!/usr/bin/env python3
"""J6 generalization probe — LLM AGENT path (frozen-model code-as-policy).

Runs the REAL rex.loop refinement agent on the NOVEL scenario and grades it with the
P0 deterministic judge (rex.scoring.score_plan). The scenario is registered ONLY in
this process's in-memory _SCENARIOS dict — the shared scenarios/cidg/generated/registry.json
on disk is NEVER written (parallel-safe). This reaches the same agent path used by
rex.eval_pass_at_k without touching any shared core file.

    set -a; source ~/.zshrc; set +a
    python3 experiments/ralph_outputs/J6/artifacts/run_novel_agent.py --model glm-5p2

Reports the graded reward and whether the frozen model GENERALIZES to a never-seen
incident type (pass = reward >= THRESHOLD).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)

import rex.harness as H  # noqa: E402
from rex.loop import refine_loop  # noqa: E402
from rex.harness import run_plan  # noqa: E402
from rex.scoring import score_plan  # noqa: E402

NAME = "chronos_ntp_lease_splitbrain"
THRESHOLD = 0.8


def register_in_memory() -> None:
    """Add the novel scenario to the in-process registry only (no disk write)."""
    H._SCENARIOS[NAME] = {
        "path": "scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml",
        "style": "cascade",
        "gold_root": ("the 'chrono-ntp' time source skewed (+1100ms) so the leader lease "
                      "read as expired and the lock service revoked it -> split-brain; re-sync "
                      "the clock and restart the lease root to re-elect a single leader "
                      "(restart_service on chrono-ntp)"),
        "red_herrings": [
            "a network partition between the API replicas",
            "the order-api needs more replicas to absorb the write load",
            "a bad deploy of the lease service",
        ],
        "fix_tools": ["restart_service"],
        "traps": [{"tool": "scale_deployment", "target": "order-api"}],
        "forbidden": ["bad_deploy", "resource_exhaustion"],
        "recent_deploy": False,
        "family": "novel",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-5p2")
    ap.add_argument("--budget", type=int, default=4)
    args = ap.parse_args()

    register_in_memory()
    import functools
    from rex.loop import propose as _propose
    # bind a reachable gateway model into propose (its default model is captured at def-time)
    propose_fn = functools.partial(_propose, model=args.model)

    sc = H.load_scenario(NAME)
    report = {"scenario": NAME, "model": args.model, "family": "novel",
              "root_cause_kind": sc.kind, "fault_node": sc.fault_node}

    trace: list = []
    try:
        res = refine_loop(sc, budget=args.budget, propose_fn=propose_fn, log=trace.append)
    except Exception as e:  # noqa: BLE001
        report["error"] = f"{type(e).__name__}: {e}"
        report["result"] = "BLOCKED"
        print(json.dumps(report, indent=2))
        return 3

    # best iteration = the highest-scoring plan the loop found
    best = res["iterations"][res["best_iter"]] if res.get("iterations") else {}
    best_plan = best.get("plan", {})
    sim_result = run_plan(best_plan, sc)
    reward, _fb = score_plan(best_plan, sc, sim_result)
    report["best_score"] = round(res.get("best_score", -1.0), 3)
    report["regraded_reward"] = round(float(reward), 3)
    report["resolved"] = sim_result.get("resolved")
    report["clean_win"] = res.get("clean_win")
    report["iterations"] = len(res.get("iterations", []))
    report["stated_root_cause"] = best.get("stated_root_cause", "")
    report["diagnosis_correct"] = best.get("diagnosis_correct")
    report["final_plan_actions"] = best_plan.get("actions", [])
    report["generalizes"] = bool(reward >= THRESHOLD)
    report["result"] = "PASS" if reward >= THRESHOLD else "FAIL"
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
