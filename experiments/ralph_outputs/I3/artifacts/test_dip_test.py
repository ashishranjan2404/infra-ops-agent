"""Validation tests for the self-contained Hartigan dip-test implementation.

Run: python3 -m pytest experiments/ralph_outputs/I3/artifacts/test_dip_test.py -q
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dip_test import dip_test, dip_statistic


def test_statistic_in_range():
    rng = np.random.default_rng(1)
    for _ in range(20):
        x = rng.random(rng.integers(4, 300))
        D = dip_statistic(x)
        assert 0.0 <= D <= 0.25


def test_uniform_is_unimodal():
    # Uniform is the least-favourable unimodal null: should NOT be rejected.
    rng = np.random.default_rng(7)
    ps = [dip_test(rng.random(200))[1] for _ in range(5)]
    assert np.mean([p > 0.05 for p in ps]) >= 0.6


def test_unimodal_normal_not_rejected():
    rng = np.random.default_rng(3)
    x = rng.normal(0, 1, 300)
    D, p = dip_test(x)
    assert p > 0.05
    assert D < 0.05


def test_clear_bimodal_rejected():
    rng = np.random.default_rng(11)
    x = np.concatenate([rng.normal(0, 0.05, 150), rng.normal(1, 0.05, 150)])
    D, p = dip_test(x)
    assert p < 0.01
    assert D > 0.1


def test_pass_fail_bimodal_rewards_rejected():
    # Mimics incident-resolution rewards: pile at 0 and 1, thin middle.
    x = np.array([0.0] * 60 + [1.0] * 60 + [0.4, 0.45, 0.75])
    D, p = dip_test(x)
    assert p < 0.05


def test_determinism():
    rng = np.random.default_rng(5)
    x = rng.random(120)
    assert dip_test(x) == dip_test(x)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
