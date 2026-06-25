# 01 — Plan (B5: Frontier sweep with pass@k)

## Objective
`rex/frontier.py` sweeps baseline-vs-REx across 5 frontier models on a shared incident
substrate, but its headline is **mean reward per model only**. Mean reward hides
reliability: a model that scores {1.0, 1.0, 0.0} and one that scores {0.7, 0.7, 0.6}
have similar means but very different *resolve-it-when-it-matters* behavior. Deliver the
**pass@k frontier**: per (model, condition) report pass@1 / pass@2 / pass@5 with Wilson
95% CIs for both the zero-shot baseline and REx, so the headline becomes reliability and
REx's lift in reliability — not just average reward.

## Approach
- Do NOT edit `rex/frontier.py` (shared core). Write a task-namespaced, self-contained
  `frontier_pass_at_k.py` under `B5/artifacts/` that reuses the EXACT grading path of
  `rex/frontier.py` (`propose -> baseline _grade`, `rex_tree(...).best_score`) and the
  EXACT estimators of `rex/eval_pass_at_k.py` (`experiments/compute_pass_at_k.py`:
  unbiased pass@k + Wilson CI + `binary_pass`).
- Grade with the P0 **deterministic** judge (`judge_fn=None`) for reproducibility.
- Run multiple seeds per (model, scenario) so pass@k has a real sample to estimate over.
- Also report within-group reward **std** (HUD doctrine: the unit of trainability).

## Files
- CREATE `B5/artifacts/frontier_pass_at_k.py` — runnable pass@k frontier script.
- CREATE `B5/artifacts/frontier_pass_at_k_result.json` — real results (subset).
- CREATE `B5/artifacts/run.log` — captured stdout.
- Do NOT modify any `rex/*.py`, `sim/*.py`, `agent/*.py`.

## Dependencies
- `agent.llm.call` (gateway via HUD_API_KEY), `rex.harness`, `rex.loop`, `rex.scoring`,
  `rex.tree`, `experiments/compute_pass_at_k.py`. Python 3.13. `set -a; source ~/.zshrc`.

## Risks
- **Anthropic direct 400 / out of credits** (per machine memory) → restrict the real run
  to working **gateway** models (gemini-3.1-pro, deepseek-v4-pro, gpt-5.5).
- **15-min compute cap**: each seed ≈ 7s baseline + ~25s REx(budget3). Full
  5×5×5 sweep is hours. Mitigation: representative subset (2 models × 2 incidents ×
  3 seeds) + a `--time-budget-s` guard, and document the cap as a blocker.
- Small n → wide Wilson CIs. Honest; the script scales with `--seeds`.

## Success criteria
1. A runnable, syntax-clean pass@k frontier script grounded in frontier.py.
2. REAL per-model pass@1/2/5 + CI for baseline AND REx on ≥2 models, ≥2 incidents.
3. No shared core file edited. Compute cap respected and documented.
