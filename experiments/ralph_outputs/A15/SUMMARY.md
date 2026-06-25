# A15 — Summary: Noisy-metrics variant (alerting degrades)

## Deliverable
A reusable, tested transform that produces a **reward-invariant, observation-degraded**
variant of any CIDG scenario, expressed through the existing assertion schema — plus one
materialized example variant.

## Artifacts
- `artifacts/noisy_metrics_transform.py` — pure `transform(doc)->doc` + CLI; sets
  `alerting=noisy`, `monitoring_degrades=True` (observation + assertions), deepens
  `buried_under` (`max(cur*3,20)`), injects a `monitoring`+`observes` edge when needed for
  schema validity, preserves `root_cause`/`canonical_fix` exactly, never mutates input or
  source files. Self-validates via `sim.spec`.
- `artifacts/55-github-network-partition-noisy.yaml` — example variant; passes the official
  `python -m sim.spec validate` (6 nodes / 5 edges). buried_under 40->120; +monitoring-stack
  node observing the root node `orchestrator`.
- `artifacts/test_noisy_metrics_transform.py` — 7 pytest cases, all green.

## Validation
- Official CLI: `1/1 specs valid`.
- pytest: `7 passed`.
- Transform runs clean on both a with-gun (#55) and no-gun (#44) baseline.
- Source scenarios unmodified; all outputs in the task artifacts dir.

## Honest scope / blocker
Tier-A `propagate()` does not yet read `alerting`/`buried_under` (consumed by the
observation/tool layer + live mesh), so the variant is reward-invariant and schema-valid but
behaviorally latent on the fast sim until that layer is wired — documented, not faked.

Status: completed.
