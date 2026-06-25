# C12 — Step 6: Implementation

## Artifacts created (all task-namespaced; NO shared core file edited)

1. **`artifacts/three_rules_proof.md`** — the deliverable: an information-theoretic /
   VC-style argument for why 3 rules suffice to cover the trap-action space. Contains:
   - Setup/notation grounded in `rex/harness.py` (`is_safe`, `TOOL_TREATS`) and
     `rex/harness_synth.py` (`features`, `ground_truth`, `FEATURES`).
   - Assumptions A1–A5 stated up front.
   - **Lemma 1 (PROVEN):** the Φ-expressible hazard space has exactly 3 mechanism
     classes (wrong-diagnosis / fault-masking / margin-destruction), by full enumeration
     of the positive branches of `ground_truth`.
   - **Proposition 2 (EMPIRICALLY VERIFIED):** 3 rules realize the label on 99.6% of the
     feature-expressible realized set; the 2 residual errors are a characterized feature
     collision (correct rollback with no deploy event).
   - **Information-theoretic core:** `I(y ; R₄ | c) = 0` — a 4th rule over Φ carries
     zero conditional information; 3 rules saturate Φ.
   - An honest negative-result section (§7) and 4 explicit limits (§9).

2. **`artifacts/verify_three_rules.py`** — runnable empirical witness. Re-implements the
   3 rule-schemas as pure functions over the `features` dict (R1 category, R2
   fault-masking, R3 precondition-exhausted), enumerates the realized trap space across
   every loadable scenario via `rex.harness_synth.labeled_examples`, and reports
   mismatches, feature collisions, and out-of-scope (topology) escapes. Imports ONLY
   pure-data helpers (`load_scenario`, `_SCENARIOS`, `labeled_examples`) to avoid the
   LLM call path; degrades to `RESULT: BLOCKED` if imports fail.

## Design decisions
- Counted rule *schemas* (3) but disclosed the 5-conjunction expansion (DOL's grill
  point) — no hidden complexity.
- The verifier is deliberately self-contained and does not import `is_safe_synth`
  (which pulls `agent.llm.call`), per Ouroboros P5.
- The proof was REWRITTEN after the witness returned a mixed result: rather than fake a
  PASS, the doc now proves the genuinely-true thing (3 *mechanism classes* / Φ-saturation)
  and reports the topology-trap and rollback-collision failures honestly.

## Shared-core safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, or any other
task's directory. The proof *describes* the existing `is_safe` decomposition; it does
not modify it. Everything lives under `experiments/ralph_outputs/C12/`.
