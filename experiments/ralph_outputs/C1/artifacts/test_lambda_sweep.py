"""Tests for the C1 lambda-sweep driver. Pure, no network."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lambda_sweep import (  # noqa: E402
    score_with_lambda, _candidate_atoms, propose_offline_builder, run_point,
)
from rex.harness_synth import (  # noqa: E402
    TRAIN, HELDOUT, COMPLEXITY_LAMBDA, labeled_examples, train_score,
)

_TRAIN_EX = [e for n in TRAIN for e in labeled_examples(n)]
_HELD_EX = [e for n in HELDOUT for e in labeled_examples(n)]

_RS = [{"match_tools": ["clear_cache"],
        "conditions": [{"feature": "treats_forbidden_category", "op": "==", "value": True}],
        "block": True, "reason": "x"},
       {"match_tools": ["drain_node", "cordon_node"],
        "conditions": [{"feature": "last_ready_node_op", "op": "==", "value": True}],
        "block": True, "reason": "y"}]


def test_score_matches_train_score_at_default_lambda():
    # the load-bearing fidelity check: our parameterized score must equal the core
    # train_score() when lambda == the module's COMPLEXITY_LAMBDA.
    for rs in ([], _RS):
        assert abs(score_with_lambda(rs, _TRAIN_EX, COMPLEXITY_LAMBDA)
                   - train_score(rs, _TRAIN_EX)) < 1e-12


def test_higher_lambda_never_increases_score_for_same_ruleset():
    a = score_with_lambda(_RS, _TRAIN_EX, 0.0)
    b = score_with_lambda(_RS, _TRAIN_EX, 0.05)
    assert b <= a


def test_atoms_are_general_no_incident_ids():
    atoms = _candidate_atoms(_TRAIN_EX)
    assert atoms, "expected at least one candidate atom"
    for a in atoms:
        for c in a["conditions"]:
            assert isinstance(c["value"], bool)  # only bool feature conditions
        assert a["block"] is True


def test_offline_propose_grows_then_stalls():
    # with lambda 0, greedy should add rules; with a huge lambda, seed stays empty.
    p0 = propose_offline_builder(_TRAIN_EX, 0.0)
    root = p0(None)
    assert len(root) >= 1
    p_big = propose_offline_builder(_TRAIN_EX, 5.0)
    assert p_big(None) == []  # no atom can beat its own condition cost


def test_run_point_offline_is_deterministic():
    a = run_point(0.01, _TRAIN_EX, _HELD_EX, budget=8, mode="offline")
    b = run_point(0.01, _TRAIN_EX, _HELD_EX, budget=8, mode="offline")
    assert a["rules"] == b["rules"]
    assert a["heldout_acc"] == b["heldout_acc"]


def test_monotone_conditions_in_lambda():
    # n_conditions should be (weakly) non-increasing as lambda grows across the grid.
    conds = [run_point(l, _TRAIN_EX, _HELD_EX, 8, "offline")["n_conditions"]
             for l in (0.0, 0.03, 0.08, 0.2)]
    assert conds == sorted(conds, reverse=True)
