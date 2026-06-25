# A11 — SUMMARY

**Task:** Create incident pairs (same root cause, different symptom) for transfer testing.

## Delivered
- 3 transfer-test pairs (6 new scenario YAMLs) in scenarios/cidg/generated/,
  task-namespaced a11-pair-* to be parallel-safe:
  - P1 fd_exhaust / restart_service — leaf log-shipper vs buried api-gw cascade.
  - P2 cert_expire / renew_certificate — leaf payments sidecar vs buried tls-ingress cascade.
  - P3 mem_leak / increase_memory_limit — leaf transcoder vs buried object-cache cascade.
- a11_pairs_manifest.json mapping each pair A<->B with shared root cause + symptom text.
- artifacts/make_pairs.py — generator + validator (refuse-if-exists, round-trip parse, invariants).
- Full 10-step Ralph cycle (01-10).

## Design
Within each pair the root cause is invariant (failure_class + canonical fix tool +
persistent/severity); the surface symptom varies (topology, service names,
SLO-violating node, smoking-gun text, leaf vs buried cascade).

## Validation (all pass)
- 6 YAMLs parse and conform to the existing scenario schema.
- Per pair: equal failure_class + fix tool, unequal node count, leaf->cascade flip.
- Only already-shipped fix tools / node kinds / sim toggles used. No existing file edited.

## Honest limits
- 3 pairs (seed set). A=leaf / B=cascade correlates transfer direction with difficulty
  (manifest exposes the axis but doesn't remove the confound). fix_resolves asserted in
  YAML, not yet confirmed in-sim.
