# B14 — Implementation

All artifacts are task-namespaced under `experiments/ralph_outputs/B14/artifacts/`.
**No shared core file was edited.** The cost model derives its call-shape constants by *reading*
`rex/eval_pass_at_k.py`, `rex/scoring.py`, and `rex/loop.py` — it does not modify them.

## Files built (real, runnable)
| File | Lines | Purpose |
|---|---|---|
| `artifacts/cost_model.py` | 166 | Price table (real Claude + assumed gateway slugs) + per-condition call-shape + `estimate_job_cost()`. |
| `artifacts/cost_per_dollar.py` | 181 | Ingests the real A1/A2 pass@1 result JSONs, computes pass@1-per-dollar, emits table (md + json). |
| `artifacts/test_cost_model.py` | 79 | 9 unit tests for the cost model. |
| `artifacts/cost_efficiency.json` | generated | Machine-readable: metric def, sources, price table, proposer calls, 10 rows. |
| `artifacts/cost_efficiency_table.md` | generated | Human-readable cost-efficiency table + best-operating-point table. |

## Cost model (grounded in real code)
- **Prices** ($/1M in/out): Opus 4.8 `$5/$25`, Sonnet 4.6 `$3/$15`, Haiku 4.5 `$1/$5` — REAL
  (Anthropic price sheet). Gateway/Fireworks roster slugs (glm-5p2, deepseek-v4-pro, gpt-5.5,
  gemini-3.1-pro, grok-4.3, minimax-m3) are fictional in this repo, so their prices are
  **documented assumptions** flagged `assumed=True` with a `note`.
- **Call shape** (proposer LLM calls/job), read off `rex/eval_pass_at_k.py` (`N=4`):
  `zero_shot=1`, `best_of_n=4`, `retry_realistic≈2.3` (early-exit, modelled expected value),
  `rex=4`, `rex_no_oracle=4`.
- **Judge = $0**: `score_plan` is the deterministic P0 simulator scorer — no LLM call. Exposed as
  overridable `JUDGE_CALLS=0`; the LLM-judge path (`max_tokens=8`) is documented for completeness.
- **Token budgets**: output `1400` (real proposer `max_tokens`) x `0.6` assumed utilization;
  input `1200` (assumed prompt size). All named constants.

## Data ingested (REAL artifacts, not placeholders)
- `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json` (glm-5p2, 42 incidents,
  5 conditions, 3 seeds, n_jobs=630).
- `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json`
  (deepseek-v4-pro, 30 incidents, 5 conditions, 5 seeds, n_jobs=750).

## Headline result (computed, real)
At equal cost (4 proposer calls), **rex buys 0.90 pass@1 vs best_of_n's 0.34** — same dollars,
2.6x the pass rate. rex's pass@1-per-$ (87.31, glm-5p2) essentially matches zero_shot's (89.64)
while delivering ~4x the absolute pass rate, so **rex is the efficient frontier point at high
pass@1**, not a cost loser. Full table in `cost_efficiency_table.md`.

## Proposed change to a shared file (NOT applied)
The clean upgrade is to log real token usage in `rex/eval_pass_at_k.py` so cost stops being
estimated. That edits a shared core file, so per the brief I did NOT apply it — documented here as
the follow-up: have `make_proposer` capture `usage` from `agent/llm.py:call` and accumulate
`prompt_tokens`/`completion_tokens` per job into the result JSON. Then `cost_per_dollar.py` reads
measured tokens instead of the call-shape model (the script is already structured to swap that in).
