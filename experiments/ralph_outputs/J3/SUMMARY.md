# J3 — SUMMARY: Human-evaluation study (5 SREs rate agent diagnoses)

## What this is
A complete, validated human-evaluation study packet for having 5 practicing SREs rate the
SRE agent's incident diagnoses on correctness / usefulness / safety (anchored 1-5 Likert) plus
a binary "would you act on this root cause?" trust item, plus a scoring/IAA script. The
research goal is a validity check on the automated deterministic judge (rex/scoring.py): do
expert humans agree with each other, and do they track the automated reward?

## Deliverables (all under J3/artifacts/, no shared core files touched)
- diagnoses_to_rate.json - 12 real, blinded agent diagnoses, stratified across 3 models
  (opus-4-8 / haiku-4-5 / kimi-k2p5), difficulty 3-5, auto-reward 0.11-0.75. Source:
  opensre-traj/out/hud_trajectories.jsonl (197 real runs).
- blinding_key.json - sealed model/trace/auto-reward key (for the validity join).
- rubric.md - anchored Likert rubric (behavioral anchor per point) + trust item.
- protocol.md - recruitment, consent/ethics, blinding, procedure, pre-registered IAA +
  validity analysis plan, 1-rater pilot fallback.
- ratings_template.csv - blank rater CSV.
- score_human_eval.py - stdlib-only analysis: per-item/per-rater means, Krippendorff's
  alpha (ordinal), mean pairwise Spearman, exact/within-1 % agreement, and human-vs-auto-reward
  Spearman/Pearson validity. Synthetic 5-rater self-test built in.
- ratings_example/*.csv + results_example.json - synthetic (clearly labeled) demo proving
  the real-CSV path.

## Validation
6 tests pass (T0 compile/parse, T1 self-test, T2 CSV-path-equals-in-memory, T3 item/key align,
T4 missing-cell tolerance, T5 degenerate alpha=1.0). Self-test emits Krippendorff alpha 0.63-0.74
and validity Spearman 0.79-0.94 (high by construction - confirms the correlation code).

## Blocker (documented, not faked)
Human recruitment. No 5 SREs are currently recruited, so no real IAA or validity numbers
exist. The entire pipeline is built and tested so real results are one command away once raters
submit. No human ratings were fabricated.

## Status: completed (deliverable real; downstream human result blocked)
