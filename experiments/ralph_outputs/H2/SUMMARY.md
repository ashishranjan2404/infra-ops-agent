# H2 — SUMMARY

**Task:** Create a CI pipeline for the eval suite (run pass@k on every PR). Write a real
GitHub Actions workflow YAML (in the artifacts dir, NOT `.github/`) that installs deps, runs
pytest and a small pass@k smoke. Validate the YAML parses. No shared-core / `.github/` edits.

**Status: completed.**

## Deliverables (all under `experiments/ralph_outputs/H2/artifacts/`)
- **`eval-ci.yml`** — GitHub Actions workflow. Triggers on PR + push to `main` +
  `workflow_dispatch`. Job `eval-suite` (ubuntu-latest, 15-min timeout): checkout →
  setup-python 3.13 (pip cache) → install `requirements-rex.txt` + pytest → run the
  deterministic pytest subset → run the pass@k smoke → upload the smoke JSON report.
  Hardened with least-priv permissions, pinned actions, concurrency cancel-in-progress.
  Shipped as an artifact (NOT installed into `.github/`).
- **`passk_smoke.py`** — deterministic, LLM-free pass@k smoke. Runs the real eval substrate
  (`rex.harness` + `rex.scoring` deterministic judge + `compute_pass_at_k`) with two fixed
  policies (gold canonical-fix vs empty) and enforces SEPARATION (gold > empty), FLOOR
  (empty pass@1 == 0.0), and GOLD-FLOOR (gold pass@1 >= 0.7). Exit 0/1, JSON report.
- **`validate_workflow.py`** — parses the YAML and asserts required shape (PR trigger,
  pytest step, pass@k step), handling the PyYAML `on:`→`True` quirk.

## Validation (real runs)
- `validate_workflow.py` → exit 0.
- `eval-ci.yml` parses, 6 steps.
- pytest subset named in the workflow → **80 passed**.
- `passk_smoke.py` → exit 0 at `--per-family 2/3/0`: gold 0.78–0.86, empty 0.0, floor holds.

## Honest caveats
- The smoke guards the *substrate*, not a model's pass@k (a per-PR real-model sweep is too
  noisy at small k/seeds and needs a secret; deferred to a label-gated/nightly job).
- Genuine finding: two scenarios (`aws_dynamodb_dns`, `azure_ddos`) have canonical-fix data
  that under-scores in the sim; the gold-floor threshold tolerates them (0.7). Documented,
  not patched (shared-core / out of scope).

## Shared-core safety
Only new files under `H2/` were created. No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`,
`experiments/*.py`, the dashboard, or `.github/`.
