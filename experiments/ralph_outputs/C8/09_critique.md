# C8 — 09 Critique (honest, adversarial)

## What a reviewer attacks
1. **"This is hindsight, not generalization."** The strongest attack. The 4th rule was
   authored *after* inspecting the held-out misses in `harness_synth_v2.json`. So for
   *this rule*, the held-out set leaked into design. We do NOT claim otherwise — the
   report leads with `train_signal_for_rule4 = 0` precisely to make this explicit. The
   honest contribution is the *diagnosis* ("the search's hypothesis space contains the
   fix but its train signal doesn't induce it"), not a generalization win.
2. **"Marginal, single-incident gain."** The entire +0.052 comes from ONE held-out
   incident (`singleton_node_notready`, 2 actions). It is not a broad improvement; on
   TRAIN it does literally nothing. The ALL-split gain is only +0.015. A skeptic is
   right that this is a narrow patch of one hazard class, not a method advance.
3. **"You stopped at 94.9% — why not chase the last 2 misses?"** Because they are
   `trap_action` hazards on `cpu_saturation_leaf` (clear_cache, restart_pod) with NO
   active feature in the current `FEATURES`. The hand-written `is_safe` misses them
   too (its held-out is also 0.949). They are unrepresentable without adding a new
   feature/signal — out of scope for a "4th rule" task, and adding one would be a core
   change. So 94.9% is the honest ceiling for this feature set.

## What's weak
- **No re-run of the actual search.** We proved the search *can't* find the rule
  (flat reward), but we did not demonstrate that *adding a last-node incident to TRAIN*
  would let the haiku operator discover it. PSRE (grill R2) warned the operator might
  still over-AND conditions. That experiment is non-deterministic, costs LLM calls, and
  needs a core-file (split) edit — deliberately not attempted. Left as future work.
- **Tiny sample.** 39 held-out labels, 3 held-out incidents. Accuracy moves in chunky
  steps; "94.9%" is 37/39. Confidence intervals would be wide. Treat the numbers as
  illustrative of the *mechanism*, not as a precise benchmark.

## What's genuinely solid
- The fix is **expressible in the existing trusted interpreter with zero code change**
  (a property of the data-rule design) and **introduces no regressions** (FB delta 0
  everywhere). That part is real and verified.
- The negative finding (zero train signal → search-blind) is **provable from the data**
  and is the more interesting scientific result than the accuracy bump.

## Honest bottom line
Mixed result. We *did* push held-out past 89.7% (to 94.9%, matching the human
baseline) with a clean, validated rule — but the value is the **diagnosis of a
train/held-out coverage gap in the synthesizer**, not a claim that the synthesis
improved. Reported as such.
