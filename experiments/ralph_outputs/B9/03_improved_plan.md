# B9 — 03 Improved Plan

## What changed after the grill
1. **Added a cluster (block) bootstrap.** The original plan had only an i.i.d. bootstrap.
   SMR and REV both showed that an i.i.d. bootstrap on incident-clustered data is wrong
   in the *same direction* as Wilson and would prove nothing. The cluster bootstrap
   resamples whole incidents (5 blocks) and is now the primary robustness statistic.
2. **Stdlib-only with a hand-written, unit-tested percentile.** Per RLE+DVO, avoiding
   numpy removes the interpolation-mode ambiguity and guarantees the script runs in any
   worker env. The percentile function is explicitly tested.
3. **Assert point-estimate equality with the shipped pipeline.** Reuse `wilson_ci` and
   `binary_pass` from `experiments/compute_pass_at_k.py`; verify pass@1 matches
   `compute_pass_at_k.py` exactly (done in 07).
4. **Lead with the honesty caveat.** n=15 episodes but only 5 distinct incidents →
   effective n ≈ 5. The writeup states this up front (PSRE).

## Critiques accepted
- SMR: respect the clustering → cluster bootstrap. **Accepted.**
- REV: i.i.d.-only bootstrap is redundant with Wilson → must add cluster. **Accepted.**
- RLE: fixed seed, reuse shipped estimators, test the percentile. **Accepted.**
- DVO: stdlib only, JSON artifact. **Accepted.**

## Critiques rejected (with reason)
- REV (R1) "cut the bootstrap if it agrees with Wilson." **Rejected.** A robustness check
  that agrees is still a valid result ("Wilson holds here"); you don't delete a passing
  control. We keep all three intervals and let the divergence (or lack of it) speak.
- PSRE "the number is too fragile to bother." **Partially rejected.** We don't drop the
  analysis; instead we *report* the fragility — the wide cluster CI quantifies exactly the
  thing PSRE worried about. We do adopt PSRE's framing in the writeup.

## Final method
For each of the 5 conditions: Wilson 95% (closed form), percentile bootstrap 95% (10k,
i.i.d. over 15 episodes), cluster bootstrap 95% (10k, resample 5 incident-blocks). Report
all three + widths + bootstrap SE. Deterministic under `--seed`.
