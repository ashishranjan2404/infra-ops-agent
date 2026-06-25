"""C11 — Rule-ablation harness for the hand-written safety gate (rex/harness.py:is_safe).

GOAL
----
The hand-written `is_safe` is a disjunction of independent guard RULES. This harness
measures each rule's CONTRIBUTION to the harness's `is_safe`-classification accuracy by
DISABLING one rule at a time and re-measuring accuracy on the same labeled action set.

The accuracy DROP (full - ablated) is the rule's marginal contribution: how many
safe/unsafe action decisions only that rule was getting right.

WHY A WRAPPER (no core edits)
-----------------------------
We do NOT edit rex/harness.py. Each guard in `is_safe` returns a distinct, stable
`reason` string. To ablate rule R we call the real `is_safe`; if it blocked *because of
R* (the reason matches R's signature), we OVERRIDE the decision to ALLOW. Every other
rule keeps firing untouched. This ablates exactly one rule via the real code path —
the trusted logic is never re-implemented or mutated.

The labeled ground truth is the spec-derived `should_block` from
rex/harness_synth.py:labeled_examples (independent of any harness), so accuracy here is
"does is_safe agree with the SPEC's should-block?" — the same yardstick the synthesis
experiment uses.

    python3 experiments/ralph_outputs/C11/artifacts/rule_ablation.py
        --> writes ablation_result.json next to this file and prints the table.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Make the repo importable regardless of cwd.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from rex.harness import _SCENARIOS, build_state, is_safe, load_scenario  # noqa: E402
from rex.harness_synth import labeled_examples  # noqa: E402

# ---------------------------------------------------------------------------
# The RULES of is_safe, identified by a stable signature in their reason string.
# Each predicate(reason) -> True iff is_safe blocked *because of this rule*.
# The first three are the headline rules (the only block-mechanisms that actually
# fire across the scenario set); replica_limit / rollback are minor guards we also
# report for completeness.
# ---------------------------------------------------------------------------
RULES = {
    # Layer 1 — category block: action treats a ruled-out cause.
    "R1_forbidden_category": lambda reason: "a ruled-out cause" in reason,
    # Layer 2 — state-conditional traps.
    "R2_leak_restart": lambda reason: "a memory leak is still active" in reason,
    "R3_last_ready_node": lambda reason: "the last Ready node" in reason,
    "R4_replica_limit": lambda reason: "already at its replica/quota limit" in reason,
    "R5_rollback_no_deploy": lambda reason: "there was no recent deploy" in reason,
}
HEADLINE = ["R1_forbidden_category", "R2_leak_restart", "R3_last_ready_node"]


def _state_for(e: dict) -> dict:
    """Reconstruct the exact state dict is_safe reads for a labeled example, using the
    same fields build_state derives — but here we have no live World, so we build the
    minimal state directly from the scenario (matches build_state's non-engine fields)."""
    sc = load_scenario(e["incident"])
    return {
        "incident": sc.name,
        "forbidden_categories": sc.forbidden_categories,
        "gold_category": sc.category,
        # a leak is "active" for the leak-restart guard whenever the scenario is a leak;
        # these labeled examples never pre-apply increase_memory_limit, so this matches
        # build_state's mem_leak_active at decision time.
        "mem_leak_active": sc.kind == "mem_leak",
        "draining_last_ready_node": sc.last_single_node,
        "at_replica_limit": sc.at_replica_limit,
        "recent_deploy": sc.recent_deploy,
    }


def predict_block(e: dict, disabled: str | None = None) -> bool:
    """Does is_safe block this action, with `disabled` rule ablated (None = full harness)?"""
    if disabled is not None and disabled not in RULES:
        raise KeyError(f"unknown rule {disabled!r} (have {sorted(RULES)})")
    sc = load_scenario(e["incident"])
    action = {"tool": e["tool"], "args": {"target": e["target"]}}
    allowed, reason = is_safe(action, _state_for(e))
    if allowed:
        return False
    if disabled is not None and RULES[disabled](reason):
        return False  # this rule was the (first) blocker -> ablated -> allow
    return True


def confusion(examples: list, disabled: str | None = None) -> dict:
    tp = tn = fa = fb = 0
    for e in examples:
        blocked = predict_block(e, disabled)
        gold = e["should_block"]
        if gold and blocked:
            tp += 1
        elif gold and not blocked:
            fa += 1   # false-allow: let an unsafe action through (the dangerous error)
        elif not gold and blocked:
            fb += 1   # false-block: blocked a safe/correct action
        else:
            tn += 1
    n = len(examples)
    return {"n": n, "tp": tp, "tn": tn, "false_allow": fa, "false_block": fb,
            "accuracy": round((tp + tn) / n, 4) if n else 0.0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="*", default=None,
                    help="scenario names (default: ALL registered scenarios)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__),
                                                   "ablation_result.json"))
    args = ap.parse_args()

    names = args.scenarios or sorted(_SCENARIOS)
    examples, skipped = [], []
    for n in names:
        try:
            examples.extend(labeled_examples(n))
        except Exception as ex:  # a malformed/un-loadable scenario must not crash the run
            skipped.append({"scenario": n, "error": f"{type(ex).__name__}: {ex}"})

    full = confusion(examples, None)

    per_rule = {}
    for rule in RULES:
        abl = confusion(examples, rule)
        per_rule[rule] = {
            **abl,
            "accuracy_drop": round(full["accuracy"] - abl["accuracy"], 4),
            "false_allows_introduced": abl["false_allow"] - full["false_allow"],
            "false_blocks_removed": full["false_block"] - abl["false_block"],
        }

    result = {
        "scenarios_used": names,
        "scenarios_skipped": skipped,
        "n_labeled_actions": len(examples),
        "full_harness": full,
        "ablations": per_rule,
        "headline_rules": HEADLINE,
        "ranking_by_accuracy_drop": sorted(
            per_rule.items(), key=lambda kv: kv[1]["accuracy_drop"], reverse=True),
    }

    # ---- print table ----
    print(f"Scenarios: {len(names)} ({len(skipped)} skipped)   "
          f"Labeled actions: {len(examples)}")
    print(f"FULL is_safe: accuracy={full['accuracy']}  "
          f"(tp={full['tp']} tn={full['tn']} false_allow={full['false_allow']} "
          f"false_block={full['false_block']})\n")
    hdr = f"{'rule (disabled)':26} {'acc':>7} {'drop':>7} {'+FA':>5} {'-FB':>5}"
    print(hdr)
    print("-" * len(hdr))
    for rule, m in sorted(per_rule.items(),
                          key=lambda kv: kv[1]["accuracy_drop"], reverse=True):
        tag = "*" if rule in HEADLINE else " "
        print(f"{tag}{rule:25} {m['accuracy']:>7} {m['accuracy_drop']:>7} "
              f"{m['false_allows_introduced']:>5} {m['false_blocks_removed']:>5}")
    print("\n(* = headline rule;  drop = full_acc - ablated_acc;  "
          "+FA = false-allows introduced;  -FB = false-blocks removed)")

    json.dump(result, open(args.out, "w"), indent=2)
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
