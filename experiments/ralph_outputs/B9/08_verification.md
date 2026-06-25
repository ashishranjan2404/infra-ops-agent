# B9 — 08 Verification

## Success criteria (from 01) — all met
| Criterion | Status | Evidence |
|---|---|---|
| Script runs, 10k resamples | ✅ | 07 §2 — table printed, JSON written |
| Deterministic under fixed seed | ✅ | 07 §4 — identical on rerun |
| Bootstrap point estimate == shipped pass@1 | ✅ | 07 §3 — matches `compute_pass_at_k.py` exactly |
| Real intervals for all 5 conditions | ✅ | `bootstrap_ci_results.json` |
| Divergences from Wilson explained | ✅ | 06 findings + 09 |
| Tests pass | ✅ | 07 §1 — 12/12 |
| No shared-core edit | ✅ | only artifacts/ written; imports read-only |

## Are the outputs REAL (not placeholder)?
Yes. Every number derives from `rex/runs/ablation.json` (real per-episode rewards from a
prior REx ablation run, model claude-haiku-4-5) via a 10,000-resample bootstrap with a
fixed RNG. The point estimates are independently reproduced by the shipped
`compute_pass_at_k.py`. Nothing is hand-typed or mocked.

## Comparison to Wilson (the requested deliverable)
- **Agreement on the i.i.d. bootstrap vs Wilson for the informative condition (rex):**
  bootstrap `[0.133, 0.667]` ≈ Wilson `[0.198, 0.643]`. Under the i.i.d. assumption the
  two methods broadly corroborate each other → Wilson is not artificially tight *given*
  i.i.d.
- **Divergence under the cluster bootstrap (rex):** `[0.000, 0.800]` is ~1.8× wider than
  Wilson. This is the substantive robustness finding: once you account for the fact that
  there are only 5 distinct incidents and passes are all-or-nothing within an incident,
  the uncertainty about generalizing to a *new* incident is far larger than the i.i.d.
  Wilson interval suggests.
- **0/n boundary:** for all-fail conditions the bootstrap degenerates to `[0,0]`; Wilson's
  `[0,0.204]` is the more honest interval there. Verified, documented, not hidden.

## Verdict
Deliverable complete and real. The bootstrap functions as intended: it *corroborates*
Wilson under i.i.d. and *exposes* its optimism under clustering, which is exactly what a
robustness check should do.
