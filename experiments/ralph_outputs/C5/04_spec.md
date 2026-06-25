# C5 — 04 Spec

## Data sources
- `rex/runs/harness_synth.json` → `["rules"]` : list of 10 synthesized rule dicts
  `{match_tools:[str], conditions:[{feature,op,value}], block:bool, reason:str}`.
- `rex/harness_synth.py:labeled_examples(name)` → list of
  `{incident, tool, target, features:{...}, should_block:bool, hazard:str}`.
- `rex/harness_synth.py:handwritten_pred(e)` → bool (hand-written is_safe blocks e?).
- `rex/harness_synth.py:is_safe_synth(feats, ruleset)` → (allowed, reason).

## Hand-written clauses under diff (the "lines")
| id | line_ref | predicate | hazard |
|----|----------|-----------|--------|
| L1_category_block | rex/harness.py:336-340 | TOOL_TREATS[tool] in forbidden_categories | treats_forbidden_category |
| L2a_leak_restart | rex/harness.py:343-345 | restart_* AND mem_leak_active | leak_restart |
| L2b_last_ready_node | rex/harness.py:346-348 | drain/cordon AND draining_last_ready_node | last_ready_node |
| L2c_replica_limit | rex/harness.py:349-351 | scale_deployment AND at_replica_limit | replica_limit |
| L2d_rollback_no_deploy | rex/harness.py:352-354 | rollback_deployment AND not recent_deploy | rollback_no_deploy |

## Functions (artifacts/gap_analysis.py)
- `synth_pred(ruleset, e) -> bool` : `not is_safe_synth(e["features"], ruleset)[0]`.
- `main() -> int` : builds the report below; writes `gap_report.json`; prints summary.

## Output contract — gap_report.json
```
{
  n_examples:int, n_incidents:int,
  handwritten_accuracy:float, synth_accuracy:float, n_disagreements:int,
  gap_handwritten_blocks_synth_misses:[row],   # synth FALSE-ALLOW gaps (headline)
  gap_synth_overblocks_vs_handwritten:[row],   # synth over-blocks
  hazard_gap:{hazard:{incidents_with_hazard,handwritten_blocks_on,synth_blocks_on,
                      missed_by_synth,missed_by_handwritten}},
  clause_to_synth_rule_map:[{id,line_ref,rule,hazard,synth_rules_covering,represented_in_synth}],
  missing_clauses_in_synth:[clause_id], n_synth_rules:int
}
row = {incident,split,tool,target,hazard,ground_truth_block,handwritten_block,synth_block,agree}
```

## Test cases (validated in 07)
- T1: report parses as JSON, has all keys above.
- T2: `missing_clauses_in_synth` is non-empty iff some clause's feature appears in no synth rule.
- T3: every row in `gap_handwritten_blocks_synth_misses` has handwritten_block==True, synth_block==False.
- T4: `trap_action` appears in BOTH `missed_by_synth` and `missed_by_handwritten` (shared limitation).
- T5: determinism — two runs produce byte-identical gap_report.json.
