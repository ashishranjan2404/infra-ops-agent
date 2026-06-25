# B5 — Frontier sweep with pass@k — SUMMARY

## Task
`rex/frontier.py` sweeps baseline-vs-REx across frontier models but headlines **mean reward
only**. Add the **pass@k** frontier (pass@1/2/5 + Wilson CI), grounded in
`rex/frontier.py` / `rex/hud_frontier.py`.

## Deliverables (all under experiments/ralph_outputs/B5/, no shared core edited)
- artifacts/frontier_pass_at_k.py — runnable pass@k frontier sweep. Reuses frontier.py's
  exact grading path (zero-shot baseline + rex_tree(...).best_score, deterministic judge)
  and the canonical experiments/compute_pass_at_k.py estimators. Reports per (model,
  condition): pass@1 (+Wilson CI), pass@2, pass@5, mean, std, n; plus per-model pass@1 lift.
- artifacts/test_frontier_pass_at_k.py — 6 unit tests (6/6 pass), incl. the n<k edge.
- artifacts/frontier_pass_at_k_result.json + artifacts/run.log — REAL subset run.
- 01..10 step files.

## Real result (subset, 558.7s ~= 9.3 min < 15-min cap, 0 errors)
2 working gateway models x 2 incidents (oom_kill, gcp_service_control) x 3 seeds, REx budget 3:

| model | baseline pass@1 [CI] | REx pass@1 [CI] | pass@1 lift |
|---|---|---|---|
| deepseek-v4-pro | 0.167 [0.03, 0.56] | 1.000 [0.61, 1.00] | +0.833 |
| gpt-5.5 | 0.000 [0.00, 0.39] | 1.000 [0.61, 1.00] | +1.000 |

**Key finding:** gpt-5.5 zero-shot has positive mean reward (0.35) but pass@1 = 0.000 —
it never actually resolves an incident first-try; REx lifts it to pass@1 = 1.000. Mean-
reward-only reporting (the old headline) hides this; pass@k surfaces it.

## Status: COMPLETED (with documented compute-cap blocker)
Full plan + spec + runnable script + passing unit tests + REAL frontier pass@k results.
Blocker: 15-min cap -> ran 2 of 5 models (Anthropic-direct = HTTP 400/out-of-credits;
gemini dropped for latency) on 2 of 5 incidents. The script runs the full 5-model roster
unchanged with more wall budget.
