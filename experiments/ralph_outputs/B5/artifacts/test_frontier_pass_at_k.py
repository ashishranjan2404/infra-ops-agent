#!/usr/bin/env python3
"""Unit tests for B5 frontier_pass_at_k.summarize (no network)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from frontier_pass_at_k import summarize  # noqa: E402


def test_basic_passk_monotone_and_bounded():
    s = summarize([1.0, 1.0, 0.0], threshold=0.8)
    assert s["n"] == 3 and s["passes"] == 2
    assert abs(s["pass@1"] - 2 / 3) < 1e-3   # summarize rounds to 4dp
    assert s["pass@2"] >= s["pass@1"] >= 0.0
    assert s["pass@5"] >= s["pass@2"]
    lo, hi = s["ci95"]
    assert 0.0 <= lo <= s["pass@1"] <= hi <= 1.0


def test_partial_credit_does_not_pass_at_1():
    # Mean=0.4 would look "okay" but NONE resolve the incident -> pass@1 (the HEADLINE)
    # must be 0. This is the whole point: pass@1 unmasks partial-credit farming.
    s = summarize([0.4, 0.4, 0.4], threshold=0.8)
    assert s["passes"] == 0
    assert s["pass@1"] == 0.0
    # pass@2 also 0 because c=0 and n-c=3 >= 2 (estimator is well-posed here).
    assert s["pass@2"] == 0.0
    assert abs(s["mean_reward"] - 0.4) < 1e-9


def test_passk_extrapolation_edge_when_n_lt_k():
    # Documented contract of the single-source estimator (compute_pass_at_k.pass_at_k):
    # when n-c < k it returns 1.0 (you cannot draw k distinct samples). With n=3,c=0,k=5
    # -> n-c=3 < 5 -> pass@5 = 1.0. This is exactly the AAAI-reviewer caveat: pass@5 from
    # n=3 is an EXTRAPOLATION, not a measurement. The script always prints n so this is
    # transparent; the headline metric (pass@1) is unaffected.
    s = summarize([0.4, 0.4, 0.4], threshold=0.8)
    assert s["pass@5"] == 1.0 and s["pass@1"] == 0.0 and s["n"] == 3


def test_all_pass():
    s = summarize([1.0, 0.9, 0.85], threshold=0.8)
    assert s["passes"] == 3 and s["pass@1"] == 1.0
    assert s["pass@5"] == 1.0


def test_empty_no_crash():
    s = summarize([], threshold=0.8)
    assert s["n"] == 0 and s["pass@1"] == 0.0 and s["reward_std"] == 0.0


def test_std_is_population_spread():
    s = summarize([0.0, 1.0], threshold=0.8)
    assert abs(s["reward_std"] - 0.5) < 1e-9  # pstdev([0,1]) = 0.5


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for f in fns:
        try:
            f(); print(f"PASS {f.__name__}")
        except Exception:
            fails += 1; print(f"FAIL {f.__name__}"); traceback.print_exc()
    print(f"\n{len(fns)-fails}/{len(fns)} passed")
    raise SystemExit(1 if fails else 0)
