# A14 — Time-pressure variants (budget-limited episodes) for realistic eval — PLAN

## Objective
Add **realistic, time-pressured episode variants** to the REx eval so an incident is
bounded the way a real on-call SRE is bounded: by **wall-clock time** (an SLA / deadline)
and by the number of **remediation actions** that can be safely fired — NOT by the current
flat *iteration count* (`budget=N`). A model that converges slowly or via many actions
should be penalized relative to one that converges fast, which the current loop cannot
express.

## Current budget mechanism (from inspection)
- `rex/loop.py::refine_loop(scenario, budget=6, ...)` — `budget` is the **max number of
  refinement iterations**. Loop: propose → run_plan → score → feedback → repeat; break on a
  clean win. No notion of time or per-action cost.
- `rex/tree.py::rex_tree(...budget=N...)` — same: `budget` caps the **number of tree nodes**
  (candidates expanded). Again purely a count.
- `rex/harness.py::run_plan` — applies a plan's actions through the sim; gates each via
  `is_safe`. Cost of a plan ≈ number of remediation actions it fires.
- `rex/eval_pass_at_k.py` — runs conditions with `budget=N=4`; reward is binary pass.

So **"budget" today == iteration count**. There is no time axis and no cumulative-action axis.

## Approach (wrapper, NO core edits)
Build `budget_wrapper.py` in my artifacts dir that wraps the unchanged `refine_loop`:
1. **Wrap the proposer**: time each model call; accumulate latency into an episode
   time budget; count the plan's remediation actions into a step budget.
2. **Pre-flight cutoff**: before starting an iteration, if a budget axis is already
   exhausted, raise `BudgetExhausted` to stop the loop at the last in-budget iteration.
3. **Lossless truncation**: capture each completed iteration via the loop's `log=` hook so
   a truncated episode still reports `best_score / resolved / clean_win / outcome`.
4. **Named presets** (`unbounded`, `relaxed`, `tight`, `pager-storm`) for eval sweeps.

## Files to create (all under experiments/ralph_outputs/A14/)
- `artifacts/budget_wrapper.py` — `BudgetConfig`, `BudgetMeter`, `budgeted_proposer`,
  `run_budgeted_episode`, `PRESETS`.
- `artifacts/test_budget_wrapper.py` — offline deterministic pytest (real scenario + real
  loop + fake proposer + fake clock).
- `artifacts/demo_budget_variants.py` — runs one scenario under every preset, prints a table.

## Dependencies
- `rex.loop.refine_loop`, `rex.harness.load_scenario/run_plan`, deterministic judge
  (`rex.scoring.default_judge`). All offline once the LLM proposer is mocked.

## Risks
- The loop's `propose_fn` signature `(scenario, prior_feedback)` must be matched exactly.
- Raising inside the proposer could discard already-run iterations → mitigated by the
  `log=` capture + result reconstruction.
- Time as "sum of proposer latencies" ignores sim time — acceptable: the model call
  dominates real cost.

## Success criteria
- Wrapper imposes time AND step limits without editing any `rex/*.py`.
- A scenario that needs ≥2 tries clean-wins under a loose budget but **escalates** under a
  tight one (demonstrated in the demo).
- All unit tests pass offline (no API key).
