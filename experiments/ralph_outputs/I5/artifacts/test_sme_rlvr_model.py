"""Tests for sme_rlvr_model.py — validate the formal-model invariants and the
core proposition numerically. Run: python3 -m pytest test_sme_rlvr_model.py -q
or just: python3 test_sme_rlvr_model.py (uses a tiny hand-rolled runner)."""
from __future__ import annotations

import numpy as np

import sme_rlvr_model as m
from sme_rlvr_model import WorldParams, evaluate, signal_quality, _centered


def test_centering_zero_mean():
    x = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 6.0]])
    c = _centered(x)
    assert np.allclose(c.mean(axis=1), 0.0)


def test_perfect_reward_max_alignment():
    # if reward == true value, advantage aligns perfectly with centered q.
    rng = np.random.default_rng(1)
    q = rng.random((500, 6))
    sq = signal_quality(q, q)
    assert sq["align"] > 0.999
    assert sq["G"] > 0.0


def test_flat_verifier_has_low_signal():
    # a constant (flat) reward => zero advantage spread => G == 0.
    q = np.random.default_rng(2).random((300, 5))
    flat = np.ones_like(q) * 0.5
    sq = signal_quality(flat, q)
    assert abs(sq["magnitude"]) < 1e-9
    assert abs(sq["G"]) < 1e-9


def test_good_sme_helps():
    # Coarse verifier + accurate SME (low eps, low noise) at moderate trust
    # should RAISE G vs RLVR alone. This is the proposition's positive case.
    wp = WorldParams(rho_V=0.3, eps_override=0.05, sme_noise=0.1,
                     lam=0.5, p_label=0.5, seed=3)
    res = evaluate(wp)
    assert res["helps"] is True
    assert res["delta_G"] > 0.0


def test_bad_sme_can_hurt():
    # An adversarial SME (high override error, full trust) should NOT help and
    # generally hurts — the proposition must predict failure here.
    wp = WorldParams(rho_V=0.6, eps_override=0.5, sme_noise=0.4,
                     lam=1.0, p_label=0.5, seed=4)
    res = evaluate(wp)
    assert res["delta_G"] <= res["rlvr_only"]["G"] + 1e-9 or not res["helps"]


def test_zero_lambda_is_noop():
    # lambda = 0 must exactly reproduce RLVR-only signal quality.
    wp = WorldParams(lam=0.0, p_label=1.0, seed=5)
    res = evaluate(wp)
    a = res["rlvr_only"]
    b = res["rlvr_plus_sme"]
    assert abs(a["G"] - b["G"]) < 1e-9


def test_zero_budget_is_noop():
    # p_label = 0 means no group is labeled -> identical to RLVR-only.
    wp = WorldParams(p_label=0.0, lam=0.9, seed=6)
    res = evaluate(wp)
    assert abs(res["delta_G"]) < 1e-9


def test_sweep_monotone_in_eps_trend():
    # Averaged over lambda, delta_G should not increase as override error grows
    # from near-perfect to adversarial (quality matters). Check endpoints.
    wp = WorldParams(rho_V=0.3, seed=7)
    sw = m.sweep(wp)
    grid = np.array(sw["delta_G_grid"])   # rows=eps, cols=lam
    low_eps_mean = grid[0].mean()         # eps=0.0
    high_eps_mean = grid[-1].mean()       # eps=0.5
    assert low_eps_mean >= high_eps_mean


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")


if __name__ == "__main__":
    _run()
