"""C9 — Run/evaluate the synthesized safety harness across the FULL 42 incidents.

Grounded in rex/harness_synth.py. We do NOT edit any shared core file; we IMPORT
its machinery (labeled_examples, confusion, confusion_pred, handwritten_pred,
is_safe_synth, train_score, propose_ruleset, hazard_coverage) and only change the
*incident universe* and the *mutation model* (Anthropic is out of credits, so the
haiku mutation operator is swapped for a HUD-gateway model via monkeypatch — the
interpreter and reward are byte-identical to the core).

What this reports (the task ask):
  - is_safe (hand-written baseline) accuracy on the SMALL split (harness_synth's
    10 incidents) vs the FULL 42-incident set.
  - synthesized-harness accuracy on TRAIN vs HELD-OUT, for BOTH the small 10-incident
    split and a 42-incident split (70/30 by incident, deterministic).

Usage:
  python3 experiments/ralph_outputs/C9/artifacts/run_full42.py            # full run (LLM synthesis)
  python3 experiments/ralph_outputs/C9/artifacts/run_full42.py --no-llm   # deterministic-only (no synthesis)
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

import rex.harness_synth as hs
from rex.harness import _SCENARIOS
from rex.tree import thompson_search

OUTDIR = os.path.join(ROOT, "experiments", "ralph_outputs", "C9", "artifacts")

# ---- gateway model swap (Anthropic credits exhausted) ----------------------------
# We override the mutation MODEL only; everything else (validate_ruleset, interpreter,
# train_score) is the unmodified core. If the gateway is unreachable we degrade to
# a no-LLM run (seed + hand-written only) and report the blocker honestly.
GATEWAY_MODEL = os.environ.get("C9_MODEL", "deepseek-v4-pro")


def all_incidents() -> list:
    return sorted(_SCENARIOS.keys())


def split_70_30(names: list, seed: int = 0):
    """Deterministic 70/30 incident-level split (sorted + strided for stability)."""
    import random
    rng = random.Random(seed)
    shuffled = list(names)
    rng.shuffle(shuffled)
    k = round(len(shuffled) * 0.7)
    train = sorted(shuffled[:k])
    held = sorted(shuffled[k:])
    return train, held


def eval_three(train_ex, held_ex, best):
    """seed / synthesized / hand-written on a (train, held) example pair."""
    harnesses = {
        "seed (empty)": lambda exs: hs.confusion([], exs),
        "synthesized": lambda exs: hs.confusion(best, exs),
        "hand-written is_safe": lambda exs: hs.confusion_pred(hs.handwritten_pred, exs),
    }
    out = {}
    for label, fn in harnesses.items():
        tr, ho = fn(train_ex), fn(held_ex)
        out[label] = {
            "train": {k: tr[k] for k in ("accuracy", "false_allow", "false_block", "n", "false_allow_rate")},
            "heldout": {k: ho[k] for k in ("accuracy", "false_allow", "false_block", "n", "false_allow_rate")},
        }
    return out


def main() -> int:
    no_llm = "--no-llm" in sys.argv
    t0 = time.time()
    os.makedirs(OUTDIR, exist_ok=True)

    names = all_incidents()
    assert len(names) == 42, f"expected 42 incidents, got {len(names)}"

    # ---- label the full universe (fully deterministic, no LLM) ----
    full_ex = [e for n in names for e in hs.labeled_examples(n)]
    n_block = sum(e["should_block"] for e in full_ex)
    print(f"=== C9: full 42-incident harness run ===")
    print(f"incidents: {len(names)}  labeled examples: {len(full_ex)}  should_block: {n_block}")

    # ---- the SMALL split that core harness_synth.py uses ----
    small_train, small_held = hs.TRAIN, hs.HELDOUT
    small_tr_ex = [e for n in small_train for e in hs.labeled_examples(n)]
    small_ho_ex = [e for n in small_held for e in hs.labeled_examples(n)]
    small_all_ex = small_tr_ex + small_ho_ex

    # ---- the FULL 42 split (70/30 by incident) ----
    f_train, f_held = split_70_30(names, seed=0)
    f_tr_ex = [e for n in f_train for e in hs.labeled_examples(n)]
    f_ho_ex = [e for n in f_held for e in hs.labeled_examples(n)]
    print(f"FULL split: {len(f_train)} train / {len(f_held)} held-out incidents")
    print(f"  labels: {len(f_tr_ex)} train, {len(f_ho_ex)} held-out")

    # ---- synthesis on the FULL train split (LLM mutation operator) ----
    blocker = None
    best_full, best_small = [], []
    synth_meta = {}
    if not no_llm:
        try:
            # swap mutation model -> gateway; interpreter/reward unchanged.
            orig_model = hs.MODEL
            hs.MODEL = GATEWAY_MODEL
            # smoke-test the gateway once; if it raises, fall back to no-LLM.
            from agent.llm import call
            call(GATEWAY_MODEL, "ok", max_tokens=4, temperature=0)

            def run_search(train_ex, budget):
                res = thompson_search(
                    propose=lambda parent: hs.propose_ruleset(parent, train_ex),
                    evaluate=lambda rs: hs.train_score(rs, train_ex),
                    budget=budget, seed=0, stop_at=1.0)
                return res["nodes"][res["best"]]["cand"], res

            print(f"\nSYNTHESIS (full-42 train) via {GATEWAY_MODEL} ...")
            best_full, res_full = run_search(f_tr_ex, budget=int(os.environ.get("C9_BUDGET", "6")))
            print(f"  full: {len(res_full['nodes'])} nodes, best TRAIN score={res_full['best_score']:.3f}")

            print(f"SYNTHESIS (small-10 train) via {GATEWAY_MODEL} ...")
            best_small, res_small = run_search(small_tr_ex, budget=int(os.environ.get("C9_BUDGET", "6")))
            print(f"  small: {len(res_small['nodes'])} nodes, best TRAIN score={res_small['best_score']:.3f}")

            hs.MODEL = orig_model
            synth_meta = {
                "model": GATEWAY_MODEL,
                "full_best_train_score": res_full["best_score"],
                "full_node_scores": [n["score"] for n in res_full["nodes"]],
                "small_best_train_score": res_small["best_score"],
                "small_node_scores": [n["score"] for n in res_small["nodes"]],
                "full_rules": best_full,
                "small_rules": best_small,
            }
        except Exception as e:
            blocker = f"LLM synthesis unavailable ({type(e).__name__}: {str(e)[:160]}); reporting deterministic harnesses only"
            print("\n[BLOCKER]", blocker)
            no_llm = True

    # ---- evaluate on BOTH splits ----
    small_eval = eval_three(small_tr_ex, small_ho_ex, best_small)
    full_eval = eval_three(f_tr_ex, f_ho_ex, best_full)

    # ---- headline: hand-written is_safe accuracy small vs full ----
    hw_small_all = hs.confusion_pred(hs.handwritten_pred, small_all_ex)
    hw_full_all = hs.confusion_pred(hs.handwritten_pred, full_ex)
    headline = {
        "handwritten_is_safe": {
            "small_split_10_incidents": {"n": hw_small_all["n"], "accuracy": hw_small_all["accuracy"],
                                          "false_allow": hw_small_all["false_allow"],
                                          "false_block": hw_small_all["false_block"]},
            "full_42_incidents": {"n": hw_full_all["n"], "accuracy": hw_full_all["accuracy"],
                                   "false_allow": hw_full_all["false_allow"],
                                   "false_block": hw_full_all["false_block"]},
        }
    }

    print("\n" + "=" * 78)
    print("HEADLINE — hand-written is_safe accuracy (whole-set):")
    print(f"  small 10-incident split: acc={hw_small_all['accuracy']} "
          f"(n={hw_small_all['n']}, FA={hw_small_all['false_allow']}, FB={hw_small_all['false_block']})")
    print(f"  FULL 42-incident set:    acc={hw_full_all['accuracy']} "
          f"(n={hw_full_all['n']}, FA={hw_full_all['false_allow']}, FB={hw_full_all['false_block']})")

    print("\nFULL-42 split, three harnesses (train / held-out accuracy):")
    print(f"  {'harness':24} {'TRAIN acc':>9} {'HELD acc':>9} {'TRAIN FA':>9} {'HELD FA':>8}")
    for label, d in full_eval.items():
        print(f"  {label:24} {d['train']['accuracy']:>9} {d['heldout']['accuracy']:>9} "
              f"{d['train']['false_allow']:>9} {d['heldout']['false_allow']:>8}")

    elapsed = round(time.time() - t0, 1)
    result = {
        "elapsed_sec": elapsed,
        "n_incidents": len(names),
        "n_labeled_examples": len(full_ex),
        "n_should_block": n_block,
        "small_split": {"train": small_train, "heldout": small_held,
                        "n_train_ex": len(small_tr_ex), "n_heldout_ex": len(small_ho_ex)},
        "full_split": {"train": f_train, "heldout": f_held,
                       "n_train_ex": len(f_tr_ex), "n_heldout_ex": len(f_ho_ex)},
        "headline": headline,
        "small_eval": small_eval,
        "full_eval": full_eval,
        "synthesis": synth_meta,
        "blocker": blocker,
        "no_llm": no_llm,
    }
    outp = os.path.join(OUTDIR, "results_full42.json")
    json.dump(result, open(outp, "w"), indent=2, default=list)
    print(f"\n-> {outp}  ({elapsed}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
