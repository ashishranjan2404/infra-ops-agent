# 02 — Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (MLR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes
- **MLR**: The point of this study isn't to "grade the agent" — it's to *validate the
  automated reward*. The headline number must be the correlation between human scores and
  `rex/scoring.py`'s reward. If that's missing, the study is decorative.
- **PSRE**: Three dimensions is right, but they aren't independent. A diagnosis can be
  *correct* yet *unsafe* (right root cause, recommends a destructive fix). Keep correctness,
  usefulness, AND safety separate or you'll average away the thing on-call actually cares about.
- **REV**: Without inter-annotator agreement you have nothing publishable. Report
  Krippendorff's alpha, not just Cohen's kappa (kappa is for 2 raters / nominal). And
  12 items × 5 raters is underpowered — be explicit that conclusions are tentative.
- **RLE**: Sample selection will make or break this. If you sample only high-reward runs,
  humans will rate everything 5/5 and alpha collapses (no variance). You MUST stratify
  across the reward distribution.
- **DOL**: Who are these 5 SREs and when do they have an hour? Recruitment is the real
  project risk, and "we'll find some" is how studies die. Need a concrete recruitment plan,
  consent, and a time budget or no one shows.

## Round 2 — genuine disagreement (react to a named persona)
- **PSRE → MLR**: I disagree that the correlation is the headline. If human alpha is low,
  the human scores are noise and correlating noise with the auto-reward tells you *nothing*.
  IAA is the gate; correlation is conditional on passing it. Order of operations matters.
- **MLR → PSRE**: Partly fair, but you've inverted it. Low alpha on a *3-dimension subjective*
  rubric is expected and doesn't void the study — it tells you which dimension is ill-defined.
  Safety often has low alpha because raters weight blast-radius differently. I won't gate the
  entire study on a single alpha threshold; report per-dimension and let the reader judge.
- **REV → RLE**: Stratifying by *reward band* bakes the auto-judge's opinion into your sample,
  then you correlate humans against that same judge — that's mild circularity. I'd stratify by
  something judge-independent (difficulty, model) too, so the validity test isn't rigged.
- **RLE → REV**: Disagree that it's circular. Stratifying by reward only ensures *spread on the
  x-axis* of the validity plot; it does not predetermine where humans land on the y-axis. If
  humans disagreed with the judge, the correlation would still be low. Spread ≠ circularity.
  I'll concede we should ALSO stratify by difficulty/model so no band dominates.
- **DOL → REV**: You and the methodology purists keep adding rater requirements; meanwhile I
  still can't staff 5 SREs for free. I'd rather ship a *validated pipeline + 1-rater pilot* than
  a perfect protocol no one can run. Pragmatism over a 6th IAA metric.

## Round 3 — synthesis
- **Gate, then correlate (PSRE+MLR compromise)**: report IAA *per dimension*; pre-register
  that the validity correlation is reported for all dimensions but only *interpreted* where
  alpha ≥ 0.667. Don't void the whole study on one number.
- **Stratify on BOTH judge-independent axes and reward (REV+RLE)**: sample across model and
  difficulty (judge-independent) AND ensure reward spread, so the validity x-axis has range
  without rigging the y-axis. (Implemented: 3 models, difficulty 3–5, reward 0.11–0.75.)
- **Keep 3 separate dimensions + a binary trust item (PSRE)**: correctness, usefulness,
  safety stay separate; add `confident_root_cause` (0/1) = "would you act on this RC?".
- **Recruitment is THE blocker, make it cheap (DOL)**: ship synthetic self-test + example
  CSVs so the analysis is proven; protocol includes a 30-min time budget, async option, and a
  1-rater pilot fallback so the study degrades gracefully.
- **IAA = Krippendorff alpha (ordinal) primary (REV)**, plus mean pairwise Spearman and
  within-1 % agreement as companions; explicitly flag underpowered N.
