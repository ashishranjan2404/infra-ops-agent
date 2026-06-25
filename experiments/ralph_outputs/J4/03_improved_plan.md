# J4 — 03 Improved Plan

## What changed after the grill
1. **Dual endpoint (accepted, SMR+PSRE).** Primary = multiplicative speedup =
   GM(unassisted)/GM(assisted) with bootstrap CI, in log space. Secondary =
   median MTTR per arm + **% incidents resolved within SLO budget** (`--slo`) so
   the result is legible to non-statisticians. Both are emitted in the report.
2. **Both designs implemented (accepted, REV+RLE).** `--design within` (paired on
   `pair_id`) and `--design between` (A/B). Within uses paired t-test + Wilcoxon +
   paired bootstrap; between uses Welch t-test + Mann-Whitney + two-sample bootstrap.
3. **Operator heterogeneity (accepted, DOL+RLE).** The simulation gives each
   operator a random-effect on how much the agent helps them, plus a per-trial
   noise term, so "agent speedup" is not a constant — this stresses the stats the
   way real operator variance would.
4. **No-benefit fraction (accepted, REV's contamination worry).** A configurable
   fraction of incidents get ~no agent benefit (novel/hard ones), so the planted
   effect is attenuated and realistic — the harness must NOT over-claim. Observed:
   planting 1.8x with 25% no-benefit yields a recovered ~1.5x, honestly attenuated.
5. **Nonparametric backups + effect size (accepted, SMR/REV).** Cliff's delta +
   Wilcoxon/Mann-Whitney so the conclusion doesn't hinge on log-normality.

## Critiques accepted
- Log-space / GM ratio (SMR) — durations span ~160x; arithmetic mean is wrong.
- Operator confound as random effect / matched pairs (DOL).
- Staged-replay external-validity limit is first-class (REV/DOL) → in `09`.

## Critiques rejected (with reasons)
- **PSRE's full TTD/TTA/TTR segmentation + severity stratification**: rejected as
  *built-in* because RLE is right that with n in the dozens it destroys power. The
  protocol *recommends* restricting collection to the diagnosis-to-resolution
  segment, but the harness stays segment-agnostic (it analyzes whatever
  `mttr_minutes` you feed it) — stratification is left to the caller via separate
  runs, not hard-coded cells.
- **REV's "between-subjects only / reject staged data" purism**: rejected as a
  blocker on shipping anything. We *implement* between-subjects AND we *disclose*
  the staged-replay limitation, but we do not refuse to deliver a harness because
  ideal production A/B is unethical (DOL's point stands: you can't withhold a
  helpful tool during a customer-impacting incident).

## Unchanged
Reuse A9 labels as the grounded baseline distribution; deliver protocol + harness
+ simulation; document the real-data blocker.
