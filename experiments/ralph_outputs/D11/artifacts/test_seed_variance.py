"""pytest for seed_variance.py — CI math, spread handling, collapse flag, edges."""
import importlib.util
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sv", os.path.join(_HERE, "seed_variance.py"))
sv = importlib.util.module_from_spec(_spec)
sys.modules["sv"] = sv          # register so @dataclass can resolve the module
_spec.loader.exec_module(sv)


def test_per_step_spread_uses_logged_std():
    assert sv.per_step_spread({"reward_std": 0.1833, "rewards": [0.1, 0.9]}) == 0.1833


def test_per_step_spread_recomputes_when_absent():
    # population std of [0.0, 1.0] = 0.5
    assert abs(sv.per_step_spread({"rewards": [0.0, 1.0]}) - 0.5) < 1e-9


def test_per_step_spread_single_value_is_zero():
    assert sv.per_step_spread({"rewards": [0.5]}) == 0.0


def test_plateau_std_zero_for_flat_curve():
    recs = [{"step": i, "mean_reward": 0.5, "n": 4, "rewards": [0.4, 0.6]} for i in range(8)]
    r = sv.run_stats("flat", recs, last_k=5, collapse_thresh=0.0)
    assert r.plateau_std == 0.0
    assert r.plateau_mean == 0.5


def test_plateau_window_clamped_when_short():
    recs = [{"step": 0, "mean_reward": 0.5, "n": 4, "rewards": [0.4, 0.6]}]
    r = sv.run_stats("one", recs, last_k=5, collapse_thresh=0.0)
    assert r.plateau_window == 1
    assert r.plateau_std == 0.0  # window < 2


def test_collapse_flag_triggers():
    recs = [
        {"step": 0, "mean_reward": 0.5, "n": 3, "rewards": [0.4, 0.5, 0.6]},
        {"step": 1, "mean_reward": 0.5, "n": 3, "rewards": [0.5, 0.5, 0.5]},  # std 0 -> collapse
    ]
    r = sv.run_stats("c", recs, last_k=5, collapse_thresh=0.03)
    assert r.collapse_steps == [1]


def test_seed_ci_known_values():
    # 3 seeds: mean 0.52, sample std 0.02, sem=0.02/sqrt(3), t(df=2)=4.303
    ci = sv.seed_ci([0.50, 0.52, 0.54], statistic="x")
    assert ci.n_seeds == 3
    assert abs(ci.mean - 0.52) < 1e-9
    assert abs(ci.std - 0.02) < 1e-6
    sem = 0.02 / math.sqrt(3)
    assert abs(ci.sem - round(sem, 4)) < 1e-3
    assert ci.t_mult == 4.303
    half = 4.303 * sem
    assert abs(ci.ci_low - round(0.52 - half, 4)) < 1e-3
    assert abs(ci.ci_high - round(0.52 + half, 4)) < 1e-3


def test_seed_ci_single_seed_none():
    assert sv.seed_ci([0.5], statistic="x") is None


def test_t_multiplier_large_df():
    assert sv.t_multiplier(100) == 1.96
    assert sv.t_multiplier(2) == 4.303


def test_build_report_status_cross_config():
    recs = [{"step": i, "mean_reward": 0.5, "n": 4, "rewards": [0.4, 0.6]} for i in range(6)]
    import json, tempfile
    p = os.path.join(tempfile.mkdtemp(), "r.jsonl")
    with open(p, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    rep = sv.build_report([p], seed_group=None, last_k=5, collapse_thresh=0.03)
    assert rep["mode"] == "cross-config"
    assert "NOT MEASURED" in rep["seed_variance_status"]
    assert rep["seed_ci"] is None
    assert rep["cross_config"] is not None
