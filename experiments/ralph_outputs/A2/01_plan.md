# A2 — 01 Plan

## Objective
Complete the **750-episode ablation** (5 conditions x 30 incidents x 5 seeds) using a
**faster / cheaper proposer model** than the original `glm-5p2`, whose prior run was
killed at **175/750 episodes** (loop wrapper SIGTERM, `rc=143`) — before the expensive
`rex` and `rex_no_oracle` conditions ran at all.

## What "the ablation" is (grounded in the repo)
- `rex/eval_pass_at_k.py::run_eval` is the canonical engine: it runs each
  `(condition, incident, seed)` job, scores with the **P0 deterministic judge**
  (`rex/scoring.py`, no LLM judge -> reproducible), aggregates pass@1/2/5 with Wilson
  CIs, and supports a **crash-survival checkpoint** (`ckpt=`).
- 30 incidents = `per_family=10` over the 3 families (`simple`/`cascade`/`novel`),
  confirmed: the repo has 12 simple / 20 cascade / 10 novel scenarios.
- 5 conditions: `zero_shot`, `best_of_n`, `retry_realistic`, `rex`, `rex_no_oracle`.
- `rex/run_ablation_v2.py` consumes the resulting JSON and adds McNemar paired tests.

## Why the prior run failed (root cause, not a guess)
`experiments/results/ablation_pass_at_k_glm-5p2.json.partial` + `.log` show:
attempt 1 reached 150/750 in ~298s then was killed (`rc=143`); attempt 2 resumed at
175/750 and was also killed. The per-call latency of glm-5p2 is fine (~2.3s); the
problem is **total wall-clock** for 750 episodes (the `rex`/`rex_no_oracle` conditions
each do up to N=4 sequential proposer calls per episode) against a fixed loop timeout.

## Approach
Deliver a **task-namespaced runner** that:
1. Defaults to a **faster, reliable proposer** chosen by measurement, not assumption.
2. Adds a **wall-clock budget** (`--max-seconds`) that stops cleanly and always flushes
   the checkpoint — a SIGTERM can never lose progress; re-run resumes.
3. Emits a **partial-aware report**: real pass@k for whatever completed + an honest
   `completed N / 750` line. No fabricated numbers if blocked.

## Model selection (measured, see 07)
Probed candidates with one real call each:
- `claude-haiku-4-5` -> 400 (model id retired on this account) — unusable.
- `minimax-m3` -> returns 0 chars (empty completion) — unusable as proposer.
- `gemini-3.1-pro` -> ~14s/call — too slow.
- **`deepseek-v4-pro` -> ~2-8s/call, parses to a valid plan, scores deterministically** — chosen.

## Files to create (NEW, task-namespaced only)
- `artifacts/run_ablation_fast.py` — the runner (imports `run_eval`, does not edit it).
- `artifacts/ablation_pass_at_k_deepseek-v4-pro.json` — the result (full or partial).
- The 10 step docs + `SUMMARY.md` + `result.json`.

## Dependencies
`requests`, the repo `.env` keys (ANTHROPIC/FIREWORKS/HUD all present), the existing
`rex/*` modules. No vLLM on this box (`vllm not found`) — so "faster model" = a fast
**API** model via the HUD gateway, which is the honest available path.

## Risks
- Gateway rate limits / transient 5xx -> mitigated by the in-engine 1-retry proposer +
  checkpoint resume + `n_errors` reporting.
- Full 750 may still exceed a single Ralph-loop turn -> mitigated by `--max-seconds`
  + resume; if so I deliver a correct runner + real partial numbers + honest blocker.

## Success criteria
1. A runnable, syntax-valid, import-correct runner that reproduces the 750-episode
   design with a faster model.
2. Real deterministic pass@k numbers for as many episodes as the budget allows
   (ideally the full 750), checkpointed and resumable.
3. No shared core file edited; no fabricated results.
