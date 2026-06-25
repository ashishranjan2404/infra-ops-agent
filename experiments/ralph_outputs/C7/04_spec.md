# C7 — Technical Spec

## Artifact: `artifacts/transfer_simple_to_cascade.py`

### Imports (from core, no edits)
```python
from rex.harness import scenarios_by_family
from rex.harness_synth import (
    labeled_examples, confusion, confusion_pred, handwritten_pred,
    propose_ruleset, train_score, hazard_coverage,
)
from rex.tree import thompson_search
```

### Config
```python
MODEL  = "claude-haiku-4-5"   # (inherited; propose_ruleset uses harness_synth.MODEL)
BUDGET = 8
SEED   = 0
OUT    = "<C7>/artifacts/transfer_result.json"
```

### Splits (by family, computed not hardcoded)
```python
fam      = scenarios_by_family()
TRAIN    = sorted(fam["simple"])    # 12 incidents
HELDOUT  = sorted(fam["cascade"])   # 20 incidents
assert not (set(TRAIN) & set(HELDOUT))
train_ex = [e for n in TRAIN   for e in labeled_examples(n)]
held_ex  = [e for n in HELDOUT for e in labeled_examples(n)]
```

### Synthesis (train=simple only)
```python
res = thompson_search(
    propose  = lambda parent: propose_ruleset(parent, train_ex),
    evaluate = lambda rs: train_score(rs, train_ex),
    budget   = BUDGET, seed = SEED, stop_at = 1.0)
best = res["nodes"][res["best"]]["cand"]
synthesis_ran = bool(best)   # non-empty rule-set ⇒ synthesis improved on seed
```

### Scoring (3 harnesses × 2 families)
```python
harnesses = {
    "seed_empty":   lambda exs: confusion([], exs),
    "synthesized":  lambda exs: confusion(best, exs),
    "handwritten":  lambda exs: confusion_pred(handwritten_pred, exs),
}
# each yields {tp,tn,false_allow,false_block,n,accuracy,false_allow_rate,...}
```

### Transfer gap
```python
def gap(h): return round(table[h]["train"]["accuracy"] - table[h]["heldout"]["accuracy"], 3)
synth_cost = round(gap("synthesized") - gap("handwritten"), 3)
```

### Output contract: `transfer_result.json`
```json
{
  "task": "C7",
  "model": "claude-haiku-4-5",
  "budget": 8, "seed": 0,
  "train_family": "simple", "heldout_family": "cascade",
  "train_incidents": [...12], "heldout_incidents": [...20],
  "n_train_labels": <int>, "n_heldout_labels": <int>,
  "synthesis_ran": true,
  "synthesized_rules": [ {match_tools, conditions, block, reason}, ... ],
  "node_scores": [floats],
  "table": {
    "<harness>": {"train": {accuracy, false_allow, false_allow_rate},
                  "heldout": {accuracy, false_allow, false_allow_rate}}, ...},
  "transfer_gap": {"synthesized": <f>, "handwritten": <f>, "synthesis_cost": <f>},
  "heldout_false_allow": [[incident, tool, target, hazard], ...],
  "hazard_train": {hazard: [incidents]}, "hazard_heldout": {hazard: [incidents]},
  "leakage_ok": true
}
```

### Test cases (in `artifacts/test_transfer.py`)
1. `test_splits_disjoint` — TRAIN ∩ HELDOUT == ∅ and families are simple/cascade.
2. `test_interpreter_deterministic` — `confusion(best, held_ex)` is identical on two calls
   (pure function over saved rules).
3. `test_result_schema` — after a run, `transfer_result.json` parses and has all required keys;
   accuracies ∈ [0,1]; `false_allow_rate` ∈ [0,1].
4. `test_handwritten_oracle_strong` — hand-written cascade accuracy ≥ 0.8 (sanity: oracle is a
   ceiling). Uses cached labels only, no LLM.

### Exit / blocker semantics
- If `synthesis_ran == False`: still write result.json with `synthesis_ran=false`; the report
  in step 09 flags BLOCKER (synthesis degenerated to seed / LLM unavailable). Numbers for the
  hand-written oracle and seed are still valid.
