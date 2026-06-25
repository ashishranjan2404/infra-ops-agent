# H5 — 06 Implementation

## Artifacts built (all under `experiments/ralph_outputs/H5/artifacts/`)
1. **`gen_manifest.py`** — reads two REAL upstream artifacts and normalizes them into one
   promotion manifest:
   - A1 `summary_table.json` (model `glm-5p2`, 630 episodes).
   - A2 `ablation_pass_at_k_deepseek-v4-pro.json` (`by_condition`, 750 episodes).
   Computes per-model baseline (each model's own `zero_shot.pass@1`), lift, and the
   three-test gate decision with human-readable reasons. ~190 LOC, stdlib only.
2. **`sample_manifest.json`** — generated output. 10 candidates (2 models x 5 conditions),
   schema `sre-degrees.promotion-manifest/v1`, with `gate`, `families`, `sources`
   provenance, and per-family pass@1/CI.
3. **`dashboard.html`** — self-contained (no deps) dashboard: summary counters
   (Candidates/Promote/Hold/Reject), per-model sortable table with a pass@1 bar + 95% CI
   band + yellow threshold tick, pass@2/5, lift, per-family pass@1, and a gate tag
   (PROMOTE/HOLD/REJECT) with the reason list. Fetches `sample_manifest.json`; on failure
   shows a loud error + `python3 -m http.server` hint; file-picker accepts any other
   manifest.

## Shared-file safety
No core file was edited. `experiments/dashboard.html` (the existing Ralph-progress
dashboard) is untouched — this is a brand-new, differently-purposed file under H5.

## Gate decisions produced (real numbers)
| candidate | pass@1 | CI_lo | lift | decision |
|---|---|---|---|---|
| glm-5p2/rex | 0.897 | 0.832 | +0.667 | **PROMOTE** |
| deepseek-v4-pro/rex | 0.893 | 0.834 | +0.653 | **PROMOTE** |
| both zero_shot / best_of_n / retry_realistic / rex_no_oracle | 0.23–0.35 | — | <0.20 | REJECT |

Only REx promotes on both models; every baseline and the no-oracle ablation is rejected —
consistent with A1/A2's own findings (the lift is the oracle feedback, not the tree).

## How to run
```
cd experiments/ralph_outputs/H5/artifacts
python3 gen_manifest.py            # regenerate sample_manifest.json
python3 -m http.server 8799        # then open http://127.0.0.1:8799/dashboard.html
```
