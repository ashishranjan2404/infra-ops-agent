# H6 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/H6/`, no shared-core edits)

### `artifacts/ci_validate_scenarios.py` (the validator)
A staged, per-scenario CI pipeline reusing the repo's authoritative core **read-only**:
- `sim.spec.load_spec` / `sim.spec.validate` — the same loader + closed-vocab/structural
  validator the repo already ships (`python -m sim.spec validate`).
- `sim.engine.World.from_spec`, `apply_action`, `World.run` — engine acceptance.

Five ordered stages per YAML (`load → schema → instantiate → apply_fix → settle`); the first
failing stage is the failure category. Structured JSON report (`--json`), human stdout,
repeatable `--glob`, `--quiet`. Self-inserts repo root on `sys.path` so it needs no env.

**Exit codes:** `0` all pass · `1` ≥1 scenario failed · `2` harness (no match / import fail).

### `artifacts/ci_check.sh` (drop-in CI step)
`set -euo pipefail` wrapper that cd's to repo root and runs the validator with `--json`,
forwarding extra args. Propagates the validator's exit code so CI fails the build.

### `artifacts/test_ci_validate.py` (self-tests)
6 tests covering the happy path (real corpus → exit 0), each early failure stage, and all three
exit codes. Runs under pytest *or* as a plain script (no plugins needed).

### `artifacts/bad_{yaml,schema,engine}.yaml` (negative fixtures)
Deliberately broken scenarios used by the self-tests to prove the gate actually fails:
- `bad_yaml.yaml` — unparseable YAML → `load` stage.
- `bad_schema.yaml` — unknown node kind / dangling edge / bad rc kind / bad SLO direction → `schema`.
- `bad_engine.yaml` — SLO victim node not in topology → `schema` (rejected before the engine).

### `ci_report.json` (the REAL run)
Committed output of the validator over the full corpus: **61/61 pass, exit 0**.
`ci_report_negative.json` — the run over the 3 fixtures: 0/3 pass, exit 1 (proof the gate bites).

## Reuse of A16
H6 reuses A16's corpus-discovery shape (dual glob: `cidg/*` + `cidg/generated/*`) and the same
core entry points, but is deliberately the **acceptance gate** (load/schema/engine-runs), distinct
from A16's **semantic** `fix_resolves` audit. No A16 files were modified.

## Shared-core changes needed? None.
The existing `sim/spec.py` already exposes everything required (`load_spec`, `validate`) and
`sim/engine.py` exposes `World.from_spec` / `apply_action` / `run`. No core edit or `.patch` was
necessary; H6 is purely additive and task-namespaced.
