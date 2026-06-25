# Human-Evaluation Study Protocol (J3) — 5 SREs rate agent diagnoses

## 1. Purpose & research question
**RQ**: Do practicing SREs agree with each other on the quality of the agent's incident
diagnoses, and does expert human judgment track the automated deterministic reward
(`rex/scoring.py`)? This is a *validity study* for the automated judge, not a model leaderboard.

## 2. Design
- **Within-subjects, fully crossed**: every rater rates every item (5 raters × 12 items = 60
  ratings per dimension).
- **Blinded**: model identity is removed from items and sealed in `blinding_key.json`.
  Ground-truth root cause is **withheld until after** a rater submits, so it cannot leak into
  correctness scores.
- **Stratified item set**: 12 real agent diagnoses sampled across 3 models
  (claude-opus-4-8, claude-haiku-4-5, kimi-k2p5), difficulty 3–5, and the automated-reward range
  (0.11–0.75), so the rating set has genuine quality spread. Source: real runs in
  `opensre-traj/out/hud_trajectories.jsonl`.

## 3. Participants & recruitment  ← **BLOCKER lives here**
- **Eligibility**: ≥2 years production on-call SRE/DevOps experience; comfortable reading
  Kubernetes/cloud incident logs. No involvement in building this agent (avoids bias).
- **N = 5** (minimum for a usable Krippendorff alpha; pre-registered as underpowered).
- **Recruitment channels** (to execute): internal SRE Slack (#sre, #incident-review); 2 external
  SREs via professional network; offer a 30-min slot + small honorarium/gift card.
- **Status**: *No raters are currently recruited.* This is the documented blocker (see 07/09).
  Until raters exist, the study is validated only via the synthetic self-test + example CSVs.

## 4. Consent & ethics
- Voluntary; raters may stop anytime. Ratings are pseudonymous (`rater_id` = `sre1..sre5`, not
  real names). No PII collected. Free-text must not contain customer data. Data used only for
  internal evaluation; aggregate results may be reported.

## 5. Procedure (per rater, ~30 min)
1. Read `rubric.md` (5 min). Optional 1-item walkthrough with the facilitator.
2. **Pilot/calibration item** (DX01): rate it, then briefly discuss anchors with the facilitator
   to align interpretation. (DX01 is *included* in analysis; calibration is light-touch.)
3. Rate the remaining 11 items independently, no discussion between raters.
4. Submit `ratings_<id>.csv` (copy of `ratings_template.csv`).
5. **Post-rating reveal**: facilitator shares ground-truth categories; rater may add free-text
   reflections. (Reveal happens only after submission.)

## 6. Pre-registered analysis plan (IAA)
Run `score_human_eval.py --ratings ratings/*.csv --key blinding_key.json`.
- **Primary IAA**: Krippendorff's alpha (ordinal) per dimension. Interpretation thresholds:
  ≥0.80 strong; ≥0.667 acceptable (tentative conclusions only); <0.667 weak.
- **Companion IAA**: mean pairwise Spearman ρ; exact and within-1 percent agreement.
- **Validity** (the payoff): Spearman & Pearson of per-item human mean vs `auto_reward`, reported
  for all three dimensions but **interpreted only** where that dimension's alpha ≥ 0.667.
- **Descriptives**: per-item means, per-rater means (leniency/strictness check).
- **Pre-registration**: N=12 items is underpowered; all conclusions are explicitly tentative.
  Bootstrap confidence intervals are a planned future extension (not in the stdlib script).

## 7. Graceful degradation (if full recruitment fails)
- **1-rater pilot fallback**: a single SRE rates all 12 items → produces descriptives and a
  validity correlation, but **no IAA** (which is the study's point). Use only to de-risk the
  rubric, not as a result.
- The analysis pipeline is already proven on synthetic data, so the moment ≥2 raters submit,
  real IAA numbers are one command away.

## 8. Deliverables checklist
- [x] `diagnoses_to_rate.json` (12 blinded real diagnoses)
- [x] `blinding_key.json` (sealed)
- [x] `rubric.md`
- [x] `ratings_template.csv`
- [x] `score_human_eval.py` (validated)
- [ ] `ratings/sre{1..5}.csv` ← **requires recruited humans (blocker)**
- [ ] `results.json` from real ratings ← **requires the above**
