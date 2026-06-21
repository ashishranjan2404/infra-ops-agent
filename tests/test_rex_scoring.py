"""Phase-1 scoring: a GRADED score in [0,1] (not binary) + SPECIFIC feedback the
model can climb on. Partial credit for the right root cause, credit for a correct
fix tool, BIG penalty for a trap action, credit when the sim resolves.
"""
from rex.harness import load_scenario
from rex.scoring import score_plan, format_feedback

SC = load_scenario("oom_kill")

PERFECT = {
    "root_cause": "per-process memory leak causing OOMKilled on image-resizer; RSS exceeds the limit",
    "actions": [
        {"tool": "increase_memory_limit", "args": {"target": "image-resizer", "mem_limit_mb": 1024}},
        {"tool": "restart_pod", "args": {"target": "image-resizer"}},
    ],
}
TRAP = {
    "root_cause": "too few replicas under load",
    "actions": [{"tool": "scale_deployment", "args": {"target": "image-resizer", "replicas": 6}}],
}
DIAG_ONLY = {"root_cause": "a memory leak / OOM on image-resizer", "actions": []}


def _sr(plan, resolved):
    return {"resolved": resolved, "root_cleared": resolved,
            "applied_actions": plan["actions"], "blocked_actions": []}


def test_perfect_resolved_plan_scores_high():
    s, _ = score_plan(PERFECT, SC, _sr(PERFECT, True))
    assert s >= 0.9


def test_trap_plan_heavily_penalized():
    s, _ = score_plan(TRAP, SC, _sr(TRAP, False))
    assert s < 0.3


def test_resolution_raises_score():
    assert score_plan(PERFECT, SC, _sr(PERFECT, True))[0] > score_plan(PERFECT, SC, _sr(PERFECT, False))[0]


def test_partial_credit_for_diagnosis_without_fix():
    s, _ = score_plan(DIAG_ONLY, SC, _sr(DIAG_ONLY, False))
    assert 0.0 < s < 0.4


def test_score_always_in_unit_interval():
    for plan, resolved in [(PERFECT, True), (TRAP, False), (DIAG_ONLY, False)]:
        s, _ = score_plan(plan, SC, _sr(plan, resolved))
        assert 0.0 <= s <= 1.0


def test_feedback_names_the_trap_and_says_why_it_is_wrong():
    fb = format_feedback(TRAP, SC, _sr(TRAP, False)).lower()
    assert "scale_deployment" in fb
    assert any(w in fb for w in ("worsen", "won't", "will not", "not resolve", "trap", "wrong"))


def test_feedback_reveals_the_correct_root_cause_when_wrong():
    fb = format_feedback(TRAP, SC, _sr(TRAP, False)).lower()
    assert "memory" in fb or "leak" in fb


def test_feedback_states_resolution_status():
    fb = format_feedback(TRAP, SC, _sr(TRAP, False)).lower()
    assert "not resolved" in fb or "did not resolve" in fb or "still breach" in fb


def test_feedback_confirms_a_correct_fix_when_present():
    fb = format_feedback(PERFECT, SC, _sr(PERFECT, True)).lower()
    assert "increase_memory_limit" in fb or "valid" in fb or "correct fix" in fb
