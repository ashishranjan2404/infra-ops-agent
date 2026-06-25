"""C7 — Harness transfer: synthesize on SIMPLE incidents, evaluate on CASCADE.

Cross-TYPE generalization probe for the AutoHarness-synthesized safety rule-set
(rex/harness_synth.py). The synthesizer (Thompson-tree search + haiku mutation
operator) sees ONLY the `simple` incident family's TRAIN labels; we then measure
is_safe-style classification accuracy on the held-out `cascade` family it never saw,
and report the transfer gap against the hand-written is_safe oracle.

Imports core machinery; edits NOTHING shared. Run:

    set -a; source ~/.zshrc; set +a
    python3 experiments/ralph_outputs/C7/artifacts/transfer_simple_to_cascade.py
"""
from __future__ import annotations

import json
import os

import rex.harness_synth as hs
from rex.harness import scenarios_by_family
from rex.harness_synth import (
    confusion, confusion_pred, handwritten_pred, hazard_coverage,
    labeled_examples, propose_ruleset, train_score,
)
from rex.tree import thompson_search

# Mutation-operator model. Default roster model is claude-haiku-4-5 (anthropic), but the
# Anthropic key is out of credits here, so we route the operator through the HUD gateway.
# Empirically only gpt-5.5 reliably emits the JSON rule-list on the FULL propose() prompt;
# deepseek-v4-pro and gemini-3.1-pro return empty content on that prompt (synthesis then
# degenerates to the empty seed). Override via C7_MODEL=<roster-name>. We monkeypatch the
# module-level MODEL that propose_ruleset() reads — NO core file is edited.
MODEL = os.environ.get("C7_MODEL", "gpt-5.5")
hs.MODEL = MODEL

BUDGET = 8
SEED = 0
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transfer_result.json")


def _safe_labels(names):
    """Build labeled examples per incident; skip (record) any incident that fails to load."""
    out, skipped = [], []
    for n in names:
        try:
            out.extend(labeled_examples(n))
        except Exception as e:  # noqa: BLE001 - one bad generated YAML must not sink the run
            skipped.append({"incident": n, "error": f"{type(e).__name__}: {e}"})
    return out, skipped


def _block_rate(exs):
    return round(sum(1 for e in exs if e["should_block"]) / len(exs), 3) if exs else 0.0


def _slim(c):
    return {k: c[k] for k in ("accuracy", "false_allow", "false_allow_rate", "tp", "tn", "false_block", "n")}


