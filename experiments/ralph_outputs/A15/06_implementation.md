# A15 — Implementation

## Artifacts built (all under experiments/ralph_outputs/A15/artifacts/)
1. **`noisy_metrics_transform.py`** — reusable, pure spec transform + CLI.
   - `transform(doc)` deep-copies the input, then:
     - re-ids `meta.id` → `<id>-noisy` (idempotent), tags `derived_from`/`variant`,
     - sets `observation.alerting="noisy"`, `observation.monitoring_degrades=True`,
     - deepens every smoking gun: `buried_under = max(cur*3, 20)`,
     - injects a `monitoring-stack` node + `observes`→root-cause-node edge **iff** the
       baseline has no `observes` edge (needed so `assertions.monitoring_degrades=True` is
       schema-valid per `sim/spec.py:350`),
     - sets `assertions.monitoring_degrades=True`.
   - `root_cause`, `canonical_fix`, `slo`, `fault` are left byte-identical → reward-invariant.
   - CLI: writes a new YAML (`-o`) or `--check` (validate only). Validates the output by
     round-tripping through the real `sim.spec._spec_from_dict` + `validate` before writing;
     never writes an invalid file. Adds repo root to `sys.path` so it runs from any cwd.

2. **`55-github-network-partition-noisy.yaml`** — the example variant, generated from baseline
   `scenarios/cidg/generated/55-github-network-partition.yaml`. Confirmed deltas: `alerting: noisy`,
   `monitoring_degrades: true` (observation + assertions), smoking gun `buried_under: 40 → 120`,
   added `monitoring-stack` node + `observes` edge to `orchestrator` (the root node).

3. **`test_noisy_metrics_transform.py`** — 7 pytest cases (see 04_spec, 07_test_results).

## Shared-core safety
No shared file was edited. `sim/spec.py` is imported read-only for validation. The example
variant is written to the task artifacts dir, NOT into `scenarios/cidg/generated/`, so no
existing scenario is overwritten. Baseline #55 is unchanged.

## How to reproduce
```
cd /Users/mei/rl
python3 experiments/ralph_outputs/A15/artifacts/noisy_metrics_transform.py \
    scenarios/cidg/generated/55-github-network-partition.yaml \
    -o experiments/ralph_outputs/A15/artifacts/55-github-network-partition-noisy.yaml
python3 -m sim.spec validate experiments/ralph_outputs/A15/artifacts/*-noisy.yaml
python3 -m pytest experiments/ralph_outputs/A15/artifacts/test_noisy_metrics_transform.py -q
```

## Note / proposed downstream change (NOT applied — shared core)
To make the variant behaviorally active in Tier-A, a future change to the observation/tool layer
(e.g. the `get_logs` reader) should scale returned noise lines by `buried_under` and treat
`alerting=="noisy"` as a non-uniform alert distribution. That touches shared core and is out of
A15 scope; recorded here and in 09 as the honest boundary.
