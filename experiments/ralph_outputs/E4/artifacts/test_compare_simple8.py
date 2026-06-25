#!/usr/bin/env python3
"""Offline tests for compare_simple8 — no network. Validates the pure pieces:
the pinned 8 are real `simple` incidents, summarize() math, and the regression
verdict logic. Run: python3 -m pytest test_compare_simple8.py -q"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import compare_simple8 as C  # noqa: E402


def test_eight_pinned_incidents():
    assert len(C.SIMPLE_8) == 8
    assert len(set(C.SIMPLE_8)) == 8  # no dupes


def test_pinned_are_simple_family():
    # raises SystemExit if any pinned incident is not in the simple family
    C.validate_incidents(C.SIMPLE_8)


def test_summarize_all_pass():
    s = C.summarize([1.0, 1.0, 1.0])
    assert s["passes"] == 3 and s["pass@1"] == 1.0 and s["n"] == 3


def test_summarize_mixed():
    s = C.summarize([1.0, 0.0, 1.0, 0.0])  # 2/4 above 0.8 threshold
    assert s["passes"] == 2 and s["pass@1"] == 0.5
    assert s["reward_std"] > 0  # within-group spread present


def test_summarize_empty():
    s = C.summarize([])
    assert s["n"] == 0 and s["pass@1"] == 0.0


def test_binary_pass_threshold():
    # below threshold does not count as a pass
    assert C.summarize([0.79, 0.79])["passes"] == 0
    assert C.summarize([0.8, 0.81])["passes"] == 2


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call(["python3", "-m", "pytest", __file__, "-q"]))