def main() -> int:
    fam = scenarios_by_family()
    TRAIN = sorted(fam.get("simple", []))
    HELDOUT = sorted(fam.get("cascade", []))
    assert TRAIN and HELDOUT, "missing simple/cascade families"
    assert not (set(TRAIN) & set(HELDOUT)), "simple/cascade overlap!"

    train_ex, sk_tr = _safe_labels(TRAIN)
    held_ex, sk_ho = _safe_labels(HELDOUT)
    skipped = sk_tr + sk_ho

    print(f"=== C7 transfer: synthesize SIMPLE -> evaluate CASCADE ({MODEL}, budget {BUDGET}) ===")
    print(f"TRAIN  (simple,  {len(TRAIN)}): {TRAIN}")
    print(f"HELDOUT(cascade, {len(HELDOUT)}): {HELDOUT}")
    print(f"labels: {len(train_ex)} train, {len(held_ex)} held-out; "
          f"block-rate train={_block_rate(train_ex)} heldout={_block_rate(held_ex)}")
    if skipped:
        print(f"SKIPPED incidents: {skipped}")
    print()

    # --- SYNTHESIS on TRAIN(simple) ONLY ---
    res = thompson_search(
        propose=lambda parent: propose_ruleset(parent, train_ex),
        evaluate=lambda rs: train_score(rs, train_ex),
        budget=BUDGET, seed=SEED, stop_at=1.0)
    best = res["nodes"][res["best"]]["cand"]
    synthesis_ran = bool(best)
    print(f"SYNTHESIS: {len(res['nodes'])} nodes, best TRAIN score={res['best_score']:.3f}, "
          f"node scores={[round(n['score'], 3) for n in res['nodes']]}")
    print("SYNTHESIZED RULE-SET:")
    for r in best:
        print(f"  - block if tool in {r['match_tools'] or 'ANY'} and {r['conditions']} | {r['reason'][:60]}")
    if not best:
        print("  (empty — synthesis did not improve on the seed)")
    print()

    # --- THREE harnesses on TRAIN(simple) and HELDOUT(cascade) ---
    harnesses = {
        "seed_empty": lambda exs: confusion([], exs),
        "synthesized": lambda exs: confusion(best, exs),
        "handwritten": lambda exs: confusion_pred(handwritten_pred, exs),
    }
    print(f"{'harness':14} {'TRAIN acc':>9} {'TRAIN FA%':>9}   {'HELDOUT acc':>11} {'HELDOUT FA%':>11}")
    table = {}
    for label, fn in harnesses.items():
        tr, ho = fn(train_ex), fn(held_ex)
        table[label] = {"train": _slim(tr), "heldout": _slim(ho)}
        print(f"{label:14} {tr['accuracy']:>9} {tr['false_allow_rate']:>9}   "
              f"{ho['accuracy']:>11} {ho['false_allow_rate']:>11}")
    print()

    def gap(h):
        return round(table[h]["train"]["accuracy"] - table[h]["heldout"]["accuracy"], 3)

    tgap = {"synthesized": gap("synthesized"), "handwritten": gap("handwritten"),
            "seed_empty": gap("seed_empty")}
    tgap["synthesis_cost"] = round(tgap["synthesized"] - tgap["handwritten"], 3)
    print(f"TRANSFER GAP (train_acc - heldout_acc): synthesized={tgap['synthesized']}, "
          f"handwritten(oracle)={tgap['handwritten']}, synthesis_cost={tgap['synthesis_cost']}")

    hc = confusion(best, held_ex)
    print(f"\nSYNTHESIZED held-out (cascade) MISTAKES: {hc['false_allow']} false-allow, "
          f"{hc['false_block']} false-block")
    for e in hc["false_allow_ex"][:20]:
        print(f"  FALSE-ALLOW: {e['incident']} / {e['tool']}->{e['target']} (hazard={e['hazard']})")

    leakage_ok = not (set(TRAIN) & set(HELDOUT))
    print(f"\nLEAKAGE CHECK: cascade labels never used in synthesis; disjoint={leakage_ok}")

    result = {
        "task": "C7", "model": MODEL, "budget": BUDGET, "seed": SEED,
        "train_family": "simple", "heldout_family": "cascade",
        "train_incidents": TRAIN, "heldout_incidents": HELDOUT,
        "n_train_labels": len(train_ex), "n_heldout_labels": len(held_ex),
        "block_rate_train": _block_rate(train_ex), "block_rate_heldout": _block_rate(held_ex),
        "skipped_incidents": skipped,
        "synthesis_ran": synthesis_ran,
        "synthesized_rules": best,
        "node_scores": [n["score"] for n in res["nodes"]],
        "best_train_score": res["best_score"],
        "table": table,
        "transfer_gap": tgap,
        "heldout_false_allow": [(e["incident"], e["tool"], e["target"], e["hazard"])
                                for e in hc["false_allow_ex"]],
        "heldout_false_block": [(e["incident"], e["tool"], e["target"], e["hazard"])
                                for e in hc["false_block_ex"]],
        "hazard_train": hazard_coverage(TRAIN),
        "hazard_heldout": hazard_coverage(HELDOUT),
        "leakage_ok": leakage_ok,
    }
    json.dump(result, open(OUT, "w"), indent=2, default=list)
    print(f"\n-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
