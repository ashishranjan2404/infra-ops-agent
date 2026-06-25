# A11 — 01 Plan

## Objective
Create **incident pairs** for transfer testing: each pair shares the SAME root
cause (same `failure_class` + same canonical fix tool) but presents a DIFFERENT
surface symptom (different topology, service names, SLO-violating node, smoking-gun
phrasing, and leaf-vs-cascade structure). These let us measure whether an
SRE-Degrees agent has learned the *mechanism* (transferable) vs memorized the
*surface* of a scenario.

## Approach
- Study the existing scenario schema in `scenarios/cidg/generated/*.yaml` (33
  scenarios) and `registry.json`.
- Identify the invariants that define a "root cause": `meta.failure_class`,
  `root_cause.kind`, the `<class>_active` sim toggle, and `canonical_fix.steps[0].tool`.
- Identify the "surface symptom" knobs that can vary freely without changing the
  root cause: topology (node names/kinds/count), edges, which node breaches SLO,
  `observation.smoking_guns`, `assertions.cascades / loudest_alert_not_cause /
  buried_gun_exists`, trap actions, seed.
- Produce 3 pairs (6 YAMLs). For each pair: variant A = leaf (root visible),
  variant B = cascade (root buried under downstream SLO breaches). Hold the fix
  tool and failure_class invariant.
- Emit a `pairs_manifest.json` mapping A<->B and recording the shared root cause.

## Files to create (all NEW, unique numbers — dir currently uses 40-79)
- `scenarios/cidg/generated/80-fd-exhaust-leaf-shipper.yaml`
- `scenarios/cidg/generated/81-fd-exhaust-cascade-gw.yaml`
- `scenarios/cidg/generated/82-cert-expire-leaf-sidecar.yaml`
- `scenarios/cidg/generated/83-cert-expire-cascade-ingress.yaml`
- `scenarios/cidg/generated/84-mem-leak-leaf-transcoder.yaml`
- `scenarios/cidg/generated/85-mem-leak-cascade-cache.yaml`
- `scenarios/cidg/generated/pairs_manifest.json`
- `experiments/ralph_outputs/A11/artifacts/make_pairs.py` (generator + validator)

## Dependencies
- `pyyaml` (already in repo deps).
- No edits to shared core `.py`. Manifest is a NEW file, not an edit to
  `registry.json`.

## Risks
- Number/name collision with existing files → mitigated by checking dir first
  (40-79 used) and a `REFUSING` guard in the generator.
- A varied scenario could accidentally change the root cause → mitigated by an
  explicit invariant assertion (same failure_class + fix tool, different node count).
- Fix tool not recognized by sim → use only tools already present in existing
  scenarios (restart_service, renew_certificate, increase_memory_limit).

## Success criteria
- 6 NEW YAMLs that parse and match the schema key set of existing scenarios.
- 3 documented pairs; within each pair failure_class & fix tool identical, surface
  symptom different.
- A machine-readable `pairs_manifest.json`.
- No existing file edited.
