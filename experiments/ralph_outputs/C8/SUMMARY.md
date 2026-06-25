# C8 — Summary: a 4th rule candidate (can we push past 89.7%?)

**Question:** The v2 synthesized safety harness (`rex/harness_synth.py`) hits **89.7%
held-out accuracy** with 3 DATA rules. Can a 4th rule push past it?

**Answer: Yes on accuracy (89.7% → 94.9%), but NOT via the synthesizer.**

## What was done
Grounded in `rex/harness_synth.py` + `rex/harness.py`. The 3 synthesized rules cover
`treats_forbidden_category`, `leak_active`, `rollback_without_deploy` but leave the
`last_ready_node_op` feature **unused** — exactly the gap that causes the held-out
false-allows on `singleton_node_notready` (draining the last Ready node). Built an
offline, deterministic harness (no LLM, no core edits) that appends a 4th rule over
that existing feature and re-scores all splits.

## The 4th rule
`block drain_node/cordon_node when last_ready_node_op == True` — mirrors the
hand-written `is_safe` Layer-2 control as a pure DATA rule (passes the synth's own
`validate_ruleset`).

## Result (rule4_result.json)
| split | baseline | +rule4 | Δ |
|-------|----------|--------|---|
| TRAIN | 0.861 | 0.861 | 0.000 |
| **HELDOUT** | **0.897** | **0.949** | **+0.052** |
| ALL | 0.871 | 0.886 | +0.015 |

- Held-out false-allows 4 → 2; now **matches hand-written `is_safe` (0.949)**.
- **No new false-blocks** (FB delta 0 on TRAIN/HELDOUT/ALL).

## The honest catch (load-bearing)
`train_signal_for_rule4 = 0` — **zero TRAIN examples activate `last_ready_node_op`**,
so `train_score` is flat (0.803→0.800, the drop is just the complexity penalty). The
Thompson/haiku search **provably cannot discover this rule**; it is human-injected
hindsight, not a synthesis improvement. The contribution is the *diagnosis of a
train/held-out coverage gap*, not "the search got better." The remaining 2 held-out
misses are `trap_action` hazards with no representable feature (`is_safe` misses them
too) → **94.9% is the honest ceiling for the current feature set.**

## Artifacts
- `artifacts/rule4_candidate.py` — harness (deterministic)
- `artifacts/test_rule4_candidate.py` — 6 pytest cases, all green
- `artifacts/rule4_result.json` — emitted report

## Tests
6/6 pass. Harness reproduces the 89.7% baseline exactly.
