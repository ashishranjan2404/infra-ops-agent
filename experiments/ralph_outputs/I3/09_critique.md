# I3 — Honest critique

## What a reviewer will attack
1. **Discrete reward atoms.** Rewards live on ~6 atoms (0, 0.3, 0.4, 0.45, 0.75,
   1.0). The dip test is valid for ties, but with mass concentrated on a 0-atom and
   a 1-atom, a high dip is almost mechanical for any policy with non-trivial
   failure rate. The test confirms what the pole masses already show; it adds rigor
   (a p-value), not a surprise. I report pole masses precisely so this is transparent.
2. **REx "unimodal" is a degenerate spike, not a bell.** REx is unimodal only in
   the sense of "one big atom at 1.0" (frac_high≈0.90). The dip test correctly does
   not reject unimodality, but a reviewer could argue the more honest statement is
   "REx is near-degenerate at the ceiling," which is a *ceiling/saturation* concern
   for the benchmark (little headroom), not evidence of a nice distribution.
3. **Within-condition independence.** The 126/150 episodes are 3-5 seeds across
   ~33-42 incidents. Rewards for the same incident across seeds are correlated, so
   the effective n is smaller than the nominal n. The dip p-values assume iid; the
   true p is somewhat larger. Given p<1e-4 with margin, the conclusion likely
   survives, but I did not compute a cluster-robust / per-incident-block version.
4. **`diptest` p=0.0.** The analytic interpolation returns exactly 0.0 for large D.
   That is "p below the table's resolution," not a literal zero; reported as <1e-4.
5. **Two models only.** A1 (glm-5p2) and A2 (deepseek-v4-pro) agree, which is
   reassuring, but it's n=2 model families. Not a population of models.

## What's weak / missing
- No GMM/BIC or Silverman bandwidth-test cross-check; the dip test is the only lens.
- No formal modality *count* (the dip test is unimodal-vs-not, not "how many
  modes"). The pooled distribution is plausibly tri-modal (0, mid, 1) but I only
  report rejection of unimodality.
- The iid caveat (3) is acknowledged but not corrected for.

## Honest bottom line
The headline finding is real and consistent across two models: weak policies are
bimodal (pass/fail), REx collapses the failure mode to a near-degenerate spike at
reward 1.0 and is statistically unimodal. The main honest caveats are the discrete-
atom mechanics, the seed-correlation (effective-n) issue, and that REx's
"unimodality" is ceiling saturation rather than a well-shaped distribution.
