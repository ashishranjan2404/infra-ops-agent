# B9 — 01 Plan

## Objective
Provide a nonparametric **bootstrap (10,000 resamples) robustness check** on the
pass@1 confidence intervals that the REx pass@k pipeline currently reports with the
closed-form **Wilson score** interval. Confirm whether the Wilson CIs are trustworthy
on the real per-episode data, or whether they understate uncertainty.

## Approach
1. Use the real per-episode rewards already on disk:
   `rex/runs/ablation.json` — 5 conditions × 5 incidents × 3 seeds = 15 episodes /
   condition. This is the same data `experiments/compute_pass_at_k.py` turns into the
   Wilson CIs, so point estimates will be directly comparable.
2. Binarize each episode with the shipped rule `binary_pass(reward, 0.8)`.
3. Compute three intervals per condition:
   - **Wilson 95%** (reuse the shipped `wilson_ci`),
   - **Percentile bootstrap 95%** over the 15 i.i.d. episode outcomes (10k resamples),
   - **Cluster (block) bootstrap 95%** resampling whole incidents (5 blocks) to
     respect within-incident correlation (seeds of one incident are not independent).
4. Emit a JSON results file + a console table; write a self-contained pytest-style test.

## Files to create (all task-namespaced — NO shared-core edits)
- `experiments/ralph_outputs/B9/artifacts/bootstrap_ci.py` — the tool.
- `experiments/ralph_outputs/B9/artifacts/test_bootstrap_ci.py` — tests.
- `experiments/ralph_outputs/B9/artifacts/bootstrap_ci_results.json` — real output.
- `01..10_*.md`, `SUMMARY.md`, `result.json`.

## Dependencies
Python 3.13 stdlib only (`random`, `math`, `json`). No numpy/scipy required → runs
anywhere. Reuses `experiments/compute_pass_at_k.py` read-only for the Wilson formula.

## Risks
- **Small n (15).** Bootstrap is known to be unreliable at small n; must report this as
  a caveat, not hide it.
- **Clustering.** Episodes are grouped by incident; a naive i.i.d. bootstrap inherits the
  same optimism as Wilson. The cluster bootstrap is the honest comparison — expect it to
  be wider where passes are all-or-nothing per incident.
- **B3 not present.** The brief says "compare to Wilson CIs (B3 if present)". B3's
  artifacts dir is empty, so I compare to the canonical Wilson source
  (`compute_pass_at_k.py`) instead and document that B3 produced no artifact.

## Success criteria
- Script runs, 10k resamples, deterministic under a fixed seed.
- Bootstrap point estimates == shipped pass@1 exactly.
- Real intervals reported for all 5 conditions; divergences from Wilson explained.
- Tests pass. No shared core file modified.
