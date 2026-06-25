# 01 — Plan (B12: per-incident pass@k breakdown)

## Objective
Turn aggregate pass@k results (currently reported per *family*: simple/cascade/novel)
into a **per-incident** view: for every incident id, show pass@1 / pass@k under each
condition, and flag which incidents are **solvable**, **partially solvable**, or
**unsolvable**. This exposes *which specific incidents* the curriculum can/can't solve —
the diagnostic the family-level numbers hide.

## Inputs (real, already on disk)
- `A1/artifacts/full_pass_at_k_glm-5p2.json` — 42 incidents (12 simple / 20 cascade / 10 novel), 3 reps, 5 conditions, model glm-5p2.
- `A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` — 30 incidents (10/10/10), 5 reps, 5 conditions, model deepseek-v4-pro.

Both share the `rex.eval_pass_at_k` schema. The key field is
`by_condition[<cond>].per_incident_rewards[<incident>] = [reward, reward, ...]`
plus top-level `incidents_by_family` and `threshold` (0.8). This is exactly the
raw material needed — no re-running of episodes required.

## Approach
1. Ingest one or more pass@k JSONs (schema-validated).
2. Build incident -> family map from `incidents_by_family`.
3. For each (source model, incident, condition): binarize rewards at `threshold`,
   compute pass@1 (= passes/n) and pass@k (unbiased Chen et al. estimator, reused
   from `experiments/compute_pass_at_k.py`).
4. Assign a solvability flag from the BEST pass@1 across conditions:
   - `solvable`   : best pass@1 == 1.0 (some policy reliably solves it)
   - `partially`  : 0 < best pass@1 < 1.0
   - `unsolvable` : best pass@1 == 0 (no condition passes even one sample)
5. Emit JSON (machine) + Markdown table (human) + a summary with the unsolvable list
   and a by-family breakdown.

## Files to create (all task-namespaced, NO shared-core edits)
- `B12/artifacts/per_incident_breakdown.py` — the tool (CLI).
- `B12/artifacts/test_per_incident_breakdown.py` — unit tests (no pytest dep).
- `B12/artifacts/out/per_incident_breakdown.{json,md}` — real outputs over A1+A2.

## Dependencies
Python 3.13 stdlib only; optional import of `experiments/compute_pass_at_k.py`
(single source of truth for the estimator) with a self-contained fallback.

## Risks
- Source JSONs might lack `per_incident_rewards` → schema validate + skip gracefully.
- Different reps (n=3 vs n=5) across sources → keep per-source, never pool reps across models.
- pass@k with k>n → clamp k to n.

## Success criteria
- Tool runs on the real A1 + A2 JSONs, 0 errors.
- Per-incident table with pass@1/pass@k per condition for all 72 (incident×model) rows.
- Explicit unsolvable-incident flag list.
- Unit tests pass.
