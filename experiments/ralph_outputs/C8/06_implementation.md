# C8 — 06 Implementation

## What was built (real artifacts, in C8/artifacts/)
1. **`rule4_candidate.py`** — offline, deterministic harness. Imports
   `rex.harness_synth` (`confusion`, `train_score`, `labeled_examples`,
   `validate_ruleset`, `TRAIN`, `HELDOUT`) — **no edits to any core file**. Loads the
   v2 3-rule baseline from `rex/runs/harness_synth_v2.json`, appends the 4th candidate
   rule (passed through the synth's own `validate_ruleset`), and scores 3-rule vs
   4-rule on TRAIN / HELDOUT / ALL. Emits `rule4_result.json`.
2. **`test_rule4_candidate.py`** — 6 pytest cases (see 04_spec). All green.
3. **`rule4_result.json`** — the emitted report (real numbers below).

## The 4th rule
```json
{"match_tools":["drain_node","cordon_node"],
 "conditions":[{"feature":"last_ready_node_op","op":"==","value":true}],
 "block":true,
 "reason":"draining/cordoning the last Ready node takes the service fully down — escalate instead"}
```
It re-expresses, as a DATA rule over the existing `last_ready_node_op` feature, the
Layer-2 `draining_last_ready_node` block that `rex/harness.py:is_safe` already has but
the v2 synthesized set lacked. The `at_replica_limit` and `last_ready_node_op`
features were both unused by the 3 synthesized rules; `at_replica_limit` is True for
zero examples in either split, so only `last_ready_node_op` is actionable.

## Results (from rule4_result.json)
| split   | baseline acc | candidate acc | Δ      |
|---------|--------------|---------------|--------|
| TRAIN   | 0.861        | 0.861         | 0.000  |
| HELDOUT | **0.897**    | **0.949**     | +0.052 |
| ALL     | 0.871        | 0.886         | +0.015 |

- Held-out false-allows: 4 → **2** (the two `singleton_node_notready` last-node misses
  fixed). Held-out accuracy now **equals the hand-written `is_safe` (0.949)**.
- **No new false-blocks** anywhere: FB delta == 0 on TRAIN, HELDOUT, and ALL.
- **train_score: 0.803 → 0.800** (flat; the −0.003 is exactly the per-condition
  complexity penalty `COMPLEXITY_LAMBDA`). `train_signal_for_rule4 = 0`.

## The load-bearing honesty point
There are **0 TRAIN examples** with `last_ready_node_op==True` (the only such examples
live in the held-out `singleton_node_notready` incident). So the Thompson search's
reward (`train_score`) is *identical* with or without this rule — actually marginally
worse due to the complexity penalty. **The LLM mutation operator provably cannot
discover this rule from the train signal.** The 5-point held-out gain is real and the
fix is expressible in the existing feature space, but it is **human-injected, not
synthesized** — this is an out-of-distribution generalization gap, not a search win.

## Proposed core change (documented, NOT applied — per parallel-safety rules)
If one wanted the *synthesizer* (not a human) to learn this, the change is to the
SPLIT in `rex/harness_synth.py`, not the rules: move a last-Ready-node incident into
TRAIN (or add one) so `last_ready_node_op==True` appears in the train labels. That is
a core-file edit and is left as a one-line proposal here, not performed.
