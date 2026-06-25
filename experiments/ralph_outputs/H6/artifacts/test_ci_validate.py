#!/usr/bin/env python3
"""Self-tests for the H6 CI scenario validator.

Run: python3 -m pytest experiments/ralph_outputs/H6/artifacts/test_ci_validate.py -q
(no external pytest plugins required; also runnable as a plain script).
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
for p in (HERE, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import ci_validate_scenarios as civ  # noqa: E402


def _fixture(name: str) -> str:
    return os.path.join(HERE, name)


def test_all_real_scenarios_pass():
    """Exit 0 over the real CIDG corpus (regression gate for the whole repo)."""
    rc = civ.main(["--quiet", "--glob", "scenarios/cidg/*.yaml",
                   "--glob", "scenarios/cidg/generated/*.yaml"])
    assert rc == 0, "real scenarios must all pass the sim engine"


def test_malformed_yaml_fails_at_load():
    rec = civ.check_one(_fixture("bad_yaml.yaml"))
    assert rec["ok"] is False
    assert rec["failed_stage"] == civ.STAGE_LOAD


def test_bad_schema_fails_at_schema():
    rec = civ.check_one(_fixture("bad_schema.yaml"))
    assert rec["ok"] is False
    assert rec["failed_stage"] == civ.STAGE_SCHEMA
    assert rec["schema_errors"], "schema errors must be reported"


def test_unknown_slo_victim_caught_before_engine():
    """An SLO naming a nonexistent node is rejected by schema, never reaching a KeyError."""
    rec = civ.check_one(_fixture("bad_engine.yaml"))
    assert rec["ok"] is False
    assert rec["failed_stage"] == civ.STAGE_SCHEMA


def test_exit_code_nonzero_on_failure():
    rc = civ.main(["--quiet", "--glob",
                   "experiments/ralph_outputs/H6/artifacts/bad_*.yaml"])
    assert rc == 1


def test_exit_code_two_on_no_match():
    rc = civ.main(["--quiet", "--glob", "experiments/ralph_outputs/H6/artifacts/__none__*.yaml"])
    assert rc == 2


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} self-tests passed")
    raise SystemExit(1 if failed else 0)
