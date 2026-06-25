# F14 — 03 Improved Plan

## What changed after the grill

The grill produced a sharper narrative spine. Concrete revisions:

1. **Thesis relocated.** Original plan hedged between "REx lifts every model" and "the env is
   the contribution." Per REV+SMR, the thesis is now unambiguously **the verifiable
   environment**, with the **searched safety verifier as the headline result inside it**. The
   0.86 REx table is demoted to *setup for the ablation*, not a result of its own.

2. **Hook split into two slides.** Per PSRE+RLE, slide 2 is the cascade war-story (the loud
   alert lies, the naive fix worsens it) and slide 3 is the explicit ML problem statement
   ("frozen model + can we verify correctness?"). Not blended.

3. **Ablation promoted to a full, prominent slide** (slide 12), framed as a self-audit:
   "REx 0.25 ≈ zero-shot 0.24 once the oracle root-cause hint is stripped → the defensible
   core is the env + searched verifier." Per REV+DOL.

4. **Added an explicit env-vs-policy slide** early (slide 5) so the ML audience doesn't
   conflate "we improved the model" with "we built an env that exposes model differences." Per RLE.

5. **Infra capped at one proof slide** (slide 11, Tier-A/Tier-B + Grafana-on-victim). Per DOL.

## Critiques accepted
- (REV) Ablation must be a slide, not a footnote → **accepted**, slide 12.
- (REV+SMR) Scope the verifier generalization claim (small n, can't invent unseen hazards) →
  **accepted**, baked into slide 10 + limitations slide 14.
- (PSRE+RLE) Split hook from ML framing → **accepted**, slides 2–3.
- (RLE) State env-vs-policy distinction explicitly → **accepted**, slide 5.
- (DOL) One infra slide only → **accepted**.

## Critiques rejected (and why)
- (PSRE) "Lead purely on the war-story, math later." **Rejected** as stated — for a 15-min AAAI
  slot the ML problem must land by ~90s or the audience mis-files the talk. We keep the
  war-story as the *opener* but immediately pivot. (This is the RLE compromise, not a full
  rejection of PSRE.)
- (SMR) "Searched verifier as the whole center of gravity." **Rejected** in favor of REV's
  framing: the env is the thesis, the verifier is the best result *within* it. Making a
  small-n result the entire thesis invites the "is 3 held-out incidents enough?" attack as the
  paper's central weakness rather than a scoped sub-result.

## Net structure (final, 17 slides)
Title → war-story → ML problem → why benchmarks fail → env-vs-policy → the environment →
the reward (anti-gaming) → REx loop → searched verifier (headline) → results table →
two-tier reality → **ablation/self-audit** → curriculum → limitations → related work →
contributions → close/Q&A. Timing budgeted in slide 04/the artifact.
