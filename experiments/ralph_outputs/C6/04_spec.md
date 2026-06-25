# C6 — 04 Spec

## Proposer hook (the thing under test)
`rex/harness_synth.py`:
- `MODEL: str = "claude-haiku-4-5"` (line 27) — module global.
- `propose_ruleset(parent_node, train_ex) -> list[rule]` (line 255) calls
  `agent.llm.call(MODEL, prompt, max_tokens=1500, temperature=0.4)` (line 273).
  This is the SOLE entry point of the base model into synthesis.

## Driver: `artifacts/run_synth_models.py`
### `run_for_model(model: str, budget: int = 8, seed: int = 0) -> dict`
- Saves `hs.MODEL`, sets `hs.MODEL = model`, runs pipeline, restores in `finally`.
- Builds `train_ex`, `held_ex` from `hs.labeled_examples` over `hs.TRAIN`/`hs.HELDOUT`.
- `thompson_search(propose=λp: hs.propose_ruleset(p, train_ex),`
  `evaluate=λrs: hs.train_score(rs, train_ex), budget, seed, stop_at=1.0)`.
- Computes `hs.confusion(best, train_ex)`, `hs.confusion(best, held_ex)`,
  `hs.confusion_pred(hs.handwritten_pred, ...)` for baseline.
- **Returns dict:**
  ```
  {model, elapsed_s, budget, n_nodes, best_train_score, node_scores[],
   n_rules, rules[<rule>], train{...}, heldout{...},
   handwritten_train{...}, handwritten_heldout{...},
   heldout_false_allow[(incident,tool,target,hazard)],
   heldout_false_block[(...)]}
  ```
  where each metrics block ∈ {accuracy, false_allow, false_block, false_allow_rate, n}.

### `main()`
- `models = argv[1:] or [gpt-5.5, deepseek-v4-pro, minimax-m3]`.
- Per model: `run_for_model`, write `synth_<model>.json` (slashes→`_`); on exception
  record `{model, error}` and continue (so one dead provider doesn't kill the study).
- Write `comparison.json = {results: [...]}`; print comparison table + baseline row.

## Rule data structure (validated, never exec'd)
`{"match_tools":[str,...], "conditions":[{"feature":str,"op":"=="|"!=","value":bool|str}],`
` "block":bool, "reason":str}`. `validate_ruleset` keeps only KNOWN
features (`FEATURES`) / ops (`_OPS`); a rule with no match criteria is dropped
(would block everything).

## Test cases / validation
- T1 (syntax/import): `python3 -c "import ast; ast.parse(open(driver).read())"` and a
  dry import of the driver module.
- T2 (override safety): assert `hs.MODEL` is restored to `claude-haiku-4-5` after a run.
- T3 (determinism of evaluator): `train_score` of a fixed rule-set is stable across
  calls (pure function over labels) — sanity that only the proposer is stochastic.
- T4 (e2e): ≥2 proposers produce a non-error result row with a rule-set and held-out
  metrics. Baseline row present.

## Output file formats
- `synth_<model>.json`: single result dict (above).
- `comparison.json`: `{"results": [result|error, ...]}`.

## Compute contract
- Budget 8 nodes/model, 3 models, single seed. Target < 15 min wall. Each gateway
  reasoning run observed ≈ 100s.
