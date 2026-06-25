# A14 — SUMMARY: Time-pressure variants (budget-limited episodes) for realistic eval

## Goal
Make REx episodes bounded the way a real on-call SRE is bounded — by **wall-clock time** and
**number of remediation actions** — instead of the current flat *iteration count*.

## Finding (the gap)
The core budget mechanism (`rex/loop.py::refine_loop(budget=N)`, `rex/tree.py::rex_tree(budget=N)`)
treats `budget` purely as an iteration/candidate **count**. There is no time axis and no
cumulative-action cost: a model that converges in 9 slow calls scores the same as one that
converges in 2 fast ones. Unrealistic for time-pressured incident response.

## Deliverable (wrapper only — NO core edits)
`experiments/ralph_outputs/A14/artifacts/`:
- **`budget_wrapper.py`** — `BudgetConfig` (time_budget_s + step_budget axes) + `PRESETS`
  (`unbounded`, `relaxed`, `tight`, `pager-storm`) + `run_budgeted_episode(...)` that drives
  the unchanged `refine_loop` via a metered, budget-aware proposer; truncates at the last
  in-budget iteration and labels budget-induced escalations.
- **`test_budget_wrapper.py`** — 7 offline deterministic tests (real scenario + real loop +
  fake proposer/clock). All pass.
- **`demo_budget_variants.py`** + `demo_results.json` — runs `oom_kill` under every preset.

## Result
A slow 2-try model **clean-wins** under unbounded/relaxed/tight budgets but **escalates
(out of time)** under `pager-storm` — the realistic time-pressure signal, reproducibly
demonstrated and labeled. 7/7 tests pass offline; no `rex/*.py`/`sim/*.py` files modified.

## Status: COMPLETED
Blocker (scoped out, not faked): a *live* budgeted frontier sweep needs API access; the
harness + offline proof are complete. Integration into `rex/eval_pass_at_k.py` is documented
as a snippet (left unwired for parallel-safety).
