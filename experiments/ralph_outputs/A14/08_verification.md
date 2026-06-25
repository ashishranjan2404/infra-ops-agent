# A14 — 08 Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|---|---|---|
| Imposes **time** limits without core edits | YES | `time_budget_s` axis; test 5 truncates after 1 call; no `rex/*.py` modified |
| Imposes **step/action** limits without core edits | YES | `step_budget` axis + `_action_cost`; test 4 truncates before the fix |
| A ≥2-try scenario wins under loose budget, **escalates** under tight | YES | demo: win under unbounded/relaxed/tight, escalate under `pager-storm` |
| All unit tests pass offline (no API key) | YES | 7/7 pytest, deterministic via injected `cost_fn` |
| No shared core file edited | YES | `git status` shows only new files under `experiments/ralph_outputs/A14/` |
| Budget-induced escalation is **labeled** (grill/ouroboros requirement) | YES | `budget_truncated`, `truncation_reason`, full per-iter meter in result |

## Are outputs REAL (not placeholder)?
Yes. `budget_wrapper.py` drives the actual `rex.loop.refine_loop` over a real YAML scenario
through the real sim and deterministic judge. The demo's table and `demo_results.json` are
produced by an actual run, not hand-written. The win→escalate flip is a genuine consequence of
the budget cutoff, reproducible by re-running the demo.

## Confirm no core files touched
```
$ git status --porcelain experiments/ralph_outputs/A14
?? experiments/ralph_outputs/A14/   # entirely new, untracked
```
No entries under `rex/`, `sim/`, `agent/`, or `experiments/*.py` from this task.

## Residual gaps (carried to 09)
- Uniform step cost (no per-action risk weighting) — v2.
- Live frontier sweep under budgets not run (needs API access) — documented follow-up.
- The integration snippet for `eval_pass_at_k.py` is documented but not wired (parallel-safety).
