# A10 — 03 Improved Plan

## What changed after the grill
1. **Propagation direction made explicit & validated** (PSRE, REV). Edges are
   "from depends on to"; faults flow to callers ⇒ reverse BFS (`to → from`).
   I hand-checked slack-consul-cache-db: root `consul-agent`, edges
   `ingress-gw→consul-agent`, `cache-ring→ingress-gw`, `vitess-db→ingress-gw`
   ⇒ reverse closure = all 4 nodes. The script must reproduce that.
2. **Tier formula combines signals** (REV + DOL accepted): SEV1 if `>=4` affected
   OR (`sev>=0.9` and cascade); SEV2 if `>=2` or cascade; SEV3 otherwise. Count
   alone rejected.
3. **SLO node set reported but NOT asserted equal to blast set** (SMR accepted
   over PSRE). SLO lists monitored nodes; blast lists impacted nodes. Different.
   I include `total_services` and `services_affected_pct` for context instead.
4. **Stay small / runnable** (RLE accepted, over REV's push for a formal model):
   one script + JSON + CSV + unit tests. No publishable propagation model.

## Critiques accepted
- Direction must be validated (PSRE/REV) → added hand-check + unit test.
- Tier must fold severity + cascade (REV/DOL) → done.

## Critiques rejected (with reason)
- "Force blast set == SLO node set" (PSRE) → REJECTED: SLO monitors a subset; the
  sets are semantically different and equating them would corrupt the metric (SMR).
- "Needs a formal/publishable propagation model" (REV) → REJECTED for scope: an RL
  difficulty covariate needs a defined, tested rule, not a research model (RLE).

## Final deliverables
`artifacts/blast_radius.py`, `blast_radius.json`, `blast_radius.csv`,
`test_blast_radius.py`. No shared files modified.
