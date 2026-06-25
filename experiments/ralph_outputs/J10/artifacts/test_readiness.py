#!/usr/bin/env python3
"""J10 — pytest for the readiness gap registry + honesty guards."""
from __future__ import annotations

from pathlib import Path

import check_readiness as cr

HERE = Path(__file__).parent
JSON = HERE / "readiness_gaps.json"
MD = HERE / "lessons_from_production.md"


def _data():
    return cr.load(JSON)


def test_json_parses_and_schema():
    d = _data()
    for key in ("task_id", "claim", "lessons", "gaps", "readiness_checklist"):
        assert key in d, f"missing {key}"
    assert d["task_id"] == "J10"


def test_three_required_gaps():
    d = _data()
    assert {g["id"] for g in d["gaps"]} == {"G1", "G2", "G3"}
    names = {g["id"]: g["name"].lower() for g in d["gaps"]}
    assert "distribution shift" in names["G1"]
    assert "shadow" in names["G2"]
    assert "mttr" in names["G3"]


def test_grounding_paths_exist_and_nonempty():
    d = _data()
    for kind in ("lessons", "gaps"):
        for item in d[kind]:
            assert item["grounding"], f"{item['id']} has no grounding"
            for rel in item["grounding"]:
                p = cr.REPO_ROOT / rel
                assert p.exists(), f"missing grounding {rel}"
                if p.is_file():
                    assert p.stat().st_size > 0, f"empty grounding {rel}"


def test_acceptance_gates_labeled():
    for g in _data()["gaps"]:
        assert g["acceptance_gate"].startswith(cr.GATE_PREFIX), g["id"]


def test_no_fabricated_prod_phrasing_md():
    assert MD.exists()
    assert cr._scan_banned(MD.read_text()) == []


def test_markdown_has_required_sections():
    problems = cr.verify_md(MD, {"G1", "G2", "G3"})
    assert problems == [], problems


def test_verify_clean():
    assert cr.verify(_data()) == []


if __name__ == "__main__":
    import sys
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
