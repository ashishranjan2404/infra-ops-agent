# H6 — Summary: CI Scenario Validator

## Task
Build a CI check: every CIDG scenario YAML must pass the sim engine. Schema + engine acceptance,
nonzero exit on failure. Run it over all scenarios and capture the real report. No shared-core edits.

## Deliverable
A real, CI-ready validator that, per scenario YAML, runs 5 staged checks reusing the repo's
authoritative core read-only (sim/spec.py, sim/engine.py):
load -> schema -> instantiate -> apply_fix -> settle. First failing stage = failure category.

Exit-code contract (CI): 0 all pass | 1 >=1 scenario failed | 2 harness (no match / import).

## Artifacts (all task-namespaced under experiments/ralph_outputs/H6/)
- artifacts/ci_validate_scenarios.py — the validator (CLI, --glob/--json/--quiet).
- artifacts/ci_check.sh — drop-in CI step wrapper (propagates exit code).
- artifacts/test_ci_validate.py — 6 self-tests (happy path + every failure stage + all exit codes).
- artifacts/bad_{yaml,schema,engine}.yaml — negative fixtures proving the gate fails.
- ci_report.json — REAL run over the full corpus: 61/61 pass, exit 0.
- ci_report_negative.json — run over the 3 broken fixtures: 0/3, exit 1.

## Real results
- Full corpus: 61 scenarios (10 scenarios/cidg/ + 51 scenarios/cidg/generated/) -> 61/61 pass.
- Negative fixtures -> exit 1, failures correctly categorized (schema: 2, load: 1).
- python3 -m pytest .../test_ci_validate.py -q -> 6 passed.

## Relationship to A16
H6 is the acceptance gate (loads + schema-clean + engine-runs). A16 is the semantic audit
(fix_resolves). H6 reuses A16's dual-glob corpus discovery + the same core entry points but is a
distinct, CI-first layer with explicit exit codes. No A16 or core files modified.

## Status: completed
