# E9 — 05 Ouroboros (3 self-critiques in sequence)

## Engineer 1 — "the schema purist"
**Problems found:**
- The reward rubric is *documented* as mirroring `rex/scoring.py` but not *verified* against
  it. If the real weights drift, my augmented rewards silently diverge. → **Fix:** pin the
  exact constants `(0.30, 0.25, 0.45, 0.60)` as named module constants with a comment citing
  the source file, and assert positive==1.0 in the self-test so any drift breaks the test.
- `state_after` for `negative_wrong_fix` and `negative_empty` are identical → a model can't
  distinguish "wrong action" from "no action." → **Accepted as known coarseness**, but the
  `action`/`label` fields differ, so the distinction is recoverable; logged, not blocking.

## Engineer 2 — "the metrics skeptic"
**Problems found:**
- `label_coverage` divides covered classes by a *hand-listed* `SRE_CLASSES` set. The raw
  scenario `root_cause.kind` strings (e.g. `cpu_starve`, `cache_flush`, `fd_exhaust`) are more
  granular / differently named than my canonical list, so coverage will read artificially LOW.
  → **Fix:** keep the metric but DOCUMENT that it measures coverage against a canonical
  vocabulary, not raw kinds; report `classes_covered` explicitly so the number is auditable,
  and call out the under-count in 07/09 instead of hiding it.
- `positive_pass_rate == 1.0` is trivially true by construction (positives are built to score
  1.0). It proves nothing about a real model. → **Fix:** keep it only as a *floor sanity*
  signal, and state plainly in 08 that it is not a model-accuracy number.

## Engineer 3 — "the fairness auditor"
**Problems found:**
- The verdict structurally favors the synthetic arm because the Fireball arm is blocked at
  zero. A naive reader sees "816 vs 0" and concludes synthetic is 816× better. → **Fix:** the
  `verdict.caveat` must say in plain words that this is a *data-quality* verdict, that the
  Fireball arm was never run end-to-end, and that a fair comparison needs both an export and a
  fine-tuning stack. (Implemented in `decide()`.)
- Off-domain claim (`domain_match=0` for D&D) is asserted, not shown. → **Accepted:** it is a
  definitional claim (FIREBALL is D&D combat; bench is k8s SRE) — defensible without an
  experiment, but flagged in 09 as an assumption a reviewer could probe.

## Final filtered spec (deltas applied)
- Reward constants pinned + asserted in self-test.
- `label_coverage` documented as canonical-vocabulary coverage; `classes_covered` surfaced;
  under-count called out honestly in test results & critique.
- `positive_pass_rate` demoted to a floor-sanity signal, explicitly not model accuracy.
- `verdict.caveat` strengthened to prevent "816 vs 0" misreading.
