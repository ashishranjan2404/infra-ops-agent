# A16 — Implementation

## What I built
A single self-contained validator, `artifacts/validate_scenarios.py`, that drives
every CIDG scenario through the real Tier-A engine and emits a machine-readable
report. It edits NO shared core file — it only imports `sim.spec` / `sim.engine`
read-only and reads the scenario YAMLs.

### Pipeline per scenario
1. `load_spec(path)` — exercises the schema loader (catches YAML/schema drift).
2. `World.from_spec(spec)` — injects the hidden root cause and propagates.
3. Record `fault_active_at_t0 = not is_resolved(world)` (guards vacuous passes).
4. Apply `canonical_fix.steps` in authored order via `apply_action`.
5. Settle `max(slo.sustain_ticks)` ticks via `world.run(...)`.
6. Verdict = `is_resolved(world)` (engine's `root_cleared AND _slo_ok`).
7. Cross-check vs the scenario's own `assertions.fix_resolves` promise.

### Artifacts produced (all task-namespaced)
- `experiments/ralph_outputs/A16/artifacts/validate_scenarios.py`
- `experiments/ralph_outputs/A16/validation_report.json` (real run output)

## Real run result (54 scenarios present at run time)
- **48 pass**, **3 fail**, **3 error**. No vacuous passes (every pass had an
  active fault at t0).
- The task title says "42"; by run time parallel Ralph workers had grown the set
  to 54. The validator globs the live set, so the report covers all 54.

## The 6 broken `fix_resolves` promises (each YAML claims true; engine says no)
1. `03-railway-gcp-suspension` — **wrong target**. Fault node is
   `gcp-network-api` (root_cause.location), but `canonical_fix` targets
   `railway-control-plane`. Per engine physics the root is never cleared.
2. `06-aws-dynamodb-dns` — **wrong target**. location `dynamodb->dns` ⇒ fault
   node `dynamodb`; fix targets `dns`. Root never cleared.
3. `82-travis-ci-leaked-secret` — **wrong tool for kind**. kind `dep_revoked`
   is remediated by `{modify_network_policy, failover_service, restart_service}`,
   but the fix uses `rotate_secret`, which is not in `REMEDIATION[dep_revoked]`.
4. `05-azure-ddos-amplification` — **unmodeled SLO metric**. SLO names
   `latency_p99_ms`; engine node vector only has `error_rate_pct`/`p99_latency_ms`
   ⇒ `KeyError: 'latency_p99_ms'`.
5. `20-leaf-cpu-saturation-positive` — same unmodeled metric `latency_p99_ms`.
6. `21-leaf-oom-positive` — unmodeled SLO metric `pod_restarts`.

Categories: (1-2) author targeted the symptom/dependent node instead of the
engine's fault node; (3) author chose a domain-correct tool the engine's physics
table doesn't map to that kind; (4-6) SLO references metrics the Tier-A engine
doesn't simulate. None were patched — per the brief they are documented for the
scenario/engine owners.

## Known engine gap (not a per-scenario failure)
`persistent`/`reset_by` hysteresis is declared in several specs (e.g. the 01-06
curated set) but `apply_action`/`is_resolved` never read it. The engine's verdict
is therefore the binding ground truth here; hysteresis is flagged, not simulated.
