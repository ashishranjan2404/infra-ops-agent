"""Unit tests for the B6 trap-avoidance metric.

Run:  python3 -m pytest experiments/ralph_outputs/B6/artifacts/test_trap_avoidance.py -q
or:   python3 experiments/ralph_outputs/B6/artifacts/test_trap_avoidance.py   (no pytest)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trap_avoidance import (  # noqa: E402
    action_is_trap, classify_episode, trap_avoidance_rate,
    SAFE, TRAP, UNKNOWN,
)

TRAP_SPEC = [{"tool": "scale_deployment", "args": {"target": "thumbnailer"}, "target": "thumbnailer"}]
WILDCARD_SPEC = [{"tool": "clear_cache"}]  # no target -> any target is a trap


# ---- action_is_trap: grounded against rex/scoring._traps_in semantics --------
def test_action_is_trap_exact_target():
    a = {"tool": "scale_deployment", "args": {"target": "thumbnailer"}}
    assert action_is_trap(a, TRAP_SPEC) is True


def test_action_is_trap_wrong_target():
    a = {"tool": "scale_deployment", "args": {"target": "other-svc"}}
    assert action_is_trap(a, TRAP_SPEC) is False


def test_action_is_trap_wrong_tool():
    a = {"tool": "increase_memory_limit", "args": {"target": "thumbnailer"}}
    assert action_is_trap(a, TRAP_SPEC) is False


def test_action_is_trap_wildcard_target_matches_any():
    assert action_is_trap({"tool": "clear_cache", "args": {"target": "x"}}, WILDCARD_SPEC) is True
    assert action_is_trap({"tool": "clear_cache"}, WILDCARD_SPEC) is True


# ---- classify_episode: the three signal paths --------------------------------
def test_classify_via_failed_checks_trap():
    ep = {"scenario": "media-oom-leak", "failed_checks": ["root_cause", "trap_action"]}
    assert classify_episode(ep) == TRAP


def test_classify_via_failed_checks_safe():
    ep = {"scenario": "media-oom-leak", "failed_checks": ["root_cause"]}
    assert classify_episode(ep) == SAFE


def test_classify_failed_checks_empty_is_safe():
    assert classify_episode({"failed_checks": []}) == SAFE


def test_classify_via_structural_recompute():
    scen = {"media-oom-leak": TRAP_SPEC}
    trap_ep = {"scenario": "media-oom-leak",
               "actions": [{"tool": "scale_deployment", "args": {"target": "thumbnailer"}}]}
    safe_ep = {"scenario": "media-oom-leak",
               "actions": [{"tool": "increase_memory_limit", "args": {"target": "thumbnailer"}}]}
    assert classify_episode(trap_ep, scen) == TRAP
    assert classify_episode(safe_ep, scen) == SAFE


def test_classify_structural_from_plan_actions():
    scen = {"media-oom-leak": TRAP_SPEC}
    ep = {"scenario": "media-oom-leak",
          "plan": {"actions": [{"tool": "scale_deployment", "args": {"target": "thumbnailer"}}]}}
    assert classify_episode(ep, scen) == TRAP


def test_classify_unknown_when_no_signal():
    # no failed_checks, no actions, no trap spec available
    assert classify_episode({"scenario": "mystery"}) == UNKNOWN


def test_failed_checks_takes_priority_over_actions():
    # failed_checks says safe even though actions look trappy -> trust the judge token
    scen = {"s": TRAP_SPEC}
    ep = {"scenario": "s", "failed_checks": [],
          "actions": [{"tool": "scale_deployment", "args": {"target": "thumbnailer"}}]}
    assert classify_episode(ep, scen) == SAFE


# ---- trap_avoidance_rate: aggregate ------------------------------------------
def test_rate_basic():
    eps = [
        {"scenario": "a", "failed_checks": []},                       # safe
        {"scenario": "a", "failed_checks": ["trap_action"]},          # trap
        {"scenario": "b", "failed_checks": ["root_cause"]},           # safe
        {"scenario": "b", "failed_checks": ["trap_action", "x"]},     # trap
    ]
    r = trap_avoidance_rate(eps)
    assert r["n_total"] == 4
    assert r["n_safe"] == 2
    assert r["n_trap"] == 2
    assert r["n_unknown"] == 0
    assert r["rate"] == 0.5


def test_rate_excludes_unknown_from_denominator():
    eps = [
        {"scenario": "a", "failed_checks": []},          # safe
        {"scenario": "a", "failed_checks": []},          # safe
        {"scenario": "b"},                               # unknown -> excluded
    ]
    r = trap_avoidance_rate(eps)
    assert r["n_unknown"] == 1
    assert r["rate"] == 1.0  # 2 safe / 2 scorable, unknown not counted


def test_rate_none_when_nothing_scorable():
    r = trap_avoidance_rate([{"scenario": "x"}, {"scenario": "y"}])
    assert r["rate"] is None
    assert r["n_unknown"] == 2


def test_per_scenario_breakdown():
    eps = [
        {"scenario": "a", "failed_checks": []},
        {"scenario": "a", "failed_checks": ["trap_action"]},
        {"scenario": "b", "failed_checks": ["trap_action"]},
    ]
    r = trap_avoidance_rate(eps)
    assert r["per_scenario"]["a"] == {"safe": 1, "trap": 1, "unknown": 0}
    assert r["per_scenario"]["b"] == {"safe": 0, "trap": 1, "unknown": 0}


# ---- consistency with rex/scoring._traps_in (if importable) ------------------
def test_matches_rex_scoring_when_available():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    sys.path.insert(0, repo_root)
    try:
        from rex import scoring  # type: ignore
    except Exception:
        return  # rex not importable in this env -> skip silently

    class _Scn:
        trap_actions = [{"tool": "scale_deployment", "target": "thumbnailer"}]

    a = {"tool": "scale_deployment", "args": {"target": "thumbnailer"}}
    rex_hit = bool(scoring._traps_in([a], _Scn()))
    ours = action_is_trap(a, _Scn.trap_actions)
    assert rex_hit == ours == True


def _run_all():
    import inspect
    mod = sys.modules[__name__]
    fns = [f for n, f in inspect.getmembers(mod, inspect.isfunction) if n.startswith("test_")]
    passed = 0
    for f in fns:
        f()
        passed += 1
        print(f"  PASS {f.__name__}")
    print(f"\n{passed}/{len(fns)} tests passed")
    return passed == len(fns)


if __name__ == "__main__":
    raise SystemExit(0 if _run_all() else 1)
