#!/usr/bin/env python3
"""Unit tests for effect_size.py (Task B8). Known-value checks for Cohen's d / h."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from effect_size import (  # noqa: E402
    cohens_d, cohens_h, pooled_sd, magnitude, effect_sizes_for_file,
)


def test_cohens_h_known_value():
    # phi(0.5)=pi/2, phi(0.25)=2*asin(0.5)=pi/3 ; h = pi/2 - pi/3 = pi/6 = 0.523599
    assert abs(cohens_h(0.5, 0.25) - math.pi / 6) < 1e-9


def test_cohens_h_sign_and_symmetry():
    assert cohens_h(0.25, 0.5) == -cohens_h(0.5, 0.25)
    assert cohens_h(0.4, 0.4) == 0.0


def test_cohens_h_extremes():
    assert abs(cohens_h(1.0, 0.0) - math.pi) < 1e-12
    assert cohens_h(1.0, 1.0) == 0.0


def test_cohens_h_rejects_out_of_range():
    for bad in (-0.1, 1.1):
        try:
            cohens_h(bad, 0.5)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_cohens_d_known_value():
    # means 7 vs 5, both SD 2, pooled SD 2 -> d = 1.0
    assert abs(cohens_d(7, 2, 2, 5, 2, 2) - 1.0) < 1e-12


def test_cohens_d_half_sd():
    assert abs(cohens_d(0.5, 1.0, 50, 0.0, 1.0, 50) - 0.5) < 1e-12


def test_cohens_d_sign():
    assert cohens_d(5, 2, 10, 7, 2, 10) < 0


def test_pooled_sd_known():
    assert abs(pooled_sd(2, 10, 2, 10) - 2.0) < 1e-12
    assert abs(pooled_sd(3, 5, 5, 5) - math.sqrt(17.0)) < 1e-12


def test_magnitude_thresholds():
    assert magnitude(0.0) == "negligible"
    assert magnitude(0.19) == "negligible"
    assert magnitude(0.2) == "small"
    assert magnitude(0.49) == "small"
    assert magnitude(0.5) == "medium"
    assert magnitude(0.79) == "medium"
    assert magnitude(0.8) == "large"
    assert magnitude(-1.5) == "large"  # uses abs


def test_effect_sizes_for_file_synthetic():
    data = {
        "model": "toy",
        "by_condition": {
            "zero_shot": {"overall": {"n": 100, "passes": 25,
                                      "mean_reward": 0.0, "reward_std": 1.0}},
            "rex": {"overall": {"n": 100, "passes": 50,
                                "mean_reward": 0.5, "reward_std": 1.0}},
        },
    }
    out = effect_sizes_for_file(data, baseline="zero_shot")
    assert len(out["lifts"]) == 1
    lift = out["lifts"][0]
    assert lift["condition"] == "rex"
    # h(0.5,0.25)=pi/6
    assert abs(lift["cohens_h"] - round(math.pi / 6, 4)) < 1e-4
    # d ~ 0.5
    assert abs(lift["cohens_d"] - 0.5) < 1e-3
    assert lift["d_magnitude"] == "medium"
    assert lift["h_magnitude"] == "medium"


if __name__ == "__main__":
    import subprocess
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
