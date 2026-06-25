# B14 — Cost-Normalized Metric (pass@1 per dollar) — Plan

## Objective
Produce a **cost-efficiency** metric for the SRE-Degrees REx evaluation: `pass@1 per dollar
of API spend`. This lets us compare conditions (zero_shot / best_of_n / retry_realistic /
rex / rex_no_oracle) and models not just on accuracy but on accuracy *bought per dollar* —
the number that actually matters for choosing an operating point.

## Why this matters
The headline result is "REx hits 0.90 pass@1 vs 0.23 zero-shot". But REx issues *many* LLM
calls per incident (Thompson-sampling tree over candidate refinements + a judge), while
zero_shot issues one. If REx costs 8x the tokens for 4x the pass rate, the cost-normalized
picture is different. A reviewer will ask for exactly this. No artifact in the repo computes it.

## Approach
1. **Token/cost model** (`cost_model.py`): a per-model price table (`$/1M input`, `$/1M output`)
   + a per-condition *call-shape* model (how many proposer calls + judge calls each condition
   issues per job, and the token budget per call). Real model prices for Claude come from the
   Anthropic price sheet (Opus 4.8 $5/$25, Sonnet 4.6 $3/$15, Haiku 4.5 $1/$5 per 1M in/out).
   Gateway/Fireworks roster models (glm-5p2, deepseek-v4-pro, …) are fictional slugs in this
   repo's roster — for those I use **documented assumptions** (a mid-tier $/token), clearly
   flagged as assumptions, not measured.
2. **Compute script** (`cost_per_dollar.py`): load the available pass@1 result JSONs
   (`experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json`,
   `.../A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json`), read `by_condition[*].overall.pass@1`,
   `n`, `seeds`, `n_jobs`, `elapsed_s`; estimate $ per job from the cost model; emit
   `pass@1 / $-per-incident` = the cost-efficiency number.
3. **Emit** a cost-efficiency table (markdown + JSON) and run it.

## Files to create (all task-namespaced, no shared edits)
- `B14/artifacts/cost_model.py` — price table + call-shape model + `estimate_job_cost()`.
- `B14/artifacts/cost_per_dollar.py` — loads result JSONs, computes metric, writes table.
- `B14/artifacts/cost_efficiency_table.md` — human-readable table (generated).
- `B14/artifacts/cost_efficiency.json` — machine-readable results (generated).
- `B14/artifacts/test_cost_model.py` — unit tests for the cost model.

## Dependencies
- Python 3.13 stdlib only (json, dataclasses, pathlib). No network, no API calls.

## Risks
- **Tokens are NOT logged** in any result JSON (verified: grep for prompt_tokens/usage finds
  nothing in the pass@1 artifacts). So $ is *estimated* from `max_tokens` budgets in the code
  (`rex/loop.py` proposer max_tokens=600; `rex/eval_pass_at_k.py` proposer max_tokens=1400;
  `rex/scoring.py` judge max_tokens=8) + assumed input sizes + per-condition call counts. This
  is a **model**, documented as such — not a measurement. This is the honest path the brief
  endorses (token counts if logged, else documented assumptions).
- Fictional roster slugs => prices for non-Claude models are assumptions.

## Success criteria
- A runnable script that ingests the real result JSONs and emits a cost-efficiency table with a
  pass@1-per-dollar column per (model, condition).
- Cost model is unit-tested and the script runs clean producing real numbers (not placeholders).
- Assumptions are explicit and overridable.
