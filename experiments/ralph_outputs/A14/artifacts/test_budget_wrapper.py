"""A14 — deterministic, OFFLINE tests for the budget wrapper.

No network: we use a REAL scenario (loaded from YAML) and the REAL `rex.loop.refine_loop`
+ deterministic judge, but inject a FAKE proposer (canned plans) and a FAKE per-call cost
so wall-clock is reproducible. Run:  python3 -m pytest test_budget_wrapper.py -q
                              or:    python3 test_budget_wrapper.py   (self-runs)
"""
from __future__ import annotations

import os
import sys

import pytest

# allow running from the artifacts dir; repo root holds rex/, sim/, agent/
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.dirname(__file__))

from budget_wrapper import (  # noqa: E402
    PRESETS, BudgetConfig, BudgetMeter, _action_cost, budgeted_proposer,
    run_budgeted_episode,
)
from rex.harness import load_scenario  # noqa: E402


# ---- fixtures: canned plans for the oom_kill scenario --------------------------------
def _wrong_plan(sc):
    return {"root_cause": "too few replicas / needs more scaling",
            "actions": [{"tool": "scale_deployment", "args": {"target": sc.fault_node}}]}


def _correct_plan(sc):
    return {"root_cause": ("a per-process memory leak on the service: its RSS climbs past the "
                           "container memory limit and the kernel OOM-kills the pod"),
            "actions": [{"tool": "increase_memory_limit", "args": {"target": sc.fault_node}}]}


def _canned_proposer(plans):
    """Return a proposer that yields the given plans in order, repeating the last."""
    state = {"i": 0}

    def _p(scenario, prior_feedback=None):
        i = min(state["i"], len(plans) - 1)
        state["i"] += 1
        return plans[i](scenario)
    return _p


def _fake_cost(seconds_per_call):
    """A cost_fn that always charges `seconds_per_call`, ignoring the real clock —
    makes time-budget tests deterministic & instant."""
    return lambda t0, t1: seconds_per_call


# ---- unit: action cost ---------------------------------------------------------------
def test_action_cost_counts_only_real_actions():
    assert _action_cost({"actions": []}) == 0
    assert _action_cost({"actions": [{"tool": "x"}, {"tool": "y"}]}) == 2
    assert _action_cost({"actions": [{"tool": "x"}, {"no_tool": 1}, "junk"]}) == 1
    assert _action_cost({}) == 0
    assert _action_cost("not a dict") == 0


# ---- unit: meter over-budget logic ---------------------------------------------------
def test_meter_time_and_step_thresholds():
    m = BudgetMeter(BudgetConfig(time_budget_s=10.0, step_budget=3))
    assert m._over_budget() is None
    m.time_spent_s = 9.9
    assert m._over_budget() is None
    m.steps_spent = 3
    assert "step_budget" in m._over_budget()
    m.steps_spent = 0
    m.time_spent_s = 10.0
    assert "time_budget" in m._over_budget()


# ---- integration: unbounded episode converges (no truncation) ------------------------
def test_unbounded_episode_converges():
    sc = load_scenario("oom_kill")
    propose = _canned_proposer([_wrong_plan, _correct_plan])
    res = run_budgeted_episode(sc, PRESETS["unbounded"], base_propose_fn=propose,
                               cost_fn=_fake_cost(1.0))
    assert res["clean_win"] is True
    assert res["outcome"] == "resolved"
    assert res["budget_truncated"] is False
    # converged in 2 iterations -> 2 proposer calls
    assert res["budget"]["iters_started"] == 2


# ---- integration: STEP budget bites before convergence -------------------------------
def test_step_budget_truncates_episode():
    sc = load_scenario("oom_kill")
    # every plan fires 1 action; step_budget=1 -> after the 1st (wrong) plan we are at
    # the limit, so the 2nd iteration pre-flight-aborts BEFORE the correct fix runs.
    cfg = BudgetConfig(step_budget=1, iter_cap=6, label="one-shot")
    propose = _canned_proposer([_wrong_plan, _correct_plan])
    res = run_budgeted_episode(sc, cfg, base_propose_fn=propose, cost_fn=_fake_cost(0.1))
    assert res["budget_truncated"] is True
    assert "step_budget" in res["truncation_reason"]
    assert res["budget"]["steps_spent"] == 1
    assert res["budget"]["iters_started"] == 1
    # truncated before the fix -> no clean win, escalates (the realistic failure mode)
    assert res["clean_win"] is False
    assert res["outcome"] == "escalated"
    # but the one in-budget iteration IS retained (nothing discarded)
    assert len(res["iterations"]) == 1


# ---- integration: TIME budget bites --------------------------------------------------
def test_time_budget_truncates_episode():
    sc = load_scenario("oom_kill")
    # each call costs 5s; budget 5s -> after 1 call cum=5s >= 5s, so the 2nd pre-flight aborts.
    cfg = BudgetConfig(time_budget_s=5.0, iter_cap=6, label="tight-clock")
    propose = _canned_proposer([_wrong_plan, _correct_plan])
    res = run_budgeted_episode(sc, cfg, base_propose_fn=propose, cost_fn=_fake_cost(5.0))
    assert res["budget_truncated"] is True
    assert "time_budget" in res["truncation_reason"]
    assert res["budget"]["iters_started"] == 1
    assert abs(res["budget"]["time_spent_s"] - 5.0) < 1e-6
    assert res["clean_win"] is False


# ---- integration: a generous budget still lets it win --------------------------------
def test_generous_budget_allows_convergence():
    sc = load_scenario("oom_kill")
    cfg = BudgetConfig(time_budget_s=100.0, step_budget=10, iter_cap=6, label="relaxed2")
    propose = _canned_proposer([_wrong_plan, _correct_plan])
    res = run_budgeted_episode(sc, cfg, base_propose_fn=propose, cost_fn=_fake_cost(2.0))
    assert res["clean_win"] is True
    assert res["budget_truncated"] is False
    assert res["budget"]["steps_spent"] == 2     # both plans fired one action each


# ---- presets are well-formed ---------------------------------------------------------
def test_presets_monotonic_pressure():
    # tighter presets must not have a larger budget than looser ones on either axis
    assert PRESETS["pager-storm"].time_budget_s < PRESETS["tight"].time_budget_s
    assert PRESETS["tight"].time_budget_s < PRESETS["relaxed"].time_budget_s
    assert PRESETS["pager-storm"].step_budget <= PRESETS["tight"].step_budget
    assert PRESETS["unbounded"].is_bounded() is False
    assert PRESETS["tight"].is_bounded() is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
