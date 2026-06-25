# A14 — 04 Technical Spec

## Module: `artifacts/budget_wrapper.py`

### Data structures
```python
class BudgetExhausted(Exception):
    reason: str                       # set on raise

@dataclass
class BudgetConfig:
    time_budget_s: Optional[float] = None   # wall-clock seconds, None/0 = unlimited
    step_budget:   Optional[int]   = None   # cumulative remediation actions, None/0 = unlimited
    iter_cap:      int             = 8      # hard ceiling passed to the loop's `budget` arg
    label:         str             = "unbounded"
    def is_bounded(self) -> bool            # True iff either axis is set

@dataclass
class BudgetMeter:
    cfg: BudgetConfig
    clock: Callable[[], float] = time.monotonic
    time_spent_s: float = 0.0
    steps_spent:  int   = 0
    iters_started: int  = 0
    stopped_reason: Optional[str] = None
    per_iter: list = []                      # [{iter, latency_s, steps, cum_time_s, cum_steps}]
    def _over_budget(self) -> Optional[str]  # reason string or None
    def report(self) -> dict
```

### Function signatures
```python
def _action_cost(plan: dict) -> int
    # count of actions with a truthy "tool"; 0 for non-dict / empty

def budgeted_proposer(base_propose_fn, meter, cost_fn=None) -> Callable
    # returns _propose(scenario, prior_feedback=None) -> plan
    # PRE-FLIGHT: if meter._over_budget(): set stopped_reason; raise BudgetExhausted
    # else: time the call via meter.clock (or cost_fn), add latency+steps to meter, return plan
    # POST-FLIGHT: if now over budget, record stopped_reason (next call aborts)

def run_budgeted_episode(scenario, cfg, base_propose_fn,
                         refine_loop_fn=None, clock=time.monotonic,
                         cost_fn=None, **loop_kwargs) -> dict
    # default refine_loop_fn = rex.loop.refine_loop
    # wraps proposer; captures iterations via loop's log= hook
    # on BudgetExhausted -> reconstruct result from captured iterations
    # returns loop result + {"budget": meter.report(),
    #                        "budget_truncated": bool, "truncation_reason": str?}

def _result_from_iterations(scenario, iterations) -> dict
    # rebuild refine_loop-shaped dict: best_score/best_iter/resolved/clean_win/outcome

PRESETS: dict[str, BudgetConfig]
    # unbounded, relaxed(60s/8), tight(20s/4), pager-storm(8s/2)
```

### Cost model (precise)
- **Step cost** of a plan = number of actions with a truthy `tool` (`_action_cost`).
- **Time cost** of an iteration = `cost_fn(t0,t1)` if given, else `t1-t0` from `meter.clock`.
- Episode `time_spent_s` / `steps_spent` = cumulative sums across iterations.

### Cutoff semantics
- Pre-flight: an iteration starts only if `_over_budget()` is None *before* it runs.
  ⇒ the budget is a **soft ceiling at the boundary**: the iteration that crosses the line is
  allowed to finish, the *next* one is refused. This matches "you finish the action you
  started, then the clock stops you."
- A refused iteration ⇒ `budget_truncated=True`, `outcome="escalated"`.

### Result contract (augmented refine_loop dict)
```jsonc
{ "scenario": "...", "iterations": [...], "best_score": 0.0, "best_iter": -1,
  "resolved": false, "clean_win": false, "outcome": "resolved|escalated",
  "budget_truncated": true,
  "truncation_reason": "step_budget exceeded: 1 >= 1",
  "budget": { "label","time_budget_s","step_budget","time_spent_s","steps_spent",
              "iters_started","stopped_reason","per_iter":[...] } }
```

## Tests (`test_budget_wrapper.py`, offline)
1. `_action_cost` counts only real actions (empty/junk/non-dict → handled).
2. `BudgetMeter._over_budget` triggers on each axis at the threshold.
3. unbounded episode converges in 2 iters, not truncated.
4. `step_budget=1` truncates before the fix → escalated, 1 iteration retained.
5. `time_budget_s=5, cost=5s/call` truncates after 1 call → escalated.
6. generous budget allows convergence, `steps_spent==2`.
7. presets are monotonic in pressure; `unbounded.is_bounded() is False`.

## Demo (`demo_budget_variants.py`)
Runs `oom_kill` under all presets with `cost_fn = 9s/call`; prints a table and writes
`demo_results.json`. Expected: win under unbounded/relaxed/tight, **escalate under pager-storm**.
