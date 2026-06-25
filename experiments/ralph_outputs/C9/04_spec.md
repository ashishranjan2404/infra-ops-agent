# C9 — 04 Spec

## Incident universe
`names = sorted(rex.harness._SCENARIOS.keys())` → asserted `len == 42`.

## Splits
- **Small split** (reference, from core): `harness_synth.TRAIN` (7) / `harness_synth.HELDOUT` (3).
- **Full split**: `split_70_30(names, seed=0)` — `random.Random(0).shuffle` then 70% cut,
  each side re-sorted for stability. ≈ 29 train / 13 held-out incidents.

## Label generation (deterministic, no LLM)
`hs.labeled_examples(name) -> list[dict]` with keys
`{incident, tool, target, features, should_block, hazard}`. `ground_truth` encodes the spec
hazards (last_ready_node, leak_restart, trap_action, treats_forbidden_category, replica_limit,
rollback_no_deploy, correct_fix exemptions).

## Harnesses under test (block-predicate → bool)
| harness | predicate |
|---|---|
| seed (empty) | `is_safe_synth(feats, []) ` → never blocks |
| synthesized | `is_safe_synth(feats, best_rules)` |
| hand-written `is_safe` | `handwritten_pred(e)` wrapping `rex.harness.is_safe` |

## Synthesis (LLM mutation operator)
```
hs.MODEL = "deepseek-v4-pro"          # gateway; interpreter+reward unchanged
thompson_search(
    propose  = lambda parent: hs.propose_ruleset(parent, train_ex),
    evaluate = lambda rs:     hs.train_score(rs, train_ex),
    budget=6, seed=0, stop_at=1.0)
```
Run once on full-42 train, once on small-10 train. Gateway smoke-tested first; on any
exception → `no_llm=True`, `best=[]`, blocker recorded.

## Metrics (`hs.confusion` / `hs.confusion_pred`)
`{tp, tn, false_allow, false_block, n, accuracy, false_allow_rate}`. `accuracy=(tp+tn)/n`;
`false_allow` = should_block but allowed (catastrophic); `false_block` = safe but blocked.

## Output contract — `results_full42.json`
```json
{
 "elapsed_sec": float, "n_incidents": 42, "n_labeled_examples": int, "n_should_block": int,
 "small_split": {"train":[...],"heldout":[...],"n_train_ex":int,"n_heldout_ex":int},
 "full_split":  {"train":[...],"heldout":[...],"n_train_ex":int,"n_heldout_ex":int},
 "headline": {"handwritten_is_safe": {
     "small_split_10_incidents": {"n","accuracy","false_allow","false_block"},
     "full_42_incidents":        {"n","accuracy","false_allow","false_block"}}},
 "small_eval": {"<harness>": {"train":{...},"heldout":{...}}},
 "full_eval":  {"<harness>": {"train":{...},"heldout":{...}}},
 "synthesis": {"model","full_best_train_score","full_node_scores","full_rules",
               "small_best_train_score","small_node_scores","small_rules"},
 "blocker": str|null, "no_llm": bool
}
```

## Tests
- `assert len(names)==42`.
- `--no-llm` path must produce identical deterministic numbers (headline + hand-written eval)
  to the full run (LLM only affects the `synthesized` rows + `synthesis` block).
- No write outside `experiments/ralph_outputs/C9/`.
