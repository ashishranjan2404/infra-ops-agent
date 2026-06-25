#!/usr/bin/env python3
"""Unit tests for the E6 Fireball ablation transforms.

Run: python3 -m pytest experiments/ralph_outputs/E6/artifacts/test_fireball_ablate.py -q
"""
import json
import os

import pytest

import fireball_ablate as fa

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "fixture_fireball.jsonl")


@pytest.fixture
def rec():
    with open(FIXTURE) as f:
        return json.loads(f.readline())


@pytest.fixture
def all_recs():
    with open(FIXTURE) as f:
        return [json.loads(l) for l in f if l.strip()]


# --- structural invariants ---------------------------------------------------

def test_fixture_loads(all_recs):
    assert len(all_recs) == 2
    for r in all_recs:
        assert r["trajectory"], "fixture must have steps"


def test_variants_constant():
    assert fa.VARIANTS == ("full", "state_only", "action_only")


def test_full_is_identity_plus_tag(rec):
    out = fa.transform_full(rec)
    assert out["ablation"] == "full"
    # deep copy: original untouched
    assert "ablation" not in rec
    out.pop("ablation")
    assert out == rec


def test_input_not_mutated(rec):
    before = json.dumps(rec, sort_keys=True)
    fa.transform_state_only(rec)
    fa.transform_action_only(rec)
    fa.transform_full(rec)
    assert json.dumps(rec, sort_keys=True) == before


# --- state_only --------------------------------------------------------------

def test_state_only_drops_assistant_steps(rec):
    out = fa.transform_state_only(rec)
    roles = {s["role"] for s in out["trajectory"]}
    assert roles == {"tool"}
    assert all("thought" not in s and "action" not in s for s in out["trajectory"])


def test_state_only_keeps_state_remediation_drops_action(rec):
    out = fa.transform_state_only(rec)
    rem = out["remediation"]
    assert "state_before" in rem and "state_after" in rem and "recovery_check" in rem
    assert "fix_tool" not in rem and "canonical_fix" not in rem


def test_state_only_strips_gold_action_sequence(rec):
    out = fa.transform_state_only(rec)
    assert "optimal_trajectory" not in out["answer"]
    assert "required_queries" not in out["answer"]
    # observations preserved
    assert "evidence" in out


# --- action_only -------------------------------------------------------------

def test_action_only_drops_tool_steps(rec):
    out = fa.transform_action_only(rec)
    roles = {s["role"] for s in out["trajectory"]}
    assert roles == {"assistant"}
    assert all("action" in s for s in out["trajectory"])


def test_action_only_keeps_fix_drops_state(rec):
    out = fa.transform_action_only(rec)
    rem = out["remediation"]
    assert "fix_tool" in rem and "canonical_fix" in rem
    assert "state_before" not in rem and "state_after" not in rem


def test_action_only_drops_evidence(rec):
    out = fa.transform_action_only(rec)
    assert "evidence" not in out


# --- complementarity: the two ablations partition the trajectory -------------

def test_state_and_action_partition_trajectory(rec):
    full = fa.transform_full(rec)
    s = fa.transform_state_only(rec)
    a = fa.transform_action_only(rec)
    # every original step lands in exactly one of the two ablations
    assert len(s["trajectory"]) + len(a["trajectory"]) == len(full["trajectory"])


def test_step_counts_concrete(rec):
    # fixture rec 0 has 3 assistant + 2 tool steps
    s = fa.transform_state_only(rec)
    a = fa.transform_action_only(rec)
    assert len(a["trajectory"]) == 3
    assert len(s["trajectory"]) == 2


# --- dispatch / streaming / errors -------------------------------------------

def test_apply_variant_dispatch(rec):
    for v in fa.VARIANTS:
        out = fa.apply_variant(rec, v)
        assert out["ablation"] == v


def test_unknown_variant_raises(rec):
    with pytest.raises(KeyError):
        fa.apply_variant(rec, "thought_only")


def test_stream_all(all_recs):
    for v in fa.VARIANTS:
        outs = list(fa.transform_stream(all_recs, v))
        assert len(outs) == len(all_recs)
        assert all(o["ablation"] == v for o in outs)


def test_validate_rejects_bad_record():
    with pytest.raises(ValueError):
        fa.transform_full({"no_trajectory": True})
    with pytest.raises(ValueError):
        fa.transform_full({"trajectory": [{"role": "wizard"}]})
    with pytest.raises(TypeError):
        fa.transform_full(["not", "a", "dict"])


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
