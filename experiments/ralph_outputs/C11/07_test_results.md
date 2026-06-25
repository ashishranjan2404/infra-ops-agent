# 07 — Test Results

## Ablation run (real output)
```
$ python3 experiments/ralph_outputs/C11/artifacts/rule_ablation.py

Scenarios: 42 (0 skipped)   Labeled actions: 580
FULL is_safe: accuracy=0.9328  (tp=216 tn=325 false_allow=37 false_block=2)

rule (disabled)                acc    drop   +FA   -FB
------------------------------------------------------
*R1_forbidden_category      0.5759  0.3569   207     0
*R2_leak_restart            0.9259  0.0069     4     0
*R3_last_ready_node         0.9293  0.0035     2     0
 R5_rollback_no_deploy       0.931  0.0018     3     2
 R4_replica_limit           0.9328     0.0     0     0

(* = headline rule;  drop = full_acc - ablated_acc;  +FA = false-allows introduced;  -FB = false-blocks removed)

-> .../ablation_result.json
```

## Per-rule contribution (interpretation)
| rule | ablated acc | accuracy drop | false-allows introduced |
|------|------------:|--------------:|------------------------:|
| **R1 forbidden_category** | 0.576 | **0.357** | **+207** |
| **R2 leak_restart** | 0.926 | 0.007 | +4 |
| **R3 last_ready_node** | 0.929 | 0.004 | +2 |
| R5 rollback_no_deploy | 0.931 | 0.002 | +3 (and removes 2 false-blocks) |
| R4 replica_limit | 0.933 | 0.000 | 0 (untriggered in this set) |

- **R1 is the load-bearing rule**: deleting it collapses accuracy from 0.933→0.576 and
  lets 207 previously-blocked unsafe actions through. It governs the dominant hazard
  (treating a ruled-out cause) across all cascades.
- **R2/R3** are rare but real: each removes a handful of false-allows. These are the
  high-severity, low-frequency guards (restart-on-leak, drain-last-node).
- **R4** never fires (no scenario is at a replica limit) → 0 drop; kept and labeled
  untriggered, NOT dead code.
- **R5** removing it both introduces 3 false-allows AND removes 2 false-blocks, so its
  net accuracy drop is small (0.002) — it's a near-wash on this set.

## Unit tests
```
$ python3 -m pytest experiments/ralph_outputs/C11/artifacts/test_rule_ablation.py -q
....                                                                     [100%]
4 passed in 44.34s
```
Tests cover: full ≥ every ablation; FA non-decreasing / FB non-increasing under ablation;
clean single-rule attribution per reason string; KeyError on unknown rule.

## Fixes applied during testing
- `test_unknown_disabled_rule_raises` initially failed because `predict_block` only
  checked the rule id when `is_safe` blocked. Fixed by validating `disabled in RULES` at
  the top of `predict_block`. Re-ran: 4 passed.
