# H5 — SUMMARY

**Task:** Build a real, self-contained HTML dashboard for live experiment monitoring
(the promotion-engine dashboard) that reads a results JSON manifest and shows
model/condition pass@k with a promotion-gate view; generate a sample manifest from real
A1/A2 numbers and verify the HTML loads it. Do not edit shared core files or the existing
`experiments/dashboard.html`.

**Status:** completed.

## Deliverables (all under `experiments/ralph_outputs/H5/artifacts/`)
- `gen_manifest.py` — reads real A1 (`summary_table.json`, glm-5p2, 630 episodes) and A2
  (`ablation_pass_at_k_deepseek-v4-pro.json`, 750 episodes); normalizes into one
  `sre-degrees.promotion-manifest/v1` manifest with per-model baseline lift and a
  three-test promotion gate.
- `sample_manifest.json` — 10 candidates (2 models x 5 conditions), real numbers, gate
  decisions precomputed.
- `dashboard.html` — dependency-free dashboard: counters, per-model sortable table with
  pass@1 bar + 95% CI band + threshold tick, pass@2/5, lift, per-family pass@1, and a
  PROMOTE/HOLD/REJECT gate tag with reasons. Fetches the manifest; file-picker fallback for
  `file://`; loud failure with serve hint.

## Promotion gate
PROMOTE requires ALL of: pass@1 >= 0.80, CI_lo >= 0.70, lift over same-model zero_shot
>= 0.20. Result: 2 PROMOTE (glm-5p2/rex 0.897, deepseek-v4-pro/rex 0.893), 8 REJECT
(all baselines + the rex_no_oracle ablation) — consistent with A1/A2 findings.

## Verification (5/5 PASS)
Generator runs and prints counts; manifest is valid v1 JSON (10 candidates); HTML parses;
served over HTTP both dashboard.html and sample_manifest.json return 200 (application/json);
a Node DOM-shim run of the page's real script over the manifest yields
tot=10, prom=2, hold=0, rej=8 with no JS error and the error box hidden.

## Honest caveats
"Live" = manifest + manual reload (no streaming/auto-poll); two-model single snapshot, no
time series; gate thresholds are documented judgment calls; CIs rendered from source, not
re-audited; visual layout verified headlessly, not by screenshot. No shared/core file
edited — the existing experiments/dashboard.html is untouched.
