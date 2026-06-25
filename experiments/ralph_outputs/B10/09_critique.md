# B10 — 09 Critique (honest)

## What's weak
1. **pass@1 is synthetic here.** The training logs record a continuous weighted reward, not a binary
   pass. Every pass@1 number is a thresholding choice. A skeptic can say "you manufactured a metric."
   Mitigation: τ=0.8 is reused verbatim from the repo's own eval; but it remains a derivation, not a
   logged ground truth.
2. **The headline result is null.** At τ=0.8 pass@1 is flat at 0 for all three runs across all steps,
   because no rollout's reward reaches 0.8. As a "learning curve" the headline figure is a flat line
   on the axis — informative (the model never resolves an incident) but unflattering and easy to
   misread as "broken tooling."
3. **τ=0.65 is a chosen knob.** A reviewer will note the second threshold was picked because it sits
   inside the reward distribution. It's labeled "substantially-correct diagnosis," but 0.65 has no
   independent operational definition — it's an analysis aid, not a validated bar.
4. **Batch-level, not per-incident.** Each step's `rewards` array mixes multiple scenarios; pass@1 is
   over the mixed GRPO batch. We cannot say "pass@1 on incident X" — the data doesn't carry the
   scenario id per rollout. A proper per-incident learning curve would require re-running training
   with richer logging.
5. **Small n, autocorrelated steps.** n=24–40 rollouts/step → wide Wilson bands; consecutive steps
   share policy lineage. The apparent v2 climb (0.375→0.525) is suggestive, not significant.
6. **Tiny training horizon.** 14–25 steps is short; "learning curve" oversells what is really an
   early-training trace.

## What a reviewer attacks first
- "Your main curve is flat-zero — did anything train?" → Answer: reward moved within [0.4,0.78]; the
  policy changed, it just never crossed the resolution bar. The mean_reward overlay shows this.
- "Why two thresholds?" → Honesty: 0.8 is the real bar (kept); 0.65 exposes dynamics (labeled).
- "Is the v2 improvement real?" → Not claimed as significant; n is small, bands overlap.

## What's missing / would strengthen it
- A longer real training run that actually pushes some rollouts past 0.8 (would make the headline
  curve non-trivial). Blocked: requires HUD Tinker GPU time + a forked Qwen slug, not available here.
- Per-incident logging in `train_rft*.py` (would enable per-family curves) — but that means editing a
  shared core file, which the parallel-safety rules forbid; left as a documented proposal.
- Seed/variance bands across repeated runs (only single runs per model on disk).

## Bottom line
The harness is correct, tested, and runs on real logs. The science it reveals is honestly a **null
headline** (no incident resolved at the operational bar) plus a **weak, unconfirmed** partial-credit
signal favoring the v2 reward. The value delivered is the reusable, documented pass@1-vs-step tool
and an honest read of the existing RFT logs — not a success story.
