# C6 — 06 Implementation

## What I built
A task-namespaced driver that runs the existing `rex/harness_synth.py` synthesis
pipeline once per **proposer model**, varying ONLY the proposer (the LLM mutation
operator) and holding the search, splits, labels, evaluator, and seed fixed.

### Artifacts (all under `experiments/ralph_outputs/C6/artifacts/`)
- `run_synth_models.py` — driver. Overrides `rex.harness_synth.MODEL` per model,
  restores it in `finally`. **No shared core file edited.**
- `synth_gpt-5.5.json`, `synth_deepseek-v4-pro.json`, `synth_minimax-m3.json` — per-model
  results (best train score, node trajectory, synthesized rules, TRAIN/HELDOUT confusion,
  held-out FA/FB tuples).
- `comparison.json` — combined results across all proposers.

### The proposer hook
`rex/harness_synth.py:27` `MODEL` → consumed only by `propose_ruleset()` (line 273) via
`agent.llm.call(MODEL, ...)`. Overriding the module global is sufficient and surgical;
the search (`rex/tree.py:thompson_search`), labels (`labeled_examples`), evaluator
(`train_score`), and baseline (`handwritten_pred`) are untouched.

### Reachability finding (blocker handled, not faked)
The **intended** proposer `claude-haiku-4-5` — and ALL Anthropic models — are
unreachable: `400 invalid_request_error … "Your credit balance is too low"`. So this
became a cross-provider study using reachable proposers via the HUD gateway + Fireworks:
`gpt-5.5`, `deepseek-v4-pro`, `minimax-m3`. (`glm-5p2` also reachable; 3 proposers was
enough to answer the question under the cap.)

## Run config
budget=8 nodes/proposer, seed=0, TRAIN=7 incidents (101 labels), HELDOUT=3 (39 labels).
Total wall ≈ 347s (gpt-5.5 102s, deepseek 239s, minimax 5s) — under the 15-min cap.

## Headline result (the answer to "does the proposer matter?")
**Yes — dramatically.** Same search, same budget, same data; only the proposer changed:

| proposer | best train | rules | TRAIN acc | HELDOUT acc | HELDOUT FA | HELDOUT FB |
|---|---|---|---|---|---|---|
| gpt-5.5 | 0.798 | 3 | 0.762 | 0.641 | 4 | **10** |
| deepseek-v4-pro | 0.464 | **0** | 0.634 | 0.667 | **13** | 0 |
| minimax-m3 | 0.781 | 3 | 0.832 | **0.897** | 4 | 0 |
| hand-written `is_safe` (baseline) | — | — | 0.842 | 0.949 | 2 | 0 |

- **deepseek-v4-pro produced an EMPTY rule-set** (every node scored the 0.4638 seed
  score → it never proposed a valid improving rule). Its held-out FA=13 is just the
  empty-harness "allow everything" failure. Proposer competence is the difference
  between a working harness and no harness.
- **minimax-m3 is the best proposer**: 0.897 held-out accuracy, 0 false-blocks, and it
  discovered the cleanest correct rule-set — the three general state-conditional rules
  (`treats_forbidden_category`, `leak_active`, `rollback_without_deploy`) with NO
  over-broad tool bans. It approaches but does not match the hand-written baseline.
- **gpt-5.5 over-blocks**: it added an over-broad rule banning
  `restart_pod/restart_service/scale_deployment/failover_service` with NO conditions,
  producing 10 held-out false-BLOCKS — exactly the failure PSRE flagged in the grill
  (trading false-allows for blocking correct fixes). High train score (0.798) masked it.
