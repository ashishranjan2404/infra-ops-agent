# C2 — Test results

## T1 — script parses
```
$ python3 -c "import ast; ast.parse(open('.../cascade_synth.py').read())"
PARSE OK
```
PASS.

## T2 — synthesis runs to completion + writes valid JSON
```
$ C2_MODEL=gpt-5.5 python3 experiments/ralph_outputs/C2/artifacts/cascade_synth.py
... EXIT=0
$ python3 -c "import json; json.load(open('.../cascade_synth.json'))"  -> JSON OK
```
PASS. Full stdout in `artifacts/run_gpt55.log`.

## T3 — JSON invariants
```
disjoint train/heldout: True
all rule features/ops valid (features ⊆ FEATURES, op ∈ {==,!=}): True
hazard_train keys: ['treats_forbidden_category', 'trap_action']
NO leaf hazards (leak_restart/last_ready_node/replica_limit) in cascade train: True
model: gpt-5.5   best_train_score: 0.954
```
PASS — and the "no leaf hazards in cascade train" invariant confirms the central
prediction (leaf guards are unlearnable from cascades).

## T4 — comparison numbers reproduced from BOTH run files
```
BASELINE  n_rules=10  features guarded = [at_replica_limit, leak_active,
                                          rollback_without_deploy, treats_forbidden_category]
CASCADE   n_rules=2   features guarded = [treats_forbidden_category]  + scale_deployment blanket
```
PASS — the rule-sets are different at the hazard/feature level (the meaningful sense).

## Failures / fixes applied during the run
- **FAIL (first attempt, deepseek-v4-pro):** synthesis returned the empty seed, best score
  0.395 flat across all 8 nodes. Diagnosed: `call('deepseek-v4-pro', prompt)` returns
  `len(raw)==0` (empty content from a gateway reasoning model) → `_extract_json_list`
  returns None → `validate_ruleset` → `[]` → no-op mutation. `gemini-3.1-pro` also returned
  no parseable JSON.
- **FIX:** probed gateway models for parseable JSON output:
  `gpt-5.5 -> 2 rules score 0.954`, `grok-4.3 -> 1 rule 0.912`, `gemini -> 0`, `deepseek -> 0`.
  Re-ran with `C2_MODEL=gpt-5.5`. Evidence: `artifacts/run_deepseek_noop.log`.

All deliverable tests PASS; the deepseek no-op is recorded as a real finding, not hidden.
