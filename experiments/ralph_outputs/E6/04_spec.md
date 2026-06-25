# E6 — 04 Spec

## Input record schema (FIREBALL / opensre format)
```jsonc
{
  "trajectory_id": str,
  "trajectory": [                       // REQUIRED, list
    {"step": int, "role": "assistant",  // ACTION channel
     "thought": str, "action": {"tool": str, "args": {...}}},
    {"step": int, "role": "tool",       // STATE channel
     "name": str, "result": {...}, "evidence_ref": str}
  ],
  "remediation": {                       // FIREBALL state_before -> fix -> state_after
    "fix_tool": str, "canonical_fix": str, "trust_tier": str,   // ACTION keys
    "primary_metric": str, "direction": str,                    // STATE keys
    "state_before": {...}, "state_after": {...},
    "recovery_check": str, "resolved": bool
  },
  "evidence": {<file>: {...}},           // STATE
  "answer": {... , "optimal_trajectory": [...], "required_queries": [...]}  // gold ACTIONS
}
```

## Constants
```python
VARIANTS = ("full", "state_only", "action_only")
_STATE_REMEDIATION_KEYS  = ("primary_metric","direction","state_before",
                            "state_after","recovery_check","resolved")
_ACTION_REMEDIATION_KEYS = ("fix_tool","canonical_fix","trust_tier")
```

## Function signatures
```python
def transform_full(rec: dict) -> dict          # deep copy + ablation="full"
def transform_state_only(rec: dict) -> dict    # keep tool steps + state remediation + evidence
def transform_action_only(rec: dict) -> dict   # keep assistant steps + fix remediation
def apply_variant(rec: dict, variant: str) -> dict
def transform_stream(records, variant) -> Iterable[dict]
def _validate_record(rec) -> None              # raises TypeError/ValueError
```

### Transform contracts
| variant | trajectory kept | remediation kept | evidence | answer gold actions |
|---|---|---|---|---|
| full | all | all | yes | yes |
| state_only | role=="tool" | STATE keys | yes | dropped |
| action_only | role=="assistant" | ACTION keys | dropped | kept (it's an action) |

Invariants (all tested):
- **Purity**: input `rec` is never mutated (deep copy).
- **Partition**: `len(state_only.traj) + len(action_only.traj) == len(full.traj)`.
- **Tagging**: output carries `ablation == variant`.
- **Validation**: missing/invalid `trajectory`, unknown role, non-dict → raise.

## CLI
```
python3 fireball_ablate.py --in IN.jsonl --variant {full,state_only,action_only} --out OUT.jsonl
python3 run_ablation_e6.py --in IN.jsonl --outdir DIR [--report REPORT.json]
```

## Harness report schema (structural facts only — NO model metrics)
```jsonc
{"input": str, "n_input": int,
 "variants": {<v>: {"out": path, "stats": {
   "n_records","total_steps","mean_steps","assistant_steps","tool_steps",
   "records_with_state_transition","records_with_canonical_fix","records_with_evidence"}}},
 "blocker": str}
```

## Test cases (pytest, 16)
fixture loads; VARIANTS constant; full==identity+tag; input-not-mutated;
state_only drops assistant; state_only keeps state-remediation drops action;
state_only strips gold actions; action_only drops tool; action_only keeps fix drops state;
action_only drops evidence; partition equality; concrete step counts (3 asst / 2 tool);
dispatch; unknown-variant raises; stream over all records; validate rejects bad records.

## Blocker (downstream)
Per-variant train + pass@k eval needs the real FIREBALL D&D corpus + fireball-trained
slug — not in repo (E2 / P7_fireball_status.md). Transform layer is the new piece and is
complete. Downstream wiring: emit variant → SFT/GRPO → `rex.eval_pass_at_k` +
`rex.scoring` on cascades. action_only is SFT-only (no `state_after` ⇒ no reward).
