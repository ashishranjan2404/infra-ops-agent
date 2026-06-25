# G5 — 03 Improved Plan

## What changed after the grill

**Accepted critiques:**
- **(PS, DL) Category honesty header.** The matrix now opens with a "what category is each thing"
  banner: us/SREGym = research substrate (benchmark/data); Komodor/Datadog = deployed SaaS. No
  single overall "winner" claim.
- **(PS, DL) Footnote the trap.** The trap-action-safety cell for us explicitly says the penalty
  is *modeled in a deterministic sim + a GKE test cluster*, NOT observed under live prod chaos.
- **(AR) Concede eval scale.** Evaluation-rigor row splits into two honest sub-claims: *what* is
  graded (we win: root-cause + trap, not "came back up") vs *how much / external benchmark*
  (SREGym wins: 90 problems, many agent/model pairs, reported 38.9–72.6% diagnosis).
- **(AR) Every competitor cell sourced + flagged.** Added a `vendor-stated/unverified` tag for
  marketing numbers (Komodor 95% accuracy, 40% ticket cut; Datadog 2,000 environments).
- **(RLE) Training-method row promoted** as the axis where we are uniquely first; phrased as fact
  (frozen policy → reward-shaped trajectories w/ within-group spread), not as a swipe.

**Rejected critiques (with reason):**
- **(RLE, implicitly) "lead with we're first everywhere."** Rejected — overclaiming is the one
  failure mode that kills the deliverable's value. We lead with category honesty, not a victory lap.
- **(PS) "make 'we don't ship' its own row."** Rejected as redundant — "deployment posture" already
  carries it; a separate row would double-count and read as self-flagellation rather than analysis.
  Instead the deployment-posture cell states plainly we are not deployed.

## Final shape
1. Header: category disclaimer + as-of dates.
2. The 5×4 matrix.
3. Per-dimension prose (1 short para each) with citations.
4. "Where our position is honestly weaker" subsection (no real customers, tiny n, modeled trap,
   clean-signal sim, self-grading judge).
5. Sources block + `sources.json` + `validate_matrix.py`.

## Success criteria (unchanged + tightened)
- No cell claims superiority over a deployed product on a shared public benchmark (none exists).
- Validator passes: every matrix cell carries a `[Sn]` citation tag resolving to `sources.json`.
