# C6 — 01 Plan

## Objective
Determine whether the **proposer base model** matters for AutoHarness-style safety-rule
synthesis (`rex/harness_synth.py`). The proposer is the LLM that acts as the *mutation
operator* in a Thompson-tree search: given the current rule-set and its training
mistakes, it proposes an edited rule-set. We hold everything else fixed (splits, labels,
evaluator, seed, budget) and vary only the proposer, then compare synthesized rule
quality on TRAIN and on HELD-OUT incidents.

## Grounding (what the code actually does)
- Proposer hook: `rex/harness_synth.py:27` `MODEL = "claude-haiku-4-5"`, consumed at
  `propose_ruleset()` (line 273) via `agent.llm.call(MODEL, ...)`. This is the ONLY
  place the base model enters synthesis.
- Search: `rex/tree.py:thompson_search(propose, evaluate, budget, seed, stop_at)`.
- Reward: `train_score()` — false-allows weighted 2x false-blocks, minus tiny
  per-condition complexity penalty. Rules are DATA, interpreted by `is_safe_synth`
  (never exec'd).
- Baseline: hand-written `is_safe` via `handwritten_pred`.
- Splits: TRAIN = 7 incidents, HELDOUT = 3 (forbidden-category hazard spans both →
  the real cross-incident generalization test).

## Approach
1. Probe model reachability (Anthropic credits, Fireworks, HUD gateway).
2. Write a task-namespaced driver (`artifacts/run_synth_models.py`) that imports
   `rex.harness_synth` and runs the full pipeline once per proposer by overriding the
   module-level `hs.MODEL`. **No core file is edited.**
3. Run 2+ reachable proposers (target: gpt-5.5, deepseek-v4-pro, minimax-m3 —
   cross-provider). Same budget=8, seed=0.
4. Compare: best TRAIN score, #nodes, rule count, TRAIN/HELDOUT accuracy & false-allows,
   vs the hand-written baseline.

## Files to create
- `experiments/ralph_outputs/C6/artifacts/run_synth_models.py` (driver)
- `experiments/ralph_outputs/C6/artifacts/synth_<model>.json` (per-model)
- `experiments/ralph_outputs/C6/artifacts/comparison.json` (combined)
- `01..10` + `SUMMARY.md` + `result.json`

## Dependencies / risks
- **Risk (materialized):** the default proposer `claude-haiku-4-5` is unreachable —
  Anthropic credit balance is too low (HTTP 400). All Anthropic models are down.
  Mitigation: use reachable gateway (gpt-5.5, deepseek) + Fireworks (minimax/glm)
  proposers; document the Anthropic blocker.
- Risk: gateway reasoning models can be slow / empty → 15-min compute cap. Mitigation:
  budget 8, 3 models, time each; fall back to fewer if needed.
- Risk: a proposer returns malformed JSON → `validate_ruleset` drops bad rules
  (fail-safe), so a weak proposer simply yields a weaker/empty rule-set — which is
  exactly the signal we want to measure.

## Success criteria
- 2+ proposer models actually run synthesis end-to-end (or documented unreachable).
- A real comparison of synthesized rule-sets + TRAIN/HELDOUT metrics per proposer.
- Zero edits to shared core files; driver is runnable and reproducible.
