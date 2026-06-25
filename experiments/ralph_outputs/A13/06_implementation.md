# A13 — Implementation

## What I built (real artifacts)

### 1. Three multi-fault scenario YAMLs (in `scenarios/cidg/generated/`)
Each declares **2 simultaneous, independently-clearable faults** — a primary `root_cause` (live in
today's engine) plus a `secondary_faults[0]` entry — and conforms to the closed-vocab schema.

| file | primary fault | secondary fault | shape | seed |
|------|---------------|-----------------|-------|------|
| `80-multi-cert-poolleak.yaml` | cert_expire @ auth-gw → renew_certificate | pool_leak @ session-pool → restart_service | independent coincidence | 1080 |
| `81-multi-rollout-cacheflush.yaml` | bad_revision @ api-edge → rollback_deployment | cache_flush @ result-cache → clear_cache (gun buried_under 80) | masking | 1081 |
| `82-multi-fdexhaust-cpustarve.yaml` | fd_exhaust @ conn-router → restart_service | cpu_starve @ rank-svc → scale_deployment | shared blast radius | 1082 |

Design choices enforced from `05_ouroboros.md`:
- Each fault has its **own distinct SLO victim** downstream of only that fault (so the secondary
  cannot be incidentally satisfied by fixing the primary).
- Every fix tool is in `REMEDIATION[kind]` (engine physics) AND in `tools_registry.json`.
- Each spec has ≥1 `required` edge (satisfies `assertions.cascades`) and two `smoking_guns`
  (satisfies `assertions.buried_gun_exists`, one per fault).
- `82` keeps a genuine trap: `scale_deployment` fixes the cpu_starve secondary but does NOT fix the
  fd_exhaust primary — right tool, wrong fault.

### 2. `artifacts/test_multifault.py`
6 patch-free pytest cases against the CURRENT engine: specs validate; exactly 2 distinct fault
locations; each fault has its own SLO victim; each fault has an engine-valid fix step; the primary
single-fault path injects, cascades, and clears in the unpatched engine. **All 6 pass.**

### 3. `artifacts/engine_multifault.patch` (PROPOSED — NOT applied)
A real 92-line unified diff against `sim/spec.py` + `sim/engine.py` that:
- adds a `secondary_faults: list` field to `ScenarioSpec` and populates it in `_spec_from_dict`;
- validates secondary faults (closed-vocab kind, real location node, distinct from other faults,
  real slo_node);
- injects every secondary fault's `own_error` at episode start (`World._fault_nodes`);
- makes `apply_action` clear whichever fault sits on the targeted node (by that fault's kind);
- adds `World.all_roots_cleared` and rewires `is_resolved` to be **conjunctive** — resolution
  requires ALL fault locations cleared, not just the primary.

I verified the patch on a throwaway copy (`/tmp/mfpatch/b`): for all 3 specs, applying only the
first canonical fix leaves `is_resolved == False`, and only after BOTH fixes does it become `True`.
This proves the multi-fault label is mechanistic, not cosmetic, once the patch lands.

## Why a patch and not an edit
The brief forbids editing shared core (`sim/*.py`). The engine today injects a single `root_cause`,
so a faithful 2-fault sim needs the engine change. I deliver it as a documented, verified `.patch`
and author the YAMLs so they are immediately correct the moment it merges. Today the specs parse,
validate, and behave as faithful single-fault scenarios on their primary fault (the `secondary_faults`
block is silently dropped by `_build`'s forward-compat key handling).

## Files
- `scenarios/cidg/generated/80-multi-cert-poolleak.yaml`
- `scenarios/cidg/generated/81-multi-rollout-cacheflush.yaml`
- `scenarios/cidg/generated/82-multi-fdexhaust-cpustarve.yaml`
- `experiments/ralph_outputs/A13/artifacts/test_multifault.py`
- `experiments/ralph_outputs/A13/artifacts/engine_multifault.patch`

No shared core file edited (verified: `diff -q` of repo `sim/engine.py` and `sim/spec.py` vs
pre-task snapshots → identical).
