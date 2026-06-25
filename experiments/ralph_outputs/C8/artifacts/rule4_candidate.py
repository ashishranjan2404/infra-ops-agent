"""C8 — 4th rule candidate: can we push the synthesized harness past 89.7% held-out?

Grounded in rex/harness_synth.py and rex/harness.py. We do NOT edit those files.
This module:
  1. loads the v2 synthesized 3-rule set (rex/runs/harness_synth_v2.json) — the
     89.7%-held-out baseline,
  2. defines a 4th candidate rule over the EXISTING `last_ready_node_op` feature
     (the one feature in FEATURES that no synthesized rule used),
  3. evaluates 3-rule vs 4-rule on TRAIN / HELD-OUT / ALL using the real
     rex.harness_synth scoring (confusion, train_score),
  4. emits a JSON report.

Reuses the trusted interpreter is_safe_synth (rules are DATA, never exec'd).

    python3 experiments/ralph_outputs/C8/artifacts/rule4_candidate.py
"""
from __future__ import annotations

import json
import os
import sys

# repo root = .../rl  (this file is at rl/experiments/ralph_outputs/C8/artifacts/)
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from rex.harness_synth import (  # noqa: E402
    HELDOUT, TRAIN, confusion, labeled_examples, train_score, validate_ruleset,
)

V2_PATH = os.path.join(REPO, "rex", "runs", "harness_synth_v2.json")
OUT = os.path.join(os.path.dirname(__file__), "rule4_result.json")

# --- the 4th candidate rule -------------------------------------------------------
# Hazard: draining/cordoning the LAST Ready node takes the service fully down. The
# hand-written is_safe blocks this (Layer-2). The v2 synthesized set does NOT — it
# has no rule over `last_ready_node_op`, because that feature is True for ZERO train
# examples (no training signal -> the haiku mutation operator never proposes it).
# This is the gap that caps held-out at 89.7%.
RULE4 = {
    "match_tools": ["drain_node", "cordon_node"],
    "conditions": [{"feature": "last_ready_node_op", "op": "==", "value": True}],
    "block": True,
    "reason": "draining/cordoning the last Ready node takes the service fully down — escalate instead",
}


def load_v2_rules() -> list:
    return json.load(open(V2_PATH))["rules"]


def evaluate(rules: list, examples: list) -> dict:
    c = confusion(rules, examples)
    return {k: c[k] for k in ("accuracy", "false_allow", "false_block", "n")}


def main() -> int:
    base = load_v2_rules()
    # validate the 4th rule through the SAME defensive validator the synth uses
    rule4 = validate_ruleset([RULE4])
    assert rule4, "4th rule failed validate_ruleset (unknown feature/op?)"
    ext = base + rule4

    tr = [e for n in TRAIN for e in labeled_examples(n)]
    ho = [e for n in HELDOUT for e in labeled_examples(n)]
    allx = tr + ho

    report = {
        "baseline_n_rules": len(base),
        "candidate_n_rules": len(ext),
        "rule4": rule4[0],
        "train_signal_for_rule4": sum(
            1 for e in tr if e["features"].get("last_ready_node_op")),
        "results": {},
        "train_score": {
            "baseline": round(train_score(base, tr), 3),
            "candidate": round(train_score(ext, tr), 3),
        },
    }
    for split, exs in (("TRAIN", tr), ("HELDOUT", ho), ("ALL", allx)):
        report["results"][split] = {
            "baseline": evaluate(base, exs),
            "candidate": evaluate(ext, exs),
        }

    ho_base = report["results"]["HELDOUT"]["baseline"]["accuracy"]
    ho_cand = report["results"]["HELDOUT"]["candidate"]["accuracy"]
    report["heldout_delta"] = round(ho_cand - ho_base, 3)
    report["beats_baseline_897"] = ho_cand > 0.897

    # which held-out misses the 4th rule actually fixes
    fixed = []
    base_fa = {(e["incident"], e["tool"]) for e in confusion(base, ho)["false_allow_ex"]}
    cand_fa = {(e["incident"], e["tool"]) for e in confusion(ext, ho)["false_allow_ex"]}
    fixed = sorted(base_fa - cand_fa)
    report["heldout_false_allows_fixed"] = [list(x) for x in fixed]
    report["heldout_false_allows_remaining"] = [list(x) for x in sorted(cand_fa)]

    json.dump(report, open(OUT, "w"), indent=2)

    print(f"baseline (3 rules) HELDOUT acc = {ho_base}")
    print(f"candidate (4 rules) HELDOUT acc = {ho_cand}  (delta {report['heldout_delta']:+})")
    print(f"beats 89.7% baseline: {report['beats_baseline_897']}")
    print(f"train signal for rule4 (last_ready_node_op==True in TRAIN): "
          f"{report['train_signal_for_rule4']}  <- 0 means search cannot discover it")
    print(f"train_score baseline={report['train_score']['baseline']} "
          f"candidate={report['train_score']['candidate']}  (flat -> no search incentive)")
    print(f"fixed held-out false-allows: {report['heldout_false_allows_fixed']}")
    print(f"remaining held-out false-allows: {report['heldout_false_allows_remaining']}")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
