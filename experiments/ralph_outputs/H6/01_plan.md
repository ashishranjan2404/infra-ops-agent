# H6 — 01 Plan

## Objective
Build a **CI check**: every CIDG scenario YAML must (a) be schema-valid and (b) be accepted
by the Tier-A sim engine. The check exits nonzero on any failure so CI fails the build.

## Approach
Reuse the existing, authoritative loader/validator in `sim/spec.py` (`load_spec`, `validate`)
and the engine in `sim/engine.py` (`World.from_spec`, `apply_action`, `World.run`). Wrap them
in a per-scenario, staged pipeline:

1. **load** — YAML parse + dataclass build (`load_spec`)
2. **schema** — closed-vocab + structural errors (`sim.spec.validate`)
3. **instantiate** — engine accepts spec: inject hidden fault + first `propagate()`
4. **apply_fix** — every `canonical_fix` step runs through `apply_action` without crashing
5. **settle** — `world.run(sustain_ticks)` keeps `propagate()` well-defined

A scenario passes iff all 5 stages pass. The first failing stage is its failure category.

## Relationship to A16 (reuse, not duplicate)
A16 already wrote a *semantic* validator that asserts `is_resolved()` after the canonical fix
(`fix_resolves`). H6 is the **acceptance gate that runs first**: it does NOT judge whether the
fix resolves the incident — only that every YAML loads, is schema-clean, and the engine runs it
without raising. This is the correct CI granularity: a green H6 gate is the precondition for
A16's deeper audit to be meaningful. H6 reuses the same core entry points (`load_spec` / engine)
and the same dual-glob corpus discovery as A16, but adds explicit CI exit-code contracts,
per-stage failure categorization, and negative-path self-tests.

## Files to create (all task-namespaced; NO shared-core edits)
- `experiments/ralph_outputs/H6/artifacts/ci_validate_scenarios.py` — the validator (CLI).
- `experiments/ralph_outputs/H6/artifacts/ci_check.sh` — drop-in CI step wrapper.
- `experiments/ralph_outputs/H6/artifacts/test_ci_validate.py` — self-tests (pass + fail paths).
- `experiments/ralph_outputs/H6/artifacts/bad_{yaml,schema,engine}.yaml` — negative fixtures.
- `experiments/ralph_outputs/H6/ci_report.json` — the real run over all scenarios.

## Dependencies
`pyyaml` (already a repo dep), stdlib only otherwise. Python 3.13. No network, no cluster.

## Risks
- Over-broad `except` could mask a real CI-relevant crash → mitigate by recording the stage,
  message, and a 3-line traceback per failure (visible in report + stdout).
- Glob drift (new scenario dirs) → default globs cover `scenarios/cidg/*.yaml` and
  `scenarios/cidg/generated/*.yaml`; `--glob` is overridable/repeatable.
- A `validate()` that itself raises would be silent → caught and classed as a schema failure.

## Success criteria
- Runs over the full corpus, exits 0 when all valid; exits 1 with a clear per-file reason
  when any scenario is broken; exits 2 on harness/usage errors (no match, import failure).
- Self-tests cover all three exit codes and each failure stage; pytest green.
- A real JSON report is written and committed under H6/.
