# A15 — Noisy-metrics variant (alerting degrades) — Plan

## Objective
Create a "noisy metrics" scenario variant where the **alerting/observability layer
degrades** while the underlying incident physics stays identical, expressed through
the existing CIDG **assertion schema** (`sim/spec.py`). Deliver a reusable transform
script + one validated example variant.

## Approach
The schema already reserves the exact fields for this property — there is no need to
invent a new concept, only to *populate* them coherently:
- `observation.alerting` : `"uniform"` -> `"noisy"` (alert storm / loudness no longer uniform)
- `observation.monitoring_degrades` : `False` -> `True`
- `observation.smoking_guns[*].buried_under` : scaled up (the discriminating log line is
  buried under far more noise)
- `assertions.monitoring_degrades` : `False` -> `True` (so tooling enforces it)
- A structural requirement (sim/spec.py:350): `assertions.monitoring_degrades=True`
  is invalid unless an `observes` edge exists. So the transform injects a
  `monitoring` node + `observes` edge into the root-cause node's blast radius when none exists.

This keeps the **physics invariant**: topology nodes/edges, root_cause, canonical_fix
are untouched — only the observation layer + one monitoring observer are added.

## Files to create (all under artifacts/, no shared-core edits)
- `artifacts/noisy_metrics_transform.py` — pure transform `transform(doc)->doc` + CLI.
- `artifacts/55-github-network-partition-noisy.yaml` — example variant (baseline #55 has a
  smoking gun and no observes edge → exercises every code path).
- `artifacts/test_noisy_metrics_transform.py` — pytest locking in behavior + validity.

## Dependencies
`pyyaml`, and `sim.spec` (read-only, for round-trip validation). Python 3.13.

## Risks
- `monitoring_degrades=True` requires an `observes` edge → handled by injection.
- Could accidentally mutate the input dict → mitigated with `copy.deepcopy`, asserted in tests.
- Double-applying the transform → id suffix made idempotent.

## Success criteria
1. Transform produces a spec that passes `python -m sim.spec validate` with 0 errors.
2. `alerting=noisy`, `monitoring_degrades=True` (both observation + assertions), guns buried deeper.
3. Physics (root_cause, canonical_fix, original topology) unchanged.
4. Original baseline files are not modified in place.
5. pytest green.
