# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — correctness / edge cases
**Problems found:**
- Tie-breaking: if two categories score equally, returning the first by dict order
  would be arbitrary and category-order-dependent. -> FIXED: ties resolve to
  "unknown" (`winners` length check), removing order sensitivity.
- Empty/whitespace answer must not crash and must be "unknown". -> covered by
  `if not toks: return "unknown"` and a test.
- A record with neither `true_category` nor `root_cause_kind` must be skipped, not
  counted as wrong (that would deflate accuracy with unlabeled data). -> FIXED:
  `if not gold: continue`, plus `test_skips_records_without_gold`.

## Engineer B — measurement validity / circularity
**Problems found:**
- Is the accuracy meaningful or circular? The gold (`true_category`) is fixed in
  the YAML before any model ran; the classifier only reads the model's `answer`.
  No leakage. Validated by feeding GOLD descriptions through the classifier
  (YAML self-test) -> 0.875, an upper bound that confirms the classifier+mapping
  are sound and the low real-data number is the model's, not the metric's bug.
- Decoupling could be vacuous if `reward` were just a function of diagnosis. It is
  not: reward also includes fix + resolved + traps. The 43.1% disagreement on real
  data is therefore genuine signal. Kept and surfaced.

## Engineer C — over/under-engineering
**Problems found:**
- Over-engineering risk: no need for a learned classifier or sklearn dependency —
  dropped per the grill. Under-engineering risk: a bare scalar would hide failure
  modes -> confusion matrix added. Balance is right.
- The `_stems` import could fail if run outside the repo; that would silently
  change tokenization. -> ADDED a guarded fallback stemmer so the module is
  self-contained, with a comment that the primary path is `rex.scoring._stems`.

## Final filtered spec changes
1. Ties -> "unknown" (no dict-order dependence).
2. Unlabeled records skipped, not penalized.
3. Guarded `_stems` import fallback.
4. YAML gold-description self-test retained as the validity upper-bound check.
No further changes; spec frozen.
