#!/usr/bin/env python3
"""Self-tests for learning_curve.py — pure-Python, no matplotlib needed to pass parsing tests."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import learning_curve as lc  # noqa: E402


def _write(lines):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w") as fh:
        for obj in lines:
            fh.write((obj if isinstance(obj, str) else json.dumps(obj)) + "\n")
    return path


def test_pass1_threshold():
    # 4 rollouts, two >= 0.8 -> pass@1 = 0.5
    p = _write([{"step": 0, "rewards": [0.9, 0.8, 0.79, 0.1], "mean_reward": 0.6475}])
    rows = lc.parse_log(p, threshold=0.8)
    assert len(rows) == 1
    assert rows[0]["passes"] == 2 and rows[0]["n"] == 4
    assert abs(rows[0]["pass1"] - 0.5) < 1e-9
    os.unlink(p)
    print("ok test_pass1_threshold")


def test_threshold_boundary():
    # exactly at threshold counts as a pass (>=)
    p = _write([{"step": 0, "rewards": [0.8, 0.8]}])
    rows = lc.parse_log(p, threshold=0.8)
    assert rows[0]["pass1"] == 1.0
    os.unlink(p)
    print("ok test_threshold_boundary")


def test_robust_to_garbage():
    p = _write([
        "",                                   # blank
        "{not json",                          # malformed
        {"step": 5, "mean_reward": 0.5},      # missing rewards -> skip
        {"step": 1, "rewards": []},           # empty rewards -> skip
        {"step": 2, "rewards": [0.9]},        # ok
        {"step": 0, "rewards": [0.1, 0.95]},  # ok, out of order
    ])
    rows = lc.parse_log(p)
    assert [r["step"] for r in rows] == [0, 2]   # sorted, only the two valid
    assert rows[0]["pass1"] == 0.5 and rows[1]["pass1"] == 1.0
    os.unlink(p)
    print("ok test_robust_to_garbage")


def test_wilson_ci_bounds():
    lo, hi = lc.wilson_ci(0.5, 24)
    assert 0.0 <= lo < 0.5 < hi <= 1.0
    assert lc.wilson_ci(0.5, 0) == (0.0, 0.0)
    print("ok test_wilson_ci_bounds")


def test_real_logs_parse():
    runs = lc._DEFAULT_RUNS
    found = False
    if os.path.isdir(runs):
        import glob
        for p in glob.glob(os.path.join(runs, "*.jsonl")):
            rows = lc.parse_log(p)
            if rows:
                found = True
                assert all(0.0 <= r["pass1"] <= 1.0 for r in rows)
                assert [r["step"] for r in rows] == sorted(r["step"] for r in rows)
    print("ok test_real_logs_parse" + ("" if found else " (no real logs present — skipped data check)"))


if __name__ == "__main__":
    test_pass1_threshold()
    test_threshold_boundary()
    test_robust_to_garbage()
    test_wilson_ci_bounds()
    test_real_logs_parse()
    print("ALL TESTS PASS")
