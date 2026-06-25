# I3 — Summary: Hartigan's dip test on SRE-Degrees reward distributions

**Task:** Analyze the bimodal reward distribution statistically with Hartigan's dip
test. Implemented (vetted `diptest` v0.11, AS 217) and ran on REAL per-episode
reward data from A1 (glm-5p2), A2 (deepseek-v4-pro), and rex/runs.

## Result (alpha = 0.05)
Bimodality is a property of the **weak policies**; **REx is unimodal** because it
collapses the failure mode toward reward 1.0.

| condition | A1 D / p | A2 D / p | verdict |
|---|---|---|---|
| zero_shot | 0.143 / <1e-4 | 0.120 / <1e-4 | BIMODAL |
| best_of_n | 0.151 / <1e-4 | 0.164 / <1e-4 | BIMODAL |
| retry_realistic | 0.147 / <1e-4 | 0.160 / <1e-4 | BIMODAL |
| rex_no_oracle | 0.147 / <1e-4 | 0.154 / <1e-4 | BIMODAL |
| **rex** | **0.033 / 0.42** | **0.025 / 0.78** | **unimodal (~90% at reward>=0.9)** |

Pooled-across-conditions: bimodal (mixed-population artifact). rex/runs (n=12):
bimodal D=0.188 p=1e-4 (small-n, flagged). Robust to Bonferroni (0.05/13).

## Interpretation
The pass/fail reward structure (mass at 0 and 1) makes weak policies statistically
bimodal. REx does not merely raise the mean — it eliminates the lower (failure)
mode, leaving a near-degenerate spike at the ceiling, which the dip test reads as
unimodal. Caveats: discrete reward atoms make high dip partly mechanical;
seed-correlation reduces effective n; REx unimodality is ceiling saturation.

## Artifacts
- artifacts/dip_test.py — dip test (diptest engine + numpy fallback)
- artifacts/run_dip_on_rewards.py — loader + runner over real data
- artifacts/test_dip_test.py — validation suite (6/6 pass)
- artifacts/dip_results.json — full numeric results (13 distributions)
- artifacts/make_figure.py + reward_dip_histograms.png
- artifacts/run.log

Validation gate (Gaussian unimodal, two-spike bimodal) passes; the analysis is
trusted only because it does.
