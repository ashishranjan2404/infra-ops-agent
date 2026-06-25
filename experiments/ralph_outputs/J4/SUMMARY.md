# J4 — SUMMARY

Task: Measure real MTTR improvement (agent-assisted vs unassisted) — design the
experiment, define metrics + statistics, build the analysis harness, reuse A9
mttr_labels as baseline, and (since real human-in-the-loop measurement is the
documented blocker) deliver the protocol + a simulation exercising the analysis
on synthetic timing data.

## Deliverables (experiments/ralph_outputs/J4/artifacts/)
- mttr_analysis.py — analysis harness. Log-space, scipy-optional (permutation
  fallback). Supports within-subjects (paired) and between-subjects (A/B).
  Primary endpoint: speedup = GM(unassisted)/GM(assisted) with bootstrap 95% CI;
  paired t-test/Wilcoxon (within) or Welch/Mann-Whitney (between); secondary:
  median min, %-within-SLO, Cliff's delta; required_n_paired power planner;
  --self-test (12 hermetic assertions).
- simulate_trials.py — synthetic trial generator grounded in A9
  mttr_labels.json real incidents; plants a known speedup with operator random
  effects, per-trial noise, and a configurable no-benefit fraction.
- trials_within.csv, trials_between.csv, report_within.json,
  report_between.json — real generated data + reports.

## Results (validation, NOT a real human study)
- Self-test: ALL PASS with scipy and with scipy blocked (permutation fallback).
- Within (50 pairs, planted 1.8x, 25% no-benefit): recovered 1.50x
  (33.6% MTTR reduction), CI [1.34, 1.68], p~0, Wilcoxon p~0.
- Between (120 incidents): 1.87x, CI [1.01, 3.39], p=0.048.
- Null negative-control (no real effect): speedup 0.96, CI brackets 1.0, p=0.34,
  not significant — the harness does not manufacture an effect.

## Reuse / safety
- Reuses A9 mttr_labels.json read-only as the baseline distribution.
- No shared core files edited (only J4/artifacts/).

## Honest limitations (see 09)
No real operator timing data — speedup figures are from simulation with a planted
effect (validates the instrument, not a real agent). Staged-replay external
validity, A9 outage-level vs diagnosis-segment scale mismatch, n~18 real labels,
resolved=False not yet excluded, fixed-effects (not mixed-model) t-test.

## Status: completed (deliverable real; real-world measurement blocked)
