# H2 — 04 Technical Spec

## A. Workflow `eval-ci.yml`
- **Triggers:** `pull_request` (branches: main), `push` (branches: main), `workflow_dispatch`.
- **Hardening:** `permissions: {contents: read}`, `concurrency: {group: eval-ci-${{github.ref}},
  cancel-in-progress: true}`.
- **Job `eval-suite`:** `runs-on: ubuntu-latest`, `timeout-minutes: 15`. Steps:
  1. `actions/checkout@v4`
  2. `actions/setup-python@v5` (python 3.13, `cache: pip`)
  3. install: `pip install -r requirements-rex.txt` + `pip install pytest`
  4. pytest the deterministic subset (env `PYTHONPATH=${{github.workspace}}`)
  5. run `passk_smoke.py --per-family 3 --out passk_smoke_report.json`
  6. `actions/upload-artifact@v4` (report, `if: always()`)
- **Excluded from CI:** `tests/test_llm.py` (live gateway).

## B. `passk_smoke.py`
Constants: `THRESHOLD = 0.8`, `MIN_GOLD_PASS = 0.8`.

Function signatures:
```python
gold_plan(sc) -> dict          # {"root_cause": sc.gold_root_description,
                               #  "actions": [{"tool": s.tool, "args": s.args}
                               #              for s in sc.spec.canonical_fix.steps]}
empty_plan(sc) -> dict         # {"root_cause": "", "actions": []}
score(plan, sc) -> float       # run_plan -> score_plan (P0 deterministic judge)
pick_incidents(per_family:int) -> list[str]    # simple+cascade+novel, [:per_family]
summarize(rewards: list[float]) -> dict        # {n,passes,pass@1,ci95,pass@2,mean_reward}
main() -> int                  # 0 = smoke ok, 1 = regression
```
Reused real APIs: `rex.harness.load_scenario / run_plan / scenarios_by_family`,
`rex.scoring.score_plan`, `experiments.compute_pass_at_k.{binary_pass,pass_at_k,wilson_ci}`.

Report JSON shape:
```json
{"threshold":0.8,"n_incidents":6,"incidents":["..."],
 "gold_policy":{"n":6,"passes":5,"pass@1":0.833,"ci95":[..],"pass@2":1.0,"mean_reward":0.90},
 "empty_policy":{"n":6,"passes":0,"pass@1":0.0,"ci95":[..],"pass@2":0.0,"mean_reward":0.0}}
```

Invariants (exit 1 if any fails):
1. SEPARATION  `gold.pass@1 > empty.pass@1`
2. FLOOR       `empty.pass@1 == 0.0`
3. GOLD-FLOOR  `gold.pass@1 >= MIN_GOLD_PASS`

## C. `validate_workflow.py`
- Loads `eval-ci.yml` with `yaml.safe_load`.
- Asserts: parses to mapping; `name == "eval-ci"`; a `pull_request` trigger exists
  (checking both `on` and the PyYAML `True` key); `eval-suite` job present; some step's
  `run` contains `pytest`; some step's `run` contains `passk_smoke.py`.
- Exit 0 valid / 1 invalid; prints each failure to stderr.

## Test cases
- T1 `validate_workflow.py` exits 0 on the shipped YAML.
- T2 `passk_smoke.py --per-family 2` exits 0; gold > empty; empty pass@1 == 0.
- T3 the exact pytest list named in the workflow passes locally.
- T4 `yaml.safe_load(eval-ci.yml)` raises no exception and has 6 steps.
