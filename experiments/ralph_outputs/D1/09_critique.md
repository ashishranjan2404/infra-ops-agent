# D1 — 09 Critique (honest evaluation)

## What's weak / what a reviewer attacks
1. **The "+0.037 trend" is within noise.** Per-step reward std is ~0.18; with n=40–60
   rollouts/step the SE of the mean is ~0.025–0.029. The OLS slope (≈+0.0017/step)
   moves the mean by <1 SE over 15 steps. My analyzer honestly verdicts this `flat`.
   A reviewer is right to say the headline trend is **not statistically established** —
   D1's deeper finding is precisely that the trend is real-in-sign but sub-noise.
2. **n=1 run, no seeds.** No confidence band on the slope. I rejected multi-seed for
   D1 (compute cap + scope) but that means the 50-step projection (~0.58) is a point
   estimate with no error bars. This is the single biggest attackable gap.
3. **Compute blocker: 50 steps did not complete in-cap.** Real GRPO on the Tinker
   backend runs ~60–90 s/step (group 6 × 10 tasks = 60 rollouts/step, plus transient
   5xx retries). 50 steps ≈ 60–75 min, far past the ~15-min attended cap. I deliver a
   runnable launcher + a REAL partial curve + this documented blocker — not 50 fabricated steps.
4. **Near-ceiling tasks.** Tasks 0–9 start at ~0.50 mean; little headroom remains, so a
   flat/weak curve is the *expected* result, not evidence RFT fails. The right
   experiment (per prior memory) is the harder real-outage cascades where the model
   starts ~0.2. D1 deliberately froze hyper-params to stay comparable to the existing
   run, which is correct for "does the trend continue?" but limits how exciting the answer is.
5. **Append-not-resume.** The launcher's JSONL is append-only; re-running duplicates
   step indices rather than resuming. The analyzer sorts but does not dedup. Acceptable
   for one attended run; noted as a limitation.

## What's solid
- The launcher reuses the **unmodified** v2 trainer — zero core-file edits, fully
  parallel-safe.
- The live smoke + the real partial curve prove the pipeline works against the GPU backend.
- The fresh run **reproduces** the original v2 slope sign and magnitude (+0.0014 vs
  +0.0017/step), so the (weak) trend is at least repeatable, not a one-off artifact.
- The analyzer makes the claim falsifiable rather than a naked delta.

## Honest bottom line
D1 is **completed as a deliverable** (launcher + analyzer + live smoke + real partial
curve) with a **documented compute blocker** on finishing 50 steps in-cap, and the
substantive scientific finding is *negative-leaning*: on these near-ceiling tasks the
+0.037 trend is real in sign but within noise and projects to only ~0.58 by step 50 —
not a strong continued climb. The recommended follow-up is harder tasks + seeds.
