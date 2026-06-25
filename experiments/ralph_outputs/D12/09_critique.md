# D12 — 09 Critique (honest)

## What a reviewer attacks
1. **No actual A/B reward curve.** I project variance reduction analytically and prove the
   plumbing with a smoke, but I never produced a 30-step group-8 curve to compare against the
   group-4 baseline. The headline claim ("does more rollouts help?") is therefore answered by
   *theory + one smoke step*, not by a converged training comparison. Honest gap, forced by the
   15-min cap and the unforked slug.
2. **Sigma is a point estimate from one model on 15 steps.** within-group sigma (0.069) comes from
   a single Qwen3-8B v2 run; a stronger/weaker policy would have different spread, so the absolute
   SEM numbers are run-specific. The *ratio* (1/√2) is exact regardless, which is what I lean on.
3. **Task-major ordering is inferred, not contractually guaranteed.** I verified it from the value
   clustering in the log, but if HUD changes rollout ordering, the per-group slicing in
   `variance_analysis.py` would silently mis-group. A more robust version would group by an explicit
   task id if the log carried one (it doesn't).
4. **The std-normalization caveat.** If HUD's `trainer.step` normalizes advantage by within-group
   std (not just subtracts the mean), the dominant G-effect is a less-biased std estimate, and my
   SEM-of-the-mean framing understates/reframes the benefit. I scoped the claim to "cleaner
   advantage estimate" to stay honest, but I can't see HUD's internals to be precise.
5. **404 on the slug.** The intended trainable model isn't forked right now. The smoke still ran
   (fallback), but a real run needs `hud models fork Qwen/Qwen3-8B --name opensre-qwen3-8b` first.

## What's weak / missing
- No matched-compute arm actually executed (group8@15 vs group4@30) — only described.
- No seed sweep (AAAI's demand) — unaffordable here; results are a projection.
- Variance reduction in the *gradient* ≠ guaranteed faster *reward* improvement; I assert the link
  qualitatively but don't measure it.

## Honest bottom line
Solid, validated, grounded deliverable (config + launcher + log-derived analysis + live smoke
proof). But the causal question "does group 8 train a better SRE policy?" remains **empirically
open** — blocked on compute + a forked slug. The math says it's a real-but-second-order win; the
flat-baseline root cause lies elsewhere (tasks/headroom).
