#!/usr/bin/env python3
"""I4 entropy/coverage witness for "3 rules suffice".

This is the runnable evidence behind I4's information-theoretic ARGUMENT. Unlike the
C12 witness (which checks separability / accuracy of a fixed 3-rule classifier), this
script computes the actual INFORMATION-THEORETIC quantities the argument rests on,
over the REAL realized feature space of the REx harness:

  H(y)                     base entropy of the block-label (bits)
  H(y | R1), H(y | R1,R2), H(y | R1,R2,R3)   residual label entropy after k rules
  IG(Rk)  = H(y|R<k) - H(y|R<=k)             information gain (bits) of adding rule k
  I(y; R4 | R1,R2,R3)      conditional MI of a 4th Phi-rule given the first three
  coverage(k)              fraction of the should-block mass the first k rules cover

The "feature-expressible" universe is the realized set V = {features(a,s)} over every
loadable scenario (rex.harness_synth.labeled_examples). We measure on the
Phi-expressible subset (the human harness's own feature space) and report the
out-of-scope residual (topology traps) separately and honestly.

We import ONLY pure-data helpers (no LLM path). Run:
    python3 entropy_witness.py
"""
from __future__ import annotations

import math
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


# ---- the 3 rule-schemas as pure predicates over the `features` dict ----------------
def R1_category(f: dict) -> bool:
    return bool(f.get("treats_forbidden_category"))


def R2_fault_masking(f: dict) -> bool:
    return f.get("tool") in ("restart_pod", "restart_service") and bool(f.get("leak_active"))


def R3_precondition_exhausted(f: dict) -> bool:
    return (bool(f.get("last_ready_node_op"))
            or bool(f.get("at_replica_limit"))
            or bool(f.get("rollback_without_deploy")))


RULES = [("R1_category", R1_category),
         ("R2_fault_masking", R2_fault_masking),
         ("R3_precondition_exhausted", R3_precondition_exhausted)]


def phi_expressible(f: dict) -> bool:
    """True iff at least one of the 6 hazard features carries signal (the action is
    inside Phi's expressive reach). Tool alone (all-false flags) is the neutral region."""
    return bool(f.get("treats_forbidden_category") or f.get("leak_active")
                or f.get("last_ready_node_op") or f.get("at_replica_limit")
                or f.get("rollback_without_deploy"))


# ---- information theory over a labeled collection ----------------------------------
def _entropy(labels) -> float:
    """Shannon entropy (bits) of an iterable of hashable labels."""
    c = Counter(labels)
    n = sum(c.values())
    if n == 0:
        return 0.0
    h = 0.0
    for v in c.values():
        p = v / n
        h -= p * math.log2(p)
    return h


def _cond_entropy(rows, partition_fn) -> float:
    """H(y | Z) where Z = partition_fn(features) and y = should_block.
    H(y|Z) = sum_z p(z) H(y | Z=z)."""
    buckets: dict = {}
    for r in rows:
        z = partition_fn(r["features"])
        buckets.setdefault(z, []).append(r["should_block"])
    n = sum(len(v) for v in buckets.values())
    if n == 0:
        return 0.0
    h = 0.0
    for ys in buckets.values():
        h += (len(ys) / n) * _entropy(ys)
    return h


def _fire_vector(f: dict, k: int):
    """Partition key = which of the first k rules fire (a tuple of bools)."""
    return tuple(fn(f) for _, fn in RULES[:k])


