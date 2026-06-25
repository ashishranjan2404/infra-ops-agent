# C8 — 04 Spec

## Data structures (reused from rex/harness_synth.py, NOT redefined)
- **rule** (DATA): `{"match_tools": [str], "conditions": [{"feature","op","value"}],
  "block": bool, "reason": str}`. Interpreted by `is_safe_synth`; never exec'd.
- **example**: `{"incident","tool","target","features":{...},"should_block":bool,
  "hazard":str}` from `labeled_examples(name)`.
- **FEATURES** (the only legal `feature` values): `tool, treats_forbidden_category,
  leak_active, last_ready_node_op, at_replica_limit, rollback_without_deploy`.

## The 4th candidate rule (the artifact under test)
```json
{"match_tools": ["drain_node","cordon_node"],
 "conditions": [{"feature":"last_ready_node_op","op":"==","value":true}],
 "block": true,
 "reason": "draining/cordoning the last Ready node takes the service fully down — escalate instead"}
```
Rationale: mirrors `rex/harness.py:is_safe` Layer-2 `draining_last_ready_node` block,
expressed purely over the existing `last_ready_node_op` feature so it survives
`validate_ruleset`.

## Function signatures (artifacts/rule4_candidate.py)
- `load_v2_rules() -> list` — the 3-rule v2 baseline from `rex/runs/harness_synth_v2.json`.
- `evaluate(rules: list, examples: list) -> dict` — `{accuracy, false_allow,
  false_block, n}` via `rex.harness_synth.confusion`.
- `main() -> int` — runs all splits, writes `rule4_result.json`, prints summary.
- module const `RULE4: dict` — the candidate above.

## Report format (rule4_result.json)
```
{ baseline_n_rules: 3, candidate_n_rules: 4,
  rule4: {...validated...},
  train_signal_for_rule4: int,          # # TRAIN examples with last_ready_node_op==True
  results: { TRAIN|HELDOUT|ALL: { baseline:{acc,fa,fb,n}, candidate:{...} } },
  train_score: { baseline: float, candidate: float },
  heldout_delta: float,                 # candidate.HELDOUT.acc - baseline.HELDOUT.acc
  beats_baseline_897: bool,
  heldout_false_allows_fixed: [[incident,tool],...],
  heldout_false_allows_remaining: [[incident,tool],...] }
```

## Test cases (artifacts/test_rule4_candidate.py)
1. `test_baseline_is_897` — baseline held-out accuracy == 0.897 (anchors the claim).
2. `test_rule4_validates` — `validate_ruleset([RULE4])` non-empty (known feature/op).
3. `test_rule4_beats_baseline` — 4-rule held-out accuracy > 0.897.
4. `test_rule4_introduces_no_new_false_blocks` — FB(ext)==FB(base) on TRAIN & HELDOUT.
5. `test_no_train_signal_for_rule4` — 0 TRAIN examples with `last_ready_node_op==True`
   (the honesty pillar: search has no gradient).
6. `test_two_misses_remain_unlearnable` — 4-rule held-out FA==2, acc==0.949 (ceiling
   for the current feature set; matches hand-written `is_safe`).

## API contract / invariants
- No edits to any `rex/*.py`, `sim/*.py`, or shared run files. Read-only imports +
  read of `rex/runs/harness_synth_v2.json`.
- Output paths confined to `experiments/ralph_outputs/C8/artifacts/`.
- Deterministic: no LLM call, no randomness; identical output every run.
