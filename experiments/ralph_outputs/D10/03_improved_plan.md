# D10 — 03 Improved Plan

## What changed after the grill

**Accepted:**
1. (RLE/SMR) Report **composite spread** alongside ranking metrics — a weighting that keeps
   tau=1 but compresses spread is a *trap* for RFT (advantages vanish). Added `composite_spread`
   and `mean_composite` per weighting.
2. (RLE/REV) Headline metric is **ranking change**, not reward magnitude: `mean_kendall_tau_vs_default`
   and `argmax_flip_rate`. RFT (GRPO) optimizes the *ordering* of in-group advantages.
3. (PSRE/REV) Sweep grid must include the operationally critical end-cases: `no_trap_penalty`,
   `harsh_trap`, and the degenerate `resolution_only`. Done (8 weightings total).
4. (REV) State plainly that rollouts are **synthetic plans executed through the real sim**, not
   LLM samples — and justify that the conclusion (how re-weighting reshapes the reward target)
   does not depend on rollout realism. Documented in 06/09.
5. (DVO) Wrapper-only; `selftest()` asserts recomposed==`score_plan` at default. Done.

**Rejected (with reason):**
- (DVO) "Don't run a real GPU RFT loop." — Not rejected so much as *out of scope by necessity*:
  no GPU/policy here. We run the **reward function** (the exact thing a weight sweep changes)
  over real rollouts. Documented as a blocker in 07/09 rather than faked.
- (REV) "If rankings never move, the contribution is null." — Partially rejected: even if the
  *argmax* rarely flips, the **spread** and **tail ordering** changes are themselves the finding
  an RFT engineer needs (they change which negatives get pushed down hardest). We report both and
  let the numbers speak — and in fact `resolution_only` / `no_trap_penalty` DO flip argmax on a
  fraction of scenarios, so the contribution is non-null.

## Final metric set per weighting
`mean_composite`, `composite_spread`, `mean_kendall_tau_vs_default`, `argmax_flip_rate`,
`argmax_flips`, `n_scenarios`.

## Final sweep grid (8)
default · diagnosis_heavy · fix_heavy · resolution_only · equal_thirds · no_trap_penalty ·
harsh_trap · diag_then_resolve.
