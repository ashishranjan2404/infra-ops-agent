"""Unit tests for the IAA library (B13). Run: python3 -m pytest test_iaa.py -q"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iaa import (cohen_kappa, fleiss_kappa, krippendorff_alpha,
                 mean_pairwise_cohen, percent_agreement)


def test_perfect_agreement():
    a = ["C", "W", "C", "W"]
    assert percent_agreement(a, a) == 1.0
    assert cohen_kappa(a, a) == 1.0


def test_chance_level_kappa_near_zero():
    # raters independent with balanced marginals -> kappa ~ 0
    a = ["C", "W"] * 50
    b = (["C", "C", "W", "W"] * 25)
    assert abs(cohen_kappa(a, b)) < 0.2


def test_known_cohen_kappa_value():
    # textbook 2x2: both rate 100 items. Agreement cells 45,30; off 15,10
    # rater A: 60 C / 40 W; rater B: 55 C / 45 W; P_o=0.75
    a = ["C"] * 45 + ["C"] * 15 + ["W"] * 10 + ["W"] * 30
    b = ["C"] * 45 + ["W"] * 15 + ["C"] * 10 + ["W"] * 30
    assert percent_agreement(a, b) == pytest.approx(0.75)
    # P_e = .6*.55 + .4*.45 = 0.51 ; kappa = (.75-.51)/(1-.51)
    assert cohen_kappa(a, b) == pytest.approx((0.75 - 0.51) / (1 - 0.51), abs=1e-9)


def test_worse_than_chance_negative():
    a = ["C", "C", "W", "W"]
    b = ["W", "W", "C", "C"]
    assert cohen_kappa(a, b) < 0


def test_degenerate_constant_raters():
    a = ["C"] * 5
    assert cohen_kappa(a, a) == 1.0           # constant + agree
    assert cohen_kappa(["C"] * 5, ["W"] * 5) == 0.0   # constant + disagree


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        cohen_kappa(["C"], ["C", "W"])
    with pytest.raises(ValueError):
        percent_agreement([], [])


def test_fleiss_perfect():
    # 3 items, 3 raters, all agree -> kappa 1 (2 categories)
    table = [[3, 0], [0, 3], [3, 0]]
    assert fleiss_kappa(table) == 1.0


def test_fleiss_uneven_raters_raises():
    with pytest.raises(ValueError):
        fleiss_kappa([[3, 0], [2, 0]])


def test_krippendorff_perfect():
    m = [["C", "W", "C"], ["C", "W", "C"]]
    assert krippendorff_alpha(m) == 1.0


def test_krippendorff_handles_missing():
    # item 2 only rated by one rater -> excluded; rest perfect -> alpha 1
    m = [["C", "W", "C"], ["C", "W", None]]
    assert krippendorff_alpha(m) == 1.0


def test_krippendorff_disagreement_below_one():
    m = [["C", "W", "C", "W"], ["C", "C", "C", "W"]]
    a = krippendorff_alpha(m)
    assert -1.0 <= a < 1.0


def test_mean_pairwise():
    labels = {"r1": ["C", "W", "C"], "r2": ["C", "W", "C"], "r3": ["C", "W", "W"]}
    k = mean_pairwise_cohen(labels)
    assert 0.0 <= k <= 1.0


def test_mean_pairwise_needs_two():
    with pytest.raises(ValueError):
        mean_pairwise_cohen({"r1": ["C"]})
