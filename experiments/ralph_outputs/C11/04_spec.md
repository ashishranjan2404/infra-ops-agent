# 04 — Technical Spec

## Data structures
- **Labeled example** (from `rex.harness_synth.labeled_examples(name)`):
  `{"incident": str, "tool": str, "target": str, "features": {...},
    "should_block": bool, "hazard": str}`. `should_block` is spec-derived ground truth.
- **RULES**: `dict[str, Callable[[str], bool]]`. Key = rule id; value = predicate over an
  `is_safe` reason string, True iff that rule was the blocker.
  ```
  R1_forbidden_category : "a ruled-out cause" in reason
  R2_leak_restart       : "a memory leak is still active" in reason
  R3_last_ready_node    : "the last Ready node" in reason
  R4_replica_limit      : "already at its replica/quota limit" in reason
  R5_rollback_no_deploy : "there was no recent deploy" in reason
  ```
  `HEADLINE = ["R1_forbidden_category","R2_leak_restart","R3_last_ready_node"]`.

## Function signatures
- `_state_for(e: dict) -> dict` — reconstruct the is_safe state dict for an example from
  its scenario (forbidden_categories, gold_category, mem_leak_active, draining_last_ready_node,
  at_replica_limit, recent_deploy). Mirrors `rex.harness.build_state`'s non-engine fields.
- `predict_block(e: dict, disabled: str|None=None) -> bool` — run real `is_safe`; if it
  blocked and `disabled` matches the reason, override to allow. Raises `KeyError` on an
  unknown `disabled` rule id.
- `confusion(examples: list, disabled: str|None=None) -> dict` ->
  `{n, tp, tn, false_allow, false_block, accuracy}`. false_allow = unsafe let through;
  false_block = safe action blocked.
- `main()` — CLI; default scenarios = all `_SCENARIOS`; writes JSON.

## Ablation metric (per rule)
```
accuracy_drop          = full.accuracy - ablated.accuracy
false_allows_introduced = ablated.false_allow - full.false_allow   (>= 0)
false_blocks_removed    = full.false_block   - ablated.false_block  (>= 0)
```

## Output JSON (`ablation_result.json`)
```
{ "scenarios_used":[...], "scenarios_skipped":[...], "n_labeled_actions":int,
  "full_harness": {n,tp,tn,false_allow,false_block,accuracy},
  "ablations": { "<rule>": {n,tp,tn,false_allow,false_block,accuracy,
                            accuracy_drop,false_allows_introduced,false_blocks_removed} },
  "headline_rules":[...], "ranking_by_accuracy_drop":[...] }
```

## CLI contract
`python3 .../rule_ablation.py [--scenarios n1 n2 ...] [--out PATH]`
Default: all scenarios, out = `ablation_result.json` beside the script. Prints a table.

## Test cases (hermetic — no LLM/network)
1. `full accuracy >= every ablated accuracy` (each rule net-helpful / neutral).
2. ablating a rule: `false_allow` non-decreasing, `false_block` non-increasing.
3. each guard's reason matches exactly ONE rule predicate (attribution is clean).
4. unknown `disabled` rule id raises `KeyError`.