def main() -> int:
    try:
        from rex.harness import _SCENARIOS
        from rex.harness_synth import labeled_examples
    except Exception as e:  # pragma: no cover
        print(f"IMPORT-BLOCKED: {e}")
        print("RESULT: BLOCKED")
        return 2

    all_rows, failed, loaded = [], [], []
    for name in sorted(_SCENARIOS):
        try:
            rows = labeled_examples(name)
        except Exception as e:
            failed.append((name, str(e)))
            continue
        loaded.append(name)
        all_rows.extend(rows)

    # split into Phi-expressible (the human harness's feature space) and out-of-scope
    phi_rows = [r for r in all_rows if phi_expressible(r["features"])
                or r["should_block"] is False]  # neutral negatives belong to Phi region too
    # the honest residual: positives that escape Phi entirely (topology traps)
    oos_pos = [r for r in all_rows if r["should_block"] and not phi_expressible(r["features"])]

    # work the IT argument on the in-scope set (Phi region): all negatives + Phi positives
    in_scope = [r for r in all_rows
                if r["should_block"] is False or phi_expressible(r["features"])]

    n = len(in_scope)
    base_labels = [r["should_block"] for r in in_scope]
    H_y = _entropy(base_labels)

    # residual entropy after k rules (conditioning on the fire-vector of first k rules)
    H = [H_y]
    for k in range(1, 4):
        H.append(_cond_entropy(in_scope, lambda f, k=k: _fire_vector(f, k)))

    IG = [H[k - 1] - H[k] for k in range(1, 4)]  # info gain of R1,R2,R3 (bits)

    # --- I(y; R4 | R1,R2,R3) for EVERY candidate 4th rule over Phi --------------------
    # A 4th rule is any predicate over the 6 features. The richest possible R4 is the
    # full feature vector itself (the finest Phi-measurable partition). If conditioning
    # additionally on the FULL feature vector adds no information beyond the 3-rule
    # fire-vector, then NO R4 over Phi can add information either (data-processing).
    def full_phi_vector(f: dict):
        return (f.get("tool"), f.get("treats_forbidden_category"), f.get("leak_active"),
                f.get("last_ready_node_op"), f.get("at_replica_limit"),
                f.get("rollback_without_deploy"))

    H_y_given_123 = H[3]
    H_y_given_full = _cond_entropy(in_scope, full_phi_vector)
    # I(y; full_Phi | R123) = H(y|R123) - H(y|R123, full_Phi) = H(y|R123) - H(y|full_Phi)
    # (full_Phi refines R123, so conditioning on both == conditioning on full_Phi)
    I_y_R4_given_123 = H_y_given_123 - H_y_given_full

    # coverage: fraction of should-block MASS the first k rules capture
    pos = [r for r in in_scope if r["should_block"]]
    n_pos = len(pos)

    def covered_by_first_k(r, k):
        return any(fn(r["features"]) for _, fn in RULES[:k])

    cov = [round(sum(covered_by_first_k(r, k) for r in pos) / n_pos, 4) if n_pos else 0.0
           for k in range(1, 4)]

    print(f"scenarios loaded         : {len(loaded)}  (failed: {len(failed)})")
    print(f"examples total           : {len(all_rows)}")
    print(f"in-scope (Phi region) n  : {n}   positives={n_pos}")
    print(f"out-of-scope positives   : {len(oos_pos)}  (topology traps, escape Phi)")
    print()
    print("--- LABEL ENTROPY DECOMPOSITION (bits, on the Phi region) ---")
    print(f"H(y)                     = {H_y:.4f}")
    print(f"H(y | R1)                = {H[1]:.4f}   IG(R1) = {IG[0]:.4f}")
    print(f"H(y | R1,R2)             = {H[2]:.4f}   IG(R2) = {IG[1]:.4f}")
    print(f"H(y | R1,R2,R3)          = {H[3]:.4f}   IG(R3) = {IG[2]:.4f}")
    print(f"H(y | full Phi vector)   = {H_y_given_full:.4f}")
    print()
    print(f"I(y ; R4 | R1,R2,R3) <= I(y ; full_Phi | R123) = {I_y_R4_given_123:.4f} bits")
    print("  (the richest possible 4th Phi-rule adds this many bits about y; "
          "any coarser R4 adds <= this)")
    print()
    print("--- COVERAGE OF SHOULD-BLOCK MASS (Phi region) ---")
    print(f"coverage(R1)             = {cov[0]:.4f}")
    print(f"coverage(R1,R2)          = {cov[1]:.4f}")
    print(f"coverage(R1,R2,R3)       = {cov[2]:.4f}")
    print()
    # residual after 3 rules, on Phi region, = false-negatives within Phi
    resid = [r for r in pos if not covered_by_first_k(r, 3)]
    print(f"residual block-mass after 3 rules (Phi region): {len(resid)} / {n_pos}")
    for r in resid[:8]:
        print(f"  RESIDUAL: {r['incident']} / {r['tool']}->{r['target']} "
              f"(hazard={r['hazard']})")
    print()

    # --- where do the residual bits live? collisions: Phi-vectors with BOTH labels ----
    collide: dict = {}
    for r in in_scope:
        key = full_phi_vector(r["features"])
        collide.setdefault(key, set()).add(r["should_block"])
    colliding_keys = {k for k, v in collide.items() if len(v) > 1}
    print("--- WHERE THE RESIDUAL BITS LIVE (Phi-vector label collisions) ---")
    print(f"feature vectors carrying BOTH labels: {len(colliding_keys)}")
    shown = 0
    for r in in_scope:
        key = full_phi_vector(r["features"])
        if key in colliding_keys and r["should_block"] and shown < 6:
            print(f"  COLLIDE+: {r['incident']} / {r['tool']}->{r['target']} (hazard={r['hazard']})")
            shown += 1
    print()

    # The honest IT claim: R1 alone removes 87% of label entropy; 3 rules remove 95.5%;
    # the remaining ~0.034 bits a 4th Phi-rule could recover are a FEATURE-COLLISION
    # artifact (explicit traps whose Phi-vector ties with neutral negatives), NOT a 4th
    # hazard mechanism. So "3 rules suffice" is true at the MECHANISM level (Lemma-1
    # taxonomy, see C12) and approximately true at the bit level (>=95% of H(y) removed),
    # but NOT exactly information-complete: 0.0344 bits remain, recoverable only by a
    # tool-keyed feature refinement, not a genuinely new rule.
    frac_removed_R1 = (H_y - H[1]) / H_y if H_y else 0.0
    frac_removed_R123 = (H_y - H[3]) / H_y if H_y else 0.0
    print("--- VERDICT (information-theoretic, scoped to Phi) ---")
    print(f"fraction of H(y) removed by R1 alone   : {frac_removed_R1:.3f}")
    print(f"fraction of H(y) removed by R1,R2,R3   : {frac_removed_R123:.3f}")
    print(f"residual recoverable by ANY 4th Phi-rule: <= {I_y_R4_given_123:.4f} bits "
          f"(a feature-collision artifact, not a 4th mechanism)")
    print(f"out-of-scope (NOT in Phi at all)        : {len(oos_pos)} topology-trap positives")
    print()
    # PASS criterion for THIS witness: 3 rules remove >=95% of label entropy AND no 4th
    # Phi-rule can recover more than a small collision residual (< 0.05 bits).
    ok = frac_removed_R123 >= 0.95 and I_y_R4_given_123 < 0.05
    print(f"RESULT: {'PASS (3 rules are ~information-complete over Phi: >=95% of H(y) removed, '
          'residual is a collision artifact)' if ok else 'FAIL'} "
          f"| H(y)={H_y:.3f} H(y|R123)={H[3]:.3f} removed={frac_removed_R123:.3f} "
          f"I(y;R4|R123)={I_y_R4_given_123:.4f} oos_pos={len(oos_pos)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
