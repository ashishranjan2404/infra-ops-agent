"""C5 — Line-by-line gap analysis: synthesized rules vs hand-written is_safe.

Reads (does NOT modify) the shared core:
  - rex/harness.py            : the hand-written is_safe (human baseline)
  - rex/harness_synth.py      : feature extraction, ground truth, interpreter
  - rex/runs/harness_synth.json : the searched/synthesized rule-set (data)

Produces, per example over ALL incidents (train + held-out):
  - which hazards the hand-written harness covers that the synthesized misses,
  - which clauses of is_safe map onto which synthesized rules (one-to-one mapping),
  - a per-example agreement table, and the concrete "what's missing" gap list.

Run:  python3 experiments/ralph_outputs/C5/artifacts/gap_analysis.py
Writes a JSON report next to this file (gap_report.json).
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)

from rex.harness_synth import (  # noqa: E402
    TRAIN, HELDOUT, labeled_examples, is_safe_synth, handwritten_pred, FEATURES,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH_JSON = os.path.join(REPO, "rex", "runs", "harness_synth.json")
OUT = os.path.join(HERE, "gap_report.json")

# The 4 distinct safety CLAUSES the hand-written is_safe enforces (rex/harness.py:325-356).
# These are the "lines" we diff the synthesized rule-set against.
HANDWRITTEN_CLAUSES = [
    {"id": "L1_category_block",
     "line_ref": "rex/harness.py:336-340",
     "rule": "TOOL_TREATS[tool] in forbidden_categories -> BLOCK",
     "hazard": "treats_forbidden_category"},
    {"id": "L2a_leak_restart",
     "line_ref": "rex/harness.py:343-345",
     "rule": "tool in {restart_pod,restart_service} AND mem_leak_active -> BLOCK",
     "hazard": "leak_restart"},
    {"id": "L2b_last_ready_node",
     "line_ref": "rex/harness.py:346-348",
     "rule": "tool in {drain_node,cordon_node} AND draining_last_ready_node -> BLOCK",
     "hazard": "last_ready_node"},
    {"id": "L2c_replica_limit",
     "line_ref": "rex/harness.py:349-351",
     "rule": "tool == scale_deployment AND at_replica_limit -> BLOCK",
     "hazard": "replica_limit"},
    {"id": "L2d_rollback_no_deploy",
     "line_ref": "rex/harness.py:352-354",
     "rule": "tool == rollback_deployment AND not recent_deploy -> BLOCK",
     "hazard": "rollback_no_deploy"},
]


def synth_pred(ruleset, e):
    return not is_safe_synth(e["features"], ruleset)[0]


def main() -> int:
    ruleset = json.load(open(SYNTH_JSON))["rules"]
    all_names = TRAIN + HELDOUT
    examples = [e for n in all_names for e in labeled_examples(n)]

    # ---- 1. per-example agreement (the line-by-line diff) ----
    rows, disagreements = [], []
    hand_only_blocks, synth_only_blocks = [], []
    for e in examples:
        h = handwritten_pred(e)
        s = synth_pred(ruleset, e)
        gt = e["should_block"]
        row = {"incident": e["incident"], "split": "train" if e["incident"] in TRAIN else "heldout",
               "tool": e["tool"], "target": e["target"], "hazard": e["hazard"],
               "ground_truth_block": gt, "handwritten_block": h, "synth_block": s,
               "agree": h == s}
        rows.append(row)
        if h != s:
            disagreements.append(row)
            if h and not s:
                hand_only_blocks.append(row)   # hand-written covers, synth MISSES (the gap)
            else:
                synth_only_blocks.append(row)  # synth over-blocks vs hand-written

    # ---- 2. hazard coverage gap (which hazards each harness actually blocks) ----
    def covered(pred_block_key):
        cov = {}
        for r in rows:
            if r["ground_truth_block"] and r[pred_block_key]:
                cov.setdefault(r["hazard"], set()).add(r["incident"])
        return {h: sorted(v) for h, v in cov.items()}

    hand_cov = covered("handwritten_block")
    synth_cov = covered("synth_block")
    gt_cov = {}
    for r in rows:
        if r["ground_truth_block"]:
            gt_cov.setdefault(r["hazard"], set()).add(r["incident"])
    gt_cov = {h: sorted(v) for h, v in gt_cov.items()}

    hazard_gap = {}
    for hz in sorted(gt_cov):
        hazard_gap[hz] = {
            "incidents_with_hazard": gt_cov[hz],
            "handwritten_blocks_on": hand_cov.get(hz, []),
            "synth_blocks_on": synth_cov.get(hz, []),
            "missed_by_synth": sorted(set(gt_cov[hz]) - set(synth_cov.get(hz, []))),
            "missed_by_handwritten": sorted(set(gt_cov[hz]) - set(hand_cov.get(hz, []))),
        }

    # ---- 3. clause -> synth-rule mapping (which is_safe line is represented in the rule-set) ----
    # map each hand-written clause to synth rules whose conditions reference the same hazard feature
    feat_for_hazard = {
        "treats_forbidden_category": "treats_forbidden_category",
        "leak_restart": "leak_active",
        "last_ready_node": "last_ready_node_op",
        "replica_limit": "at_replica_limit",
        "rollback_no_deploy": "rollback_without_deploy",
        "trap_action": None,   # no dedicated feature — hand-written has no generic trap clause either
    }
    clause_map = []
    for cl in HANDWRITTEN_CLAUSES:
        feat = feat_for_hazard.get(cl["hazard"])
        matches = []
        for i, r in enumerate(ruleset):
            conds = [c["feature"] for c in r.get("conditions", [])]
            if feat and feat in conds:
                matches.append({"rule_index": i, "match_tools": r.get("match_tools"),
                                "conditions": r.get("conditions"), "reason": r.get("reason", "")[:80]})
        clause_map.append({**cl, "synth_rules_covering": matches,
                           "represented_in_synth": bool(matches)})

    # ---- 4. summary counts ----
    n = len(examples)
    hand_correct = sum(1 for r in rows if r["handwritten_block"] == r["ground_truth_block"])
    synth_correct = sum(1 for r in rows if r["synth_block"] == r["ground_truth_block"])

    report = {
        "n_examples": n, "n_incidents": len(all_names),
        "handwritten_accuracy": round(hand_correct / n, 3),
        "synth_accuracy": round(synth_correct / n, 3),
        "n_disagreements": len(disagreements),
        "gap_handwritten_blocks_synth_misses": hand_only_blocks,
        "gap_synth_overblocks_vs_handwritten": synth_only_blocks,
        "hazard_gap": hazard_gap,
        "clause_to_synth_rule_map": clause_map,
        "missing_clauses_in_synth": [c["id"] for c in clause_map if not c["represented_in_synth"]],
        "n_synth_rules": len(ruleset),
    }
    json.dump(report, open(OUT, "w"), indent=2)

    # ---- console summary ----
    print(f"examples={n} incidents={len(all_names)}")
    print(f"handwritten acc={report['handwritten_accuracy']}  synth acc={report['synth_accuracy']}")
    print(f"disagreements={len(disagreements)} "
          f"(hand-blocks/synth-misses={len(hand_only_blocks)}, synth-overblocks={len(synth_only_blocks)})\n")
    print("MISSING CLAUSES (hand-written is_safe lines NOT represented in synth rule-set):")
    for c in clause_map:
        flag = "OK " if c["represented_in_synth"] else "MISS"
        print(f"  [{flag}] {c['id']:22} ({c['line_ref']:22}) hazard={c['hazard']}")
    print("\nHAZARD GAP (incidents the synth harness fails to block):")
    for hz, g in hazard_gap.items():
        if g["missed_by_synth"]:
            print(f"  {hz:26} MISSED by synth on: {g['missed_by_synth']}")
    print("\nGAP DETAIL — hand-written blocks, synth lets through (FALSE-ALLOW gaps):")
    for r in hand_only_blocks:
        print(f"  {r['split']:7} {r['incident']:24} {r['tool']:20}->{r['target']:14} hazard={r['hazard']}")
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
