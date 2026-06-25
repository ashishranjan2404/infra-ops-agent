# H6 — 07 Test Results

All commands run from `/Users/mei/rl`, Python 3.13.7.

## 1. Validator over the full corpus (the real CI run)
```
$ python3 experiments/ralph_outputs/H6/artifacts/ci_validate_scenarios.py \
      --json experiments/ralph_outputs/H6/ci_report.json
OK    scenarios/cidg/...  [...]            (61 OK lines)
...
61/61 scenarios pass the sim engine
report -> experiments/ralph_outputs/H6/ci_report.json
EXIT=0
```
Report summary (`ci_report.json`):
```json
{"total": 61, "pass": 61, "fail": 0, "all_pass": true, "failures_by_stage": {}}
```
51 scenarios under `scenarios/cidg/generated/` + 10 under `scenarios/cidg/` = 61 total.

## 2. Negative path — exit code + per-stage categorization
```
$ python3 .../ci_validate_scenarios.py --glob 'experiments/ralph_outputs/H6/artifacts/bad_*.yaml' \
      --json experiments/ralph_outputs/H6/ci_report_negative.json
FAIL  .../bad_engine.yaml  [bad-engine]  stage=schema  3 schema error(s)
        - slo 'error_rate_pct': node 'NONEXISTENT_VICTIM' not in topology
        - assertions.cascades=true but no required/pool/queue edges to propagate through
        - assertions.buried_gun_exists=true but no observation.smoking_guns defined
FAIL  .../bad_schema.yaml  [bad-schema]  stage=schema  6 schema error(s)
        - node 'svc-a': unknown kind 'NOT_A_KIND' ...
        - edge svc-a->ghost: dst not a node
        - root_cause.kind 'not_a_kind' not in closed vocab ...
        - root_cause.location 'nowhere' is not a node or edge
        - slo 'error_rate_pct': bad direction 'sideways'
        ...
FAIL  .../bad_yaml.yaml  [None]  stage=load  ParserError: while parsing a flow mapping ...

0/3 scenarios pass the sim engine  (failures by stage: {'schema': 2, 'load': 1})
EXIT=1
```
Confirms: load + schema failures caught, distinct stages reported, **exit 1**. Notably the
nonexistent SLO victim is rejected at the **schema** stage — it never reaches the engine to
`KeyError`, which is the desired CI behavior (clear message, not a stack trace).

## 3. Self-tests (pytest)
```
$ python3 -m pytest experiments/ralph_outputs/H6/artifacts/test_ci_validate.py -q
......                                                                   [100%]
6 passed in 0.23s
EXIT=0
```
Covers: real corpus → 0, malformed YAML → load stage, bad schema → schema stage + errors,
unknown SLO victim → schema (pre-engine), failure → exit 1, no-match → exit 2.

## 4. CI wrapper
```
$ experiments/ralph_outputs/H6/artifacts/ci_check.sh --quiet
61/61 scenarios pass the sim engine
report -> experiments/ralph_outputs/H6/ci_report.json
EXIT=0
```

## Fixes applied during testing
None required — the validator passed all paths on first full run. The negative fixtures were
authored to *prove* the failure path; they behaved exactly as specified (load vs schema staging,
exit 1). Observed that `validate()` catches the unknown-SLO-victim case before the engine, which
made a separate `instantiate`-stage fixture unnecessary for that class of bug.
