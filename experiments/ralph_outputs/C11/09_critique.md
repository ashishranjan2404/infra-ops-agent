# 09 — Honest Critique

## What a reviewer attacks
1. **Accuracy is the wrong headline for a safety gate.** The dominant rule R1 looks
   important on accuracy (35.7pt) while R3 (last_ready_node) looks negligible (0.4pt) —
   but R3 prevents taking the whole cluster down. Accuracy-drop ranking buries the
   highest-SEVERITY rule. Mitigation present (the +FA column shows R3 removes real
   false-allows), but I did NOT produce a severity-weighted ranking. A real safety audit
   would weight a single last-node false-allow far above 200 forbidden-category ones.
2. **Imbalanced label set inflates the baseline.** 580 labeled actions are dominated by
   forbidden-category-style decisions (195+ blockable forbidden_category hazards), so R1
   mechanically dominates the accuracy story. The ranking partly reflects label
   composition, not just rule value. A per-hazard or per-scenario-normalized accuracy
   would be fairer and is not done here.
3. **Marginal-given-others masking.** Because is_safe is first-match-wins, R2/R3 numbers
   are lower bounds; if R1 fires first on an action that R2 would also catch, R2 gets no
   credit. I report this honestly but did not quantify the masking (would need a
   standalone-rule pass).
4. **`trap_action` hazard is not an is_safe rule.** The labels include `trap_action`
   (spec trap lists) which `is_safe` does NOT directly gate — those become structural
   false-allows of the FULL harness (the 37 baseline false-allows). So the harness's
   absolute accuracy ceiling here is < 1.0 by construction; the ablation measures
   contribution relative to that ceiling, which is the right framing but worth stating.
5. **Label source coupling.** Labels come from `labeled_examples`, authored alongside the
   harness design — not a fully independent oracle. Shared assumptions could flatter both.

## What's weak / missing
- No severity weighting; no per-scenario or per-family breakdown of where each rule earns
  its keep (would localize R2/R3 to the leak / single-node scenarios).
- R4 is untriggered, so this scenario set cannot estimate its value at all.
- No confidence intervals (deterministic single pass — defensible, but a bootstrap over
  scenarios would show how concentrated R1's contribution is in the cascade family).

## Honest bottom line
The deliverable is real, reproducible, and correctly answers the literal task (per-rule
accuracy drop via a non-core wrapper). Its main limitation is that ACCURACY under-serves
the two low-frequency, high-severity rules — a limitation I surfaced rather than hid.
