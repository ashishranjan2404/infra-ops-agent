#!/usr/bin/env python3
"""D9 tests — schedule builder + comparison harness invariants.

Pure/deterministic; no model calls, no network. Run:
    python3 -m pytest test_curriculum_schedule.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import curriculum_schedule as cs
import curriculum_vs_random as cvr


def test_a12_order_loads():
    data = cs.load_order()
    assert data["n"] == len(data["order_easy_to_hard"]) == len(data["incidents"])
    assert data["n"] >= 30  # the CIDG set


def test_curriculum_is_easy_to_hard():
    data = cs.load_order()
    diff = {r["id"]: r["difficulty"] for r in data["incidents"]}
    order = data["order_easy_to_hard"]
    diffs = [diff[i] for i in order]
    # A12 guarantees non-decreasing difficulty along the order
    assert diffs == sorted(diffs)


def test_bands_cover_all_ids_no_overlap():
    sched = cs.build_schedule("curriculum", n_stages=5)
    seen = []
    for stg in sched["stages"]:
        seen.extend(stg["newly_unlocked"])
    assert sorted(seen) == sorted(sched["ordered_ids"])
    assert len(seen) == len(set(seen))  # no incident unlocked twice


def test_curriculum_progressive_unlock_and_rehearsal():
    sched = cs.build_schedule("curriculum", n_stages=5, rehearsal=0.3)
    # active set grows monotonically; newest band has weight 1.0, old bands 0.3
    prev = 0
    for stg in sched["stages"]:
        assert stg["n_active"] >= prev
        prev = stg["n_active"]
        weights = {a["weight"] for a in stg["active_incidents"]}
        assert 1.0 in weights
        if stg["stage"] > 0:
            assert 0.3 in weights


def test_random_seed_deterministic():
    a = cs.build_schedule("random", n_stages=5, seed=42)
    b = cs.build_schedule("random", n_stages=5, seed=42)
    c = cs.build_schedule("random", n_stages=5, seed=43)
    assert a["ordered_ids"] == b["ordered_ids"]
    assert a["ordered_ids"] != c["ordered_ids"]  # different seed -> different shuffle


def test_random_and_curriculum_same_incident_set():
    cur = cs.build_schedule("curriculum", n_stages=5)
    rnd = cs.build_schedule("random", n_stages=5, seed=1)
    assert sorted(cur["ordered_ids"]) == sorted(rnd["ordered_ids"])


def test_training_config_embeds_schedule_and_blocker():
    cfg = cs.training_config(n_stages=5)
    assert cfg["algorithm"] == "GRPO"
    assert "curriculum" in cfg and cfg["curriculum"]["n_stages"] == 5
    assert "blocker" in cfg and cfg["blocker"]


def test_comparison_rewards_in_unit_interval():
    rep = cvr.compare(n_stages=6, seeds=3)
    for order, r in rep["results"].items():
        for s in r["stage_eval"]:
            assert 0.0 <= s["mean_reward"] <= 1.0
            assert 0.0 <= s["competence"]


def test_curriculum_auc_beats_random_in_sim():
    # The core hypothesis the harness encodes: easy->hard keeps incidents in the
    # learnable band -> higher area under the learning curve than random.
    rep = cvr.compare(n_stages=6, seeds=5)
    assert rep["verdict"]["curriculum_beats_random"] is True
    assert rep["verdict"]["auc_delta"] > 0.0


def test_anti_curriculum_is_worst_or_tied():
    rep = cvr.compare(n_stages=6, seeds=5)
    anti = rep["results"]["anti"]["auc"]
    cur = rep["results"]["curriculum"]["auc"]
    assert anti <= cur  # hard-first should not beat easy-first


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
