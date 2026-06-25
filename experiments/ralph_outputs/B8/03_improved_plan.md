# 03 — Improved Plan

## What changed after the grill
1. **Dual measure, explicit.** Cohen's **h** for `pass@1` proportions, Cohen's **d** for
   `mean_reward`. Both emitted per lift, never conflated. (Accepted: SMR, RLE.)
2. **Report n and both group SDs / baseline on every row** so unequal-variance and power
   are visible without changing the estimator. (Accepted: AAAI, SMR.)
3. **Headline stays pooled-SD Cohen's d.** Rejected RLE's Glass's-Δ swap — for an
   effect-size *summary* (not a test) pooled d is conventional and reproducible, and
   switching to chase the variance ratio is over-engineering for B8's scope. We instead
   *surface* both SDs.
4. **Overall lifts only**, with a loud "not per-family" caveat in SUMMARY. (Accepted scope
   bound from AAAI; rejected PSRE's request to build per-family into B8 — out of scope, it
   is A-series slice work.)
5. **`--selftest` + pytest** with hand-computed known values. (Accepted: DVO.)

## Critiques rejected and why
- *Glass's Δ instead of pooled d* (RLE): rejected — over-engineering; report both SDs instead.
- *Per-family breakdown inside B8* (PSRE): rejected — scope creep; deferred, caveat added.
- *Build CIs on the effect sizes* (AAAI implied): deferred to limitations — source JSONs
  already carry Wilson CIs on the underlying pass@1; bootstrap CI on d/h is future work.

## Final deliverable shape
`effect_size.py` (lib+CLI) + `test_effect_size.py` + `effect_size_report.json` on the two
real result files, with magnitude labels and a SUMMARY that states the baseline, n, and the
overall-only caveat.
