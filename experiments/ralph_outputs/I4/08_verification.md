# I4 — Verification against success criteria

## Success criteria (from 01_plan / 03_improved_plan)
1. **Witness runs clean over the real 42 scenarios, prints real entropy/coverage numbers.**
   ✓ `entropy_witness.py` loads 42/42 scenarios, 580 examples, exit 0. Numbers are computed
   from `ground_truth`, not hardcoded.
2. **The doc derives "3 rules suffice" from those numbers, scoped to Φ, residual named/quantified.**
   ✓ `three_rules_information_argument.md` §3–§6: every claim cites a measured bit value;
   the 0.0344-bit collision residual and 35 topology-trap positives are both named and located.
3. **Honest about argument vs proof.** ✓ §7 has an explicit table: Lemma 1 PROVEN (C12),
   entropy decomposition MEASURED, universal sufficiency NOT CLAIMED / FALSE out of scope.
4. **Builds on C12, does not duplicate.** ✓ I4 reuses C12's rule-schemas but contributes the
   *measured* entropy decomposition that C12 only asserted (its §6 said `I(y;R4|c)=0`; I4
   measures it at 0.0344 and shows why). The two compose: C12 = mechanism proof, I4 = bit budget.
5. **No shared core file edited.** ✓ `git status` shows only `?? experiments/ralph_outputs/I4/`.
   `rex/harness.py` and `rex/harness_synth.py` are imported read-only.

## Are the outputs real (not placeholder)?
- Entropy values are produced by `_entropy`/`_cond_entropy` on the actual label distribution;
  re-running is deterministic and reproduces them (T6).
- The residual rows (`oom_kill / clear_cache`, the `rollback` collision on three cascades) are
  pulled live from the data, not invented — they match the structural story (Φ can't see
  topology / rollback-target provenance).
- The MI ceiling 0.0344 = `H(y|R123) − H(y|full_Φ)` = `0.0433 − 0.0089`, arithmetic checks.

## Honest gaps (carried to 09)
- The claim is over the *realized* set (A5), not a generalization bound.
- "≤ 0.0344 bits" is a ceiling on *any* Φ-rule, not the value of a specific writable R4.
- Entropy ≠ safety (direction-symmetric); coverage + C12's accuracy cover the safety side.

## Verdict: meets all five success criteria; outputs real and reproducible.
