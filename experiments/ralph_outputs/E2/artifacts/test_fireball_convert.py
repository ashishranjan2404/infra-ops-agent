#!/usr/bin/env python3
"""Tests for the FIREBALL -> trajectory converter, using the synthetic fixture
(SYNTH_* rows that match the REAL schema but contain fabricated, clearly-labeled
content — we never invent real dataset rows).

Run:  python -m pytest test_fireball_convert.py -q
  or:  python test_fireball_convert.py   (self-running fallback)
"""
from __future__ import annotations

import json
from pathlib import Path

import fireball_convert as fc
from fireball_schema import validate_row

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fireball_fixture.jsonl"


def _rows():
    return [json.loads(l) for l in FIXTURE.read_text().splitlines() if l.strip()]


def test_fixture_rows_validate():
    for r in _rows():
        assert validate_row(r) == [], r


def test_convert_basic_fields():
    rec = fc.convert_row(_rows()[0])
    assert rec["schema"] == fc.SCHEMA_VERSION
    assert rec["actions"] == ["!attack longsword -t goblin"]
    assert rec["tools_used"] == ["attack"]
    assert rec["n_tool_calls"] == 1
    assert "Goblin is dead" in rec["result"]
    assert "crumples" in rec["target"]
    assert "Aria [<30/30 HP; Healthy>]" in rec["observation"]
    assert "Goblin [<0/7 HP; Dead>]" in rec["next_observation"]


def test_multi_command_tool_verbs():
    rec = fc.convert_row(_rows()[1])
    assert rec["tools_used"] == ["cast"]        # deduped verb
    assert rec["n_tool_calls"] == 2             # two commands
    assert rec["actions"][1].startswith("!cast fireball")


def test_trace_id_deterministic_and_unique():
    rows = _rows()
    ids = [fc.make_trace_id(r) for r in rows]
    assert len(set(ids)) == len(ids)            # unique
    assert fc.make_trace_id(rows[0]) == fc.make_trace_id(rows[0])  # stable


def test_skip_empty_target():
    # row[2] has empty after_utterances -> skipped by default
    recs = list(fc.convert_file([FIXTURE]))
    ids = {r["speaker_id"] for r in recs}
    assert "SYNTH_0003" not in ids
    assert {"SYNTH_0001", "SYNTH_0002"} <= ids
    # ...but kept when skip_empty=False
    recs_all = list(fc.convert_file([FIXTURE], skip_empty=False))
    assert len(recs_all) == 3


def test_invalid_row_raises():
    bad = {"speaker_id": "x"}  # missing required keys
    try:
        fc.convert_row(bad)
    except ValueError as e:
        assert "missing key" in str(e)
    else:
        raise AssertionError("expected ValueError on invalid row")


def test_output_json_serializable():
    for r in _rows():
        rec = fc.convert_row(r)
        json.dumps(rec)  # must not raise


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print(f"\nALL {len(fns)} TESTS PASSED")
