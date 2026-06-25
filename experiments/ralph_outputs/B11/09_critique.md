# 09 — Honest critique

## What a reviewer attacks

1. **Tiny, clustered sample.** n=15/arm, but those are 5 incidents x 3 seeds — seeds
   within an incident are correlated, so the EFFECTIVE sample size is closer to 5.
   The reported Wilson CIs (pooled n=15) are therefore optimistically narrow. The
   honest claim is "rank-order and gap preserved across thresholds," NOT "statistically
   separated at every cutoff." With overlapping CIs at n=15, significance is not
   established here.

2. **The sweep is partly degenerate by construction.** The reward lands on discrete
   bands and nothing falls in (0.70, 1.0). So 0.80, 0.86, 0.90 return IDENTICAL
   pass-rates — three of the four thresholds are redundant. The only real cut is
   0.70-vs-above. A skeptic calls the 4-threshold table padded. Mitigation: this is
   reported openly (06, RLE's prediction confirmed); the redundancy is itself a
   finding — it shows REx's wins sit at the TOP reward band (1.0), so no plausible
   strict threshold erodes them.

3. **Single model, single ablation file.** Robustness is shown only for
   claude-haiku-4-5 on the 5 hard cascades. It does not prove threshold-robustness for
   other models or the simple/novel families. A fuller version would sweep over the
   pass@k frontier data too (`rex/runs/frontier.json`, `harness_synth_v2.json`) — but
   those store aggregated pass-rates, not per-attempt rewards, so re-thresholding is
   not possible without re-running. Documented as the natural next step.

4. **`robust` flag is weak with one threshold.** It means "REx wins at every supplied
   threshold," so a single-threshold call makes it trivially the base claim. Only
   meaningful for >=2 thresholds (documented).

5. **Absolute pass-rates are low (REx 0.40).** These are the HARDEST cascades by
   design; the point is the relative lift over controls, not absolute mastery.

## What is genuinely solid
- The threshold is correctly located and the math is the canonical one (test-pinned to
  `compute_pass_at_k`).
- The data is real, the script is deterministic and reproducible, no core file touched.
- The headline (gap widens under stricter gates) is the strongest possible robustness
  signal for this dataset and directly rebuts "you tuned 0.80."

## Bottom line
Deliverable is real and correct; the result is robust for the one model/ablation it
covers. The honest limitation is statistical power (clustered n=15) and coverage
(one model), not the validity of the sweep.
