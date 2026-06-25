# C5 — SUMMARY: synthesized rules vs hand-written rules (line-by-line gap analysis)

## Task
Compare the synthesized safety rules (`rex/runs/harness_synth.json`, searched by
`rex/harness_synth.py`) against the hand-written `rex/harness.py:is_safe`, line-by-line, and report
what the synthesized harness is missing.

## Method
Deterministic behavioral + structural diff over all 140 labeled examples (10 incidents) using the saved
synth rule-set and the in-repo `handwritten_pred`. Three views: per-example agreement, false-allow gap
list, and a clause->synth-rule map. No shared core file edited; analysis imports core read-only.
Artifact: `artifacts/gap_analysis.py` -> `artifacts/gap_report.json` (reproducible, md5-stable).

## Headline result
| harness | accuracy (140 ex) |
|---|---|
| hand-written `is_safe` | **0.871** |
| synthesized rule-set | **0.864** |

Near-parity, but **5 disagreements** — 3 synth false-allows, 2 synth over-blocks.

## What's missing (the gap)
1. **L2b `last_ready_node` clause (rex/harness.py:346-348) is entirely absent** from the synthesized
   rule-set -> `drain_node`/`cordon_node` on the last Ready node (`singleton_node_notready`) is NOT
   blocked. **Highest-severity miss** (drains the only node -> full outage). Root cause: this hazard is
   held-out-only in the train/held-out split, so the synthesizer never saw a label for it
   (structurally unlearnable, not just unlucky).
2. **Brittle port of `treats_forbidden_category`:** synth expresses it as per-tool-list rules instead
   of one general rule, so `failover_service` on `cpu_saturation_leaf` slips through (3rd false-allow).
3. **Over-blocks:** synth's broad leak-active rule blocks `clear_cache`/`scale_deployment` on `oom_kill`
   that the human harness allows.

## Fair caveat
`trap_action` is missed by BOTH harnesses (neither has a generic trap clause) — reported as a shared
limitation, not charged to the synthesized side.

## Clauses represented vs missing
L1 category-block OK, L2a leak-restart OK, **L2b last-ready-node MISSING**, L2c replica-limit OK,
L2d rollback-no-deploy OK.

## Status: completed (real plan + spec + runnable artifact + passing tests; finding is negative-leaning
and honest). No downstream blocker.
