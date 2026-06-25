# B12 — Per-incident pass@k breakdown — SUMMARY

## Goal
Convert family-level pass@k results into a per-incident view and flag unsolvable
incidents, by ingesting the A1/A2 pass@k result JSONs (no episode re-runs needed).

## Deliverables (all under B12/, no shared-core edits)
- `artifacts/per_incident_breakdown.py` — CLI: ingests N pass@k JSONs -> per-incident
  table (incident -> pass@1/pass@k per condition) + solvability flag; emits machine JSON
  + human Markdown.
- `artifacts/test_per_incident_breakdown.py` — 7 unit tests (no pytest dep), all pass.
- `artifacts/out/per_incident_breakdown.{json,md}` — real output over A1 (glm-5p2, 42 inc)
  + A2 (deepseek-v4-pro, 30 inc) = 72 incident x model rows.

## Reproduce
```
cd experiments/ralph_outputs/B12/artifacts
python3 per_incident_breakdown.py \
  --inputs ../../A1/artifacts/full_pass_at_k_glm-5p2.json \
           ../../A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json \
  --out-json out/per_incident_breakdown.json --out-md out/per_incident_breakdown.md
```

## Key findings (real data, threshold 0.8)
- 72 rows: solvable 64 / partially 1 / unsolvable 7.
- By family (solvable/partially/unsolvable): cascade 24/0/6 / novel 20/0/0 / simple 20/1/1.
- Unsolvable under BOTH models (robust): azure_ddos, cloudflare_waf, crowdstrike_bsod.
- glm-5p2-only unsolvable: singleton_node_notready; partially: payments_dep_revoked.
- 41 learnable-but-hard rows: zero_shot pass@1 == 0 but rex pass@1 == 1 — mostly
  cascade + novel; this is the population the REx tree is built to win.

## Honest caveats
- Small rep counts (3-5) and correlated conditions -> "unsolvable" is an operational
  triage label, not a statistical impossibility claim; n+passes disclosed per cell, no
  per-incident CIs asserted. Single threshold (0.8); threshold sweep is future work.

Status: completed — real plan + spec + runnable tool + passing tests + real outputs.
