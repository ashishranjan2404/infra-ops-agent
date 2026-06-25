# A16 — Verification

## Success criteria (from 01/03) vs reality
| criterion | met? | evidence |
|-----------|------|----------|
| Validator loads every scenario through the sim engine | YES | `validate_one` calls `load_spec` + `World.from_spec` for all 61 files |
| Asserts the documented fix resolves (`fix_resolves`) via the engine | YES | verdict = `is_resolved(world)` after applying `canonical_fix.steps`, not the YAML flag |
| Actually RUN, real per-scenario pass/fail captured | YES | `validation_report.json` written with 61 records; transcript in 07 |
| No shared-core edits | YES | only `artifacts/validate_scenarios.py` + report created; `sim/*` and YAMLs untouched |
| Failures documented, not silently fixed | YES | 06/07/09 enumerate all 7 broken promises with root cause; zero patches |

## Outputs are real, not placeholder
- `validation_report.json` is a real run artifact: 61 scenario records, each with
  engine verdict, `root_cleared`, `fix_steps`, and error string where applicable.
- The pass set is non-vacuous: all 54 passes had an active fault at t0 and ended
  with the root cleared — verified programmatically (no `fault_active_at_t0=false`).
- Failures are reproducible: re-running reproduces the same 6 stable broken
  promises (+ the 7th once its YAML was added by a parallel worker).

## Honest gap vs the task title
The title says "42 scenarios". At run time the live set was 61 (parallel workers
kept adding YAMLs). The validator covers the whole live set rather than a frozen
42, which is the correct behavior — but it means the headline is "54/61 resolve,
7 do not", NOT "42/42 resolve". The fix_resolves property does NOT hold for all
scenarios; that is a real, documented finding, not a pass.
