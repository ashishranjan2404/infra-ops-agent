# C2 — Technical spec

## Data structures (reused verbatim from rex/harness_synth.py)

### FEATURES (the only signals the trusted interpreter reads)
```
["tool", "treats_forbidden_category", "leak_active", "last_ready_node_op",
 "at_replica_limit", "rollback_without_deploy"]
```

### labeled example
```json
{"incident": str, "tool": str, "target": str,
 "features": {<FEATURE>: bool|str}, "should_block": bool, "hazard": str}
```
`hazard` in {trap_action, treats_forbidden_category, rollback_no_deploy,
leak_restart, last_ready_node, replica_limit, correct_fix, neutral}.

### rule (DATA, never exec'd)
```json
{"match_tools": [str,...], "conditions": [{"feature","op","value"}],
 "block": true, "reason": str}
```
A rule BLOCKS when (match_tools empty OR tool in match_tools) AND every condition
holds. `op` in {"==","!="}. First matching block-rule wins, else allow.

## Cascade-only split (the ONLY changed inputs vs baseline)
```
CASCADE  = sorted(scenarios_by_family()["cascade"])   # 20 incidents
HELDOUT  = [aws_dynamodb_dns, cloudflare_waf, crowdstrike_bsod,
            gcp_service_control, azure_ddos, railway_gcp_suspension]   # 6
TRAIN    = CASCADE \ HELDOUT                                            # 14
MODEL    = "deepseek-v4-pro"  (gateway; Anthropic 400s)
BUDGET   = 8
```

## Function contracts (imported, read-only)
- `hs.labeled_examples(name) -> list[example]`
- `hs.hazard_coverage(names) -> {hazard: [incident,...]}`
- `hs.train_score(ruleset, train_ex) -> float in [0,1]`
- `hs.confusion(ruleset, examples) -> {tp,tn,false_allow,false_block,n,accuracy,
   false_allow_rate, false_allow_ex, false_block_ex}`
- `hs.confusion_pred(hs.handwritten_pred, examples) -> same shape` (baseline harness)
- `hs.propose_ruleset(parent_node, train_ex) -> validated ruleset` (LLM mutation; reads `hs.MODEL`)
- `thompson_search(propose, evaluate, budget, seed, stop_at) -> {nodes, best, best_score}`

`propose()` wrapper temporarily sets `hs.MODEL = "deepseek-v4-pro"` around the call,
then restores it — so no global module state leaks.

## Output file format: cascade_synth.json
```json
{"split":"cascade-only","model":str,"budget":int,
 "train":[...],"heldout":[...],
 "rules":[<rule>...],
 "table":{"<harness>":{"train":{accuracy,false_allow,false_allow_rate},
                        "heldout":{...}}},
 "hazard_train":{...},"hazard_heldout":{...},
 "node_scores":[float...],"best_train_score":float,
 "heldout_false_allow":[[incident,tool,target,hazard]...],
 "heldout_false_block":[...] }
```

## Test cases (validation, see 07)
1. `python3 -c "import ast; ast.parse(open(...).read())"` — script parses.
2. Script runs to completion, writes valid JSON (`json.load` round-trips).
3. Invariants on the JSON:
   - `set(train) & set(heldout) == {}` (disjoint).
   - every rule validates: features ⊆ FEATURES, ops ⊆ {==,!=}.
   - `hazard_train` keys ⊆ {trap_action, treats_forbidden_category, rollback_no_deploy}
     and contain NONE of {leak_restart, last_ready_node, replica_limit} (the
     cascade-specialization prediction).
4. Comparison: hazard coverage of cascade-synth rules vs baseline rules vs hand-written.
