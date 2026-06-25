#!/usr/bin/env python3
"""pytest suite for the SREGym adapter (task G2).

Run:  python -m pytest experiments/ralph_outputs/G2/artifacts/test_adapter.py -q
"""
from __future__ import annotations

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from sregym_adapter import SREGymEnv  # noqa: E402

# error_rate_pct-only SLO scenario the Tier-A engine fully supports (rollback resolves).
SCEN = "scenarios/cidg/22-leaf-bad-deploy-positive.yaml"


@pytest.fixture()
def env():
    e = SREGymEnv(SCEN)
    e.reset()
    return e


def test_reset_returns_problem(env):
    obs = env.reset()
    assert obs["problem"]
    assert obs["phases"] == ["diagnosis", "mitigation"]
    assert env.fault_node in obs["nodes"]


def test_metrics_reflect_fault(env):
    m = env.get_metrics(env.fault_node)
    assert m[env.fault_node]["error_rate_pct"] > 0.0


def test_structured_fix_resolves(env):
    r = env.cluster_control(tool=env.canonical_fix_tool(), args={"target": env.fault_node})
    assert r["applied"] and r["target_matched_node"]
    assert env.submit_mitigation()["resolved"] is True


def test_wrong_tool_does_not_resolve(env):
    env.cluster_control(tool="restart_pod", args={"target": env.fault_node})
    assert env.submit_mitigation()["resolved"] is False


def test_kubectl_translation_resolves(env):
    r = env.cluster_control(command=f"kubectl rollout undo deploy/{env.fault_node}")
    assert r["untranslated"] is False
    assert r["tool"] == "rollback_deployment"
    assert env.submit_mitigation()["resolved"] is True
    assert env.fidelity()["untranslated_kubectl"] == 0


def test_kubectl_read_verb_is_noop(env):
    r = env.cluster_control(command=f"kubectl get pods {env.fault_node}")
    assert r.get("read_only") is True
    assert r["untranslated"] is False


def test_kubectl_untranslated_counted(env):
    r = env.cluster_control(command="kubectl edit configmap app-flags")
    assert r["untranslated"] is True
    assert env.fidelity()["untranslated_kubectl"] == 1
    assert env.fidelity()["untranslated_rate"] == 1.0


def test_diagnosis_grading_positive(env):
    d = env.submit_diagnosis(f"The {env.fault_node} is serving a bad deploy revision.")
    assert d["diagnosis_correct"] is True


def test_diagnosis_grading_negative(env):
    d = env.submit_diagnosis("Everything looks fine, probably the weather.")
    assert d["diagnosis_correct"] is False


def test_traces_flagged_low_fidelity(env):
    t = env.get_traces()
    assert t["low_fidelity"] is True
