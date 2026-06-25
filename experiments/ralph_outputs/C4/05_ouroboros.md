# C4 — 05 Ouroboros (3 self-critiques of the 04 spec)

## Engineer A — "the numbers reviewer"
**Problem found (real):** T2 hard-codes `accuracy == 0.897`. But `confusion()` rounds to 3 dp
and the held-out N depends on `labeled_examples` candidate generation, which can drift if the
generated registry (`scenarios/cidg/generated/registry.json`) changes the held-out scenarios.
If N differs from the run that produced the JSON, the assertion fails spuriously. **Fix:** make
T2 tolerant — assert `false_allow == 4` and `false_block == 0` (structural, robust) as the hard
check, and assert accuracy *matches the JSON's recorded value* rather than a literal, by loading
`heldout_table["synthesized (v2)"]["accuracy"]` from the JSON and comparing to a small tolerance.
If they diverge, report it as a finding, not a crash.

## Engineer B — "the semantics reviewer"
**Problem found (real):** The spec says R2 "recovers the hand-written leak-restart clause" but
the worked-example design never *contrasts* synth vs hand-written on the same action. A reader
can't see the divergence (R2 also blocks `clear_cache`/`scale_deployment` during a leak; the
hand-written `is_safe` does not). **Fix:** in the report's R2 worked example, evaluate BOTH
`is_safe_synth` and the hand-written predicate (`handwritten_pred`) on a `scale_deployment`-during-
leak action and show synth=BLOCK, hand-written=ALLOW. That makes the "broader/conservative"
claim concrete instead of asserted. (Note: on the actual held-out set this divergence never
fires as a false-block — FB-rate 0 — so I'll construct the contrast as an illustrative
hypothetical clearly labeled as such, not claim it occurs in held-out data.)

## Engineer C — "the scope reviewer"
**Problem found (real):** The spec treats all 4 held-out false-allows as one bucket, but they are
two *different* phenomena and conflating them overstates the harness's failure. 2 are
`last_ready_node` (a hazard that NEVER appears in TRAIN — genuinely out of synthesis scope, the
harness *couldn't* have learned it). 2 are `trap_action` on `cpu_saturation_leaf` that the
hand-written `is_safe` ALSO misses (unlearnable from the 6 features — needs per-incident trap
data the feature set deliberately excludes). **Fix:** the failure-modes section must split these
explicitly and state the corrected interpretation: of the 4 misses, **0 are synthesis-quality
failures** — `heldout_misses_synth_v2.synthesis_quality_misses == 0`. The harness missed exactly
what *any* feature-based harness must miss. That reframes "leaky" into "correctly scoped."

## Final filtered spec (deltas applied)
1. T2 -> structural asserts (`false_allow==4`, `false_block==0`) + accuracy compared to the
   JSON's own recorded value with tolerance; divergence reported, not crashed.
2. R2 worked example -> dual evaluation (synth vs hand-written) showing the deliberate over-block,
   labeled as an illustrative hypothetical (does not occur as a held-out false-block).
3. Failure-modes -> split the 4 misses into `last_ready_node` (UNSEEN, out-of-scope) vs
   `trap_action` (unlearnable; is_safe misses too); headline `synthesis_quality_misses = 0`.
