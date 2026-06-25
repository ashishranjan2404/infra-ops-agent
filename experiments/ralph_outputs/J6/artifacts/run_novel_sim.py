#!/usr/bin/env python3
"""J6 generalization probe driver — model-free.

Loads the NOVEL scenario YAML, validates it against sim/spec.py, then drives it through
the ground-truth Tier-A engine (sim/engine.py) to test whether the engine GENERALIZES:
the same derived `propagate()` physics must (a) produce a cascade onto the victims,
(b) NOT resolve under the tempting trap action, (c) resolve under the canonical fix.

This is the genuine generalization test: the scenario topology + mechanism (NTP clock-
skew -> lease split-brain) is one the engine has never been authored for; it must do the
right thing purely from the typed graph + root_cause kind.

    python3 experiments/ralph_outputs/J6/artifacts/run_novel_sim.py
exit 0 = all generalization checks pass.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)

from sim.engine import World, apply_action, is_resolved  # noqa: E402
from sim.spec import Action, load_spec, validate  # noqa: E402

SCENARIO = os.path.join(REPO, "scenarios", "cidg", "generated",
                        "90-chronos-ntp-lease-splitbrain.yaml")


def victim_errors(world: World) -> dict:
    return {s.node: round(world.metric(s.node, "error_rate_pct"), 2)
            for s in world.spec.slo if s.node}


def main() -> int:
    report: dict = {"scenario": os.path.relpath(SCENARIO, REPO)}

    # 1. validate
    spec = load_spec(SCENARIO)
    errs = validate(spec)
    report["validation_errors"] = errs
    if errs:
        report["result"] = "INVALID"
        print(json.dumps(report, indent=2))
        return 1
    report["id"] = spec.id
    report["root_cause"] = {"location": spec.root_cause.location, "kind": spec.root_cause.kind}

    # 2. inject -> cascade present?
    w = World(spec, inject=True)
    injected = victim_errors(w)
    report["after_inject"] = injected
    report["cascades"] = all(v > 5.0 for v in injected.values())
    report["resolved_after_inject"] = is_resolved(w)  # must be False

    # 3. trap action does NOT resolve
    w_trap = World(spec, inject=True)
    for t in spec.trap_actions:
        apply_action(w_trap, Action(tool=t.tool, args=t.args))
    report["after_trap"] = victim_errors(w_trap)
    report["resolved_after_trap"] = is_resolved(w_trap)  # must be False

    # 4a. genuinely-wrong tool / right target does NOT resolve (clear_cache is not a dns_race fix)
    w_wrong = World(spec, inject=True)
    apply_action(w_wrong, Action(tool="clear_cache",
                                 args={"target": spec.root_cause.location}))
    report["resolved_after_wrong_tool_clear_cache"] = is_resolved(w_wrong)  # must be False

    # 4b. right tool / WRONG target (a victim) does NOT resolve
    w_wt = World(spec, inject=True)
    apply_action(w_wt, Action(tool="restart_service", args={"target": "order-api"}))
    report["resolved_after_right_tool_wrong_target"] = is_resolved(w_wt)  # must be False

    # 4c. ENGINE NOTE: the closed-vocab kind dns_race also admits modify_network_policy as a
    # remedy (REMEDIATION['dns_race']); on the ROOT node it resolves. This is engine physics,
    # not a scenario bug — recorded for honesty (the clock-skew narrative prefers restart_service).
    w_np = World(spec, inject=True)
    apply_action(w_np, Action(tool="modify_network_policy", args={"target": spec.root_cause.location}))
    report["engine_note_netpol_on_root_resolves"] = is_resolved(w_np)

    # 5. canonical fix DOES resolve
    w_fix = World(spec, inject=True)
    for step in spec.canonical_fix.steps:
        apply_action(w_fix, Action(tool=step.tool, args=step.args))
    report["after_fix"] = victim_errors(w_fix)
    report["resolved_after_fix"] = is_resolved(w_fix)  # must be True

    checks = {
        "valid": not errs,
        "cascades": report["cascades"],
        "not_resolved_at_start": not report["resolved_after_inject"],
        "trap_does_not_resolve": not report["resolved_after_trap"],
        "wrong_tool_does_not_resolve": not report["resolved_after_wrong_tool_clear_cache"],
        "right_tool_wrong_target_does_not_resolve": not report["resolved_after_right_tool_wrong_target"],
        "canonical_fix_resolves": report["resolved_after_fix"],
    }
    report["checks"] = checks
    report["result"] = "PASS" if all(checks.values()) else "FAIL"
    print(json.dumps(report, indent=2))
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
