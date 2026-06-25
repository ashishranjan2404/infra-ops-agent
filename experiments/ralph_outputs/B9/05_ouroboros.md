# B9 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "Statistician"
**Problems found:**
1. A percentile bootstrap on a proportion with 0 successes (zero_shot, retry_realistic,
   rex_no_oracle) is **degenerate** — every resample yields 0, so the CI is `[0,0]`. That
   is *narrower* than Wilson `[0,0.204]` and is statistically WRONG (true coverage ≈ 0).
   The script must not present `[0,0]` as if it were a real interval.
2. SE reported as 0 for degenerate cases — fine, but the writeup must flag that bootstrap
   fails at the boundary (the "0/n problem"), which is precisely where Wilson is *better*.
3. `n_blocks` resampling keeps block count fixed but block size is uniform (3) here; if
   seeds varied per incident the flat length would vary. OK for this data, document it.

**Resolution:** Keep `[0,0]` in the JSON (it's the honest bootstrap output) but the docs
(08/09) must explicitly call out the 0/n boundary failure and conclude *Wilson is the
right default; bootstrap is a cross-check*, not a replacement.

## Engineer B — "Reproducibility/Tooling"
**Problems found:**
1. `REPO = parents[N]` is brittle — I miscounted once already (parents[3] vs [4]). A wrong
   index silently points at the wrong file. → Mitigated: the script fails loudly with
   `FileNotFoundError` (it did, and was fixed), and `--data` lets you override.
2. Importing from `experiments/compute_pass_at_k.py` mutates `sys.path`. If that import
   fails the fallback must be *identical* math or the comparison is invalid. → The test
   asserts `WILSON_CI` matches the hand formula (case 7).
3. No assertion that bootstrap pass@1 == shipped pass@1. → Verified in 07 by diffing
   against `compute_pass_at_k.py` output (both give rex=0.400, etc.).

## Engineer C — "Skeptical Reviewer"
**Problems found:**
1. **Over-claiming risk.** With only 5 incidents, ALL three intervals are weak. The
   deliverable must not imply the bootstrap "fixes" anything — it only *reveals* that the
   tight Wilson interval on rex (`[0.198,0.643]`) hides incident-level all-or-nothing
   behavior (cluster CI `[0,0.8]`). State plainly.
2. **Is the cluster bootstrap even the right model?** Resampling incidents treats the 5
   incidents as a sample from a population of incidents — defensible for "will REx
   generalize to new incidents?", which is the actual research question. Good, but say so.
3. Missing: comparison of *widths*. Added `*_width` fields so the divergence is one glance.

## Final filtered spec (deltas applied)
- Keep degenerate `[0,0]` outputs but document the 0/n boundary failure (Eng A).
- `--data` override + loud failure + Wilson-match test (Eng B).
- Add width fields; frame cluster bootstrap as the "new-incident generalization" question;
  no over-claiming (Eng C). Lead findings with the honesty caveat.
