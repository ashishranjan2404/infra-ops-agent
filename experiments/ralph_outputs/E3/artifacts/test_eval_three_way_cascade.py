#!/usr/bin/env python3
"""Network-free tests for the E3 three-way cascade harness.

Validates the parts that don't need a live model: incident selection (exactly 14
distinct cascade incidents, all genuinely family=cascade), arm wiring (3 arms,
exactly one blocked = fireball), the local-roster registration (no mutation of the
two trained/zero-shot slugs into shared agent/models on import), and the summarize
stats. Run: python3 -m pytest experiments/ralph_outputs/E3/artifacts/test_eval_three_way_cascade.py -q
"""
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))

import eval_three_way_cascade as E  # noqa: E402
from rex.harness import scenarios_by_family  # noqa: E402


def test_selects_14_distinct_cascade_incidents():
    inc = E.select_cascade_incidents(14)
    assert len(inc) == 14
    assert len(set(inc)) == 14
    cascade = set(scenarios_by_family().get("cascade", []))
    assert set(inc).issubset(cascade), "every selected incident must be family=cascade"


def test_selection_is_deterministic():
    assert E.select_cascade_incidents(14) == E.select_cascade_incidents(14)


def test_three_arms_one_blocked_is_fireball():
    assert set(E.ARMS) == {"zero_shot", "opensre_trained", "fireball_trained"}
    blocked = [a for a, s in E.ARMS.items() if s["status"] == "blocked"]
    assert blocked == ["fireball_trained"]
    assert E.ARMS["fireball_trained"]["roster_key"] is None


def test_runnable_arms_have_distinct_real_slugs():
    z = E.ARMS["zero_shot"]["roster_key"]
    o = E.ARMS["opensre_trained"]["roster_key"]
    assert z != o
    assert E.EXTRA_ROSTER[z]["model"] == "Qwen/Qwen3-8B"            # base = control
    assert E.EXTRA_ROSTER[o]["model"] == "opensre-qwen3-8b-1e439a"  # OpenSRE forked slug


def test_register_extra_models_is_local_and_idempotent():
    from agent.models import ROSTER
    assert "qwen3-8b-base" not in ROSTER  # not present until we register
    E.register_extra_models()
    E.register_extra_models()  # idempotent (setdefault)
    assert ROSTER["qwen3-8b-base"]["model"] == "Qwen/Qwen3-8B"
    assert ROSTER["opensre-qwen3-8b"]["provider"] == "gateway"


def test_summarize_pass_and_floor():
    # 4 rewards: two pass (>=0.8), two fail
    s = E.summarize([0.9, 0.85, 0.3, 0.0])
    assert s["n"] == 4 and s["passes"] == 2
    assert s["pass@1"] == 0.5
    assert s["mean_reward"] == 0.5125
    assert s["reward_std"] > 0  # within-group spread exists
    empty = E.summarize([])
    assert empty["n"] == 0 and empty["pass@1"] == 0.0


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
