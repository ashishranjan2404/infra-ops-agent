# A16 — Plan: Validate all scenarios through the sim engine (fix_resolves)

## Objective
Verify, by actually running each CIDG scenario through the Tier-A simulator
(`sim/engine.py`), that the documented `canonical_fix` resolves the injected
incident — i.e. the emergent `fix_resolves` property holds, not just the
self-declared `assertions.fix_resolves: true` flag in the YAML.

## Approach
1. Read `sim/engine.py` + `sim/spec.py` to learn the real resolution physics:
   - `World.from_spec(spec)` injects the hidden root cause and propagates.
   - `apply_action(world, action)` clears the root ONLY if the tool causally
     fixes the root-cause `kind` (per `REMEDIATION`) AND targets the fault node.
   - `is_resolved(world) == root_cleared and _slo_ok(world)`.
2. For each scenario YAML: load → instantiate world → confirm fault is active
   at t0 → apply every `canonical_fix.steps` action in order → settle for
   `max(sustain_ticks)` → assert `is_resolved` is True.
3. Cross-check the engine verdict against the scenario's own
   `assertions.fix_resolves` flag; any "broken promise" (flag says true, engine
   says false) is a real defect to document, not silently patch.
4. Emit a per-scenario `validation_report.json` with pass/fail/error + reason.

## Files to create (all task-namespaced; NO shared-core edits)
- `experiments/ralph_outputs/A16/artifacts/validate_scenarios.py` — the validator.
- `experiments/ralph_outputs/A16/validation_report.json` — real run output.
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
- `sim.spec.load_spec`, `sim.engine.{World,apply_action,is_resolved}` (read-only).
- `pyyaml` (already a project dep). Python 3.13.

## Risks
- Scenario count is a moving target (parallel Ralph workers are adding YAMLs).
  Mitigation: validate ALL present scenarios via glob; report the actual count.
- The engine models only `error_rate_pct` + `p99_latency_ms`. SLOs that name
  other metrics will KeyError — that's a real engine/spec mismatch to surface.
- `persistent`/`reset_by` hysteresis is in the spec but NOT in the engine, so
  the engine's `fix_resolves` is the binding ground truth here.

## Success criteria
- Validator runs cleanly over every scenario and writes a real JSON report.
- Every failure is explained with a concrete root cause, none silently "fixed".
