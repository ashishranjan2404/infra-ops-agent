#!/usr/bin/env python3
"""SRE-Degrees — terminal demo trace (asciinema-style, fully offline & deterministic).

Plays an end-to-end incident-response episode over the REAL Tier-A simulator
(sim/engine.py) on a REAL CIDG scenario. No network, no LLM key, no GPU — the agent
policy here is a fixed, scripted "diagnose -> wrong-tool -> feedback -> right-tool"
trajectory so the demo is reproducible byte-for-byte for a screen recording.

The point it dramatizes (the paper's thesis): a small refinement loop with a
deterministic safety/resolve oracle beats one-shot guessing — it tries a tempting
band-aid, the oracle says "root still active", and the loop climbs to the causal fix.

Usage:
    python3 demo_trace.py                      # default scenario, typed playback
    python3 demo_trace.py --scenario <path>    # any CIDG yaml with error_rate_pct SLO
    python3 demo_trace.py --fast               # no typing delay (CI / capture)

Exit code 0 iff the incident is resolved (root cleared AND SLOs green).
"""
from __future__ import annotations

import argparse
import os
import sys
import time

# Make repo root importable no matter where this is run from.
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, _REPO)

from sim.spec import Action, load_spec          # noqa: E402
from sim.engine import World, apply_action, is_resolved  # noqa: E402

DEFAULT_SCENARIO = "scenarios/cidg/generated/44-search-cpu-starve.yaml"

# ANSI (kept minimal; degrade gracefully if NO_COLOR set)
_NC = os.environ.get("NO_COLOR")
def _c(code: str, s: str) -> str:
    return s if _NC else f"\033[{code}m{s}\033[0m"
DIM = lambda s: _c("2", s)
BOLD = lambda s: _c("1", s)
GREEN = lambda s: _c("32", s)
RED = lambda s: _c("31", s)
YELLOW = lambda s: _c("33", s)
CYAN = lambda s: _c("36", s)

_TYPE_DELAY = 0.012
_LINE_PAUSE = 0.35


def _emit(text: str, *, type_it: bool = False) -> None:
    if type_it and _TYPE_DELAY:
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(_TYPE_DELAY)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _prompt(cmd: str) -> None:
    _emit(DIM("sre-degrees$ ") + cmd, type_it=True)
    if _LINE_PAUSE:
        time.sleep(_LINE_PAUSE)


def _snapshot(world: World, node: str) -> str:
    err = world.metric(node, "error_rate_pct")
    lat = world.metric(node, "p99_latency_ms")
    color = GREEN if err < 5 else RED
    return f"{node:<16} error={color(f'{err:5.1f}%')}  p99={lat:6.1f}ms"


def run(scenario_path: str) -> int:
    spec = load_spec(scenario_path)
    root_node = spec.root_cause.location.split("->")[0].strip()
    kind = spec.root_cause.kind
    victim = next((s.node for s in spec.slo if s.node), root_node)

    _emit(BOLD(CYAN("\n=== SRE-Degrees: autonomous incident response demo ===")))
    _emit(DIM(f"scenario : {os.path.basename(scenario_path)}"))
    _emit(DIM(f"simulator: sim/engine.py (deterministic Tier-A graph kernel)\n"))

    _prompt("incident open --auto")
    world = World.from_spec(spec)
    _emit(YELLOW(f"  [PAGE] SLO breach on '{victim}' — error rate over threshold"))
    _emit("  " + _snapshot(world, victim))
    _emit(DIM(f"  hidden root-cause kind = {kind} @ {root_node} "
              f"(unknown to the agent)\n"))

    # ---- step 1: diagnose ----------------------------------------------------
    _prompt("agent diagnose")
    _emit(f"  hypothesis : degradation localizes to {BOLD(root_node)}")
    _emit(f"  category   : resource/cpu pressure (from metric shape)\n")

    # ---- step 2: tempting band-aid (wrong tool) ------------------------------
    wrong = Action(tool="restart_pod", args={"target": root_node})
    _prompt(f"agent act --tool restart_pod --target {root_node}")
    apply_action(world, wrong)
    ok = is_resolved(world)
    _emit("  " + _snapshot(world, victim))
    _emit(RED("  [ORACLE] root still active — restart did not clear the fault"))
    _emit(DIM("  feedback -> refine: restart treats symptoms, not cpu starvation\n"))
    assert not ok, "demo invariant: band-aid must NOT resolve"

    # ---- step 3: causal fix (right tool) -------------------------------------
    right = Action(tool="scale_deployment", args={"target": root_node})
    _prompt(f"agent act --tool scale_deployment --target {root_node}")
    apply_action(world, right)
    ok = is_resolved(world)
    _emit("  " + _snapshot(world, victim))
    if ok:
        _emit(GREEN("  [ORACLE] root cleared AND SLOs green — incident RESOLVED\n"))
    else:
        _emit(RED("  [ORACLE] still unresolved\n"))

    # ---- summary -------------------------------------------------------------
    _prompt("incident summary")
    _emit(f"  attempts     : 2 (1 refinement)")
    _emit(f"  fix          : scale_deployment @ {root_node}")
    _emit(f"  resolved     : {GREEN('yes') if ok else RED('no')}")
    _emit(BOLD(CYAN("=== end of trace ===\n")))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=DEFAULT_SCENARIO)
    ap.add_argument("--fast", action="store_true", help="disable typing/pauses")
    args = ap.parse_args()
    if args.fast or os.environ.get("DEMO_FAST"):
        global _TYPE_DELAY, _LINE_PAUSE
        _TYPE_DELAY = 0.0
        _LINE_PAUSE = 0.0
    path = args.scenario
    if not os.path.isabs(path):
        path = os.path.join(_REPO, path)
    return run(path)


if __name__ == "__main__":
    raise SystemExit(main())
