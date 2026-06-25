#!/usr/bin/env python3
"""J5 case-study runner: run the REAL REx linear refine loop on the Cloudflare
2019-07-02 WAF-regex CPU-exhaustion incident and dump a full structured trace.

Scenario: cloudflare_waf_regex (scenarios/cidg/generated/76-cloudflare-waf-regex.yaml)
Output:   trace.json  (full per-iteration record from rex.loop.refine_loop)

This does NOT edit any shared core file; it only imports them and writes a
task-namespaced JSON artifact. If the frozen LLM is unreachable it falls back to
tracing the deterministic sim with the canonical fix and the canonical trap, so a
valid artifact is always produced (the fallback is clearly flagged).
"""
from __future__ import annotations

import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
sys.path.insert(0, _REPO)

SCENARIO = "cloudflare_waf_regex"
OUT = os.path.join(_HERE, "trace.json")
# Anthropic credits are exhausted on this machine; route the frozen proposer to a
# reachable HUD-gateway frontier model instead (env override, default gpt-5.5).
PROPOSER_MODEL = os.environ.get("J5_PROPOSER_MODEL", "gpt-5.5")


def _live_run() -> dict:
    """Run the real frozen-LLM REx loop. Raises on transport error."""
    from rex.harness import load_scenario
    from rex.loop import refine_loop, propose

    scenario = load_scenario(SCENARIO)

    def proposer(sc, prior_feedback=None):
        return propose(sc, prior_feedback, model=PROPOSER_MODEL)

    steps = []
    res = refine_loop(scenario, budget=6, propose_fn=proposer,
                      log=lambda rec: steps.append(rec))
    return {"mode": "live-llm", "scenario": SCENARIO, "model": PROPOSER_MODEL,
            "prompt": scenario.prompt_text, "result": res, "steps": steps}


def _deterministic_trace() -> dict:
    """Fallback: drive the sim directly with (a) the canonical TRAP, then (b) the
    canonical FIX, so we still produce a real, non-fabricated sim trace."""
    from rex.harness import load_scenario, run_plan

    scenario = load_scenario(SCENARIO)

    trap_plan = {
        "root_cause": "edge-proxy is CPU-starved and needs more capacity",
        "actions": [{"tool": "scale_deployment",
                     "args": {"target": "edge-proxy", "replicas": 8}}],
    }
    fix_plan = {
        "root_cause": ("a WAF rule with a catastrophically-backtracking regex was "
                       "rolled out to waf-engine, pinning CPU; roll the rule back"),
        "actions": [{"tool": "rollback_deployment", "args": {"target": "waf-engine"}}],
    }
    trap_res = run_plan(trap_plan, scenario)
    fix_res = run_plan(fix_plan, scenario)
    return {
        "mode": "deterministic-sim-fallback",
        "scenario": SCENARIO,
        "prompt": scenario.prompt_text,
        "trap": {"plan": trap_plan, "result": trap_res},
        "fix": {"plan": fix_plan, "result": fix_res},
    }


def main() -> None:
    t0 = time.time()
    try:
        out = _live_run()
        out["error"] = None
    except Exception as e:  # network / key / provider failure -> honest fallback
        det = _deterministic_trace()
        det["live_error"] = f"{type(e).__name__}: {e}"
        out = det
    out["elapsed_s"] = round(time.time() - t0, 2)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"mode={out['mode']} elapsed={out['elapsed_s']}s -> {OUT}")
    if out["mode"].startswith("live"):
        r = out["result"]
        print(f"outcome={r['outcome']} clean_win={r['clean_win']} "
              f"best_iter={r['best_iter']} iters={len(out['steps'])}")


if __name__ == "__main__":
    main()
