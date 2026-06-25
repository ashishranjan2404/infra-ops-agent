# 08 — Verification against success criteria

| # | Success criterion (from 01) | Met? | Evidence |
|---|---|---|---|
| 1 | Runnable, syntax-clean pass@k frontier script grounded in `rex/frontier.py` | YES | `py_compile` OK; reuses frontier.py's `_propose`/`_grade`/`rex_tree` grading path verbatim and `compute_pass_at_k` estimators (the same source `rex/eval_pass_at_k.py` uses). |
| 2 | REAL per-model pass@1/2/5 + CI for baseline AND REx on ≥2 models, ≥2 incidents | YES | `frontier_pass_at_k_result.json`: deepseek-v4-pro & gpt-5.5, oom_kill & gcp_service_control, 3 seeds each, both conditions, 0 errors. |
| 3 | No shared core file edited; compute cap respected + documented | YES | Only files written are under `B5/artifacts/`. Run finished in 558.7s < 15-min cap; subset + cap blocker documented in 07/09. |

## Are the outputs real (not placeholder)?
- Numbers come from live gateway model calls (deepseek-v4-pro, gpt-5.5) graded by the real
  deterministic judge through `sim/engine.py` — not hand-written. `run.log` shows the live
  per-incident lines accumulating over ~9 min; `n_errors=0`.
- The pass@k values are internally consistent: e.g. deepseek baseline rewards
  {oom: mean 0.60, gcp: mean 0.55} → 1 of 6 episodes ≥ 0.8 → pass@1 = 0.167, Wilson CI
  [0.03, 0.56]; REx 6/6 ≥ 0.8 → pass@1 = 1.0, CI [0.61, 1.0]. Matches the printed table.
- Unit tests independently verify the estimator wiring (6/6) without network.

## Does it answer the task?
Task B5 = "run the frontier sweep with pass@k (currently only mean reward for 5 models)."
Delivered: the frontier sweep now reports **pass@1/2/5 + Wilson CI + std + n** per model per
condition, headlined by **pass@1 and pass@1 lift**, replacing the mean-reward-only headline.
Real results delivered for a 2-model representative subset; the script runs the full 5-model
roster unchanged when given more wall budget (`--models` defaults to the frontier.py roster).
The compute-cap reduction (5→2 models) is the only gap, and it is the documented blocker.
