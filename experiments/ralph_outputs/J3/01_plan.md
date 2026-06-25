# 01 — Plan (J3: Human-eval study — 5 SREs rate agent diagnoses)

## Objective
Design a rigorous, runnable human-evaluation study in which 5 practicing SREs rate the
SRE agent's incident diagnoses on **correctness**, **usefulness**, and **safety**, and
produce the full study packet plus a scoring/IAA script. The goal is a *validity check*:
do automated rewards (`rex/scoring.py` deterministic judge) actually track expert human
judgment? Human recruitment is the known/expected blocker — everything around it must be
real and ready to execute the moment raters exist.

## Approach
1. Pull **real** agent diagnoses from `opensre-traj/out/hud_trajectories.jsonl`
   (197 runs across claude-opus-4-8, claude-haiku-4-5, kimi-k2p5; each has
   `answer`, `reward`, `subscores`, `true_category`, difficulty, source company/URL).
2. **Stratified-sample 12 diagnoses** across model × reward-band × difficulty so the
   rating set has spread (avoids the "all-same-quality" defect that kills IAA studies).
3. **Blind** the items (strip model identity into a sealed `blinding_key.json`) so raters
   are not biased by provider.
4. Write a **protocol** (recruitment, eligibility, blinding, task flow, time budget,
   ethics/consent, pilot) and a **rubric** (anchored 1–5 Likert per dimension + a binary
   "would you act on this root cause?" trust item).
5. Write a **scoring script** that computes per-item / per-rater means, **Krippendorff's
   alpha (ordinal)** + mean pairwise Spearman + percent agreement for IAA, and the
   **human-vs-automated-reward correlation** (the actual research payoff).
6. Validate the script with a **synthetic 5-rater self-test** (no human data needed) and
   on **example filled CSVs**, so the analysis pipeline is proven before recruitment.

## Files to create (all task-namespaced under J3/)
- `artifacts/diagnoses_to_rate.json` — 12 blinded real diagnoses (the rating set)
- `artifacts/blinding_key.json` — sealed model/trace/auto-reward key
- `artifacts/rubric.md` — anchored Likert rubric + instructions
- `artifacts/protocol.md` — recruitment / consent / procedure / analysis plan
- `artifacts/ratings_template.csv` — blank CSV raters fill in
- `artifacts/ratings_example/*.csv` — 5 demo rater CSVs (synthetic, labeled) to prove the path
- `artifacts/score_human_eval.py` — analysis + IAA + validity script (stdlib only)
- 10 step docs + SUMMARY.md + result.json

## Dependencies
- Python 3.13 stdlib only (csv, json, math). No numpy/scipy — keeps it runnable anywhere.
- Source data: `opensre-traj/out/hud_trajectories.jsonl` (read-only).

## Risks
- **Recruitment blocker** (primary): no 5 SREs on hand → study cannot return real ratings.
  Mitigation: ship a synthetic self-test + example CSVs so the pipeline is fully validated;
  document recruitment as the explicit blocker.
- **IAA fragility**: 5 raters × 12 items is small; alpha CIs will be wide. Mitigation: report
  alpha + Spearman + within-1 agreement together; pre-register that conclusions are tentative
  below alpha 0.667.
- **Single-rater leniency**: handled by per-rater mean reporting.

## Success criteria
- 12 real, blinded, stratified diagnoses written and parseable.
- Rubric has concrete behavioral anchors for every Likert point (not bare 1–5).
- Protocol covers recruitment, consent, blinding, pilot, and a pre-registered analysis plan.
- Scoring script runs green on synthetic self-test AND on example CSVs, emitting
  Krippendorff alpha + validity correlations.
- Blocker (human recruitment) documented honestly; no fabricated human ratings.
