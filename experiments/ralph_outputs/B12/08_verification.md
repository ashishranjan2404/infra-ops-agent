# 08 — Verification against success criteria

| Criterion (from 01/03) | Status | Evidence |
|---|---|---|
| Ingest available pass@k result JSONs (A1/A2) | ✅ | Loaded both, 0 errors (07 §3) |
| Per-incident table: incident → pass@1/pass@k per condition | ✅ | `out/per_incident_breakdown.md`, 72 rows, 5 conditions × {p@1,p@k} |
| Flag unsolvable incidents | ✅ | `solvability` field + dedicated unsolvable list (7 rows; 3 cross-model) |
| Tool runs on real data, 0 errors | ✅ | `[done] 72 rows` (07 §3) |
| Unit tests pass | ✅ | 7/7 (07 §2) |
| Operational (not statistical) unsolvable wording | ✅ | md header + docstring state "no condition passes a single sample" |
| Dual machine+human output | ✅ | `.json` (full per-condition) + `.md` (table + lists) |
| One row per (model, incident); reps not pooled | ✅ | 42 (A1) + 30 (A2) = 72 rows; n taken per source |
| No shared-core edits | ✅ | only `B12/**` written; `compute_pass_at_k` imported read-only |

## Outputs are real, not placeholder
- Numbers are derived from the actual A1/A2 `per_incident_rewards` arrays, not hand-typed.
- Re-running the command regenerates identical outputs (deterministic over fixed inputs).
- The unsolvable set is corroborated across two independent models, which is exactly the
  kind of cross-check a placeholder would not survive.

## Independent sanity check
- `azure_ddos`, `cloudflare_waf`, `crowdstrike_bsod` show all-zero pass@1 in every
  condition for BOTH models in the source JSONs — consistent with the flag.
- simple-family incidents are mostly solvable (20/22), matching the family-level pass@1
  reported by A1/A2; the per-incident view refines, not contradicts, the aggregate.

Verdict: meets all success criteria with real, reproducible outputs.
