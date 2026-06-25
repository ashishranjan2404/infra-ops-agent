# A10 — 09 Critique (honest)

## What's weak
1. **Tier label has low discriminative power on this data.** Because every scenario's
   root cause reaches its *entire* topology (`mean affected == mean topo size`), the
   blast count is fully determined by topology size, and 24/33 land SEV1. The "blast
   radius" doesn't separate incidents *within* a topology size — there is no scenario
   here where the fault reaches only part of the graph. So the metric is honest but
   coarse on the current scenario set.

2. **Blast set ≈ topology by construction.** The generator appears to always place the
   root cause at a sink dependency that everything else transitively calls. A reviewer
   could argue the "blast radius" is therefore just `total_services` and adds little
   new information for *these* scenarios. It would become meaningful only on richer
   topologies with partial-impact faults.

3. **No use of edge `weight`/`retry`/`type` beyond `required`.** I treated all edges
   as hard propagation. A weighted/probabilistic blast model (e.g. impact attenuates
   with weight, or `optional` edges don't propagate) would be more realistic but all
   present edges are `required` so it wouldn't change current numbers.

4. **Severity floats are uniform (~0.7).** The `sev>=0.9 & cascade` SEV1 branch
   essentially never fires on this data (only gitlab at 0.8 is above the pack), so the
   tier is driven almost entirely by count.

## What a reviewer attacks
- "Your blast radius equals topology size — what does it add?" → Fair for *this* set;
  the value is the *mechanism* (correct directional propagation + sidecar plumbing)
  that pays off when topologies grow / faults become partial. I'd note this explicitly.
- "Tiers are arbitrary thresholds." → True; mitigated by shipping raw counts + pct so
  consumers can re-tier.

## What's missing / would strengthen it
- A scenario with a *partial* blast (fault in a leaf with few callers) to prove the
  metric varies independently of topology size.
- Cross-check against the `slo` monitored-node set as a *report* (not assertion).
- Join the sidecar into pass@k / curriculum tooling to show downstream use.

## Honest status
Deliverable is real, correct, tested, and runnable. Its analytical *payoff* is
limited by the current scenario generator always producing full-graph blasts —
a property of the data, which I report rather than hide.
