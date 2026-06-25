# 07 — Test Results

## pytest (all pass)
```
$ python3 -m pytest experiments/ralph_outputs/J2/artifacts/test_shadow_runner.py -v
collected 6 items
test_fixture_parses_and_derives_victims PASSED   [ 16%]
test_write_actions_are_never_executed  PASSED   [ 33%]
test_classification_read_vs_write      PASSED   [ 50%]
test_assert_no_side_effects_raises_if_executed PASSED [ 66%]
test_runner_has_no_execution_imports   PASSED   [ 83%]
test_nominal_telemetry_proposes_nothing PASSED  [100%]
============================== 6 passed in 0.02s ===============================
```

## compile / syntax
```
$ python3 -m py_compile .../shadow_runner.py  ->  compile OK
```

## forbidden-execution-primitive scan
```
$ grep -nE "^import |^from |__import__|urlopen|kubectl" shadow_runner.py
import json | os | re | time | urllib.request
urllib.request.urlopen(url, ...)  # GET only, /metrics
```
No `subprocess`, no `apply_action(` call, no `__import__`, no `/ctl/` POST. The only
network primitive is a `GET /metrics` scrape. (Lines 17/28/237 matching "apply_action"
are docstring/string text, not code paths.)

## end-to-end CLI run on the recorded fixture
```
$ python3 shadow_runner.py --fixture fixture_metrics.txt
executed_count = 0
victims = ['payments', 'gateway', 'checkout']
guarantee = 0 actions executed. Shadow mode has no apply_action / kubectl /
            control-POST path; remediation is recorded, not run.
```
The runner parsed real Prometheus exposition, derived the cascade (payments=98% 5xx root;
gateway/checkout downstream victims; orders/db nominal), the proposer emitted a
`rollback_deployment` action, and the runner recorded it as `executed: false` with
`executed_count == 0`.

## BLOCKER — live incident access (honest)
The **live** path (`--prometheus <url>` against a real faulted GKE mesh, and `--live-llm`)
was **not exercised** here:
- **No live cluster:** this worker has no `KUBECONFIG` to the GKE Standard cluster, no
  `gcloud` auth (the hackathon temp account requires an interactive browser login — see
  `gcp-bench/README.md`), and no port-forward to the in-cluster Prometheus. So a *real*
  injected fault could not be observed.
- **No live LLM:** the `--live-llm` proposer needs API credits/keys (`MEMORY.md` notes
  Anthropic credits exhausted). The offline stub proposer was used instead.

Mitigation: the `FixtureSource` uses a **recorded-real** `/metrics` snapshot (byte shape
identical to `mreal/server.py`), so the parser, observation, classification, and the
safety guarantee are all exercised on real-shaped data. The live path is the *same code*
with only the byte source and proposer swapped.
