#!/usr/bin/env python3
"""Unit tests for A10 blast_radius propagation + tiering."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import blast_radius as br  # noqa: E402


def test_linear_chain_fault_at_dependency():
    # A depends on B depends on C; fault at C reaches all callers.
    edges = [("A", "B"), ("B", "C")]
    assert br.reverse_reachable("C", edges) == {"A", "B", "C"}


def test_linear_chain_fault_at_top_caller():
    edges = [("A", "B"), ("B", "C")]
    assert br.reverse_reachable("A", edges) == {"A"}


def test_fanout():
    # B and C both depend on A; fault at A reaches B and C.
    edges = [("B", "A"), ("C", "A")]
    assert br.reverse_reachable("A", edges) == {"A", "B", "C"}


def test_no_edges():
    assert br.reverse_reachable("solo", []) == {"solo"}


def test_tier_sev1_by_count():
    assert br.severity_tier(4, 0.7, False) == "SEV1"


def test_tier_sev1_by_highsev_cascade():
    assert br.severity_tier(2, 0.95, True) == "SEV1"


def test_tier_sev2_by_count():
    assert br.severity_tier(2, 0.1, False) == "SEV2"


def test_tier_sev2_by_cascade():
    assert br.severity_tier(1, 0.1, True) == "SEV2"


def test_tier_sev3_contained():
    assert br.severity_tier(1, 0.7, False) == "SEV3"


def test_real_scenario_consul():
    path = os.path.join(
        br.REPO_ROOT, "scenarios", "cidg", "generated",
        "54-slack-consul-cache-db.yaml",
    )
    if not os.path.exists(path):
        return  # scenario not present; skip silently
    rec = br.compute_for_scenario(path)
    assert rec["root_cause_node"] == "consul-agent"
    assert rec["services_affected"] == 4
    assert set(rec["affected_services"]) == {
        "consul-agent", "ingress-gw", "cache-ring", "vitess-db"}
    assert rec["severity_tier"] == "SEV1"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns)-failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
