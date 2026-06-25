#!/usr/bin/env python3
"""Offline contract tests for the G1 SREGym adapter. No cluster, no model, no network.

Run:  python3 -m pytest experiments/ralph_outputs/G1/artifacts/test_sregym_adapter.py -q
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sregym_adapter as A  # noqa: E402

ALL_TOOLS = ["restart_pod", "restart_service", "scale_deployment", "scale_consumers",
             "rollback_deployment", "increase_memory_limit", "rotate_logs",
             "cordon_node", "drain_node", "failover_service", "modify_network_policy",
             "renew_certificate", "clear_cache"]
EXPRESSIBLE = {"restart_pod", "restart_service", "scale_deployment", "scale_consumers",
               "rollback_deployment", "increase_memory_limit", "rotate_logs",
               "cordon_node", "drain_node"}


def test_t1_import_and_translation_load():
    tools = A.load_translation()
    assert set(tools) == set(ALL_TOOLS)


def test_t2_every_tool_translates():
    a = A.make_offline_adapter()
    for tool in ALL_TOOLS:
        # node tools resolve a node name; the StubResolver resolves any non-empty target
        rec = a.translate_action({"tool": tool, "args": {"target": "checkout"}})
        if tool in EXPRESSIBLE:
            assert rec["expressible"] is True, tool
            assert rec["argv"] and rec["argv"][0] == "kubectl", tool
            assert all(isinstance(t, str) for t in rec["argv"]), tool
        else:
            assert rec["expressible"] is False, tool
            assert rec["reason"], tool


def test_t3_build_diagnosis_nonempty():
    a = A.make_offline_adapter()
    obs = A.StubGatherer().gather("x")
    plan = {"root_cause": "service-control control plane crash-looping on bad quota policy",
            "actions": []}
    text = a.build_diagnosis(plan, obs)
    assert "service-control" in text
    assert "victims" in text  # downstream services labeled


def test_t4_dry_run_contract():
    a = A.make_offline_adapter()
    rec = a.run_problem("p-0001")
    for k in ("problem_id", "entry_kind", "diagnosis_text", "plan", "commands",
              "skipped", "out_of_action_space", "partial_action_space", "escalated",
              "submitted", "dry_run", "caveat"):
        assert k in rec, k
    assert rec["submitted"] is False
    assert rec["dry_run"] is True
    assert "non-interactive" in rec["caveat"]


def test_t5_out_of_action_space():
    a = A.make_offline_adapter(stub_plan={
        "root_cause": "bad network policy", "actions": [
            {"tool": "modify_network_policy", "args": {"target": "checkout"}}]})
    rec = a.run_problem("p-0002")
    assert rec["out_of_action_space"] is True
    assert rec["commands"] == []
    assert rec["skipped"] and rec["skipped"][0]["reason"]


def test_t5b_partial_action_space():
    a = A.make_offline_adapter(stub_plan={"root_cause": "mixed", "actions": [
        {"tool": "scale_deployment", "args": {"target": "checkout", "replicas": 4}},
        {"tool": "clear_cache", "args": {"target": "checkout"}}]})
    rec = a.run_problem("p-0003")
    assert rec["partial_action_space"] is True
    assert rec["out_of_action_space"] is False
    assert len(rec["commands"]) == 1


def test_t6_escalation_passthrough():
    a = A.make_offline_adapter(stub_plan={"root_cause": "unknown novel fault", "actions": []})
    rec = a.run_problem("p-0004")
    assert rec["escalated"] is True
    assert rec["commands"] == []


def test_t7_resolver_binding_in_argv():
    a = A.make_offline_adapter()
    rec = a.translate_action({"tool": "scale_deployment",
                              "args": {"target": "payments", "replicas": 5}})
    assert rec["expressible"]
    joined = " ".join(rec["argv"])
    assert "payments" in joined            # resolved name appears (substring, not golden)
    assert "5" in rec["argv"]


def test_t8_unresolved_target_not_expressible():
    a = A.SREGymPlannerAdapter(
        propose_fn=lambda o, f: {},
        gatherer=A.StubGatherer(),
        resolver=A.StubResolver(known={"checkout"}))  # only 'checkout' resolves
    rec = a.translate_action({"tool": "scale_deployment", "args": {"target": "ghost"}})
    assert rec["expressible"] is False
    assert rec["reason"] == "unresolved target"


def test_t9_translation_json_valid():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "action_translation.json")
    with open(path) as fh:
        data = json.load(fh)
    assert "tools" in data and len(data["tools"]) == len(ALL_TOOLS)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
