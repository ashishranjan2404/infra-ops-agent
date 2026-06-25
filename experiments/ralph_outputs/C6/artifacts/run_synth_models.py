"""C6 — Does the proposer model matter for harness synthesis?

Task-namespaced driver. Imports rex.harness_synth WITHOUT editing it, and runs
the SAME Thompson-tree synthesis pipeline once per proposer model by overriding
the module-level `harness_synth.MODEL` (the only proposer hook: it is consumed by
propose_ruleset -> agent.llm.call(MODEL, ...)).

For each proposer we report:
  - best TRAIN score, #tree nodes, node score trajectory
  - the synthesized rule-set (data, never exec'd)
  - TRAIN and HELD-OUT confusion vs the hand-written is_safe baseline
  - held-out false-allows / false-blocks

Everything below the proposer is identical across models (same TRAIN/HELDOUT
splits, same labels, same evaluator, same seed) so any difference is attributable
to the proposer.

Usage:
  python3 experiments/ralph_outputs/C6/artifacts/run_synth_models.py MODEL1 MODEL2 ...
Writes JSON to experiments/ralph_outputs/C6/artifacts/synth_<model>.json and a
combined comparison to experiments/ralph_outputs/C6/artifacts/comparison.json
"""
from __future__ import annotations

import json
import os
import sys
import time

# repo root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

import rex.harness_synth as hs  # noqa: E402
from rex.tree import thompson_search  # noqa: E402

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def run_for_model(model: str, budget: int = 8, seed: int = 0) -> dict:
    """Run the full synthesis pipeline with `model` as the proposer."""
    prev = hs.MODEL
    hs.MODEL = model  # override the proposer hook (module-level, no core edit)
    try:
        train_ex = [e for n in hs.TRAIN for e in hs.labeled_examples(n)]
        held_ex = [e for n in hs.HELDOUT for e in hs.labeled_examples(n)]

        t0 = time.time()
        res = thompson_search(
            propose=lambda parent: hs.propose_ruleset(parent, train_ex),
            evaluate=lambda rs: hs.train_score(rs, train_ex),
            budget=budget, seed=seed, stop_at=1.0)
        elapsed = round(time.time() - t0, 1)
        best = res["nodes"][res["best"]]["cand"]

        tr = hs.confusion(best, train_ex)
        ho = hs.confusion(best, held_ex)
        hw_tr = hs.confusion_pred(hs.handwritten_pred, train_ex)
        hw_ho = hs.confusion_pred(hs.handwritten_pred, held_ex)

        return {
            "model": model,
            "elapsed_s": elapsed,
            "budget": budget,
            "n_nodes": len(res["nodes"]),
            "best_train_score": round(res["best_score"], 4),
            "node_scores": [round(n["score"], 4) for n in res["nodes"]],
            "n_rules": len(best),
            "rules": best,
            "train": {k: tr[k] for k in ("accuracy", "false_allow", "false_block", "false_allow_rate", "n")},
            "heldout": {k: ho[k] for k in ("accuracy", "false_allow", "false_block", "false_allow_rate", "n")},
            "handwritten_train": {k: hw_tr[k] for k in ("accuracy", "false_allow", "false_block", "n")},
            "handwritten_heldout": {k: hw_ho[k] for k in ("accuracy", "false_allow", "false_block", "n")},
            "heldout_false_allow": [(e["incident"], e["tool"], e["target"], e["hazard"]) for e in ho["false_allow_ex"]],
            "heldout_false_block": [(e["incident"], e["tool"], e["target"], e["hazard"]) for e in ho["false_block_ex"]],
        }
    finally:
        hs.MODEL = prev


def main() -> int:
    models = sys.argv[1:] or ["gpt-5.5", "deepseek-v4-pro", "minimax-m3"]
    results = []
    for m in models:
        print(f"\n=== proposer = {m} ===", flush=True)
        try:
            r = run_for_model(m)
            results.append(r)
            outp = os.path.join(OUTDIR, f"synth_{m.replace('/', '_')}.json")
            json.dump(r, open(outp, "w"), indent=2, default=list)
            print(f"  best_train={r['best_train_score']} nodes={r['n_nodes']} "
                  f"rules={r['n_rules']} heldout_acc={r['heldout']['accuracy']} "
                  f"heldout_FA={r['heldout']['false_allow']} ({r['elapsed_s']}s) -> {outp}", flush=True)
        except Exception as e:
            err = {"model": m, "error": f"{type(e).__name__}: {e}"}
            results.append(err)
            print(f"  ERROR: {err['error']}", flush=True)

    combined = os.path.join(OUTDIR, "comparison.json")
    json.dump({"results": results}, open(combined, "w"), indent=2, default=list)
    print(f"\n-> {combined}")

    # human-readable comparison table
    print("\n" + "=" * 90)
    print(f"{'proposer':18} {'best_tr':>8} {'nodes':>6} {'rules':>6} "
          f"{'tr_acc':>7} {'tr_FA':>6} {'ho_acc':>7} {'ho_FA':>6} {'ho_FB':>6}")
    for r in results:
        if "error" in r:
            print(f"{r['model']:18} ERROR {r['error'][:60]}")
            continue
        print(f"{r['model']:18} {r['best_train_score']:>8} {r['n_nodes']:>6} {r['n_rules']:>6} "
              f"{r['train']['accuracy']:>7} {r['train']['false_allow']:>6} "
              f"{r['heldout']['accuracy']:>7} {r['heldout']['false_allow']:>6} "
              f"{r['heldout']['false_block']:>6}")
    # baseline (same for all)
    ok = next((r for r in results if "error" not in r), None)
    if ok:
        print(f"{'hand-written':18} {'--':>8} {'--':>6} {'--':>6} "
              f"{ok['handwritten_train']['accuracy']:>7} {ok['handwritten_train']['false_allow']:>6} "
              f"{ok['handwritten_heldout']['accuracy']:>7} {ok['handwritten_heldout']['false_allow']:>6} "
              f"{ok['handwritten_heldout']['false_block']:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
