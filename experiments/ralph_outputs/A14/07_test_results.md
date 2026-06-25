# A14 — 07 Test Results

## Unit + integration tests — PASS (7/7, offline, no API key)
```
$ python3 -m pytest experiments/ralph_outputs/A14/artifacts/test_budget_wrapper.py -v
platform darwin -- Python 3.13.7, pytest-9.0.2
collected 7 items
test_action_cost_counts_only_real_actions PASSED        [ 14%]
test_meter_time_and_step_thresholds       PASSED        [ 28%]
test_unbounded_episode_converges          PASSED        [ 42%]
test_step_budget_truncates_episode        PASSED        [ 57%]
test_time_budget_truncates_episode        PASSED        [ 71%]
test_generous_budget_allows_convergence   PASSED        [ 85%]
test_presets_monotonic_pressure           PASSED        [100%]
============================== 7 passed in 0.04s ===============================
```
These use the REAL `oom_kill` scenario + REAL `rex.loop.refine_loop` + deterministic judge,
with a canned proposer and a fixed `cost_fn`. No network involved.

## Syntax / compile check — PASS
```
$ python3 -m py_compile experiments/ralph_outputs/A14/artifacts/*.py
all 3 modules compile OK
```

## Demo run — PASS (shows the headline flip)
```
$ python3 experiments/ralph_outputs/A14/artifacts/demo_budget_variants.py
variant      t_budget s_budget iters  t_spent steps    outcome   win
--------------------------------------------------------------------
unbounded        None     None     2     18.0     2   resolved  True
relaxed          60.0        8     2     18.0     2   resolved  True
tight            20.0        4     2     18.0     2   resolved  True
pager-storm       8.0        2     1      9.0     1  escalated False
clean win under: ['unbounded', 'relaxed', 'tight']
escalated (out of budget) under: ['pager-storm']
```
**Interpretation**: a slow on-call model (9s/call) that needs 2 tries to converge clean-wins
under unbounded/relaxed/tight budgets but **runs out of time and escalates** under
`pager-storm` (8s budget allows only 1 call). This is exactly the realistic time-pressure
signal A14 was asked to add — and it is *labeled* (`budget_truncated=True`,
`truncation_reason="time_budget exceeded: 9.00s >= 8.00s"`).

## Fixes applied during development
1. Initial design raised `BudgetExhausted` and lost the loop's accumulated iterations →
   refactored to capture iterations via the loop's `log=` hook + `_result_from_iterations`.
2. `_REPO` path used 3× `..` (resolved to `/Users/mei/rl/experiments`) → fixed to 4× `..`
   so the modules import `rex` from any cwd.
3. Time-budget test expectation off-by-one at the boundary (6s vs 5s budget with 5s/call) →
   corrected to match the documented soft-ceiling-at-boundary semantics.

## Blockers
None for the deliverable. A *live* budgeted frontier sweep (real LLM under each preset) needs
an API key + model access and is left as a documented follow-up (see 09_critique) — the
harness + offline demo are complete and real.
