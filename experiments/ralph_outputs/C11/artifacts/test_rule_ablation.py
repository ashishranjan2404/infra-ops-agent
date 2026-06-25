"""Self-contained tests for C11 rule_ablation. Hermetic (no LLM, no network)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import rule_ablation as ra  # noqa: E402


def test_full_harness_beats_every_ablation():
    """No single rule's removal can IMPROVE accuracy (each rule is net-helpful or neutral)."""
    ex = []
    from rex.harness import _SCENARIOS
    from rex.harness_synth import labeled_examples
    for n in sorted(_SCENARIOS):
        ex.extend(labeled_examples(n))
    full = ra.confusion(ex, None)["accuracy"]
    for rule in ra.RULES:
        abl = ra.confusion(ex, rule)["accuracy"]
        assert abl <= full + 1e-9, f"{rule}: ablated {abl} > full {full}"


def test_ablating_a_rule_never_reduces_blocks_below_full_minus():
    """Disabling a rule can only turn blocks into allows -> false_allow non-decreasing."""
    from rex.harness import _SCENARIOS
    from rex.harness_synth import labeled_examples
    ex = [e for n in sorted(_SCENARIOS) for e in labeled_examples(n)]
    full = ra.confusion(ex, None)
    for rule in ra.RULES:
        abl = ra.confusion(ex, rule)
        assert abl["false_allow"] >= full["false_allow"]
        assert abl["false_block"] <= full["false_block"]


def test_predicate_signatures_are_mutually_exclusive_on_real_reasons():
    """Each is_safe block reason must match AT MOST ONE rule predicate (clean attribution)."""
    from rex.harness import is_safe
    samples = [
        # (action, state) tuples that trigger each distinct guard
        ({"tool": "scale_deployment", "args": {"target": "x"}},
         {"forbidden_categories": ["saturation"], "incident": "i", "gold_category": "c"}),
        ({"tool": "restart_pod", "args": {"target": "x"}},
         {"mem_leak_active": True}),
        ({"tool": "drain_node", "args": {"target": "x"}},
         {"draining_last_ready_node": True}),
        ({"tool": "scale_deployment", "args": {"target": "x"}},
         {"at_replica_limit": True}),
        ({"tool": "rollback_deployment", "args": {"target": "x"}},
         {"recent_deploy": False}),
    ]
    for action, state in samples:
        allowed, reason = is_safe(action, state)
        assert not allowed, (action, state)
        hits = [r for r, pred in ra.RULES.items() if pred(reason)]
        assert len(hits) == 1, f"reason {reason!r} matched {hits}"


def test_unknown_disabled_rule_raises():
    try:
        ra.predict_block({"incident": "oom_kill", "tool": "scale_deployment",
                          "target": "image-resizer", "should_block": True}, disabled="NOPE")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown rule")
