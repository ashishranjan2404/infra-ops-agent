# I3 — Improved plan (post-grill)

## What changed
1. **Engine swapped to vetted `diptest` (AS 217).** My first hand-rolled GCM/LCM
   statistic returned D≈0.16 for a Gaussian (should be ~0.02) — exactly the bug
   MLR/REV warned about. The whole-support GCM-to-ECDF gap is NOT the dip; the
   correct AS 217 modal-interval recursion is. Rather than ship a subtly-wrong
   recursion, use the packaged C routine as the source of truth, keep numpy as a
   labelled fallback only.
2. **Validation gate added (REV).** `test_dip_test.py` now asserts D<0.05 & p>0.05
   for a Gaussian and D>0.1 & p<0.01 for a two-spike sample. The analysis is only
   trusted because these pass.
3. **Headline reframed (RLE+SRE).** Not "rewards are bimodal" but: *weak policies
   (zero_shot/best_of_n/retry/rex_no_oracle) are bimodal; REx is unimodal because
   it collapses the lower (failure) mode toward reward 1.0.* This is the
   falsifiable, more interesting claim — and it held.
4. **Pole masses reported (MLR).** Each result carries frac(<=0.1), frac(>=0.9),
   frac(mid) so a reader sees the 0/1 structure directly.
5. **Pooled flagged as mixed-population (RLE).** Reported but interpreted as the
   mixture of high- and low-mean policies, not as within-policy structure.
6. **Provenance pinned (DVO).** JSON records engine "diptest v0.11 (AS 217)", null
   "Uniform(0,1)", alpha 0.05.

## Critiques accepted
- Hand-rolled stat is untrustworthy for non-uniform unimodal → use package. (MLR)
- Gate on Gaussian sanity. (REV)
- Per-condition is the real story; pooled is a mixture artifact. (RLE)
- Report pole masses. (MLR)

## Critiques rejected (and why)
- "Drop rex/runs (n=12) entirely" — REJECTED. It is real committed rollout data;
  I report it but explicitly flag the small n rather than hide it.
- "Reward atoms make the dip test invalid" — REJECTED. The dip test makes no
  continuity assumption; ties are fine. The atoms are WHY it's bimodal, which we
  surface via pole masses, not a reason to abandon the test.
