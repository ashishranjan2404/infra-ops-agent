# H2 — 06 Implementation

## What I built (all real, all task-namespaced under `H2/artifacts/`)

### 1. `eval-ci.yml` (87 lines) — the GitHub Actions workflow (the deliverable)
A complete CI pipeline that runs the eval suite on every PR/push to `main` (plus manual
`workflow_dispatch`). Shipped as an artifact, **not** installed into `.github/` (per the
parallel-safety rule). Header documents how a maintainer activates it.

Job `eval-suite` (ubuntu-latest, `timeout-minutes: 15`):
1. `actions/checkout@v4`
2. `actions/setup-python@v5` — Python 3.13, `cache: pip`
3. install `requirements-rex.txt` + pytest
4. run the deterministic, LLM-free pytest subset (9 test files; `test_llm.py` excluded
   because it calls a live gateway)
5. run the deterministic pass@k smoke (`passk_smoke.py --per-family 3`)
6. `actions/upload-artifact@v4` — the smoke JSON report (`if: always()`)

Hardening: `permissions: {contents: read}`, `concurrency` with `cancel-in-progress`,
pinned action majors, explicit timeout.

### 2. `passk_smoke.py` (133 lines) — deterministic pass@k smoke
LLM-free. Imports the **real** eval substrate (`rex.harness.load_scenario / run_plan /
scenarios_by_family`, `rex.scoring.score_plan` with the default deterministic judge,
`experiments.compute_pass_at_k.{binary_pass,pass_at_k,wilson_ci}`). Two fixed policies:
- `gold`  = canonical-fix steps + correct root cause,
- `empty` = no diagnosis / no actions.

Computes pass@1/pass@2 + Wilson CI for each, prints a JSON report, and enforces three
invariants (SEPARATION, FLOOR, GOLD-FLOOR). Exit 0 = healthy, 1 = substrate regression.

### 3. `validate_workflow.py` (56 lines) — YAML shape validator
`yaml.safe_load`s the workflow and asserts name, a `pull_request` trigger (handling the
PyYAML `on:`→`True` quirk), the `eval-suite` job, and that the steps invoke both `pytest`
and `passk_smoke.py`. Exit 0/1.

## Shared core: NOT touched
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, `.github/`, or any
other task's directory. I discovered that scenario `aws_dynamodb_dns`'s canonical-fix plan
under-scores (0.425) in the sim. That is a shared-core/data issue and out of scope — I did
**not** patch it; instead the smoke's gold-floor invariant is tolerant of it and 09_critique
records it as a finding for a future task.

## Key design decision
The required PR gate is **deterministic and hermetic** — a per-PR real-model sweep was
rejected (Wilson CI too wide at small k/seeds to separate regression from noise). A real
model sweep belongs in a label-gated/nightly job (documented as future work).
