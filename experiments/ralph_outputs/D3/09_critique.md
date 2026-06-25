# D3 — 09 Critique (honest)

## Where a reviewer will attack

1. **No end-to-end training evidence.** The strongest possible result — "v3 same-scenario groups
   make the GRPO reward curve climb where the flat v2 baseline (0.522→0.491) did not" — is exactly
   what we did NOT run. We proved the *mechanism*, not the *outcome*. A skeptical AAAI reviewer is
   entirely right to say "show me the learning curve." This is the central weakness, and it's a
   genuine blocker (compute cap + Tinker endpoint + forked-slug + credits), not laziness.

2. **The demo is synthetic.** Numbers are grounded in v2's logged mean (~0.5) and within-spread
   (~0.17), but the per-scenario difficulty spread `[0.2..0.8]` is assumed, not measured from the
   real per-scenario reward means (those weren't broken out in the v2 log we have). The
   *reduction_factor* magnitude (2.38x) is therefore illustrative; only its **sign and structure**
   (between-term removed, signs corrected) are guaranteed by the math.

3. **`E[A^2]` ≠ gradient variance, strictly.** As flagged in 05-pass-2, we report the advantage
   second moment as a proxy upper bound holding `∇logπ` fixed. If `∇logπ` is correlated with the
   between-scenario term, the true gradient-variance reduction could be smaller (or, less likely,
   larger). Defensible but not airtight.

4. **Positional re-chunking risk in `trainer.step`.** The driver concatenates per-scenario blocks
   and calls one `trainer.step(group_size=G)`. If HUD chunks by position AND a scenario returns a
   ragged count (timeout dropped a rollout), a group could straddle a boundary — silently
   re-mixing. We add a pre-step sanity grouping + assert and document a robust per-scenario
   `trainer.step` fallback, but confirming HUD's exact `step` contract needs the live trainer.

5. **Maybe a phantom bug.** Per RLE in the grill: HUD may already group within-task internally.
   If so, v3 is an explicit no-op (zero downside, but no gain). We honestly cannot confirm or deny
   without the live trainer; we reframed the claim to "guarantees the invariant" to stay truthful.

6. **Necessary-not-sufficient.** Same-scenario grouping does nothing for degenerate (flat) groups.
   The flat baseline is plausibly a *combination* of this fix + the graded-reward fix (v2's
   `hud_env_v2`) + more tasks. D3 isolates ONE of three confounded levers; attributing the cure to
   it alone would be wrong, and we don't.

## What's genuinely solid
- The total-variance decomposition is exact and unit-tested (invariant holds to 6 dp).
- The sign-corruption test is concrete and damning for mixed baselining (28% of gradients wrong-way).
- The v3 driver is a real, minimal, drop-in change with the diff documented for core fold-back.

## If I had more compute
Fork `Qwen/Qwen3-8B`, run v2 (mixed) vs v3 (same-scenario) for 30 steps each on tasks 0-9, G=6,
identical seed, and plot mean_reward + the logged `cross_scenario_spread_removed`. That A/B is the
missing evidence and is the natural next task.
