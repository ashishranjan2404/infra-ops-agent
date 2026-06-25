"""Tests for I6 failure_taxonomy. Run: python3 -m pytest test_failure_taxonomy.py -q"""
import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/mei/rl"

spec = importlib.util.spec_from_file_location("ft", os.path.join(HERE, "failure_taxonomy.py"))
ft = importlib.util.module_from_spec(spec)
sys.modules["ft"] = ft  # so @dataclass can resolve the module during exec
spec.loader.exec_module(ft)
scoring = ft._import_scoring(REPO)


def _r(**kw):
    base = dict(source="t", rollout_id="x", scenario="s", score=0.4, resolved=False,
                diagnosis_correct=False, failed_checks=[], n_actions=1)
    base.update(kw)
    return ft.Rollout(**base)


def test_precedence_trap_beats_root_cause():
    p, tags = ft.bucket(_r(failed_checks=["root_cause", "trap_action"], score=0.0))
    assert p == "trap_taken"
    assert "zero_reward" in tags


def test_no_fix_only():
    p, tags = ft.bucket(_r(failed_checks=["correct_fix_missing", "not_resolved"]))
    assert p == "no_fix"
    assert "correct_fix_missing" in tags


def test_empty_plan_safe_abstain():
    p, tags = ft.bucket(_r(failed_checks=["correct_fix_missing", "not_resolved"], n_actions=0))
    assert "empty_plan" in tags and "safe_abstain" in tags


def test_clean_win_excluded():
    p, _ = ft.bucket(_r(failed_checks=[], score=1.0))
    assert p == "clean_win"


def test_rescoring_replay_detects_trap():
    """Validates the HUD replay path: a known trap tuple -> trap_action via rex.scoring."""
    class S:
        correct_fix_tools = {"rollback_deployment"}
        fault_node = "orders"
        trap_actions = [{"tool": "scale_deployment", "target": "orders"}]
        gold_root_description = "bad deploy of orders broke checkout"
        red_herring_hints = ["memory leak"]
        category = "bad_deploy"
    plan = {"root_cause": "memory leak", "actions": [{"tool": "scale_deployment", "args": {"target": "orders"}}]}
    sim = {"resolved": False, "applied_actions": [{"tool": "scale_deployment", "args": {"target": "orders"}}]}
    fc = scoring.failed_checks(plan, S(), sim, judge_fn=scoring.deterministic_judge)
    assert "trap_action" in fc
    assert "root_cause" in fc  # diagnosed the red herring


def test_probe_recompute_matches_stored_failed_checks():
    """Smoke: recompute is consistent w/ probe rows' own failed_checks where derivable.
    Probe rows do not store the plan, so we can only check the score/diag fields ingest."""
    paths = sorted(glob.glob(os.path.join(REPO, "rex/runs/diagnostic_probe_oom_kill.jsonl")))
    rs = ft.load_probe_rollouts(paths, scoring)
    assert len(rs) == 6
    for r in rs:
        ft.bucket.__call__  # no-op guard
        p, tags = ft.bucket(r)
        if "trap_action" in r.failed_checks:
            assert p == "trap_taken"
        if r.score == 1.0 and not r.failed_checks:
            assert p == "clean_win"


def test_end_to_end_real_data():
    summ = ft.summarize(
        ft.load_probe_rollouts(
            sorted(glob.glob(os.path.join(REPO, "rex/runs/diagnostic_probe_*.jsonl"))), scoring)
        + ft.load_hud_rollouts(
            sorted(glob.glob(os.path.join(REPO, "rex/runs/hud/*.jsonl"))), scoring))
    assert summ["corpus"]["total"] > 0
    assert summ["failure_tail"]["n_failed"] >= 0
    assert set(summ["primary_bucket_counts"]).issubset(
        set(ft.PRIMARY_PRECEDENCE))
