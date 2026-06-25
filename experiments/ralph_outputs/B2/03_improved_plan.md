# B2 — Step 3: Improved Plan

## What changed after the grill

### Accepted critiques
1. **Exact binomial, not chi-square** (SR, REV). Discordant counts in the novel family
   are as low as 1-2; asymptotic chi-square is invalid there. We compute the exact
   two-sided binomial p via `math.comb`; chi2_cc is reported only as a secondary column.
2. **Holm-Bonferroni multiple-comparison correction** (REV). With 10 pairs per family we
   would otherwise p-hack. We report `p_exact` (raw), `p_holm` (corrected), and two flags
   `significant_raw` / `significant_holm`. This directly answers the reviewer's rejection.
3. **Always surface `n_discordant`** (REV). Underpowered cells (e.g. n_disc=1 where the
   minimum achievable two-sided p is 1.0) are visible, so "not significant" there is read
   correctly as "underpowered," not "no effect."
4. **No hardcoded seeds/threshold/conditions** (RLE). Everything is read from the file;
   the tool works on A1 (3 seeds, 42 inc) and A2 (5 seeds, 30 inc) unchanged.
5. **Alignment proof** (RLE). A unit test asserts the flattened bit vector order on a known
   synthetic; incident-major + seed-index iteration guarantees identical pairing.
6. **`--threshold` override** (SRE). Lets a reviewer probe the 0.8 reward "cliff" sensitivity
   without editing code.
7. **Significance never affects exit code** (DO). Exit 2 only on structurally broken input
   (missing `by_condition`, missing incident); significance is reporting-only.

### Rejected critiques (and why)
- **SRE: "binarization throws away magnitude, so add a paired t/Wilcoxon on rewards."**
  Rejected for B2 scope. McNemar is explicitly the *paired companion to pass@k*, the paper's
  headline metric, which is itself a threshold-at-0.8 binary. Testing a different quantity
  (mean reward) would be a different claim. We address the underlying worry instead via the
  `--threshold` knob (cheap) rather than a whole second statistical pipeline (scope creep).
- **DO: "hard-fail in CI on any missing condition."** Partially rejected. We surface a clear
  KeyError with the missing incident/condition name and exit 2 on broken structure, but we do
  not treat a legitimately partial result as catastrophic beyond a clear error — RLE's point.

## Final shape
Single stdlib `mcnemar.py` + `test_mcnemar.py`. Run on A1 and A2 cached pass@k JSONs,
cross-validate rex-vs-control discordant counts against A2's existing mcnemar artifact,
emit `mcnemar_pairwise_report.json`, and report which pairs survive Holm correction.
