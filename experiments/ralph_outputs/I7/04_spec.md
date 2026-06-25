# 04 — Technical Spec

## Categories (fixed)
`["scale-trap", "restart-trap", "rollback-trap", "failover-trap", "other-trap"]`

## Tool → category map (`TOOL_TO_CATEGORY`)
```
scale_deployment    -> scale-trap
restart_service     -> restart-trap
restart_pod         -> restart-trap
rollback_deployment -> rollback-trap
failover            -> failover-trap
promote_replica     -> failover-trap
switch_to_standby   -> failover-trap
drain_node          -> failover-trap
(anything else)     -> other-trap
```

## Function signatures (`classify_traps.py`)
- `classify_tool(tool: str) -> str` — pure lookup, default `other-trap`.
- `_records_from_g4(repo) -> list[dict] | None` — reuse G4 records as
  `{file, scenario_id, fault_node, tool, target}`.
- `_records_from_yaml(repo) -> list[dict]` — fallback YAML scan of
  `scenarios/cidg/generated/*.yaml` reading `trap_actions[0]`.
- `build(repo: str) -> dict` — returns:
  ```
  {input_source, n_scenarios_with_trap, categories, tool_to_category,
   distribution{cat:count for all 5}, dominant_category, skew_fraction,
   empty_categories[], records[{...,category}]}
  ```
- `main(argv) -> int` — write JSON, print ASCII bar chart, exit 0 if any trap else 2.

## Output file format (`trap_classification.json`)
Single JSON object matching `build()` return. `distribution` ALWAYS has all 5 keys
(zeros included) so empty categories are visible.

## Test cases (`test_classify_traps.py`)
1. `classify_tool` maps each known tool correctly.
2. unknown tool / `None` → `other-trap`.
3. `build("/Users/mei/rl")`: traps > 0; distribution sums to total; all 5 keys
   present; dominant == `scale-trap`.
4. skew_fraction in [0,1] and > 0.8 (corpus is known-skewed).

## Contracts / invariants
- Read-only: never writes outside this task's `artifacts/`.
- No network, no LLM import.
- `sum(distribution.values()) == n_scenarios_with_trap`.
