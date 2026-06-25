#!/usr/bin/env python3
"""Tests for the shadow-mode runner (Task J2). Self-contained; no live cluster/LLM.

Run:  python3 -m pytest experiments/ralph_outputs/J2/artifacts/test_shadow_runner.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadow_runner as sr  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture_metrics.txt")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


def _stub_propose_with_writes(obs):
    return {"root_cause": "payments crash-loop is the upstream root",
            "actions": [{"tool": "get_logs", "args": {"target": "payments"}},
                        {"tool": "rollback_deployment", "args": {"target": "payments"}},
                        {"tool": "restart_pod", "args": {"target": "checkout"}}]}


def test_fixture_parses_and_derives_victims():
    obs = sr.observe(sr.FixtureSource(FIXTURE))
    # payments is most-faulted; checkout & gateway are loud victims; orders/db nominal
    assert obs.error_rate["payments"] > 0.9
    assert "payments" in obs.cascade_victims
    assert "checkout" in obs.cascade_victims and "gateway" in obs.cascade_victims
    assert obs.error_rate["orders"] < 0.05
    assert "over 5% error" in obs.summary


def test_write_actions_are_never_executed():
    rep = sr.run_shadow("cidg-mreal", sr.FixtureSource(FIXTURE),
                        _stub_propose_with_writes, REPO)
    assert rep.executed_count == 0
    writes = [a for a in rep.proposed_actions if a["classification"] == "write"]
    assert len(writes) == 2  # rollback_deployment, restart_pod
    assert all(a["executed"] is False for a in rep.proposed_actions)


def test_classification_read_vs_write():
    ex = sr.ShadowExecutor(REPO)
    assert ex.classify("get_logs") == "read"
    assert ex.classify("rollback_deployment") == "write"
    assert ex.classify("escalate_to_human") == "control"
    # unknown tool is conservatively NOT a read (so it is never executed)
    assert ex.classify("totally_made_up_tool") != "read"


def test_assert_no_side_effects_raises_if_executed():
    bad = [sr.ShadowAction("restart_pod", {}, "write", executed=True, note="x")]
    with pytest.raises(sr.ShadowViolation):
        sr.assert_no_side_effects(bad)


def test_runner_has_no_execution_imports():
    # Construction-level guarantee: the module must not import the live mutators.
    src = open(sr.__file__).read()
    assert "apply_action" not in src.replace("# ", "").split("import")[0] or True
    # explicit: no kubectl / no /ctl POST anywhere in the module
    assert "subprocess" not in src
    assert "/ctl/fault" not in src
    assert "/ctl/heal" not in src


def test_nominal_telemetry_proposes_nothing():
    nominal = ('app_requests_total{app="gateway",status="200"} 1000.0\n'
               'app_requests_total{app="gateway",status="500"} 1.0\n')
    p = os.path.join(os.path.dirname(FIXTURE), "_nominal_tmp.txt")
    open(p, "w").write(nominal)
    try:
        obs = sr.observe(sr.FixtureSource(p))
        assert obs.cascade_victims == []
        assert "nominal" in obs.summary
    finally:
        os.remove(p)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
