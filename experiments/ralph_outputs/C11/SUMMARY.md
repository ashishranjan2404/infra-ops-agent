# C11 — Rule-Ablation of the safety harness (SUMMARY)

## What
Built a rule-ablation harness that disables each rule of the hand-written safety gate
`rex/harness.py:is_safe` one at a time and measures the resulting `is_safe`-classification
accuracy drop on a fixed, spec-derived labeled action set. No core files edited — the
ablation is a wrapper that overrides the real `is_safe` decision when it blocked because
of the targeted rule (each guard returns a distinct reason string).

## The rules ablated (grounded in is_safe)
- R1 forbidden_category (Layer 1), R2 leak_restart (Layer 2), R3 last_ready_node (Layer 2)
  — the 3 headline guards that actually fire as blocks across the scenario set.
- R4 replica_limit, R5 rollback_no_deploy — reported for completeness.

## Result (42 scenarios, 580 labeled actions; full is_safe accuracy = 0.933)
| rule disabled | ablated acc | accuracy drop | false-allows introduced |
|---|---:|---:|---:|
| R1 forbidden_category | 0.576 | 0.357 | +207 |
| R2 leak_restart | 0.926 | 0.007 | +4 |
| R3 last_ready_node | 0.929 | 0.004 | +2 |
| R5 rollback_no_deploy | 0.931 | 0.002 | +3 |
| R4 replica_limit | 0.933 | 0.000 | 0 (untriggered) |

Per-rule contribution: R1 is load-bearing (deleting it nearly halves accuracy and lets
207 unsafe actions through). R2/R3 are rare but high-severity (each prevents a handful of
catastrophic false-allows). R4 never fires in this scenario set.

Key caveat (honest): accuracy drop under-serves the low-frequency, high-severity rules
(R2/R3) — the false-allows-introduced column is the safety-relevant signal and is reported
alongside.

## Artifacts
- artifacts/rule_ablation.py — ablation harness + CLI
- artifacts/test_rule_ablation.py — 4 hermetic tests (all pass)
- artifacts/ablation_result.json — produced numbers

## Reproduce
python3 experiments/ralph_outputs/C11/artifacts/rule_ablation.py
