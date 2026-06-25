# A16 — Technical Spec

## Inputs
- Scenario YAMLs:
  - `scenarios/cidg/*.yaml`        (curated set)
  - `scenarios/cidg/generated/*.yaml` (generated set)
- Engine (read-only): `sim/engine.py`, schema: `sim/spec.py`.

## Engine resolution physics (as implemented, the binding ground truth)
```
World.from_spec(spec)          # injects own_error[fault_node] = severity, propagates
apply_action(world, action):
    kind   = spec.root_cause.kind
    target = action.args.get("target")
    if action.tool in REMEDIATION[kind] and target == world._fault_node:
        world.own_error[fault_node] = 0.0
    world.propagate()
is_resolved(world) == world.root_cleared and _slo_ok(world)
_slo_ok: for each SLO, metric(node, s.metric) must stay on the safe side of threshold
```
Note: `_fault_node = location.split("->")[0]` for edge-located faults.
Note: `persistent`/`reset_by` are NOT read by the engine (unmodeled hysteresis).

## Validator function signatures
```python
def scenario_paths() -> list[str]
def validate_one(path: str) -> dict   # one record (schema below)
def main() -> int                     # writes report, returns 0 iff all pass
```

## Per-scenario record schema (validation_report.json -> scenarios[i])
```json
{
  "file": "scenarios/cidg/40-...yaml",
  "id": "redis-cache-flush",
  "status": "pass | fail | error",
  "fix_resolves": true,                 // engine verdict (is_resolved)
  "asserts_fix_resolves": true,         // the YAML's self-declared promise
  "fault_active_at_t0": true,           // sanity: incident actually bites pre-fix
  "root_cleared_after_fix": true,
  "slo_ok_after_fix": true,             // informational
  "fix_steps": [{"tool": "...", "target": "..."}],
  "error": null                         // or "KeyError: 'latency_p99_ms'"
}
```

## Report summary schema
```json
{"summary": {"total": int, "pass": int, "fail": int, "error": int,
             "all_pass": bool, "broken_fix_resolves_promises": [file,...]},
 "scenarios": [ <record>, ... ]}
```

## Test cases (expected behavior)
- T1 cache_flush (40-redis): `clear_cache@session-cache` ∈ REMEDIATION[cache_flush],
  target == fault → `status:"pass"`, `fault_active_at_t0:true`.
- T2 wrong-target (03-railway): fault node `gcp-network-api`, fix targets
  `railway-control-plane` → root never cleared → `status:"fail"`.
- T3 unmodeled metric (05-azure): SLO metric `latency_p99_ms` absent from engine
  node vector → `status:"error"`, `error:"KeyError: 'latency_p99_ms'"`.
- T4 exit code: `main()` returns non-zero iff any fail/error exists.

## Non-goals
- No edits to `sim/*` or any scenario YAML.
- No modeling of hysteresis/chance/flap — out of engine scope.
