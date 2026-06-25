#!/usr/bin/env python3
"""Tests for the E8 Fireball sweep harness. Run: pytest test_fireball_sweep.py -q

Validates the harness on a synthetic fixture only. Asserts the anti-fabrication
guards: no fit callback => no scores, <4 points => no learning curve.
"""
import json
import math
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fireball_sweep as fb
import make_fixture


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    d = tmp_path_factory.mktemp("fx")
    p = d / "fixture.jsonl"
    recs = make_fixture.make(2000, seed=1)
    with open(p, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return fb.read_corpus(str(p))


def test_reader_parses_all(corpus):
    assert len(corpus) == 2000
    assert all(isinstance(r, fb.Record) for r in corpus)


def test_reader_skips_non_fireball(tmp_path):
    p = tmp_path / "mixed.jsonl"
    p.write_text(
        json.dumps({"trajectory_id": "a", "incident": "x", "trajectory": [{}]}) + "\n"
        + json.dumps({"foo": "bar"}) + "\n"            # not fireball-shaped -> skip
        + "\n"                                          # blank -> skip
        + json.dumps({"trajectory_id": "a", "incident": "x", "trajectory": [{}]}) + "\n"  # dup id
    )
    recs = fb.read_corpus(str(p))
    assert len(recs) == 1


def test_reader_raises_on_bad_json(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text("{not json}\n")
    with pytest.raises(ValueError):
        fb.read_corpus(str(p))


def test_subset_size_and_cap(corpus):
    assert len(fb.stratified_subset(corpus, 500, "s1")) == 500
    assert len(fb.stratified_subset(corpus, 0, "s1")) == 0
    # cannot draw more than corpus size
    assert len(fb.stratified_subset(corpus, 99999, "s1")) == len(corpus)


def test_subset_deterministic(corpus):
    a = [r.rid for r in fb.stratified_subset(corpus, 300, "s1")]
    b = [r.rid for r in fb.stratified_subset(corpus, 300, "s1")]
    assert a == b
    c = set(r.rid for r in fb.stratified_subset(corpus, 300, "s2"))
    assert set(a) != c  # different seed => different draw


def test_subset_preserves_strata(corpus):
    full = fb.corpus_profile(corpus)["per_difficulty"]
    sub = fb.corpus_profile(fb.stratified_subset(corpus, 800, "s1"))["per_difficulty"]
    full_total = sum(full.values())
    sub_total = sum(sub.values())
    for d, cnt in full.items():
        exp = cnt / full_total
        got = sub.get(d, 0) / sub_total
        assert abs(exp - got) < 0.05, f"difficulty {d}: {exp:.3f} vs {got:.3f}"


def test_nested_subsets(corpus):
    small = set(r.rid for r in fb.stratified_subset(corpus, 200, "s1"))
    big = set(r.rid for r in fb.stratified_subset(corpus, 600, "s1"))
    overlap = len(small & big) / len(small)
    assert overlap > 0.8, f"nesting too weak: {overlap:.2f}"


def test_power_analysis_monotone():
    # smaller effect => need more N; more variance => need more N
    n_big_effect = fb.required_n_for_effect(0.10, 0.22)
    n_small_effect = fb.required_n_for_effect(0.05, 0.22)
    assert n_small_effect > n_big_effect
    n_low_var = fb.required_n_for_effect(0.05, 0.10)
    assert fb.required_n_for_effect(0.05, 0.30) > n_low_var


def test_power_analysis_known_value():
    # delta=0.05, sd=0.22, alpha .05, power .80: n = 2*((1.96+0.8416)*0.22/0.05)^2
    z = (1.959964 + 0.841621)
    expected = math.ceil(2 * (z * 0.22 / 0.05) ** 2)
    assert fb.required_n_for_effect(0.05, 0.22) == expected


def test_power_rejects_bad_args():
    with pytest.raises(ValueError):
        fb.required_n_for_effect(0, 0.2)
    with pytest.raises(ValueError):
        fb.required_n_for_effect(0.05, 0)


def test_no_fit_means_blocked_and_no_scores(corpus):
    sweep = fb.run_sweep(corpus, [100, 200], ["s1"], fit=None)
    assert sweep["blocked"] is True
    assert all(p["score"] is None for p in sweep["points"])
    assert sweep["learning_curve"] is None  # cannot fit without scores


def test_learning_curve_needs_4_points():
    assert fb.fit_learning_curve([(1, 0.1), (2, 0.2)]) is None
    pts = [(100, 0.40), (1000, 0.55), (10000, 0.63), (50000, 0.66)]
    fit = fb.fit_learning_curve(pts)
    assert fit is not None and fit["n_points"] == 4
    assert "knee_N_95pct" in fit


def test_fit_callback_records_scores(corpus):
    # deterministic fake fit just to exercise the wiring (NOT a real curve)
    def fake_fit(sub, seed):
        return min(0.7, 0.3 + 0.05 * math.log10(len(sub)))
    sweep = fb.run_sweep(corpus, [100, 500, 1000], ["s1"], fit=fake_fit)
    assert sweep["blocked"] is False
    assert all(p["score"] is not None for p in sweep["points"])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
