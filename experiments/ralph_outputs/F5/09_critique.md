# F5 — Critique (honest)

## What a reviewer attacks
1. **"You cite 0.90 vs 0.95 verifier accuracy but only re-verified the 7/3/3 structure,
   not the accuracy itself."** True. The accuracy is on the authority of
   `headline_insights.md` §2; I did not re-run `harness_synth` to recompute it (out of
   scope for an abstract task, and it needs the eval harness). If that doc is stale, the
   abstract inherits the staleness. Mitigation: I wrote "roughly 0.90" and "approaching
   hand-written," which survive small drift.

2. **"The abstract reports a single-model ablation."** `ablation.json` is
   `claude-haiku-4-5`, N=4, 3 seeds, 5 incidents. The 0.69/0.24/0.25 spread is real but
   narrow (one model, five incidents). The abstract does not claim cross-model generality
   for these numbers — but a reviewer will note the n. The outline's cross-model spanning
   set (§4) would broaden this; it is not yet in a JSON I could cite, so I left it out.
   This is the honest cost of not over-claiming.

3. **"42-incident benchmark, but you evaluate on 5."** Correct, and I deliberately phrased
   the benchmark as something we *build/release* (design: 12/20/10) while the cited
   results live on a smaller measured subset. A skeptic could still read the juxtaposition
   as implying 42 were run. This is the single sharpest residual ambiguity in the abstract;
   I judged the phrasing acceptable but it is the first thing I'd tighten with a 251st word.

4. **"By foregrounding the oracle-leakage negative, you undercut your own method."** The
   AAAI Reviewer persona (02_grill) made exactly this objection and I overruled it. It is
   a genuine strategic bet: I believe the honesty earns more credibility than it costs,
   but a hostile reviewer could read it as "the loop doesn't work, why is this a paper."
   The defense is that the paper's contribution is the verifiable env + learned verifier,
   which the negative *strengthens*, not the loop.

## What's weak / missing
- No comparison to SREGym / AIOpsLab numbers in the abstract (related-work positioning is
  in §2; an abstract arguably should name the closest competitor). Omitted for word budget.
- The deterministic-reward "credit-free / reproducible" benefit is asserted, not shown, at
  abstract altitude — appropriate for an abstract, but it's a promissory note to §3.4.
- C2 transfer (a stated *three-claim* paper) is entirely absent from the abstract. If C2
  lands before submission, the abstract must be revised to restore the three-claim spine;
  right now it honestly reads as a two-contribution paper.

## Blocked / negative results (stated plainly)
Nothing was *blocked* — this is a pure writing task with no cluster/API/GPU dependency.
The honest negative is structural: the strongest version of this abstract (all three
claims, cross-model, full 42-incident, McNemar-significant) cannot yet be written because
those results are pending in the repo. I wrote the strongest *defensible* abstract instead.
