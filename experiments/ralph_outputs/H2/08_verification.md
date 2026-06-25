# H2 — 08 Verification

## Success criteria (from 01_plan) — all met

| Criterion | Status | Evidence |
|---|---|---|
| Real GitHub Actions workflow YAML, parse-valid | MET | `validate_workflow.py` exit 0; `yaml.safe_load` ok, 6 steps (T1/T2) |
| Installs deps | MET | step 3 installs `requirements-rex.txt` + pytest |
| Runs the test suite (pytest) | MET | step 4 runs a 9-file deterministic subset; 80 passed locally (T3) |
| Runs a small pass@k smoke | MET | step 5 runs `passk_smoke.py --per-family 3`; exit 0 (T4) |
| Triggers on every PR | MET | `on.pull_request` (branches main) + push + workflow_dispatch |
| In artifacts dir, NOT `.github/` | MET | files live under `experiments/ralph_outputs/H2/artifacts/` only |
| No shared-core edits | MET | git status shows only new files under `H2/`; no `rex/`,`sim/`,`agent/`,`.github/` changes |

## Outputs are REAL, not placeholder
- `eval-ci.yml` is a runnable workflow using real published actions (`checkout@v4`,
  `setup-python@v5`, `upload-artifact@v4`) and real repo paths/commands.
- `passk_smoke.py` executes the **actual** eval substrate (`load_scenario` → `run_plan` →
  `score_plan`, deterministic judge) over real scenarios; the numbers (gold 0.78–0.86,
  empty 0.0) are produced by running it, not hand-written.
- `validate_workflow.py` actually parses the YAML and asserts structure.

## Independence / hermeticity check
- The smoke imports only `rex.harness`, `rex.scoring`, `experiments.compute_pass_at_k` — no
  `agent.llm`, no network, no `HUD_API_KEY`. Confirmed it runs with no env loaded.
- CI job sets `PYTHONPATH=${{github.workspace}}` so imports resolve the same way they do
  locally (verified the local runs use the identical `PYTHONPATH=$PWD`).

## Verdict
The deliverable meets every stated success criterion with real, validated artifacts.
