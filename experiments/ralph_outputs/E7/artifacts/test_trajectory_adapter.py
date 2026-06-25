"""
Unit tests for the domain-agnostic trajectory adapter (E7).

Run:
    cd /Users/mei/rl
    python3 -m pytest experiments/ralph_outputs/E7/artifacts/test_trajectory_adapter.py -q

Also wires into the project's REAL deterministic judge (rex/scoring.py) WITHOUT
modifying it, proving an adapted game trajectory is scorable by the existing
SRE eval stack.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

sys.path.insert(0, HERE)        # for trajectory_adapter
sys.path.insert(0, REPO_ROOT)   # for rex.scoring

import trajectory_adapter as ta  # noqa: E402

FIXTURES = json.load(open(os.path.join(HERE, "synthetic_fixtures.json")))


def test_all_domains_registered():
    assert set(ta.registered_domains()) >= {"textworld", "jericho", "alfworld", "sre"}


@pytest.mark.parametrize("domain", ["textworld", "jericho", "alfworld", "sre"])
def test_adapt_produces_canonical(domain):
    raw = FIXTURES[domain][0]
    t = ta.adapt(domain, raw)
    assert isinstance(t, ta.CanonicalTrajectory)
    assert t.domain == domain
    assert t.episode_id
    assert t.gold_target               # required for scoring
    # round-trips to a JSON-serializable dict
    d = t.to_dict()
    json.dumps(d)


def test_step_indices_are_contiguous():
    t = ta.adapt("textworld", FIXTURES["textworld"][0])
    assert [s.t for s in t.steps] == list(range(len(t.steps)))


def test_actions_view():
    t = ta.adapt("jericho", FIXTURES["jericho"][0])
    assert t.actions == ["open window", "enter house"]


def test_missing_gold_target_rejected():
    bad = {"game_id": "x", "objective": "", "walkthrough_goal": "",
           "transitions": []}
    with pytest.raises(ValueError):
        ta.adapt("textworld", bad)


def test_unknown_domain_raises():
    with pytest.raises(KeyError):
        ta.adapt("nethack", {"episode_id": "n", "gold_target": "g"})


def test_sre_scoring_inputs_shape():
    t = ta.adapt("sre", FIXTURES["sre"][0])
    inp = t.to_sre_scoring_inputs()
    assert set(inp) == {"stated_cause", "gold_root", "red_herrings"}
    assert isinstance(inp["red_herrings"], list)


def test_adapted_game_traj_scorable_by_real_sre_judge():
    """
    The load-bearing transfer claim: an adapted *game* trajectory can be fed
    to the project's REAL deterministic judge unchanged.
    """
    from rex.scoring import deterministic_judge, mechanism_score

    # Build a textworld trajectory whose stated answer matches its gold.
    t = ta.adapt("textworld", FIXTURES["textworld"][0])
    # Make the final answer lexically overlap the gold target for a clear pass.
    t.final_answer = "take coin from the pedestal after going east"
    inp = t.to_sre_scoring_inputs()

    score = mechanism_score(**inp)
    assert 0.0 <= score <= 1.0
    # deterministic_judge returns a bool and must not raise on game input
    verdict = deterministic_judge(**inp)
    assert isinstance(verdict, bool)


def test_distractors_flow_as_red_herrings():
    t = ta.adapt("alfworld", FIXTURES["alfworld"][0])
    inp = t.to_sre_scoring_inputs()
    assert "apple" in inp["red_herrings"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
