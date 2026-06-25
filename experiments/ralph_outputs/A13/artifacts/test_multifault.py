"""A13 — tests for multi-fault (2 simultaneous faults) scenarios.

Patch-free: exercises only the CURRENT (unpatched) sim.spec / sim.engine. Asserts the new
specs validate, declare exactly 2 distinct clearable faults each (primary root_cause +
one secondary_fault), each fault has its own SLO victim and a canonical-fix step using a
tool that the engine's REMEDIATION physics accepts, and that the primary single-fault path
still runs and clears in the unpatched engine.

Run:  python3 -m pytest experiments/ralph_outputs/A13/artifacts/test_multifault.py -q
"""
from __future__ import annotations

import glob
import os

import yaml

from sim.engine import REMEDIATION, World, apply_action, is_resolved
from sim.spec import Action, load_spec, validate

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SPECS = sorted(
    glob.glob(os.path.join(REPO, "scenarios/cidg/generated/8?-multi-*.yaml"))
)


def _raw(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def test_found_three_specs():
    assert len(SPECS) == 3, f"expected 3 multi-fault specs, found {SPECS}"


def test_specs_validate():
    for p in SPECS:
        errs = validate(load_spec(p))
        assert errs == [], f"{os.path.basename(p)} validation errors: {errs}"


def test_two_distinct_fault_locations():
    for p in SPECS:
        d = _raw(p)
        primary = d["root_cause"]["location"]
        secondary = [sf["location"] for sf in d.get("secondary_faults", [])]
        locs = [primary] + secondary
        assert len(secondary) == 1, f"{p}: expected exactly 1 secondary fault"
        assert len(set(locs)) == 2, f"{p}: fault locations not distinct: {locs}"


def test_each_fault_has_its_own_slo_victim():
    for p in SPECS:
        d = _raw(p)
        slo_nodes = {s.get("node") for s in d["slo"]}
        victims = {sf["slo_node"] for sf in d["secondary_faults"]}
        # every secondary fault's declared SLO victim must actually appear in the SLO block
        assert victims <= slo_nodes, f"{p}: secondary victim {victims} not in SLO {slo_nodes}"
        # and there must be >= 2 SLO victims (one per fault)
        assert len([s for s in slo_nodes if s]) >= 2, f"{p}: <2 SLO victims"


def test_each_fault_has_engine_valid_fix_step():
    for p in SPECS:
        d = _raw(p)
        fix_targets = {(s["tool"], s["args"].get("target")) for s in d["canonical_fix"]["steps"]}
        # primary
        prc = d["root_cause"]
        prim_ok = any(
            tool in REMEDIATION.get(prc["kind"], set()) and tgt == prc["location"]
            for tool, tgt in fix_targets
        )
        assert prim_ok, f"{p}: no engine-valid fix for primary {prc['kind']}@{prc['location']}"
        # secondary
        for sf in d["secondary_faults"]:
            sec_ok = any(
                tool in REMEDIATION.get(sf["kind"], set()) and tgt == sf["location"]
                for tool, tgt in fix_targets
            )
            assert sec_ok, f"{p}: no engine-valid fix for secondary {sf['kind']}@{sf['location']}"
            # declared fix_tool must also be physically valid
            assert sf["fix_tool"] in REMEDIATION.get(sf["kind"], set()), (
                f"{p}: secondary fix_tool {sf['fix_tool']} not in REMEDIATION[{sf['kind']}]"
            )


def test_primary_runs_and_clears_in_unpatched_engine():
    """The primary root_cause is fully live in today's engine: it injects, cascades to its
    victim, and the primary canonical-fix step clears it."""
    for p in SPECS:
        spec = load_spec(p)
        world = World.from_spec(spec)
        # cascade: at least one node carries non-zero error after propagation
        assert any(v["error_rate_pct"] > 0 for v in world.nodes.values()), f"{p}: no cascade"
        assert not is_resolved(world), f"{p}: resolved before any fix"
        # apply the primary fix step (the one targeting the root_cause location)
        prim_step = next(
            s for s in spec.canonical_fix.steps
            if s.args.get("target") == spec.root_cause.location
        )
        apply_action(world, Action(tool=prim_step.tool, args=prim_step.args))
        assert world.root_cleared, f"{p}: primary fix did not clear root {spec.root_cause.location}"
