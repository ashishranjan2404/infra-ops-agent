# 06 — Implementation

## What I built (real artifacts)
- `artifacts/per_incident_breakdown.py` — CLI tool. Ingests one or more pass@k result
  JSONs (A1/A2 `rex.eval_pass_at_k` schema), builds one row per (model, incident) with
  per-condition pass@1 / pass@k / mean_reward, assigns a solvability flag, and writes a
  machine JSON + a human Markdown table (per-incident table, prominent unsolvable list,
  by-family rollup).
- `artifacts/test_per_incident_breakdown.py` — 7 self-contained unit tests (no pytest dep).
- `artifacts/out/per_incident_breakdown.json` — real output over A1 + A2 (72 rows).
- `artifacts/out/per_incident_breakdown.md` — rendered human table over A1 + A2.

## Key implementation points
- pass@k uses the unbiased Chen et al. (2021) estimator, imported from
  `experiments/compute_pass_at_k.py` (the repo's single source of truth) when available,
  with a local fallback so the script is standalone. Imported, not copied.
- n = `len(per_incident_rewards[inc])` always (never the `seeds` field) — defends against
  a desynced metadata field.
- One row per (source model, incident). Reps from different models are never pooled.
- Solvability from best pass@1 across conditions: `==1 solvable`, `(0,1) partially`, `==0 unsolvable`.
- Schema-validated ingest; invalid files are skipped with a stderr note, not fatal.

## Command used (reproducible)
```
python3 per_incident_breakdown.py \
  --inputs ../../A1/artifacts/full_pass_at_k_glm-5p2.json \
           ../../A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json \
  --out-json out/per_incident_breakdown.json \
  --out-md   out/per_incident_breakdown.md
```

## No shared-core edits
Only files under `experiments/ralph_outputs/B12/` were created. `compute_pass_at_k.py`
is imported read-only; no `rex/*.py`, `sim/*.py`, `agent/*.py`, status, or dashboard
files were touched.

## Real results (A1 glm-5p2 + A2 deepseek-v4-pro, 72 incident×model rows)
- solvable = 64, partially = 1, unsolvable = 7.
- By family: cascade 24/0/6, novel 20/0/0, simple 20/1/1 (solvable/partially/unsolvable).
- **Cross-model unsolvable (fail under BOTH models):** `azure_ddos`, `cloudflare_waf`,
  `crowdstrike_bsod` — robust, not single-model noise.
- glm-5p2-only unsolvable: `singleton_node_notready`; glm-5p2 partially: `payments_dep_revoked`.
- **Learnable-but-hard:** 41 rows where zero_shot pass@1 == 0 but rex pass@1 == 1 — the
  incidents that motivate the REx tree (mostly cascade + novel).
