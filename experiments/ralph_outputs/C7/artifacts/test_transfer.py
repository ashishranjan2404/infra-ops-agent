"""C7 tests — offline, no LLM. Validate splits, interpreter determinism, result schema."""
from __future__ import annotations

import json
import os

import pytest

from rex.harness import scenarios_by_family
from rex.harness_synth import confusion, confusion_pred, handwritten_pred, labeled_examples

RESULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transfer_result.json")


def _labels(names):
    out = []
    for n in names:
        try:
            out.extend(labeled_examples(n))
        except Exception:  # noqa: BLE001
            pass
    return out


def test_splits_disjoint_and_families():
    fam = scenarios_by_family()
    simple, cascade = set(fam["simple"]), set(fam["cascade"])
    assert simple and cascade
    assert not (simple & cascade)


def test_interpreter_deterministic():
    held = _labels(sorted(scenarios_by_family()["cascade"]))
    rules = [{"match_tools": [], "conditions": [
        {"feature": "treats_forbidden_category", "op": "==", "value": True}], "block": True, "reason": "t"}]
    a = confusion(rules, held)
    b = confusion(rules, held)
    assert (a["tp"], a["tn"], a["false_allow"], a["false_block"]) == \
           (b["tp"], b["tn"], b["false_allow"], b["false_block"])


def test_handwritten_beats_allow_all_on_cascade():
    """Oracle invariant: hand-written is_safe must beat the allow-everything floor on cascade."""
    held = _labels(sorted(scenarios_by_family()["cascade"]))
    seed = confusion([], held)               # allow-all floor
    hand = confusion_pred(handwritten_pred, held)
    assert hand["accuracy"] >= seed["accuracy"]
    assert hand["false_allow"] <= seed["false_allow"]


@pytest.mark.skipif(not os.path.exists(RESULT), reason="run transfer_simple_to_cascade.py first")
def test_result_schema():
    r = json.load(open(RESULT))
    for k in ("table", "transfer_gap", "synthesized_rules", "synthesis_ran",
              "leakage_ok", "block_rate_train", "block_rate_heldout"):
        assert k in r, f"missing {k}"
    assert r["leakage_ok"] is True
    for h, t in r["table"].items():
        for fam in ("train", "heldout"):
            assert 0.0 <= t[fam]["accuracy"] <= 1.0
            assert 0.0 <= t[fam]["false_allow_rate"] <= 1.0
