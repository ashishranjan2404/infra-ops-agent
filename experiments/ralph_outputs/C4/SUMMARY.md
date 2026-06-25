# C4 — SUMMARY

**Task:** Analyze the 3 synthesized safety rules — are they interpretable? Write rule
explanations grounded in `rex/harness_synth.py` and `rex/harness.py`.

## Answer: YES — interpretable by construction.
The 3 rules (canonical run `rex/runs/harness_synth_v2.json`, `n_rules:3`) are literal data
tuples over 6 named features, executed by ~20 lines of trusted Python with no eval/exec (haiku
is only the mutation operator). A human reads all 3 in under a minute and can predict every verdict.

| # | rule | corresponds to hand-written is_safe |
|---|---|---|
| R1 | block ANY tool if treats_forbidden_category==True | clean recovery of Layer-1 category block |
| R2 | block clear_cache/restart_pod/restart_service/scale_deployment if leak_active==True | broadens the leak-restart clause (deliberate conservatism) |
| R3 | block rollback_deployment if rollback_without_deploy==True | clean recovery of rollback clause |

## Verified numbers (reproduced by artifacts/validate_rules.py, exit 0)
- Held-out: acc 0.897, false_allow 4, false_block 0 (synth v2) vs 0.949 hand-written vs 0.667 empty-seed. Reproduces the published JSON exactly.
- The 4 held-out false-allows are 0 synthesis-quality misses: 2 are last_ready_node (hazard absent from TRAIN -> out of scope), 2 are trap_action (unlearnable from the 6 features — hand-written is_safe misses them too).
- v1->v2 collapse: 10 rules -> 3 rules while accuracy rose (+0.025) and false-allows fell (-0.077).

## Key weaknesses (honest)
- R2/R3 hard-code match_tools enumerations -> silently miss new tools. R1 is fully general.
- Clean R1/R3 recoveries are partly because the 6 features were designed to mirror is_safe.
- Synth trails hand-written (0.897 vs 0.949) entirely on the out-of-scope last_ready_node hazard.

## Artifacts
- artifacts/rule_interpretability.md — primary interpretability report.
- artifacts/validate_rules.py — runnable validator reproducing held-out confusion + worked examples.
- 01_plan.md … 10_feedback.md — full 10-step cycle.

No shared core file edited. No fabricated numbers.
