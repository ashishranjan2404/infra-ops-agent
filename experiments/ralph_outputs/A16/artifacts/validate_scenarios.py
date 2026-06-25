#!/usr/bin/env python3
"""A16 scenario validator — load every CIDG scenario through the Tier-A sim engine
and assert the documented canonical fix actually resolves the injected incident.

For each scenario YAML under scenarios/cidg/ (+ generated/):
  1. load_spec() it (catches malformed YAML / schema drift)
  2. instantiate World.from_spec() (injects the hidden root cause)
  3. confirm the world is NOT already resolved at t0 (sanity: the fault bites)
  4. apply every step of canonical_fix.steps in order via apply_action()
  5. settle for max(slo.sustain_ticks) ticks
  6. assert is_resolved(world) is True  ==> "fix_resolves" holds in the engine
  7. cross-check against the scenario's own assertions.fix_resolves flag

This does NOT edit any shared core file. It only READS sim/engine.py + the YAMLs.
Failures are reported, never silently patched.

Run:
  python3 experiments/ralph_outputs/A16/artifacts/validate_scenarios.py \
      --out experiments/ralph_outputs/A16/validation_report.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import traceback

REPO = "/Users/mei/rl"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from sim.spec import load_spec  # noqa: E402
from sim.engine import World, apply_action, is_resolved  # noqa: E402


def scenario_paths() -> list[str]:
    """All authored scenarios: the curated cidg/ set + the generated/ set."""
    a = sorted(glob.glob(os.path.join(REPO, "scenarios/cidg/*.yaml")))
    b = sorted(glob.glob(os.path.join(REPO, "scenarios/cidg/generated/*.yaml")))
    return a + b


def validate_one(path: str) -> dict:
    rel = os.path.relpath(path, REPO)
    rec: dict = {
        "file": rel,
        "id": None,
        "status": "error",
        "fix_resolves": False,
        "asserts_fix_resolves": None,
        "fault_active_at_t0": None,
        "root_cleared_after_fix": None,
        "slo_ok_after_fix": None,
        "fix_steps": [],
        "error": None,
    }
    try:
        spec = load_spec(path)
        rec["id"] = spec.id
        rec["asserts_fix_resolves"] = spec.assertions.fix_resolves
        rec["fix_steps"] = [
            {"tool": a.tool, "target": a.args.get("target")} for a in spec.canonical_fix.steps
        ]

        world = World.from_spec(spec)
        rec["fault_active_at_t0"] = not is_resolved(world)

        for action in spec.canonical_fix.steps:
            apply_action(world, action)

        sustain = max((s.sustain_ticks for s in spec.slo), default=3)
        world.run(sustain)

        rec["root_cleared_after_fix"] = world.root_cleared
        # _slo_ok is internal; recompute resolution cleanly via is_resolved.
        resolved = is_resolved(world)
        rec["slo_ok_after_fix"] = resolved or world.root_cleared  # informational
        rec["fix_resolves"] = bool(resolved)
        rec["status"] = "pass" if resolved else "fail"
    except Exception as e:  # noqa: BLE001 — surface per-file, keep going
        rec["status"] = "error"
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc().splitlines()[-3:]
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO, "experiments/ralph_outputs/A16/validation_report.json"))
    args = ap.parse_args()

    paths = scenario_paths()
    results = [validate_one(p) for p in paths]

    n = len(results)
    npass = sum(1 for r in results if r["status"] == "pass")
    nfail = sum(1 for r in results if r["status"] == "fail")
    nerr = sum(1 for r in results if r["status"] == "error")
    # scenarios whose own spec promises fix_resolves but the engine disagrees
    broken_promise = [
        r["file"] for r in results
        if r["asserts_fix_resolves"] and r["status"] != "pass"
    ]

    report = {
        "summary": {
            "total": n, "pass": npass, "fail": nfail, "error": nerr,
            "all_pass": nfail == 0 and nerr == 0,
            "broken_fix_resolves_promises": broken_promise,
        },
        "scenarios": results,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(f"validated {n} scenarios: {npass} pass / {nfail} fail / {nerr} error")
    for r in results:
        if r["status"] != "pass":
            print(f"  {r['status'].upper():5} {r['file']}  "
                  f"(asserts_fix_resolves={r['asserts_fix_resolves']}) "
                  f"{r['error'] or 'root_cleared=' + str(r['root_cleared_after_fix'])}")
    print(f"report -> {args.out}")
    return 0 if report["summary"]["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
