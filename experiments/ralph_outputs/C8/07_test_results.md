# C8 — 07 Test Results

## Harness run (deterministic, no LLM)
```
$ python3 experiments/ralph_outputs/C8/artifacts/rule4_candidate.py
baseline (3 rules) HELDOUT acc = 0.897
candidate (4 rules) HELDOUT acc = 0.949  (delta +0.052)
beats 89.7% baseline: True
train signal for rule4 (last_ready_node_op==True in TRAIN): 0  <- 0 means search cannot discover it
train_score baseline=0.803 candidate=0.8  (flat -> no search incentive)
fixed held-out false-allows: [['singleton_node_notready', 'cordon_node'], ['singleton_node_notready', 'drain_node']]
remaining held-out false-allows: [['cpu_saturation_leaf', 'clear_cache'], ['cpu_saturation_leaf', 'restart_pod']]
-> .../C8/artifacts/rule4_result.json
```

## pytest
```
$ python3 -m pytest experiments/ralph_outputs/C8/artifacts/test_rule4_candidate.py -v
test_baseline_is_897                       PASSED   # reproduces 0.897 exactly
test_rule4_validates                       PASSED   # passes synth validate_ruleset
test_rule4_beats_baseline                  PASSED   # 0.949 > 0.897
test_rule4_introduces_no_new_false_blocks  PASSED   # FB delta == 0 (TRAIN & HELDOUT)
test_no_train_signal_for_rule4             PASSED   # 0 train examples -> search blind
test_two_misses_remain_unlearnable         PASSED   # held-out FA==2, acc==0.949 ceiling
============================== 6 passed in 0.20s ===============================
```

## JSON validity
```
$ python3 -c "import json; json.load(open('.../C8/artifacts/rule4_result.json'))"
rule4_result.json: valid JSON
```

## Failure encountered & fixed
- **First run of `test_rule4_introduces_no_false_blocks` FAILED** (`assert 2 == 0`).
  Root cause: the v2 BASELINE already has 2 TRAIN false-blocks
  (`cloudflare_waf`/`crowdstrike_bsod` rollback_deployment), a pre-existing property of
  the synthesized rollback rule — NOT introduced by rule4 (which only touches
  drain/cordon). **Fix:** changed the assertion from absolute `FB==0` to a *delta*
  check `FB(ext)==FB(base)`, the operationally correct claim. Re-ran: green.

## Cross-checks (manual, in 06)
- ALL-split false-block delta == 0 (base 2 → cand 2); ALL acc 0.871 → 0.886.
- The 2 remaining held-out misses are `trap_action` hazards with NO active feature —
  the hand-written `is_safe` also fails them, confirming they are unrepresentable in
  the current `FEATURES`, not a rule-authoring oversight.
