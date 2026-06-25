# E3 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Apples-to-apples zero-shot** (accepted SMR): the zero-shot arm uses the EXACT base model
   the OpenSRE arm was forked from — `Qwen/Qwen3-8B` (not a stronger frontier model). Otherwise
   we'd measure model identity, not training.
2. **Auditability** (accepted RLE): the result records the exact gateway `model` string per arm
   (`roster_key` + underlying model), so the comparison is verifiable, not just labeled.
3. **Descriptive framing** (accepted AAAI/SMR): no significance claims on a small gap; report
   pass@1 + Wilson CI + mean + std and explicitly flag CI overlap. 14×2 seeds = 28 trials/arm is
   stated as underpowered for hypothesis testing.
4. **Headroom / floor-effect check** (accepted AAAI/RLE): the output includes per-incident means
   and within-arm reward std; if base sits strictly between 0 and 1 a null lift is interpretable
   (not a floor artifact). This is reported, not asserted.
5. **Serving-parity caveat** (accepted DOL/SMR): documented that gateway sampling defaults for the
   base slug vs the forked slug may differ slightly and can't be fully controlled from here.

## What I rejected and why
- **PSRE: "don't add seeds, spend budget on scoring instead."** Partially rejected. The scoring is
  the repo's already-validated P0 deterministic judge (root-cause-aware, trap-penalizing) — I don't
  re-litigate it. But I keep seeds modest (2) rather than 1, to get a non-degenerate std, while
  agreeing with PSRE that chasing tight CIs on a known-flat model isn't worth heavy spend.
- **AAAI: "raise seeds for significance."** Rejected as the primary goal. The prior OpenSRE run was
  flat; the honest deliverable is a runnable harness + a descriptive result + the Fireball blocker,
  not a powered hypothesis test of a model known to be near-flat.

## Final shape (unchanged from 01 otherwise)
Reuse `rex.harness` / `rex.loop` / `rex.scoring` / `compute_pass_at_k`; new standalone harness in
`artifacts/`; local roster registration (no shared-file edits); 14 deterministic cascade incidents;
Fireball arm = blocked, documented, never fabricated.
