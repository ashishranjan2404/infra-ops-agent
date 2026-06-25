# I3 — Verification against success criteria

| Criterion | Status | Evidence |
|---|---|---|
| Correct dip implementation | MET | `diptest` v0.11 (AS 217); validation suite 6/6 pass; Gaussian D=0.018 p=0.76 (unimodal), two-spike D=0.191 p=0 (rejected). |
| Run on REAL reward distributions | MET | A1 (126/cond) + A2 (150/cond) `per_incident_rewards` + rex/runs `score`; all committed data, not synthetic. |
| Report D + p + conclusion | MET | `dip_results.json` has D, p, alpha, conclusion, pole masses for all 13 distributions. |
| No shared core files edited | MET | All new files under `experiments/ralph_outputs/I3/artifacts/`; only `pip install diptest` (dependency, not a repo file). |
| Outputs real, not placeholder | MET | Numbers come from executed runs (run.log verbatim); figure rendered from real data. |

## Are the outputs real?
Yes. Every D/p is produced by running the vetted dip test over reward arrays read
from committed JSON/JSONL. The p=0.0 entries are the analytic table's exact output
for large D (reported as p<1e-4 in prose), not rounded fabrications.

## Does the result answer the task?
The task asked to "analyze the bimodal distribution statistically." Result:
- **Weak policies (zero_shot, best_of_n, retry, rex_no_oracle): statistically
  BIMODAL** — dip D ∈ [0.12, 0.16], p<1e-4 in both A1 and A2. The bimodality is the
  pass/fail structure (mass at reward 0 and reward 1).
- **REx: statistically UNIMODAL** (A1 D=0.033 p=0.42; A2 D=0.025 p=0.78) — it
  concentrates ~90% of episodes at reward>=0.9, collapsing the failure mode.
- Pooled-across-conditions reads bimodal but is a mixed-population artifact (high-
  vs low-mean policies), interpreted as such, not as within-policy structure.
- rex/runs (n=12): bimodal (D=0.188, p=1e-4) but flagged for small n.

Robust to multiple-comparison correction: every weak-policy p (<1e-4) survives
Bonferroni at 0.05/13≈0.0038.
