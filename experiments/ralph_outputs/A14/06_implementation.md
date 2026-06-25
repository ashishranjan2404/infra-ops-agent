# A14 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/A14/artifacts/`, NO core edits)

### `budget_wrapper.py` (≈210 lines)
The deliverable. Imposes time/step budget limits on an unchanged `rex.loop.refine_loop`:
- `BudgetExhausted(reason)` — raised on pre-flight when an axis is exhausted.
- `BudgetConfig(time_budget_s, step_budget, iter_cap, label)` + `is_bounded()`.
- `PRESETS` — `unbounded`, `relaxed`(60s/8 steps), `tight`(20s/4), `pager-storm`(8s/2).
- `BudgetMeter` — cumulative time/steps/iters, `_over_budget()` reason, `report()`, per-iter log.
- `_action_cost(plan)` — step cost = number of actions with a truthy `tool`.
- `budgeted_proposer(base_propose_fn, meter, cost_fn=None)` — wraps the proposer:
  pre-flight budget check (raise if exhausted) → time the call (real `clock` or injected
  `cost_fn`) → accumulate latency + step cost → return plan.
- `run_budgeted_episode(scenario, cfg, base_propose_fn, refine_loop_fn=None, clock=...,
  cost_fn=..., **loop_kwargs)` — drives the real loop with the wrapped proposer, captures
  every completed iteration via the loop's `log=` hook, and on `BudgetExhausted` rebuilds a
  consistent result via `_result_from_iterations`. Appends `budget`, `budget_truncated`,
  `truncation_reason` to the loop's normal result dict.

### `test_budget_wrapper.py` (7 tests, fully offline)
Uses a REAL scenario (`oom_kill` from YAML) + the REAL `refine_loop` + deterministic judge,
with a FAKE canned proposer and a FAKE per-call `cost_fn`. No API key, no network.

### `demo_budget_variants.py`
Runs `oom_kill` under every preset with a slow (9s/call) 2-try model; prints a table and
writes `demo_results.json`.

## How it integrates with the existing eval (documented, not wired into core)
`rex/eval_pass_at_k.py` condition functions take `(scenario, seed, propose)`. To run a
budgeted condition you wrap the inner episode, e.g.:
```python
from budget_wrapper import PRESETS, run_budgeted_episode
def c_rex_budgeted(sc, seed, propose):
    res = run_budgeted_episode(sc, PRESETS["tight"], base_propose_fn=propose)
    return res["best_score"]
```
This is shown as a snippet only — I did NOT edit `eval_pass_at_k.py` (parallel-safety rule).
A patch wiring it in is described but left for an integration task with API access.

## Why a wrapper (not a core edit)
The brief forbids editing `rex/*.py`. The budget is enforced entirely through the proposer
(`propose_fn`) and the loop's public `log=`/`budget=` parameters, so the frozen env is
untouched and many workers can run in parallel safely.
