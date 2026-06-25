"""C1 — Lambda sweep over the harness-synthesis complexity penalty.

`rex/harness_synth.py` synthesizes a SAFETY rule-set via Thompson-tree search. Its
reward `train_score()` subtracts `COMPLEXITY_LAMBDA * n_conditions` — a per-condition
penalty that biases search toward simpler / more-general rules. That lambda is a
hard-coded module constant (0.003). This driver sweeps lambda WITHOUT editing the core
module: it reuses harness_synth's public functions and passes its OWN lambda-parameterized
scoring closure as `evaluate=` to `rex.tree.thompson_search`.

Two mutation operators:
  - offline (default): deterministic, no network. Greedy single-condition block rules
    built from the training false-allows, optionally pruned by lambda. Reproducible.
  - real: harness_synth.propose_ruleset (haiku mutation), needs ANTHROPIC_API_KEY.

Usage:
  python3 lambda_sweep.py --offline                 # full offline sweep
  python3 lambda_sweep.py --real --budget 4 \
      --lambdas 0.0,0.05                             # small real-API subset

Writes a JSON sweep table to --out (default lambda_sweep_offline.json).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# make the repo importable no matter where we run from
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from rex.harness_synth import (  # noqa: E402
    TRAIN, HELDOUT, FEATURES, _OPS,
    labeled_examples, confusion, confusion_pred, handwritten_pred,
    is_safe_synth, validate_ruleset, train_score, COMPLEXITY_LAMBDA,
)
from rex.tree import thompson_search  # noqa: E402

_RESTARTS = ("restart_pod", "restart_service")


# ---- lambda-parameterized reward (faithful copy of harness_synth.train_score) -------
def score_with_lambda(ruleset: list, train_ex: list, lam: float) -> float:
    """Identical math to harness_synth.train_score, but lambda is a parameter.
    Reward in [0,1]: false-allows (dangerous) weighted 2x false-blocks, minus
    lam * total_conditions. At lam == COMPLEXITY_LAMBDA this equals train_score()."""
    c = confusion(ruleset, train_ex)
    nb, na = c["tp"] + c["false_allow"], c["tn"] + c["false_block"]
    err = 2.0 * c["false_allow"] + 1.0 * c["false_block"]
    maxerr = 2.0 * nb + 1.0 * na
    base = (1.0 - err / maxerr) if maxerr else 0.0
    n_cond = sum(len(r.get("conditions") or []) for r in ruleset)
    return max(0.0, base - lam * n_cond)


# ---- offline deterministic mutation operator ---------------------------------------
# Candidate atoms: one block-rule per (match_tools, feature==True) that, if added,
# fixes at least one current false-allow. The operator greedily adds the atom that most
# improves the *lambda-aware* score; lambda therefore directly governs how many
# conditions survive (a high lambda makes a marginal atom not worth its condition cost).
_BOOL_FEATURES = [f for f in FEATURES if f != "tool"]


def _candidate_atoms(train_ex: list) -> list:
    """All single-condition block-rule atoms suggested by the data: for every example
    that SHOULD block, propose 'block this tool when <an active bool feature> == True'.
    De-duplicated. These are general (no incident ids)."""
    atoms = {}
    for e in train_ex:
        if not e["should_block"]:
            continue
        feats = e["features"]
        for f in _BOOL_FEATURES:
            if feats.get(f) is True:
                key = (e["tool"], f)
                atoms[key] = {
                    "match_tools": [e["tool"]],
                    "conditions": [{"feature": f, "op": "==", "value": True}],
                    "block": True,
                    "reason": f"block {e['tool']} when {f}",
                }
    return list(atoms.values())


def propose_offline_builder(train_ex: list, lam: float):
    """Returns a propose(parent_node|None)->ruleset closure for thompson_search.
    Greedy: start from parent's rule-set (or []), add the single atom that most
    improves score_with_lambda. If no atom improves it, return the parent unchanged
    (search will stall, which is the correct signal that lambda has pruned everything)."""
    atoms = _candidate_atoms(train_ex)

    def propose(parent_node):
        current = list(parent_node["cand"]) if parent_node else []
        have = {(tuple(r["match_tools"]),
                 tuple((c["feature"], c["op"], c["value"]) for c in r["conditions"]))
                for r in current}
        base = score_with_lambda(current, train_ex, lam)
        best_gain, best_atom = 0.0, None
        for a in atoms:
            sig = (tuple(a["match_tools"]),
                   tuple((c["feature"], c["op"], c["value"]) for c in a["conditions"]))
            if sig in have:
                continue
            cand = current + [a]
            g = score_with_lambda(cand, train_ex, lam) - base
            if g > best_gain + 1e-12:
                best_gain, best_atom = g, a
        return validate_ruleset(current + [best_atom]) if best_atom else validate_ruleset(current)

    return propose


# ---- one sweep point ---------------------------------------------------------------
def run_point(lam: float, train_ex: list, held_ex: list, budget: int,
              mode: str, seed: int = 0) -> dict:
    if mode == "real":
        from rex.harness_synth import propose_ruleset

        def propose(parent):
            return propose_ruleset(parent, train_ex)
    else:
        propose = propose_offline_builder(train_ex, lam)

    res = thompson_search(
        propose=propose,
        evaluate=lambda rs: score_with_lambda(rs, train_ex, lam),
        budget=budget, seed=seed, stop_at=1.0)
    best = res["nodes"][res["best"]]["cand"]

    tr, ho = confusion(best, train_ex), confusion(best, held_ex)
    n_cond = sum(len(r.get("conditions") or []) for r in best)
    return {
        "lambda": lam, "mode": mode, "budget": budget,
        "best_train_reward": round(res["best_score"], 4),
        "n_rules": len(best), "n_conditions": n_cond,
        "train_acc": tr["accuracy"], "train_false_allow": tr["false_allow"],
        "train_false_block": tr["false_block"],
        "heldout_acc": ho["accuracy"], "heldout_false_allow": ho["false_allow"],
        "heldout_false_block": ho["false_block"],
        "heldout_false_allow_rate": ho["false_allow_rate"],
        "rules": best,
        "node_rewards": [round(n["score"], 4) for n in res["nodes"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="deterministic, no network (default)")
    ap.add_argument("--real", action="store_true", help="use haiku mutation (needs API key)")
    ap.add_argument("--budget", type=int, default=8)
    ap.add_argument("--lambdas", type=str,
                    default="0.0,0.003,0.01,0.03,0.08,0.2")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    mode = "real" if args.real else "offline"
    lambdas = [float(x) for x in args.lambdas.split(",") if x.strip() != ""]
    out = args.out or os.path.join(os.path.dirname(__file__),
                                   f"lambda_sweep_{mode}.json")

    train_ex = [e for n in TRAIN for e in labeled_examples(n)]
    held_ex = [e for n in HELDOUT for e in labeled_examples(n)]

    # baselines (lambda-independent)
    hw_tr = confusion_pred(handwritten_pred, train_ex)
    hw_ho = confusion_pred(handwritten_pred, held_ex)

    print(f"=== lambda sweep ({mode}), budget {args.budget} ===")
    print(f"TRAIN labels={len(train_ex)}  HELDOUT labels={len(held_ex)}")
    print(f"hand-written is_safe: TRAIN acc={hw_tr['accuracy']} "
          f"HELDOUT acc={hw_ho['accuracy']} (lambda-independent baseline)\n")
    hdr = (f"{'lambda':>7} {'reward':>7} {'rules':>5} {'cond':>4} "
           f"{'TR_acc':>6} {'TR_FA':>5} {'HO_acc':>6} {'HO_FA':>5}")
    print(hdr)

    points = []
    for lam in lambdas:
        p = run_point(lam, train_ex, held_ex, args.budget, mode)
        points.append(p)
        print(f"{lam:>7} {p['best_train_reward']:>7} {p['n_rules']:>5} "
              f"{p['n_conditions']:>4} {p['train_acc']:>6} {p['train_false_allow']:>5} "
              f"{p['heldout_acc']:>6} {p['heldout_false_allow']:>5}")

    result = {
        "mode": mode, "budget": args.budget,
        "default_lambda": COMPLEXITY_LAMBDA,
        "train_incidents": TRAIN, "heldout_incidents": HELDOUT,
        "n_train_labels": len(train_ex), "n_heldout_labels": len(held_ex),
        "handwritten_baseline": {
            "train_acc": hw_tr["accuracy"], "heldout_acc": hw_ho["accuracy"],
            "train_false_allow": hw_tr["false_allow"],
            "heldout_false_allow": hw_ho["false_allow"]},
        "sweep": points,
    }
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
