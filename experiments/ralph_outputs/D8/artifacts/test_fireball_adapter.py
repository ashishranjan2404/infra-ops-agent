"""Unit tests for the Fireball -> SRE training-format adapter (Task D8).

Exercises the adapter against the tiny SYNTHETIC fixture only. No real Fireball
data is involved (blocked on Wenji). Run:

    python3 -m pytest experiments/ralph_outputs/D8/artifacts/test_fireball_adapter.py -q
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fireball_adapter as fa  # noqa: E402

FIXTURE = os.path.join(HERE, "fireball_fixture.jsonl")


def _load_fixture():
    return list(fa._read_jsonl(FIXTURE))


def test_fixture_loads():
    recs = _load_fixture()
    assert len(recs) == 7  # 7 lines in the fixture


def test_record_with_no_command_is_skipped():
    # syn-combat-004 first turn has commands: [] -> not a transition
    rec = {"combat_id": "x", "commands": [], "before_state": [{"name": "A"}],
           "after_state": [{"name": "A"}]}
    assert fa.adapt_record(rec) is None


def test_record_with_no_state_is_skipped():
    rec = {"combat_id": "x", "commands": ["!attack"]}
    assert fa.adapt_record(rec) is None


def test_non_dict_is_skipped():
    assert fa.adapt_record(["not", "a", "dict"]) is None
    assert fa.adapt_record(None) is None


def test_basic_shape():
    recs = _load_fixture()
    ex = fa.adapt_record(recs[0])
    assert ex is not None
    roles = [m["role"] for m in ex.messages]
    assert roles == ["system", "user", "assistant"]
    assert "STATE_BEFORE:" in ex.messages[1]["content"]
    assert "ACTION:" in ex.messages[1]["content"]
    assert "STATE_AFTER:" in ex.messages[2]["content"]
    assert 0.0 <= ex.reward <= 1.0


def test_state_change_detected():
    recs = _load_fixture()
    ex = fa.adapt_record(recs[0])  # goblin hits Aragorn -> hp + bleeding change
    assert ex.meta["state_changed"] is True
    assert ex.reward == 1.0  # command + both states + change


def test_no_state_change_lower_reward():
    recs = _load_fixture()
    # syn-combat-002 last record: orc misses, before==after
    miss = [r for r in recs if "AC too high" in r.get("automation_results", "")][0]
    ex = fa.adapt_record(miss)
    assert ex is not None
    assert ex.meta["state_changed"] is False
    assert ex.reward == pytest.approx(0.8)  # command+before+after, no change bonus


def test_fireball_multitarget_renders_all_actors():
    recs = _load_fixture()
    fb = [r for r in recs if "fireball" in fa._join(r.get("commands")).lower()][0]
    ex = fa.adapt_record(fb)
    after = ex.messages[2]["content"]
    assert "Orc1" in after and "Orc3" in after
    assert "dead" in after  # effect rendered


def test_stream_filters_unusable():
    recs = _load_fixture()
    out = list(fa.adapt_stream(recs))
    # 7 records, 1 has empty commands -> 6 usable
    assert len(out) == 6
    assert all(0.0 <= e.reward <= 1.0 for e in out)


def test_convert_file_roundtrip(tmp_path):
    out = tmp_path / "out.jsonl"
    stats = fa.convert_file(FIXTURE, str(out))
    assert stats["records_in"] == 7
    assert stats["examples_out"] == 6
    assert stats["skipped"] == 1
    # every output line is valid training-format json
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 6
    for ln in lines:
        obj = json.loads(ln)
        assert "messages" in obj and "reward" in obj and "meta" in obj
        assert obj["meta"]["source"] == "fireball"


def test_malformed_line_skipped(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(
        '{"combat_id":"ok","commands":["!a"],"before_state":[{"name":"A","hp":1}],'
        '"after_state":[{"name":"A","hp":0}]}\n'
        "{ this is not json }\n"
    )
    recs = list(fa._read_jsonl(str(bad)))
    assert len(recs) == 1  # malformed line dropped, good one kept


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
