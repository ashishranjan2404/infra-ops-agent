#!/usr/bin/env python3
"""H6 — CI scenario validator for CIDG.

A CI gate that asserts EVERY scenario YAML is (a) schema-valid and (b) accepted by
the Tier-A sim engine. It is the "does this YAML even load and run" gate that must be
green before any deeper semantic audit (e.g. A16's fix_resolves check) is meaningful.

Per scenario YAML (scenarios/cidg/*.yaml + scenarios/cidg/generated/*.yaml):
  1. YAML parses + load_spec() builds a ScenarioSpec   -> catches malformed YAML / drift
  2. sim.spec.validate(spec) returns no errors          -> closed-vocab + structural schema
  3. World.from_spec(spec) instantiates without raising -> engine injects + propagates t0
  4. each canonical_fix step applies via apply_action() -> action space is runnable
  5. world.run(sustain) settles without raising         -> propagate() is stable

A scenario PASSES iff all 5 hold. Any failure is reported with its category and the
process exits nonzero so CI fails the build. Nothing is patched; this only READS the
shared core (sim/spec.py, sim/engine.py) and the YAMLs.

Exit codes (CI contract):
  0  every scenario passed
  1  one or more scenarios failed (schema or engine-acceptance)
  2  usage / harness error (no scenarios found, bad args, import failure)

Usage:
  python3 experiments/ralph_outputs/H6/artifacts/ci_validate_scenarios.py
  python3 .../ci_validate_scenarios.py --json report.json --quiet
  python3 .../ci_validate_scenarios.py --glob 'scenarios/cidg/generated/*.yaml'
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import traceback

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Stages, in order. The first failing stage is the scenario's failure category.
STAGE_LOAD = "load"           # YAML parse + dataclass build
STAGE_SCHEMA = "schema"       # sim.spec.validate() closed-vocab/structural errors
STAGE_INSTANTIATE = "instantiate"  # World.from_spec (inject + first propagate)
STAGE_APPLY = "apply_fix"     # apply_action over canonical_fix steps
STAGE_SETTLE = "settle"       # world.run(sustain_ticks) propagate stability


def default_globs() -> list[str]:
    return [
        os.path.join(REPO, "scenarios/cidg/*.yaml"),
        os.path.join(REPO, "scenarios/cidg/generated/*.yaml"),
    ]


def resolve_paths(patterns: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for pat in patterns:
        p = pat if os.path.isabs(pat) else os.path.join(REPO, pat)
        for m in glob.glob(p):
            seen.setdefault(os.path.abspath(m), None)
    return sorted(seen)


def check_one(path: str) -> dict:
    """Run the 5 CI stages over one scenario. Returns a structured record."""
    from sim.spec import load_spec, validate
    from sim.engine import World, apply_action

    rel = os.path.relpath(path, REPO)
    rec: dict = {
        "file": rel,
        "id": None,
        "ok": False,
        "failed_stage": None,
        "schema_errors": [],
        "error": None,
    }
    # 1. load
    try:
        spec = load_spec(path)
        rec["id"] = spec.id
    except Exception as e:  # noqa: BLE001
        rec["failed_stage"] = STAGE_LOAD
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc().splitlines()[-3:]
        return rec

    # 2. schema
    try:
        errs = validate(spec)
    except Exception as e:  # noqa: BLE001 — validate() itself blowing up is a schema fail
        rec["failed_stage"] = STAGE_SCHEMA
        rec["error"] = f"validate() raised {type(e).__name__}: {e}"
        return rec
    if errs:
        rec["failed_stage"] = STAGE_SCHEMA
        rec["schema_errors"] = errs
        rec["error"] = f"{len(errs)} schema error(s)"
        return rec

    # 3. instantiate (engine acceptance: inject hidden fault + first propagate)
    try:
        world = World.from_spec(spec)
    except Exception as e:  # noqa: BLE001
        rec["failed_stage"] = STAGE_INSTANTIATE
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc().splitlines()[-3:]
        return rec

    # 4. apply canonical fix (action space is runnable against the engine)
    try:
        for action in spec.canonical_fix.steps:
            apply_action(world, action)
    except Exception as e:  # noqa: BLE001
        rec["failed_stage"] = STAGE_APPLY
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc().splitlines()[-3:]
        return rec

    # 5. settle (propagate stays well-defined over sustain window)
    try:
        sustain = max((s.sustain_ticks for s in spec.slo), default=3)
        world.run(sustain)
    except Exception as e:  # noqa: BLE001
        rec["failed_stage"] = STAGE_SETTLE
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc().splitlines()[-3:]
        return rec

    rec["ok"] = True
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CI validator: every CIDG YAML must pass the sim engine.")
    ap.add_argument("--glob", action="append", default=None,
                    help="Glob(s) of scenario YAMLs (repeatable). Default: scenarios/cidg + generated.")
    ap.add_argument("--json", default=None, help="Write the full JSON report to this path.")
    ap.add_argument("--quiet", action="store_true", help="Only print the summary line + failures.")
    args = ap.parse_args(argv)

    try:
        # Import early so an import failure is a clean exit 2, not a crash mid-loop.
        import sim.spec  # noqa: F401
        import sim.engine  # noqa: F401
    except Exception as e:  # noqa: BLE001
        print(f"HARNESS ERROR: cannot import sim engine: {e}", file=sys.stderr)
        return 2

    patterns = args.glob if args.glob else default_globs()
    paths = resolve_paths(patterns)
    if not paths:
        print(f"HARNESS ERROR: no scenario YAMLs matched {patterns}", file=sys.stderr)
        return 2

    results = [check_one(p) for p in paths]
    npass = sum(1 for r in results if r["ok"])
    failed = [r for r in results if not r["ok"]]

    by_stage: dict[str, int] = {}
    for r in failed:
        by_stage[r["failed_stage"]] = by_stage.get(r["failed_stage"], 0) + 1

    report = {
        "summary": {
            "total": len(results),
            "pass": npass,
            "fail": len(failed),
            "all_pass": not failed,
            "failures_by_stage": by_stage,
        },
        "scenarios": results,
    }

    if args.json:
        out = args.json if os.path.isabs(args.json) else os.path.join(REPO, args.json)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w") as f:
            json.dump(report, f, indent=2)

    if not args.quiet:
        for r in results:
            if r["ok"]:
                print(f"OK    {r['file']}  [{r['id']}]")
    for r in failed:
        print(f"FAIL  {r['file']}  [{r['id']}]  stage={r['failed_stage']}  {r['error']}")
        for se in r.get("schema_errors", []):
            print(f"        - {se}")

    print(f"\n{npass}/{len(results)} scenarios pass the sim engine"
          + (f"  (failures by stage: {by_stage})" if by_stage else ""))
    if args.json:
        print(f"report -> {args.json}")

    return 0 if report["summary"]["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
