# A15 — Improved Plan (post-grill)

## What changed vs. 01_plan
1. **Reframing (accepted SMR/PSRE):** the variant is **reward-invariant, observation-degraded**,
   not "physics-identical." `is_resolved` ground truth (`root_cleared && slo_ok`) is unchanged;
   only the observation channel degrades. I no longer claim "zero topology change" — adding a
   `monitoring` node + `observes` edge is a deliberate, minimal topology addition that is what the
   schema uses to *cause* `monitoring_degrades`.
2. **Honest scoping (accepted AAAI/RLE):** I will NOT claim a measured behavioral effect on agent
   success. Tier-A `propagate()` computes error/latency from topology+fault and does not read
   `alerting`/`buried_under`; those fields are consumed by the observation/tool layer and the live
   mesh. This is documented as a scoped blocker in `07`/`09`, not hidden.
3. **Reproducibility (accepted DOL):** ship a one-command transform runnable on any baseline +
   pytest, not a hand-authored YAML. Never edit source scenarios in place.

## Rejected critiques (and why)
- **AAAI: "the variant is hollow."** Rejected. A schema-valid, reward-invariant variant that the
  observation layer is built to consume is legitimate research infrastructure; the correct response
  is to *scope the claim*, which I do, not to discard the deliverable.

## Final deliverable
- `noisy_metrics_transform.py`: pure `transform(doc)->doc` + CLI with `--check`. Sets
  `alerting=noisy`, `monitoring_degrades=True` (obs + assertions), scales `buried_under`
  (`max(cur*3, 20)`), injects monitoring/observes only if absent, re-ids to `<id>-noisy`,
  preserves root_cause/canonical_fix exactly, never mutates input.
- `55-github-network-partition-noisy.yaml`: example variant, validates via official CLI.
- `test_noisy_metrics_transform.py`: 7 tests (validity, purity, physics preserved, idempotency).

## Success criteria (unchanged + sharpened)
Validates clean; obs+assertion flags set; gun buried deeper; root_cause/canonical_fix identical;
baseline untouched; pytest green; honest blocker recorded on engine-consumption.
