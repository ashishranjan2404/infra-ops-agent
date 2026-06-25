"""Self-contained tests for the J7 agent bench runner (offline, no network, no cloud)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "agent_bench_runner", Path(__file__).with_name("agent_bench_runner.py"))
abr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(abr)


def test_both_registries_load_15():
    for bench in ("gcp", "linode"):
        scen = abr.load_registry(bench)
        assert len(scen) == 15, f"{bench} should have 15 runnable scenarios"


def test_action_space_is_deduped_and_covers_every_gold():
    scen = abr.load_registry("gcp")
    actions = abr.build_action_space(scen)
    assert len(actions) == len(set(actions))
    for s in scen:
        assert s["fix"].strip() in actions  # every gold fix is selectable


def test_prompt_lists_all_actions_and_symptom():
    scen = abr.load_registry("gcp")
    actions = abr.build_action_space(scen)
    s = scen[0]
    p = abr.build_prompt(s, abr.load_cre_text("gcp", s["cre_id"]), actions)
    assert s["service"] in p
    assert all(f"{i}." in p for i in range(len(actions)))


def test_request_assembles_offline_for_every_scenario():
    # build_request is pure (no network); proves provider wiring without a key.
    scen = abr.load_registry("gcp")
    actions = abr.build_action_space(scen)
    for s in scen:
        p = abr.build_prompt(s, abr.load_cre_text("gcp", s["cre_id"]), actions)
        assert abr.prove_request_assembles("claude-haiku-4-5", p)


def test_dryrun_run_is_deterministic_and_scored():
    r1 = abr.run("gcp", "dry-run", "claude-haiku-4-5")
    r2 = abr.run("gcp", "dry-run", "claude-haiku-4-5")
    assert r1 == r2                                  # deterministic
    assert r1["n"] == 15
    assert r1["cloud_executed"] is False             # never touches cloud
    assert 0.0 <= r1["action_select_accuracy"] <= 1.0
    assert all(row["cloud_applied"] is False for row in r1["rows"])
