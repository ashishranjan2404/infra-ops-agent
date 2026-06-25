#!/usr/bin/env python3
"""C12 empirical witness: does a 3-rule classifier separate the realized
trap-action space of the REx harness with zero error?

This is the runnable premise-check behind three_rules_proof.md. It enumerates the
realized (feature -> should_block) space over every loadable scenario and applies the
3 rule-schemas (R1 category, R2 fault-masking, R3 precondition-exhausted). It reports:
  - n            : labeled (action, scenario) examples
  - mismatches   : where the 3-rule classifier disagrees with the spec oracle
  - collisions   : feature vectors that appear with BOTH labels (separability disproof)
  - escapes      : positive labels (should_block=True) whose feature vector is all-false
                   for the 6 hazard features (out-of-scope explicit traps)

We re-implement the tiny matcher locally and import ONLY pure-data helpers from
rex.harness_synth so we never pull in the LLM call path. Run:
    python3 verify_three_rules.py
"""
from __future__ import annotations

import os
import sys

# make repo root importable regardless of cwd
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


# ---- the 3 rule-schemas, as pure functions over the `features` dict ----------------
def R1_category(f: dict) -> bool:
    # spanning hazard: action treats a ruled-out cause
    return bool(f.get("treats_forbidden_category"))


def R2_fault_masking(f: dict) -> bool:
    # reset/restart while the live fault is still uncapped (leak clock reset)
    return f.get("tool") in ("restart_pod", "restart_service") and bool(f.get("leak_active"))


def R3_precondition_exhausted(f: dict) -> bool:
    # the action's enabling resource/condition is exhausted -> can't help, burns margin
    return (
        bool(f.get("last_ready_node_op"))      # drain/cordon the last Ready node
        or bool(f.get("at_replica_limit"))     # scale at replica/quota cap
        or bool(f.get("rollback_without_deploy"))  # rollback with no recent deploy
    )


RULES = [("R1_category", R1_category),
         ("R2_fault_masking", R2_fault_masking),
         ("R3_precondition_exhausted", R3_precondition_exhausted)]


def classify(f: dict):
    """Return (block, firing_class_or_None). Disjunctive; class = lowest-index firing rule."""
    cls = None
    block = False
    for name, fn in RULES:
        if fn(f):
            block = True
            if cls is None:
                cls = name
    return block, cls


def hazard_feature_all_false(f: dict) -> bool:
    return not (
        f.get("treats_forbidden_category") or f.get("leak_active")
        or f.get("last_ready_node_op") or f.get("at_replica_limit")
        or f.get("rollback_without_deploy")
    )


def main() -> int:
    try:
        from rex.harness import _SCENARIOS, load_scenario  # noqa: F401
        from rex.harness_synth import labeled_examples
    except Exception as e:  # pragma: no cover - environment blocker path
        print(f"IMPORT-BLOCKED: {e}")
        print("RESULT: BLOCKED")
        return 2

    n = mismatches = escapes = 0
    seen: dict = {}          # feature-key -> set of labels (collision detector)
    collisions = 0
    bad_rows = []
    loaded, failed = [], []

    for name in sorted(_SCENARIOS):
        try:
            rows = labeled_examples(name)
        except Exception as e:
            failed.append((name, str(e)))
            continue
        loaded.append(name)
        for r in rows:
            f = r["features"]
            gold = bool(r["should_block"])
            pred, cls = classify(f)
            n += 1
            if pred != gold:
                mismatches += 1
                bad_rows.append((name, r["tool"], r["target"], r["hazard"], gold, pred, cls))
            if gold and hazard_feature_all_false(f):
                escapes += 1
            key = (f.get("tool"), f.get("treats_forbidden_category"), f.get("leak_active"),
                   f.get("last_ready_node_op"), f.get("at_replica_limit"),
                   f.get("rollback_without_deploy"))
            seen.setdefault(key, set()).add(gold)

    for key, labels in seen.items():
        if len(labels) > 1:
            collisions += 1

    print(f"scenarios loaded : {len(loaded)}")
    if failed:
        print(f"scenarios failed : {len(failed)} -> {failed[:3]}{' ...' if len(failed) > 3 else ''}")
    print(f"examples (n)     : {n}")
    print(f"mismatches       : {mismatches}")
    print(f"collisions       : {collisions}  (feature vectors carrying BOTH labels)")
    print(f"out-of-scope     : {escapes}  (block-labels with all-false hazard features)")
    if bad_rows:
        print("\n-- mismatched rows (first 15) --")
        for row in bad_rows[:15]:
            print("  ", row)

    ok = (mismatches == 0 and collisions == 0 and escapes == 0)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} "
          f"n={n} mismatches={mismatches} collisions={collisions} escapes={escapes}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
