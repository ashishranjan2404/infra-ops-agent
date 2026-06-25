# 09 — Honest Critique

## The headline weakness
**No human ratings exist.** This is by far the biggest gap. We delivered a validated *apparatus*
but zero real human data, so the actual research question — "do SREs agree, and do they track the
auto-judge?" — is unanswered. A reviewer can fairly say "this is a study design, not a study."
That is true; the task explicitly named human recruitment as the documented blocker, and we did
not fabricate around it. But it must be stated plainly: **the validity finding is pending.**

## Statistical weaknesses
- **Underpowered**: 12 items × 5 raters. Krippendorff alpha at this N has a very wide CI; a
  point estimate near the 0.667 threshold is essentially a coin flip about whether the study
  "passed." We flag this but do not fix it (would need more items + bootstrap CIs).
- **No confidence intervals**: the stdlib-only constraint means no bootstrap CI on alpha or on
  the validity correlation. Reported numbers are point estimates only.
- **Stratified (non-random) sampling** of 12 items can inflate the human-vs-reward correlation;
  we label it exploratory, but a purist would want a random held-out sample too.

## Design weaknesses an AAAI/SRE reviewer would attack
- **Rubric subjectivity, especially Safety.** "Correctly defers = safe" is a judgment call;
  raters may disagree on whether an RCA-only answer is "safe" or "useless," coupling the Safety
  and Usefulness dimensions. Expect lower alpha on Safety.
- **Calibration item is also scored.** Light-touch calibration on DX01 then including it in
  analysis mildly contaminates independence. A stricter design uses a separate throwaway item.
- **Circularity residue**: we correlate humans against the same judge whose reward we used to
  spread the sample. We argued (02/03) this only spreads the x-axis, but a skeptic won't be
  fully satisfied; a cleaner test draws items blind to reward.
- **Self-graded ouroboros/grill**: the critique personas are all me; real adversarial review
  from an external methodologist would likely surface more.

## Tooling weaknesses
- No JSON-schema validation on rating CSVs; a malformed header yields empty output with only a
  stderr note. Acceptable for a 5-rater internal study, not for scale.
- The ordinal-alpha implementation is hand-rolled; though it passes degenerate (=1.0) and
  plausibility checks, it has not been cross-validated against a reference library (e.g.
  `krippendorff` / `nltk`) — a worthwhile future check.

## What I'd do with more resources
Recruit 5 SREs, run the protocol, cross-check alpha against a reference implementation, add
bootstrap CIs, and draw a second random (reward-blind) sample to kill the circularity critique.

## Honest status
**Completed deliverable, blocked downstream result.** The packet + scoring pipeline are real and
tested; the human study itself is not run because no raters are recruited. No human numbers were
invented.
