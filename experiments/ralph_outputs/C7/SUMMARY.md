# C7 — SUMMARY: Harness transfer (synthesize on simple, evaluate on cascade)

## Question
Does an AutoHarness-synthesized safety rule-set, searched on the **simple** incident family,
transfer to the structurally different **cascade** family it never saw? Report the transfer gap.

## Method
Standalone harness `artifacts/transfer_simple_to_cascade.py` (imports `rex/harness_synth.py` +
`rex/tree.py`; edits no core file). Thompson-tree search synthesizes a DATA rule-set from
TRAIN=all 12 simple incidents (156 labels) ONLY; cascade labels are never seen (leakage-clean).
The learned harness, the empty seed, and the hand-written `is_safe` oracle are each scored on
TRAIN(simple) and HELDOUT=all 20 cascade incidents (284 labels). Operator routed through HUD
gateway `gpt-5.5` (roster-default Anthropic haiku is out of credits).

## Result (real run, synthesis_ran=true, budget 8, seed 0)

| harness | TRAIN(simple) acc | HELDOUT(cascade) acc | cascade false-allow rate |
|---|---|---|---|
| seed (allow-all) | 0.494 | 0.627 | 1.000 |
| synthesized (learned on simple) | 0.923 | 0.845 | 0.066 |
| hand-written is_safe (oracle) | 0.936 | 0.915 | 0.208 |

- Cross-type transfer gap (synthesized) = 0.078; oracle gap = 0.021 => synthesis-induced
  transfer cost ~= 0.057. Rules learned on simple incidents generalize to cascades with only an
  ~8-point accuracy drop.
- The synthesizer recovered the general, family-agnostic rule `treats_forbidden_category==True ->
  block` (plus state-conditional rules for leak-restart and last-ready-node) — this is what
  transfers.
- Safety: cascade false-allows fall from 106 (allow-all) to 7 (rate 0.066), below the
  hand-written oracle's 0.208. It is conservative (37 false-blocks on unseen cascade actions).
- Ceiling: the 7 residual false-allows are trap_action/rollback_no_deploy hazards that depend on
  incident-specific targets NOT expressible in the shared feature set — a genuine cap on
  feature-only cross-type transfer.

## Status
COMPLETED. Real plan + spec + runnable artifact + tests (4/4 pass) + a real synthesis-and-transfer
measurement. Caveats: single seed/budget-8 (no CI); operator swapped to gpt-5.5 because Anthropic
is out of credits, and 2 of 3 gateway models returned empty content on the full prompt (documented).

## Artifacts
- artifacts/transfer_simple_to_cascade.py — the transfer harness (no core edit)
- artifacts/test_transfer.py — 4 offline tests
- artifacts/transfer_result.json — measured numbers + saved synthesized rule-set
- 01..10_*.md — full Ralph cycle
