#!/usr/bin/env python3
"""Self-contained tests for per_incident_breakdown (no pytest dependency)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from per_incident_breakdown import (  # noqa: E402
    _pass_at_k, binary_pass, build_rows, summarize, incident_family_map,
)


def _src(model, threshold, fam, per_cond):
    return {
        "model": model, "label": "test", "threshold": threshold,
        "seeds": 3, "incidents_by_family": fam,
        "by_condition": {c: {"per_incident_rewards": pir} for c, pir in per_cond.items()},
    }


def test_pass_at_k_bounds():
    assert _pass_at_k(3, 0, 2) == 0.0          # never passes -> 0
    assert _pass_at_k(3, 3, 2) == 1.0          # always passes -> 1
    assert abs(_pass_at_k(3, 1, 1) - 1 / 3) < 1e-9
    # monotonic in c
    assert _pass_at_k(5, 1, 2) < _pass_at_k(5, 3, 2)


def test_binary_pass():
    assert binary_pass(0.8, 0.8) == 1
    assert binary_pass(0.79, 0.8) == 0


def test_family_map():
    d = _src("m", 0.8, {"simple": ["a"], "novel": ["b"]}, {"rex": {"a": [1.0], "b": [0.0]}})
    fm = incident_family_map(d)
    assert fm == {"a": "simple", "b": "novel"}


def test_solvability_flags():
    fam = {"simple": ["solv"], "cascade": ["part"], "novel": ["uns"]}
    src = _src("m", 0.8, fam, {
        "zero_shot": {"solv": [0.0, 0.0, 0.0], "part": [1.0, 0.0, 0.0], "uns": [0.3, 0.0, 0.5]},
        "rex":       {"solv": [1.0, 1.0, 1.0], "part": [0.0, 1.0, 0.0], "uns": [0.0, 0.2, 0.0]},
    })
    rows = build_rows([src], None)
    flags = {r["incident"]: r["solvability"] for r in rows}
    assert flags["solv"] == "solvable"      # rex passes all 3 -> best p@1==1
    assert flags["part"] == "partially"     # some pass, none reliable
    assert flags["uns"] == "unsolvable"     # never crosses 0.8


def test_summary_counts_and_unsolvable_list():
    fam = {"simple": ["solv"], "novel": ["uns"]}
    src = _src("mod", 0.8, fam, {
        "rex": {"solv": [1.0, 1.0], "uns": [0.0, 0.1]},
    })
    rows = build_rows([src], None)
    s = summarize(rows)
    assert s["counts"]["solvable"] == 1
    assert s["counts"]["unsolvable"] == 1
    assert s["unsolvable"] == ["mod:uns"]
    assert s["by_family"]["novel"]["unsolvable"] == 1


def test_multi_source_rows():
    fam = {"simple": ["a"]}
    s1 = _src("m1", 0.8, fam, {"rex": {"a": [1.0, 1.0]}})
    s2 = _src("m2", 0.8, fam, {"rex": {"a": [0.0, 0.0]}})
    rows = build_rows([s1, s2], None)
    assert len(rows) == 2
    by_model = {r["source_model"]: r["solvability"] for r in rows}
    assert by_model == {"m1": "solvable", "m2": "unsolvable"}


def test_k_override():
    fam = {"simple": ["a"]}
    src = _src("m", 0.8, fam, {"rex": {"a": [1.0, 0.0, 0.0, 0.0, 0.0]}})
    rows = build_rows([src], 2)
    pc = rows[0]["by_condition"]["rex"]
    assert pc["k"] == 2
    assert "pass@2" in pc


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
