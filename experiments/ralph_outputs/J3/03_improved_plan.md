# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Validity is gated, not unconditional.** Pre-register: report Krippendorff alpha per
   dimension; *interpret* the human-vs-auto-reward correlation only for dimensions with
   alpha ≥ 0.667 (Krippendorff's tentative-conclusion threshold). Still compute & report it
   everywhere. (Accepted PSRE's gate, kept MLR's "don't void the study".)
2. **Two-axis stratification.** Sample stratified by **model** and **difficulty**
   (judge-independent) AND ensure **reward spread** for x-axis range — addressing REV's
   circularity worry while keeping RLE's variance argument. Final set: 3 models, difficulty
   3–5, auto-reward 0.11–0.75.
3. **Added a binary trust item** `confident_root_cause` (0/1): "would you act on this root
   cause on-call?" — captures the correctness≠safety gap PSRE raised, separate from Likerts.
4. **Graceful degradation for the recruitment blocker** (DOL): protocol adds a 30-min time
   budget, async-by-CSV option, and a **1-rater pilot** fallback; pipeline validated via a
   synthetic 5-rater self-test + example CSVs so zero human data is needed to prove it runs.
5. **IAA metric stack** fixed: Krippendorff alpha (ordinal) primary; mean pairwise Spearman +
   exact/within-1 % agreement as companions; N flagged as underpowered in every report.

## Critiques accepted
- PSRE: keep 3 dimensions separate + add trust binary. (accepted)
- REV: Krippendorff over Cohen's kappa; flag underpowered N; two-axis stratification. (accepted)
- RLE: stratify for reward variance or IAA collapses. (accepted)
- MLR: the human↔auto-reward correlation is the research payoff and must be computed. (accepted)
- DOL: concrete recruitment + consent + time budget + pilot fallback. (accepted)

## Critiques rejected (with reason)
- **REV's "reward stratification is circular" (rejected as stated).** Stratifying the *sample*
  by reward only gives x-axis spread on the validity plot; it does not determine where humans
  score (y-axis). If humans disagreed with the judge, correlation would still be low. We keep
  reward spread but *add* judge-independent axes as a compromise rather than dropping it.
- **PSRE's "gate the entire study on alpha" (rejected).** Per-dimension gating only; a single
  low-alpha dimension (likely safety) does not void correctness/usefulness findings.
- **DOL's "ship a 1-rater pilot instead of the full protocol" (rejected as the primary plan).**
  We ship the full 5-rater protocol AND keep the 1-rater pilot strictly as a fallback, not the
  headline — a 1-rater study can't produce IAA, which is the point.

## Net deliverable
Full study packet (protocol + rubric + 12 blinded real diagnoses + blinding key + CSV
template + example CSVs) and a stdlib scoring script proven green on synthetic + example data;
human recruitment documented as the blocker.
