# A7 — 03 Improved Plan

## What changed vs 01 (driven by the grill)
1. **Auditability first (AAAI).** The JSON now ships a per-incident
   `trap_breakdown` and `pass_rate_penalties` map so every contributing term is
   visible and individually contestable. No black box.
2. **Reweighted toward SRE-salient traps (PSRE).** `cascades` and
   `loudest_alert_not_cause` get 0.16 each; `buried_under` depth 0.12; topology
   node count demoted to 0.18 *spread over up to 6 nodes* (small per-node
   effect). The "is the loud alert the cause" signal now dominates, as on-call
   intuition demands.
3. **Explicit prior labelling (SMR).** Field stays `expected_pass_rate` per the
   task, but the JSON `schema` block declares it a *prior single-attempt
   resolve probability*, and 09 carries the uncalibrated limitation.
4. **Ordinal buckets (RLE).** Added `difficulty_bucket` easy(≥0.70)/
   medium(≥0.45)/hard(<0.45) for curriculum sampling — ordering, not absolute
   accuracy, is the contract.
5. **Determinism + idempotency (DVO).** `sorted(glob(...))`, no RNG, pure
   function of YAML content. Re-running overwrites the same two files with
   identical bytes. Sidecar only; source YAMLs untouched.

## Critiques accepted
- AAAI's "expose the breakdown" → implemented.
- PSRE's "topology alone is weak" → reweighted.
- RLE's "give me buckets" → implemented.
- DVO's "determinism + sidecar" → implemented.

## Critiques rejected (with reason)
- SMR's "rename the field": rejected — the task spec literally names the field
  `expected_pass_rate`; renaming would break the contract. Mitigated instead by
  loud schema documentation. The disagreement is resolved by labelling, not
  renaming.
- AAAI's "block on empirical validation": rejected — there are no labelled pass
  rates in the corpus; blocking would produce nothing. Calibration is filed as
  explicit future work in 09, which is the honest resolution.

## Unchanged
Heuristic, model-agnostic, stdlib+pyyaml, no network, sidecar JSON+CSV.
