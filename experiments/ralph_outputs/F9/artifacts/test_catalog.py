#!/usr/bin/env python3
"""Self-contained tests for the F9 incident catalog generator.

Run: python3 test_catalog.py   (no pytest dependency required)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gen_incident_catalog as gic  # noqa: E402


def test_extract_minimal():
    spec = {
        "meta": {"id": "x", "title": "T", "source": "S", "failure_class": "fd_exhaust"},
        "root_cause": {"location": "node-a", "kind": "fd_exhaust", "severity": 0.7, "hidden": True},
        "canonical_fix": {"steps": [{"tool": "raise_fd_limit", "args": {"target": "node-a"}}]},
        "topology": {"nodes": [{"name": "node-a"}]},
        "assertions": {"cascades": True},
    }
    r = gic.extract(spec, Path("x.yaml"))
    assert r["id"] == "x"
    assert r["root_cause_kind"] == "fd_exhaust"
    assert r["root_cause_hidden"] is True
    assert "raise_fd_limit" in r["fix"]
    assert "node-a" in r["fix"]
    assert r["cascades"] is True
    assert r["n_nodes"] == 1
    print("ok test_extract_minimal")


def test_extract_missing_keys():
    # Must not crash on a sparse spec.
    r = gic.extract({}, Path("empty.yaml"))
    assert r["id"] == "empty"
    assert r["fix"] == "(none)"
    assert r["cascades"] is False
    print("ok test_extract_missing_keys")


def test_real_yamls_all_parse():
    rows = gic.collect(gic.DEFAULT_SRC)
    assert len(rows) >= 33, f"expected >=33 specs, got {len(rows)}"
    # Every row must have an id and a non-empty root cause string.
    for r in rows:
        assert r["id"], r
        assert "@" in r["root_cause"], r
    print(f"ok test_real_yamls_all_parse ({len(rows)} specs)")


def test_generated_outputs_consistent():
    md = gic.DEFAULT_OUT_MD
    js = gic.DEFAULT_OUT_JSON
    assert md.exists() and js.exists(), "run gen_incident_catalog.py first"
    rows = json.loads(js.read_text())
    text = md.read_text()
    assert f"Total incidents: **{len(rows)}**" in text
    # Every id should appear in the markdown.
    for r in rows:
        assert r["id"] in text, f"missing {r['id']} in markdown"
    print(f"ok test_generated_outputs_consistent ({len(rows)} ids present)")


if __name__ == "__main__":
    test_extract_minimal()
    test_extract_missing_keys()
    test_real_yamls_all_parse()
    test_generated_outputs_consistent()
    print("ALL PASS")
