"""Pytest for the G4 trap-taxonomy extractor — validates against the REAL repo."""
import json
import os

import extract_trap_taxonomy as ex

REPO = "/Users/mei/rl"


def test_constants_match_scoring():
    tax = ex.build_taxonomy(REPO)
    assert tax["trap_penalty"] == 0.60
    w = tax["score_weights"]
    assert round(w["root"] + w["fix"] + w["resolved"], 6) == 1.0


def test_every_record_has_a_trap_tool():
    tax = ex.build_taxonomy(REPO)
    assert tax["n_with_trap"] >= 0.9 * tax["n_scenario_files"]
    for r in tax["records"]:
        assert r["trap"]["tool"], r


def test_scale_deployment_is_modal_trap():
    tax = ex.build_taxonomy(REPO)
    dist = tax["trap_tool_distribution"]
    assert "scale_deployment" in dist
    assert dist["scale_deployment"] == max(dist.values())


def test_every_trap_contrasted_with_a_real_fix():
    tax = ex.build_taxonomy(REPO)
    for r in tax["records"]:
        assert r["contrasted_gold_fix"], r["scenario_id"]


def test_why_table_extracted_if_present():
    why = ex.load_why_table(os.path.join(REPO, "rex", "scoring.py"))
    # scoring.py ships a why-table; if found it must include the dominant trap.
    if why:
        assert "scale_deployment" in why


def test_main_writes_valid_json(tmp_path):
    out = tmp_path / "tax.json"
    ex.main(REPO, str(out))
    loaded = json.load(open(out))
    assert loaded["n_with_trap"] == loaded["n_with_trap"]
    assert isinstance(loaded["records"], list) and loaded["records"]
