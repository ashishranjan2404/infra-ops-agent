#!/usr/bin/env python3
"""Unit tests for wilson_ci.py — validate against known textbook/reference values.

Run:  python3 -m pytest test_wilson_ci.py -q     (from this directory)
  or: python3 test_wilson_ci.py                  (no-pytest fallback runner)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wilson_ci import wilson_ci, point_estimate, iter_cells, Z95  # noqa: E402


def _ref_wilson(passes, n, z=Z95):
    """Independent reference implementation (the closed form, written separately)."""
    p = passes / n
    z2 = z * z
    d = 1 + z2 / n
    c = (p + z2 / (2 * n)) / d
    h = z / d * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (c - h, c + h)


def test_matches_independent_reference():
    for passes, n in [(0, 30), (1, 30), (8, 30), (15, 30), (29, 30),
                      (36, 150), (4, 60), (1, 50), (50, 50)]:
        lo, hi = wilson_ci(passes, n)
        rlo, rhi = _ref_wilson(passes, n)
        assert abs(lo - max(0.0, rlo)) < 1e-9, (passes, n, lo, rlo)
        assert abs(hi - min(1.0, rhi)) < 1e-9, (passes, n, hi, rhi)


def test_known_value_p_half():
    # Classic textbook case: 50/100 with z=1.96 -> Wilson [0.4038, 0.5962].
    lo, hi = wilson_ci(50, 100, z=1.96)
    assert abs(lo - 0.4038) < 1e-3, lo
    assert abs(hi - 0.5962) < 1e-3, hi


def test_known_value_zero_successes():
    # 0/10, z=1.96. Wilson upper bound is the classic "rule of 3.7"-ish: 0.2775.
    lo, hi = wilson_ci(0, 10, z=1.96)
    assert lo == 0.0, lo
    assert abs(hi - 0.2775) < 1e-3, hi


def test_known_value_all_successes():
    # 10/10 is the mirror of 0/10: lo = 1 - 0.2775 = 0.7225, hi = 1.0.
    lo, hi = wilson_ci(10, 10, z=1.96)
    assert abs(lo - 0.7225) < 1e-3, lo
    assert hi == 1.0, hi


def test_symmetry():
    # Wilson is symmetric: CI(c,n) is the mirror of CI(n-c,n) about 0.5.
    for c, n in [(3, 17), (7, 41), (12, 90)]:
        lo1, hi1 = wilson_ci(c, n)
        lo2, hi2 = wilson_ci(n - c, n)
        assert abs(lo1 - (1 - hi2)) < 1e-9
        assert abs(hi1 - (1 - lo2)) < 1e-9


def test_bounds_inside_unit_interval():
    for c in range(0, 31):
        lo, hi = wilson_ci(c, 30)
        assert 0.0 <= lo <= hi <= 1.0, (c, lo, hi)


def test_contains_point_estimate():
    for c, n in [(0, 30), (1, 30), (15, 30), (29, 30), (36, 150)]:
        p = point_estimate(c, n)
        lo, hi = wilson_ci(c, n)
        assert lo <= p <= hi, (c, n, p, lo, hi)


def test_width_shrinks_with_n():
    # Same proportion, more data -> tighter interval.
    lo1, hi1 = wilson_ci(5, 10)
    lo2, hi2 = wilson_ci(50, 100)
    assert (hi2 - lo2) < (hi1 - lo1)


def test_n_zero_is_full_interval():
    assert wilson_ci(0, 0) == (0.0, 1.0)


def test_bad_inputs_raise():
    for bad in [(-1, 10), (11, 10), (5, -1)]:
        try:
            wilson_ci(*bad)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {bad}")


def test_iter_cells_parses_schema():
    doc = {
        "label": "demo",
        "by_condition": {
            "zero_shot": {
                "overall": {"n": 150, "passes": 36, "pass@1": 0.24,
                            "ci95": [0.1787, 0.3143]},
                "by_family": {"simple": {"n": 50, "passes": 31, "pass@1": 0.62,
                                         "ci95": [0.4815, 0.7414]}},
            }
        },
    }
    rows = list(iter_cells(doc))
    assert len(rows) == 2
    overall = [r for r in rows if r["scope"] == "overall"][0]
    assert overall["n"] == 150 and overall["passes"] == 36
    # our recomputed Wilson must agree with the upstream stored ci95 (<= 0.01).
    assert abs(overall["wilson_lo"] - 0.1787) < 0.01
    assert abs(overall["wilson_hi"] - 0.3143) < 0.01


def _run_fallback():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"  PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")


if __name__ == "__main__":
    _run_fallback()
