"""Tests for the J8 demo trace — guards the engine invariants the demo depends on,
so the video can never be staged or silently drift. Offline, no network/LLM.

Run:  python3 -m pytest experiments/ralph_outputs/J8/artifacts/test_demo_trace.py -q
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, REPO)

from sim.spec import Action, load_spec          # noqa: E402
from sim.engine import World, apply_action, is_resolved  # noqa: E402

SCENARIO = os.path.join(REPO, "scenarios/cidg/generated/44-search-cpu-starve.yaml")


def _world():
    spec = load_spec(SCENARIO)
    root = spec.root_cause.location.split("->")[0].strip()
    return spec, root, World.from_spec(spec)


def test_t1_fault_injected_unresolved():
    _, _, w = _world()
    assert is_resolved(w) is False


def test_t2_bandaid_does_not_resolve():
    _, root, w = _world()
    apply_action(w, Action(tool="restart_pod", args={"target": root}))
    assert is_resolved(w) is False, "restart_pod must NOT fix cpu_starve"


def test_t3_causal_fix_resolves():
    _, root, w = _world()
    apply_action(w, Action(tool="restart_pod", args={"target": root}))
    apply_action(w, Action(tool="scale_deployment", args={"target": root}))
    assert is_resolved(w) is True


def test_t4_t5_demo_runs_and_transcript_content():
    env = dict(os.environ, NO_COLOR="1")
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "demo_trace.py"), "--fast"],
        capture_output=True, text=True, env=env,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "[ORACLE] root still active" in out
    assert "RESOLVED" in out
    assert "search-api" in out
