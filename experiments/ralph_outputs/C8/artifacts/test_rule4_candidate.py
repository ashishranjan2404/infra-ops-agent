"""Tests for the C8 4th-rule candidate. Run:
    python3 -m pytest experiments/ralph_outputs/C8/artifacts/test_rule4_candidate.py -q
"""
import os
import sys

HERE = os.path.dirname(__file__)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
for p in (HERE, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import rule4_candidate as r4  # noqa: E402
from rex.harness_synth import HELDOUT, TRAIN, confusion, labeled_examples  # noqa: E402


def _ho():
    return [e for n in HELDOUT for e in labeled_examples(n)]


def _tr():
    return [e for n in TRAIN for e in labeled_examples(n)]


def test_baseline_is_897():
    """The saved v2 3-rule set reproduces the 89.7% held-out baseline."""
    assert confusion(r4.load_v2_rules(), _ho())["accuracy"] == 0.897


def test_rule4_validates():
    """The 4th rule passes the synth's own defensive validator (known feature/op)."""
    from rex.harness_synth import validate_ruleset
    assert validate_ruleset([r4.RULE4]), "rule4 must survive validate_ruleset"


def test_rule4_beats_baseline():
    """4-rule set pushes held-out accuracy strictly past 89.7%."""
    ext = r4.load_v2_rules() + [r4.RULE4]
    assert confusion(ext, _ho())["accuracy"] > 0.897


def test_rule4_introduces_no_new_false_blocks():
    """The new rule must not add any false-block vs the baseline. (The baseline
    already has 2 rollback_deployment false-blocks on TRAIN — those are pre-existing
    and NOT caused by rule4; rule4 only touches drain/cordon actions.)"""
    base = r4.load_v2_rules()
    ext = base + [r4.RULE4]
    assert confusion(ext, _tr())["false_block"] == confusion(base, _tr())["false_block"]
    assert confusion(ext, _ho())["false_block"] == confusion(base, _ho())["false_block"]


def test_no_train_signal_for_rule4():
    """Honest finding: zero TRAIN examples activate last_ready_node_op, so the
    LLM search has no gradient to discover this rule — it is human-injected."""
    tr = _tr()
    assert sum(1 for e in tr if e["features"].get("last_ready_node_op")) == 0


def test_two_misses_remain_unlearnable():
    """The 4th rule cannot fix the cpu_saturation trap_actions (is_safe misses
    them too) — held-out caps at 0.949, matching hand-written is_safe."""
    ext = r4.load_v2_rules() + [r4.RULE4]
    c = confusion(ext, _ho())
    assert c["false_allow"] == 2
    assert c["accuracy"] == 0.949
