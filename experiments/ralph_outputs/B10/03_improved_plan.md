# B10 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Two thresholds, not one.** Headline curve at the repo-canonical τ=0.8 ("incident resolved"),
   PLUS a companion curve at τ=0.65 labeled "substantially-correct diagnosis." (Grill R3 #1/#2.)
2. **Report the reward range** alongside the curve so a flat-zero pass@1 is interpretable rather
   than mistaken for "no learning." (REV in R2.)
3. **Wilson 95% CI bands** on every pass@1 line; `mean_reward` plotted as a faint dashed reference.
   (REV + SR.)
4. **Robustness is a first-class requirement**, but the pass@1 derivation is tested FIRST
   (SR's ordering beat DO's), then I/O hardening. Self-tests cover blank/malformed/empty lines,
   the `>=` boundary, out-of-order steps, and the real on-disk logs.
5. Metric is documented as **batch-level pass@1 over GRPO rollouts**, not per-incident. (RL.)

## Critiques accepted
- SR: derivation is load-bearing → explicit, documented, tested first. **Accepted.**
- SRE/REV: keep τ=0.8 as headline + show reward ceiling. **Accepted.**
- RL: add a lower threshold to expose dynamics, but labeled honestly. **Accepted (guard-railed).**
- DO: auto-discovery + graceful degradation. **Accepted.**
- REV: CI bands. **Accepted.**

## Critiques rejected (with reason)
- "Drop τ=0.8 because it's flat-zero" (early RL framing) — **Rejected.** That bar is the operational
  definition of success and is reused verbatim from `rex/eval_pass_at_k.py`. Replacing it to make the
  figure prettier is reward-hacking the plot. We keep it and add context instead.
- "Compute per-incident pass@1 by joining rollouts back to scenarios" — **Rejected for scope.** The
  JSONL logs do not record which scenario each rollout in the `rewards` array came from, so a
  per-incident split is not reconstructable from the on-disk data. Documented as a known limitation,
  not faked.
- "Bootstrap CI instead of Wilson" — **Rejected.** Wilson matches the existing repo estimator
  (`compute_pass_at_k.wilson_ci`); consistency beats marginal statistical nicety here.
