# 04 — Technical Spec

## Module: `artifacts/lambda_sweep.py`

### Reused from `rex.harness_synth` (no edits)
`TRAIN`, `HELDOUT`, `FEATURES`, `labeled_examples(name)->list`,
`confusion(ruleset, examples)->dict`, `confusion_pred(pred_fn, examples)->dict`,
`handwritten_pred(example)->bool`, `validate_ruleset(raw)->list`,
`train_score(ruleset, train_ex)->float`, `COMPLEXITY_LAMBDA`.
From `rex.tree`: `thompson_search(propose, evaluate, budget, seed, stop_at)->dict`.

### `score_with_lambda(ruleset: list, train_ex: list, lam: float) -> float`
Faithful re-implementation of `train_score` with lambda as a parameter:
```
c     = confusion(ruleset, train_ex)
nb,na = c.tp + c.false_allow , c.tn + c.false_block
err   = 2.0*c.false_allow + 1.0*c.false_block
maxerr= 2.0*nb + 1.0*na
base  = 1 - err/maxerr   (0 if maxerr==0)
ncond = sum(len(r.conditions) for r in ruleset)
return max(0.0, base - lam*ncond)
```
CONTRACT: `score_with_lambda(rs, ex, COMPLEXITY_LAMBDA) == train_score(rs, ex)` exactly.

### `_candidate_atoms(train_ex) -> list[rule]`
For every example with `should_block==True`, for every bool feature `f` in
`FEATURES\{tool}` that is active (`==True`), emit the general atom
`{"match_tools":[tool], "conditions":[{f,"==",True}], "block":True}`. De-duped by
`(tool, f)`. No incident ids (keeps rules general — same constraint the LLM schema imposes).

### `propose_offline_builder(train_ex, lam) -> propose(parent_node|None)->ruleset`
Greedy hill-climb: from the parent's rule-set (or `[]` at root), add the single atom with
the largest positive gain in `score_with_lambda`. If no atom yields gain > 1e-12, return the
parent unchanged (search stalls — the correct signal that lambda has priced out all atoms).
Output passed through `validate_ruleset`.

### `run_point(lam, train_ex, held_ex, budget, mode, seed=0) -> dict`
Runs `thompson_search(propose, evaluate=score_with_lambda(.,lam), budget, seed, stop_at=1.0)`,
takes `best` rule-set, returns:
`{lambda, mode, budget, best_train_reward, n_rules, n_conditions, train_acc,
train_false_allow, train_false_block, heldout_acc, heldout_false_allow,
heldout_false_block, heldout_false_allow_rate, rules, node_rewards}`.

### `main()` CLI
`--offline` (default) | `--real` ; `--budget` (8) ; `--lambdas` (csv, default
`0.0,0.003,0.01,0.03,0.08,0.2`) ; `--out`. Prints a table, writes
`lambda_sweep_<mode>.json` = `{mode, budget, default_lambda, train_incidents,
heldout_incidents, n_train_labels, n_heldout_labels, handwritten_baseline, sweep:[points]}`.

## Tests (`test_lambda_sweep.py`)
1. `score_with_lambda == train_score` at default lambda (rs=[] and a 2-rule rs).
2. Higher lambda never increases score for a fixed rule-set.
3. Atoms are general (bool values only, block True).
4. Offline propose grows at lambda 0, returns [] at lambda 5.0.
5. `run_point` offline is deterministic (same rules/acc on repeat).
6. n_conditions is weakly non-increasing across the lambda grid.

## File formats
JSON, 2-space indent. Real-mode blocker recorded as
`lambda_sweep_real.json` with `status:"blocked"`, `blocker`, `remediation`.
