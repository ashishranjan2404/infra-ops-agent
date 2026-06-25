"""A14 — demo: run the SAME scenario under every budget preset and show how
time/step pressure changes the outcome. OFFLINE (canned proposer + fake clock),
so it runs instantly with no API key. Swap `canned` for `rex.loop.propose` (and
drop cost_fn) for a live run.

    python3 demo_budget_variants.py
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.dirname(__file__))

from budget_wrapper import PRESETS, run_budgeted_episode  # noqa: E402
from rex.harness import load_scenario  # noqa: E402

# A model that needs TWO tries to converge: a wrong first plan, then the real fix.
# Under tight budgets it never reaches the fix -> realistic "ran out of time, escalate".
SECONDS_PER_CALL = 9.0   # pretend each proposal costs 9s of wall clock (a slow on-call model)


def make_proposer(sc):
    plans = [
        {"root_cause": "too few replicas / needs more scaling",
         "actions": [{"tool": "scale_deployment", "args": {"target": sc.fault_node}}]},
        {"root_cause": ("a per-process memory leak: RSS climbs past the container memory "
                        "limit and the kernel OOM-kills the pod"),
         "actions": [{"tool": "increase_memory_limit", "args": {"target": sc.fault_node}}]},
    ]
    state = {"i": 0}

    def _p(scenario, prior_feedback=None):
        i = min(state["i"], len(plans) - 1)
        state["i"] += 1
        return plans[i]
    return _p


def main():
    sc = load_scenario("oom_kill")
    rows = []
    for name, cfg in PRESETS.items():
        res = run_budgeted_episode(
            sc, cfg, base_propose_fn=make_proposer(sc),
            cost_fn=lambda a, b: SECONDS_PER_CALL,   # deterministic offline clock
        )
        b = res["budget"]
        rows.append({
            "variant": name,
            "time_budget_s": cfg.time_budget_s,
            "step_budget": cfg.step_budget,
            "iters": b["iters_started"],
            "time_spent_s": b["time_spent_s"],
            "steps_spent": b["steps_spent"],
            "outcome": res["outcome"],
            "clean_win": res["clean_win"],
            "truncated": res["budget_truncated"],
            "stopped": b["stopped_reason"],
        })

    hdr = f"{'variant':<12}{'t_budget':>9}{'s_budget':>9}{'iters':>6}{'t_spent':>9}{'steps':>6}{'outcome':>11}{'win':>6}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['variant']:<12}{str(r['time_budget_s']):>9}{str(r['step_budget']):>9}"
              f"{r['iters']:>6}{r['time_spent_s']:>9}{r['steps_spent']:>6}"
              f"{r['outcome']:>11}{str(r['clean_win']):>6}")

    out = os.path.join(os.path.dirname(__file__), "demo_results.json")
    json.dump({"scenario": sc.name, "seconds_per_call": SECONDS_PER_CALL, "rows": rows},
              open(out, "w"), indent=2)
    print(f"\nwrote {out}")
    # Headline finding: under enough time pressure the model that needs 2 tries can't win.
    won = [r["variant"] for r in rows if r["clean_win"]]
    lost = [r["variant"] for r in rows if not r["clean_win"]]
    print(f"clean win under: {won}")
    print(f"escalated (out of budget) under: {lost}")


if __name__ == "__main__":
    main()
