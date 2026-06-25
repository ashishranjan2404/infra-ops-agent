# I3 — Statistical analysis of the bimodal reward distribution (Hartigan's dip test)

## Objective
Test, rigorously, whether the per-episode reward distributions in SRE-Degrees are
bimodal (a pass/fail "0-or-1" structure with a thin middle) using Hartigan &
Hartigan's (1985) dip test of unimodality. Report the dip statistic D, the
p-value, and a conclusion at alpha=0.05 for each real reward distribution we have.

## Approach
1. Implement / obtain a correct dip test. Hartigan's D is the max distance from the
   ECDF to the closest unimodal CDF (via GCM left of the mode, LCM right of it),
   in [0, 0.25]. p-value vs the least-favourable unimodal null (Uniform).
2. Source REAL per-episode reward arrays:
   - A1 full pass@k (`full_pass_at_k_glm-5p2.json`) — `by_condition[*].per_incident_rewards`
     (glm-5p2, 5 conditions x 126 episodes).
   - A2 ablation (`ablation_pass_at_k_deepseek-v4-pro.json`) — same shape, 5 x 150.
   - `rex/runs/diagnostic_probe_*.jsonl` — per-iteration `score`.
3. Run the dip test per condition + pooled + rex/runs; report D, p, conclusion,
   and pole-mass descriptors (frac at <=0.1, >=0.9, middle).
4. Validate the implementation against known cases (uniform/normal = unimodal,
   two-spike = bimodal) before trusting the numbers on real data.

## Files to create (task-namespaced — NO shared core edits)
- `artifacts/dip_test.py` — dip test (vetted `diptest` pkg + numpy fallback).
- `artifacts/run_dip_on_rewards.py` — loader + runner over real data.
- `artifacts/test_dip_test.py` — validation suite.
- `artifacts/make_figure.py` + `reward_dip_histograms.png`.
- `artifacts/dip_results.json`, `artifacts/run.log`.

## Dependencies
numpy, scipy (present); `diptest` (pip-installable, vetted AS 217 binding);
matplotlib for the figure (optional — degrade gracefully).

## Risks
- A hand-rolled dip statistic is easy to get subtly wrong for non-uniform unimodal
  shapes (Gaussian) — mitigate by using the vetted `diptest` package as primary
  engine and validating on known distributions.
- Rewards are discrete/clumped (0, 0.3, 0.4, 0.75, 1.0) — ties are fine for the
  dip test but worth noting.

## Success criteria
- A correct dip implementation (passes uniform/normal/bimodal sanity tests).
- Dip D + p reported for every real reward distribution available.
- An honest conclusion per distribution, written to JSON + a figure.
