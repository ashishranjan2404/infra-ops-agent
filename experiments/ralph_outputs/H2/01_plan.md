# H2 — 01 Plan

## Objective
Create a CI pipeline that runs the eval suite (pytest + a small pass@k smoke) on every PR.
Deliver a **real, parse-valid GitHub Actions workflow YAML** living in the task artifacts
dir (NOT `.github/`), plus the deterministic pass@k smoke it invokes, plus a validator.

## Approach
1. Inspect existing eval substrate: `rex/eval_pass_at_k.py`, `rex/harness.py`,
   `rex/scoring.py`, `experiments/compute_pass_at_k.py`, and `tests/`.
2. Build a **deterministic, LLM-free** pass@k smoke. The full sweep needs a gateway API
   key and is flaky/slow — wrong for per-PR CI. Instead run two fixed policies whose
   outcome is determined by the sim+judge:
   - `gold` = canonical-fix plan + correct root cause  -> should pass.
   - `empty` = no diagnosis, no actions               -> should never pass (floor).
3. Write `eval-ci.yml`: checkout -> setup-python 3.13 -> install `requirements-rex.txt`
   + pytest -> run the deterministic test subset -> run the pass@k smoke -> upload report.
4. Validate: YAML parses (pyyaml), the named tests pass, the smoke exits 0.

## Files to create (all task-namespaced, no shared edits)
- `experiments/ralph_outputs/H2/artifacts/eval-ci.yml`        — the workflow (deliverable)
- `experiments/ralph_outputs/H2/artifacts/passk_smoke.py`     — deterministic pass@k smoke
- `experiments/ralph_outputs/H2/artifacts/validate_workflow.py` — YAML shape validator

## Dependencies
- pyyaml (already in `requirements-rex.txt`), pytest (installed), Python 3.13.
- The smoke imports the real `rex.harness`, `rex.scoring`, `experiments.compute_pass_at_k`.

## Risks
- The bare `on:` key in GitHub Actions YAML parses to Python `True` under PyYAML
  (YAML 1.1 boolean) — the validator must check both `on` and `True`.
- A mis-specified scenario could make a "gold==1.0" assertion brittle. Mitigate by
  asserting **separation + floor + a gold-floor fraction**, not perfection.
- CI must not call any LLM/gateway → exclude `tests/test_llm.py`.

## Success criteria
- `eval-ci.yml` parses and has: PR trigger, a job, a pytest step, a pass@k smoke step.
- The exact test list named in the workflow passes locally.
- `passk_smoke.py` exits 0 with gold > empty and empty pass@1 == 0.0.
- Nothing under `.github/` or shared core (`rex/*.py`, `sim/*.py`, ...) is modified.
