"""C2: Harness synthesis on CASCADE incidents ONLY.

Task C2 asks: if we run AutoHarness-style rule synthesis using *only* cascade
incidents, does the Thompson-tree search discover a DIFFERENT rule-set than the
baseline (mixed leaf+cascade) run, and than the conceptual hand-written rule set?

This is a task-namespaced wrapper. It does NOT edit any shared core file. It
imports the (read-only) machinery from rex.harness_synth and rex.harness and only
overrides:
  * the incident split  -> cascade-only TRAIN / HELD-OUT
  * the mutation model  -> a gateway model (Anthropic is out of credits)

The trusted interpreter, feature set, ground-truth labels, scoring and search are
the SAME functions used by the baseline, so the comparison is apples-to-apples.

Output: writes cascade_synth.json next to this file.
Run:    python3 experiments/ralph_outputs/C2/artifacts/cascade_synth.py
"""
from __future__ import annotations

import json
import os
import sys

# repo root on path (script lives 4 dirs deep)
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import rex.harness_synth as hs
from rex.harness import scenarios_by_family
from rex.tree import thompson_search

# Gateway model — Anthropic 400s (out of credits); REx gets diversity from
# per-node feedback, not sampling temperature, so a no_temperature reasoning
# model is fine as the mutation operator.
MODEL = os.environ.get("C2_MODEL", "deepseek-v4-pro")
BUDGET = int(os.environ.get("C2_BUDGET", "8"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cascade_synth.json")

# Cascade-only split. 14 train / 6 held-out. The split is fixed (sorted) for
# reproducibility; held-out keeps incidents that exhibit each cascade hazard so the
# generalization claim is testable, not a lookup.
_CASCADE = sorted(scenarios_by_family()["cascade"])
HELDOUT = ["aws_dynamodb_dns", "cloudflare_waf", "crowdstrike_bsod",
           "gcp_service_control", "azure_ddos", "railway_gcp_suspension"]
TRAIN = [n for n in _CASCADE if n not in HELDOUT]


def propose(parent):
    # reuse the exact baseline propose, but force our MODEL for the call
    saved = hs.MODEL
    hs.MODEL = MODEL
    try:
        return hs.propose_ruleset(parent, _TRAIN_EX)
    finally:
        hs.MODEL = saved


def main() -> int:
    global _TRAIN_EX
    assert not (set(TRAIN) & set(HELDOUT)), "train/held-out overlap!"
    _TRAIN_EX = [e for n in TRAIN for e in hs.labeled_examples(n)]
    held_ex = [e for n in HELDOUT for e in hs.labeled_examples(n)]

    print(f"=== CASCADE-ONLY harness synthesis: {MODEL}, budget {BUDGET} ===")
    print(f"TRAIN cascade incidents ({len(TRAIN)}): {TRAIN}")
    print(f"HELD-OUT cascade incidents ({len(HELDOUT)}): {HELDOUT}")
    print(f"labels: {len(_TRAIN_EX)} train, {len(held_ex)} held-out\n")

    tr_cov, ho_cov = hs.hazard_coverage(TRAIN), hs.hazard_coverage(HELDOUT)
    print("HAZARD COVERAGE (cascade subset):")
    for h in sorted(set(tr_cov) | set(ho_cov)):
        in_tr, in_ho = tr_cov.get(h, []), ho_cov.get(h, [])
        gen = "GENERALIZABLE (in train)" if (in_ho and in_tr) else \
              ("UNSEEN in train" if in_ho else "train-only")
        print(f"  {h:26} train={len(in_tr)}  held_out={len(in_ho)}  [{gen}]")
    print()

    res = thompson_search(
        propose=propose,
        evaluate=lambda rs: hs.train_score(rs, _TRAIN_EX),
        budget=BUDGET, seed=0, stop_at=1.0)
    best = res["nodes"][res["best"]]["cand"]
    print(f"SYNTHESIS done: {len(res['nodes'])} tree nodes, best TRAIN score={res['best_score']:.3f}")
    print(f"  node train-scores: {[round(n['score'], 3) for n in res['nodes']]}\n")

    print("CASCADE-ONLY SYNTHESIZED RULE-SET (best by TRAIN):")
    for r in best:
        print(f"  - block if tool in {r['match_tools'] or 'ANY'} and "
              f"{[(c['feature'], c['op'], c['value']) for c in r['conditions']]}  | {r['reason'][:60]}")
    if not best:
        print("  (empty — synthesis found no improving rule)")
    print()

    harnesses = {
        "seed (empty)": lambda exs: hs.confusion([], exs),
        "cascade-synth": lambda exs: hs.confusion(best, exs),
        "hand-written is_safe": lambda exs: hs.confusion_pred(hs.handwritten_pred, exs),
    }
    print("=" * 78)
    print(f"{'harness':24}  {'TRAIN acc':>9} {'TRAIN FA%':>9}   {'HELDOUT acc':>11} {'HELDOUT FA%':>11}")
    table = {}
    for label, fn in harnesses.items():
        tr, ho = fn(_TRAIN_EX), fn(held_ex)
        table[label] = {"train": {k: tr[k] for k in ("accuracy", "false_allow", "false_allow_rate")},
                        "heldout": {k: ho[k] for k in ("accuracy", "false_allow", "false_allow_rate")}}
        print(f"{label:24}  {tr['accuracy']:>9} {tr['false_allow_rate']:>9}   "
              f"{ho['accuracy']:>11} {ho['false_allow_rate']:>11}")
    print()

    hc = hs.confusion(best, held_ex)
    print(f"CASCADE-SYNTH held-out MISTAKES: {hc['false_allow']} false-allow, {hc['false_block']} false-block")
    for e in hc["false_allow_ex"]:
        active = {k: v for k, v in e["features"].items() if v is True}
        print(f"  FALSE-ALLOW: {e['incident']} / {e['tool']}->{e['target']} "
              f"(hazard={e['hazard']}, active={active})")
    for e in hc["false_block_ex"]:
        print(f"  FALSE-BLOCK: {e['incident']} / {e['tool']}->{e['target']} (was {e['hazard']})")

    out = {"split": "cascade-only", "model": MODEL, "budget": BUDGET,
           "train": TRAIN, "heldout": HELDOUT, "rules": best, "table": table,
           "hazard_train": tr_cov, "hazard_heldout": ho_cov,
           "node_scores": [n["score"] for n in res["nodes"]],
           "best_train_score": res["best_score"],
           "heldout_false_allow": [(e["incident"], e["tool"], e["target"], e["hazard"]) for e in hc["false_allow_ex"]],
           "heldout_false_block": [(e["incident"], e["tool"], e["target"], e["hazard"]) for e in hc["false_block_ex"]]}
    json.dump(out, open(OUT, "w"), indent=2, default=list)
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
