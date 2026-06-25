# B13 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer 1 — correctness of the statistics

**Problems found.**
- Cohen's kappa degenerate case: if both raters are constant and equal, P_e=1 and the
  formula is 0/0. Original draft would have raised ZeroDivisionError. FIX: explicit branch
  returning 1.0 (agree) / 0.0 (disagree). Covered by `test_degenerate_constant_raters`.
- Krippendorff's alpha with the coincidence-matrix formula is the part most likely to be
  subtly wrong (the 1/(m_u-1) weighting and the (n_total-1) in D_e). FIX: pinned with a
  perfect-agreement test, a missing-data test, and a partial-disagreement bound test. Also
  hand-checked Cohen against a textbook 2x2 (`test_known_cohen_kappa_value`).
- Unverified: I did NOT cross-check Krippendorff against an external library (no numpy/
  krippendorff package installed). Mitigation: nominal-metric alpha equals a known
  transform of observed/expected disagreement; perfect+missing cases match by hand. Flagged
  as residual risk in 09.

## Engineer 2 — does the worksheet measure the right thing?

**Problems found.**
- The synthetic candidate panel is "easy": gold paraphrase = obvious CORRECT, generic =
  obvious WRONG. Human kappa on THIS set will be inflated and won't stress the judge's
  borderline behavior (the cases that actually matter for the 30% reward term). This is a
  real limitation: the worksheet proves the pipeline, not the judge's hard cases. FIX
  (documented, not auto-generated to stay deterministic/no-LLM): 04 protocol says to add
  real model-generated stated_causes (from `rex.eval_pass_at_k` traces) as additional
  worksheet rows when running for real — those are the contestable episodes.
- `provenance=gold` rows use the gold string verbatim as the stated_cause, so they aren't
  really "annotations a model produced". Acknowledged: these are calibration anchors
  (sanity rows), the protocol notes to mix in real traces for the substantive test.

## Engineer 3 — robustness / over- vs under-engineering

**Problems found.**
- Over-engineering risk: Fleiss AND Krippendorff AND mean-pairwise Cohen for a study with
  zero current labels. Justified? KEEP — the marginal cost is ~40 lines and tested, and it
  removes the "we'd have to write more code when labels arrive" friction. Under-engineering
  would re-block the next worker.
- Under-engineering: no CLI flag to subsample scenarios; worksheet emits all 42 x 3 = 126
  rows. For 126 episodes that's fine for humans; no flag needed. Accepted as-is.
- Path fragility: `build_worksheet.py` computes REPO via `../../../..`. If the file moves,
  imports break. Mitigation: it also `sys.path.insert`s the repo + experiments; verified to
  run from its own directory (07). Documented that it must run from the artifacts dir.

## Final filtered spec deltas
- Keep the degenerate-kappa branch + all tests (E1).
- Document the easy-panel limitation and the "mix in real traces" extension in the
  protocol (E2) — do NOT fabricate model traces here (stays deterministic).
- Keep the full multi-rater library; document the run-from-artifacts-dir requirement (E3).
- Residual unverified item (no external Krippendorff cross-check) carried to 09.
