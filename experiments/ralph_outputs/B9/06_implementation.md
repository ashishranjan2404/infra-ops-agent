# B9 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/B9/artifacts/`)
1. **`bootstrap_ci.py`** — the robustness tool.
   - Loads real per-episode rewards from `rex/runs/ablation.json`.
   - Binarizes with the shipped `binary_pass(reward, 0.8)`.
   - Computes three 95% intervals per condition:
     - **Wilson** (reused `experiments/compute_pass_at_k.py::wilson_ci`),
     - **i.i.d. percentile bootstrap** (10,000 resamples over 15 episodes),
     - **cluster/block bootstrap** (10,000 resamples over the 5 incident blocks).
   - Hand-written, tested `percentile()` (linear interpolation) — no numpy, stdlib only.
   - Deterministic via `random.Random(--seed)`; writes a JSON artifact + prints a table.
   - Graceful fallback to a local (identical) Wilson formula if the import fails;
     records which path was used in `reference_estimator_source`.
2. **`test_bootstrap_ci.py`** — 12 self-contained assertions (loads the module by path).
3. **`bootstrap_ci_results.json`** — the real 10k-resample output.

## Commands run
```
python3 experiments/ralph_outputs/B9/artifacts/bootstrap_ci.py \
    --resamples 10000 --seed 12345 \
    --out experiments/ralph_outputs/B9/artifacts/bootstrap_ci_results.json
python3 experiments/ralph_outputs/B9/artifacts/test_bootstrap_ci.py
python3 experiments/compute_pass_at_k.py   # cross-check point estimates / Wilson
```

## Real results (pass@1, 95% CI; model = claude-haiku-4-5, n=15, 5 incidents)
| condition | pass@1 | Wilson | i.i.d. bootstrap | cluster bootstrap |
|---|---|---|---|---|
| zero_shot | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |
| best_of_n | 0.067 | [0.012, 0.298] | [0.000, 0.200] | [0.000, 0.200] |
| retry_realistic | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |
| **rex** | **0.400** | **[0.198, 0.643]** | **[0.133, 0.667]** | **[0.000, 0.800]** |
| rex_no_oracle | 0.000 | [0.000, 0.204] | [0.000, 0.000] | [0.000, 0.000] |

## Key findings
- **Point estimates match the shipped pipeline exactly** (rex=0.400, best_of_n=0.067,
  others 0.000) — the bootstrap operates on the same binarized data.
- **rex is the informative row.** i.i.d. bootstrap `[0.133, 0.667]` roughly tracks Wilson
  `[0.198, 0.643]`. The **cluster bootstrap balloons to `[0.000, 0.800]`** because rex
  passes are all-or-nothing per incident (3/3 on aws_dynamodb_dns & railway_gcp_suspension,
  0/3 on the other three). Resampling whole incidents can therefore land on 0/5 or 4/5
  incidents passing → the true uncertainty about generalizing to *new* incidents is much
  larger than Wilson's i.i.d. interval implies.
- **0/n boundary:** for the three all-fail conditions the bootstrap returns a degenerate
  `[0,0]`, narrower than Wilson's `[0,0.204]`. This is the well-known bootstrap failure at
  the boundary — Wilson is the correct default there.

## Shared-core safety
No shared core file modified. `compute_pass_at_k.py` is imported read-only; `ablation.json`
is read-only. Proposed integration (optional) is documented in 09, NOT applied.
