# B9 — SUMMARY

**Task:** Bootstrap confidence intervals (10,000 resamples) as a robustness check on the
pass@k pipeline's Wilson CIs.

**Delivered (all in `artifacts/`, no shared-core edits):**
- `bootstrap_ci.py` — stdlib-only tool computing, per condition, Wilson 95% + i.i.d.
  percentile bootstrap 95% (10k) + cluster/block bootstrap 95% (10k) from real
  per-episode rewards in `rex/runs/ablation.json`. Deterministic via `--seed`.
- `test_bootstrap_ci.py` — 12 assertions, all pass.
- `bootstrap_ci_results.json` — real output.

**Real results (pass@1, model claude-haiku-4-5, n=15, 5 incidents):**

| condition | pass@1 | Wilson 95% | i.i.d. bootstrap | cluster bootstrap |
|---|---|---|---|---|
| zero_shot | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |
| best_of_n | 0.067 | [0.012, 0.298] | [0.000, 0.200] | [0.000, 0.200] |
| retry_realistic | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |
| **rex** | **0.400** | **[0.198, 0.643]** | **[0.133, 0.667]** | **[0.000, 0.800]** |
| rex_no_oracle | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |

**Findings:**
- Point estimates reproduce `experiments/compute_pass_at_k.py` exactly.
- Under i.i.d., the bootstrap corroborates Wilson (rex [0.133,0.667] ~ [0.198,0.643]).
- The cluster bootstrap exposes Wilson's optimism: REx passes are all-or-nothing per
  incident, so resampling whole incidents widens the rex CI to [0.000, 0.800] — the
  true new-incident generalization uncertainty is much larger than Wilson implies.
- 0/n boundary: bootstrap degenerates to [0,0] for all-fail conditions; Wilson stays the
  correct default there.

**Verdict:** Robustness check complete. Wilson CIs are fine given i.i.d.; the real
limitation is only 5 distinct incidents. Actionable takeaway: add more incidents, not a
new estimator. B3's artifacts dir was empty, so comparison was made to the canonical
Wilson source (compute_pass_at_k.py).
