#!/usr/bin/env python3
"""Unit tests for the standalone root-cause accuracy metric (Task B7).

Hermetic: no network, no LLM. Run with:
    python3 -m pytest experiments/ralph_outputs/B7/artifacts/test_root_cause_accuracy.py -q
or directly:
    python3 experiments/ralph_outputs/B7/artifacts/test_root_cause_accuracy.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import root_cause_accuracy as rca  # noqa: E402


# --- classifier: phrasing-robust, discriminative -----------------------------
def test_classify_resource_exhaustion():
    assert rca.classify_root_cause(
        "The thumbnailer pod has a memory leak and is getting OOMKilled") \
        == "resource_exhaustion"


def test_classify_network_fault():
    assert rca.classify_root_cause(
        "Transit gateway saturation caused cross-VPC packet loss and DNS timeouts") \
        == "network_fault"


def test_classify_bad_deploy():
    assert rca.classify_root_cause(
        "A bad rollout / revision regressed checkout; rollback the deployment") \
        == "bad_deploy"


def test_classify_config_error():
    assert rca.classify_root_cause(
        "An expired TLS certificate (a configuration/cert expiry) broke auth") \
        == "config_error"


def test_empty_answer_is_unknown():
    assert rca.classify_root_cause("") == "unknown"
    assert rca.classify_root_cause("   ") == "unknown"


def test_no_signal_is_unknown():
    # generic text with zero category keywords
    assert rca.classify_root_cause("something went wrong with the thing") == "unknown"


def test_phrasing_robust_via_stems():
    # 'leaking' / 'leaked' must stem to the same as 'leak'
    assert rca.classify_root_cause("the service was leaking memory") \
        == rca.classify_root_cause("the service had a memory leak")


# --- gold mapping is grounded in the harness taxonomy ------------------------
def test_gold_category_from_kind():
    assert rca.gold_category_from_kind("mem_leak") == "resource_exhaustion"
    assert rca.gold_category_from_kind("cache_flush") == "saturation"
    assert rca.gold_category_from_kind("dep_revoked") == "dependency_failure"
    assert rca.gold_category_from_kind("totally_made_up") == "unknown"


# --- evaluate(): accuracy, confusion, decoupling -----------------------------
def test_evaluate_perfect():
    recs = [
        {"true_category": "resource_exhaustion",
         "answer": "memory leak, OOMKilled, heap exhausted", "reward": 1.0},
        {"true_category": "network_fault",
         "answer": "DNS packet loss on the network gateway", "reward": 1.0},
    ]
    res = rca.evaluate(recs)
    assert res.n == 2
    assert res.accuracy == 1.0
    assert res.correct == 2


def test_evaluate_mixed_and_confusion():
    recs = [
        {"true_category": "resource_exhaustion", "answer": "memory leak oom"},
        # misdiagnosis: gold is network but answer says memory -> wrong
        {"true_category": "network_fault", "answer": "looks like a memory leak"},
    ]
    res = rca.evaluate(recs)
    assert res.n == 2
    assert res.correct == 1
    assert res.accuracy == 0.5
    # the network gold was predicted as resource_exhaustion
    assert res.confusion["network_fault"]["resource_exhaustion"] == 1


def test_decoupling_from_pass_fail():
    # root-cause CORRECT but incident NOT resolved (reward low) -> disagreement.
    # This is the whole point: the metric is separate from pass/fail.
    recs = [{"true_category": "resource_exhaustion",
             "answer": "clear memory leak, OOMKilled", "reward": 0.1}]
    res = rca.evaluate(recs)
    assert res.accuracy == 1.0          # diagnosis right
    assert res.n_with_resolved == 1
    assert res.rc_vs_resolved_disagree == 1.0   # but pass/fail says fail


def test_root_cause_kind_grounding_path():
    # when no true_category, derive gold from scenario YAML root_cause.kind
    recs = [{"root_cause_kind": "mem_leak", "root_cause": "memory leak, OOM"}]
    res = rca.evaluate(recs)
    assert res.accuracy == 1.0


def test_skips_records_without_gold():
    recs = [{"answer": "memory leak"}, {"true_category": "saturation",
                                        "answer": "cache flush traffic spike"}]
    res = rca.evaluate(recs)
    assert res.n == 1  # first record skipped (no gold label)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
