# A16 — Summary: Validate scenarios through the sim engine (fix_resolves)

## Task
Validate all CIDG scenarios with the Tier-A sim engine: confirm each documented
`canonical_fix` actually resolves the injected incident (`fix_resolves == true`).

## What I did
Wrote a standalone validator, `artifacts/validate_scenarios.py`, that for every
scenario YAML: loads the spec, injects the hidden root cause via `World.from_spec`,
confirms the fault bites at t0, applies `canonical_fix.steps` in order, settles
`max(sustain_ticks)`, and takes the engine's own `is_resolved(world)`
(= `root_cleared AND slo_ok`) as the verdict — independent of the YAML's
self-declared `assertions.fix_resolves`. Ran it for real; output is
`validation_report.json`. No shared-core file was edited.

## Result (live run, 61 scenarios present at run time)
- 54 pass / 4 fail / 3 error. all_pass = false.
- No vacuous passes (all 54 had an active fault at t0 and ended root-cleared).
- Title says "42"; parallel workers grew the set to 61. Validator globs the live set.

## Finding: fix_resolves is NOT universally true — 7 broken promises
Wrong target / wrong tool (root never cleared):
- 03-railway-gcp-suspension (targets railway-control-plane, fault=gcp-network-api)
- 06-aws-dynamodb-dns (targets dns, fault=dynamodb)
- 82-travis-ci-leaked-secret (rotate_secret not in REMEDIATION[dep_revoked])
- 87-aws-s3-typo-capacity (restart_service@index-subsystem doesn't clear root)

Unmodeled SLO metric (engine only tracks error_rate_pct + p99_latency_ms):
- 05-azure-ddos-amplification (KeyError latency_p99_ms)
- 20-leaf-cpu-saturation-positive (KeyError latency_p99_ms)
- 21-leaf-oom-positive (KeyError pod_restarts)

Per the brief, none were patched. Known engine gap: persistent/reset_by hysteresis
is declared in specs but not modeled by the engine.

## Artifacts
- experiments/ralph_outputs/A16/artifacts/validate_scenarios.py
- experiments/ralph_outputs/A16/validation_report.json
- 01_plan.md … 10_feedback.md, this SUMMARY.md, result.json
