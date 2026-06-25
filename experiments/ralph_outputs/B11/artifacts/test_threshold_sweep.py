#!/usr/bin/env python3
"""B11 offline tests for threshold_sweep — no network, no shared imports.

Verifies the COPIED estimators match the canonical formula in
experiments/compute_pass_at_k.py (PSRE/DEVOPS compromise, 05_ouroboros), and that
the sweep produces the contracted output on real data.
"""
import importlib.util
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ts = _load("threshold_sweep", os.path.join(HERE, "threshold_sweep.py"))


def test_binary_pass_matches_canonical():
    # binary_pass(r, thr) = 1 if r >= thr else 0
    assert ts.binary_pass(0.7, 0.8) == 0
    assert ts.binary_pass(0.8, 0.8) == 1
    assert ts.binary_pass(0.86, 0.86) == 1
    assert ts.binary_pass(0.85, 0.86) == 0
    assert ts.binary_pass(1.0, 0.9) == 1


def test_wilson_matches_hand_formula():
    # recompute the canonical Wilson formula by hand and compare
    def hand(p, n, z=1.96):
        denom = 1 + z * z / n
        c = (p + z * z / (2 * n)) / denom
        s = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
        return (max(0.0, c - s), min(1.0, c + s))
    for p, n in [(0.4, 15), (0.0, 15), (0.07, 15), (1.0, 15)]:
        lo, hi = ts.wilson_ci(p, n)
        hlo, hhi = hand(p, n)
        assert abs(lo - hlo) < 1e-3 and abs(hi - hhi) < 1e-3, (p, n, lo, hi)


def test_sweep_on_real_data():
    import json
    data = json.load(open(os.path.join("/Users/mei/rl/rex/runs/ablation.json")))
    rows = ts.sweep(data["per_incident"], [0.7, 0.8, 0.86, 0.9])
    assert set(rows) == {"0.70", "0.80", "0.86", "0.90"}
    for t, r in rows.items():
        assert len(r["per_arm"]) == 5
        assert "rex" in r["per_arm"]
    # REx beats best control at the PUBLISHED cutoff
    assert rows["0.80"]["rex_pass_rate"] > rows["0.80"]["best_control_pass_rate"]
    # robustness: REx wins at every threshold
    assert all(r["rex_wins"] for r in rows.values())


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            fails += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns)-fails}/{len(fns)} passed")
    raise SystemExit(1 if fails else 0)
