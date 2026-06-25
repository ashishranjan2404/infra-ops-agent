# C4 — 03 Improved Plan

## What changed after the grill

### Accepted
- **(DVO, RLE) v1->v2 collapse is primary evidence.** Add a dedicated section: v1 had 10 rules,
  held-out acc 0.872, FA-rate 0.385; v2 has 3 rules, held-out acc 0.897, FA-rate 0.308. The fix
  was removing an over-conditioned `failover_service AND leak_active` rule. This *is* the
  interpretability story — minimality pressure (`COMPLEXITY_LAMBDA`, `_SCHEMA` minimality nudge)
  collapsed an over-fit 10-rule blob into 3 legible rules.
- **(PSRE) Document divergence from the human baseline, don't claim clean 1:1.** Rule 2 blocks a
  *broader* tool set during a leak than hand-written `is_safe` (which only blocks restarts). I will
  explicitly mark each rule as "recovers / broadens / narrows" vs the human clause.
- **(SMR) Frame over-blocking as deliberate conservatism**, justified by the 2x false-allow
  reward weight, and *empirically validated* by held-out false-block-rate = 0.0.
- **(AAAI) Three explicit interpretability yardsticks**: (1) 1:1 human-clause mapping,
  (2) simulability, (3) sparsity. Score each rule on all three.
- **(PSRE, DVO) Failure modes are a top-level section**, with the 4 held-out false-allows
  classified.
- **(RLE) Provenance section**: rules are interpretable by construction.

### Rejected
- **(RLE) "Don't overstate `match_tools` brittleness".** Rejected — DVO's rebuttal (the v1
  over-conditioned rule that silently leaked) shows the brittleness is concrete and already bit
  the system once. It stays a first-class failure mode. I keep RLE's *true* observation that Rule 1
  (the load-bearing rule) is fully general (empty `match_tools`), so the brittleness is scoped to
  Rules 2/3 — I'll say exactly that rather than dropping the point.
- **(AAAI) "1:1 mapping is sufficient for interpretability".** Rejected as the *sole* criterion;
  kept as *one of three* yardsticks (per AAAI's own R2 concession that simulability subsumes it).

## Final deliverable shape
`rule_interpretability.md` with sections: TL;DR verdict -> the 3 rules verbatim -> per-rule
analysis (what / corresponds-to / why-it-helps / failure-modes / worked example) -> three
interpretability yardsticks scored -> v1->v2 collapse -> failure modes & held-out misses ->
provenance -> honest limitations. Plus `validate_rules.py` reproducing the numbers.
