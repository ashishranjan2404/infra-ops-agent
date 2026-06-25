# 09 — Critique (honest)

## What a reviewer attacks
1. **No CI on the effect sizes.** I report point-estimate d and h with no interval. A
   reviewer rightly asks for a bootstrap or analytic CI on d/h itself. The source JSONs
   carry Wilson CIs on pass@1, but I did not propagate them into the effect-size layer.
   This is the biggest gap. (Deferred per scope; flagged here.)
2. **Pooled-SD equal-variance assumption is violated.** rex reward std (~0.17–0.22) vs
   zero_shot (~0.37–0.38). Pooled Cohen's d is then mildly optimistic. I report both group
   counts and surface the SDs upstream, but I kept pooled d as the headline rather than
   switching to Glass's Δ. A purist would want Glass's Δ or Hedges' g (small-sample
   bias-corrected) shown alongside. Hedges' g would be a cheap, defensible addition.
3. **Overall-only, not per-family.** The pooled n=126/150 effect size can be dominated by
   one incident family (the "simple" family is near-ceiling for several conditions). A
   pooled d=1.7 does NOT mean REx is large on the *novel* family — that needs a per-family
   cut, which B8 deliberately did not do. Risk of over-reading the headline.
4. **The pass@1 → h uses pooled per-condition proportion**, which mixes seeds and incidents.
   That is the right object for "the claimed overall lift", but it ignores within-incident
   correlation across seeds — the effective n is smaller than 126/150, so even h's implicit
   precision is overstated.
5. **Reward distribution is non-normal and clumpy** (discrete spikes at 0.0/0.25/0.55/1.0).
   Cohen's d's interpretability leans on roughly normal data; on a lumpy bounded scale the
   "standard deviations of separation" framing is approximate.

## What's weak / missing
- Only 2 model files were available with the full `by_condition.overall` shape; a fuller
  sweep (more models) would strengthen the generality of "only REx is large".
- No comparison of REx vs the *strongest* non-trivial baseline (best_of_n) — I measured all
  lifts vs zero_shot. The more honest contrastive claim is REx-vs-best_of_n; the tool
  supports `--baseline best_of_n` but the report uses zero_shot.

## Honest bottom line
The machinery is correct and unit-verified, and the headline finding (REx = large effect,
the cheaper conditions = small/negligible) is real and reproducible. But the deliverable is
a *point-estimate, overall, pooled-d/h* summary; the defensible-paper version still needs
CIs, Hedges' g, a per-family cut, and a REx-vs-best_of_n contrast. None of those are faked
— they are scoped out and named.
