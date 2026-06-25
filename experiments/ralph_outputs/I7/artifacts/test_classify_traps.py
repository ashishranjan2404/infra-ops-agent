#!/usr/bin/env python3
"""Self-contained tests for classify_traps.py (no network, no repo mutation)."""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ct", os.path.join(_HERE, "classify_traps.py"))
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def test_tool_mapping():
    assert ct.classify_tool("scale_deployment") == "scale-trap"
    assert ct.classify_tool("restart_service") == "restart-trap"
    assert ct.classify_tool("restart_pod") == "restart-trap"
    assert ct.classify_tool("rollback_deployment") == "rollback-trap"
    assert ct.classify_tool("failover") == "failover-trap"


def test_unknown_tool_is_other():
    assert ct.classify_tool("teleport") == "other-trap"
    assert ct.classify_tool(None) == "other-trap"


def test_build_on_real_repo():
    res = ct.build("/Users/mei/rl")
    # there are traps in the corpus and they sum to the per-category distribution
    assert res["n_scenarios_with_trap"] > 0
    assert sum(res["distribution"].values()) == res["n_scenarios_with_trap"]
    # every category key is present (even empty ones) -> honest about gaps
    for c in ct.CATEGORIES:
        assert c in res["distribution"]
    # known ground truth: corpus is scale-trap dominant
    assert res["dominant_category"] == "scale-trap"
    assert res["distribution"]["scale-trap"] >= res["distribution"]["restart-trap"]


def test_skew_is_reported():
    res = ct.build("/Users/mei/rl")
    assert 0.0 <= res["skew_fraction"] <= 1.0
    # corpus is heavily skewed; assert it is honestly flagged as such
    assert res["skew_fraction"] > 0.8


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    sys.exit(1 if failed else 0)
