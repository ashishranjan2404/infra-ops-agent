# D10 — 09 Critique (honest)

## What a reviewer will attack

1. **"It's not real RFT."** Correct, and the biggest weakness. We ran the reward function,
   not a policy-gradient loop. There is no learned policy, no advantage estimation over real
   model samples, no training curve. Defense: a weight sweep's *entire effect* is on the
   reward/ranking, which is what we measured over real sim rollouts — but a skeptic is right
   that we cannot show downstream *learning* changed without the GPU loop. Honest blocker.

2. **Synthetic rollout bank.** The candidate plans are hand-designed, not sampled from a
   model. So the rollout *distribution* is artificial. The argmax flips we report are real but
   come from a curated candidate set — the flip rate (2.4%) is not an estimate of what a real
   policy's rollouts would show. A real model would produce messier, partial-credit plans where
   re-weighting could move rankings much more (or less). We over-claim if we read 2.4% as a
   population statistic; it is a *lower-bound existence proof* that re-weighting reorders.

3. **Kendall tau deflated by ties.** Many candidates score exactly 0.0 (empty / wrong-diag /
   blocked-trap). Tau-a counts those pairs in the denominator, so tau understates ranking
   preservation. We mitigated by leaning on argmax-flip as the headline, but the tau column
   should be read directionally, not absolutely.

4. **Spread is always 1.0.** Because every scenario contains a `correct_full` (→1.0) and an
   `empty`/`trap` (→0.0), the *global* spread is pinned at 1.0 for every weighting — so the
   spread column is uninformative here. The trainability-relevant quantity is the *within-group*
   spread per scenario, which we did not aggregate separately. A genuine gap; the global spread
   metric is near-useless as built and should be replaced with mean per-scenario std.

5. **Only 8 weightings.** A defensible bracket, but not a systematic 4-D sweep. We can't draw a
   response surface or find the trainability-optimal weighting — only show *that* re-weighting
   reorders.

## What's missing
- Per-scenario within-group reward std (the real RFT trainability signal) — only global spread.
- Rollouts from an actual model (would make the flip-rate meaningful).
- The actual GRPO update + a downstream pass@k delta per weighting.

## What's genuinely solid
- Non-invasive, selftest-proven equivalence to core scoring — numbers are trustworthy.
- Real sim execution of every rollout (resolved/trap are observed, not asserted).
- Falsifiable design that actually fired: `no_trap_penalty` and `resolution_only` reorder the
  argmax, proving the trap penalty and resolution weight are load-bearing for ranking.
