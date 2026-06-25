# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "data-integrity pedant"
Problems found:
- **A1**: `seeds` is the rep count but the actual list length is the source of truth.
  If a future JSON has `seeds != len(rewards)`, trusting `seeds` would corrupt pass@1.
  → Spec mandates n = `len(rewards)`, never the `seeds` field. (Implemented.)
- **A2**: Pooling reps across two models with different n (3 vs 5) into one cell would be
  statistically invalid. → One row per (model, incident); reps never crossed. (Implemented.)
- **A3**: `incidents_by_family` may list an incident that has no rewards in some condition.
  → Universe of incidents taken from the union of per_incident_rewards keys; missing cells
  render as "-". (Implemented.)

## Engineer B — "edge-case hunter"
Problems found:
- **B1**: pass@k with k>n silently wrong. → `_pass_at_k` clamps k to n. (Implemented.)
- **B2**: Empty input list / all files invalid → must not crash. → `main` returns exit 2
  with a clear message. (Implemented.)
- **B3**: Imported upstream estimator may differ from the fallback on degenerate n=0.
  → `build_rows` only iterates incidents that actually have reward lists, so n>=1 always
  reaches the estimator; the n=0 branch is never exercised on real data. Test re-scoped to
  not assume fallback-specific n=0 behavior. (Fixed during test run.)
- **B4**: Markdown column order could be unstable across runs. → cond order derived by
  first-seen across rows, deterministic for a fixed input set. (Implemented.)

## Engineer C — "scope & honesty referee"
Problems found:
- **C1**: Over-engineering risk — Wilson CIs per incident-cell. Cut: with n=3 a per-cell CI
  is [0,1]-wide and misleading; we instead disclose raw n+passes and keep CIs at the
  family level (already in the source). Correct call to NOT add per-cell CIs.
- **C2**: "unsolvable" wording could overclaim. → Header explicitly says "no condition passes
  a single sample"; docstring states it is an operational triage label, not in-principle
  impossibility. (Implemented.)
- **C3**: Under-engineering risk — only one model would make "unsolvable" model-specific noise.
  Ingesting BOTH A1 (glm-5p2) and A2 (deepseek-v4-pro) lets us see *cross-model* unsolvable
  incidents, which is a far stronger signal. (Implemented — and it paid off: 3 incidents are
  unsolvable under BOTH models.)

## Final filtered spec deltas
- n always = len(rewards). One row per (model, incident).
- No per-cell CIs; disclose n+passes instead.
- Operational wording for the flag.
- Ingest multiple sources to surface cross-model unsolvability.
