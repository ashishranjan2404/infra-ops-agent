# B2 — Step 1: Plan

## Objective
The SRE-Degrees paper *claims* McNemar's paired significance test for comparing
conditions but never ran the full pairwise matrix. Deliver a real, standalone
`mcnemar.py` that ingests per-episode pass/fail from any pass@k result JSON and
emits a McNemar 2x2 table + exact p-value for **every** condition pair (not just
REx-vs-control), then run it on the real cached results and report real p-values.

## Approach
1. Reuse the existing pass@k result schema (`by_condition[c].per_incident_rewards`
   = per-(incident,seed) reward lists, plus `threshold`, `seeds`,
   `incidents_by_family`). Each (incident, seed) pair is a **paired** episode shared
   across all conditions — exactly what McNemar needs.
2. Threshold reward -> binary pass; flatten to an aligned bit vector per condition
   (incident-major, seed order preserved -> identical alignment across conditions).
3. For every unordered pair of conditions (C(k,2) = 10 for k=5), compute the 2x2
   table (both-pass, both-fail, b01=A>B, b10=B>A), the exact two-sided binomial
   p-value on the discordant cells, and the continuity-corrected chi-square.
4. Do this overall and per family (simple / cascade / novel).
5. Apply **Holm-Bonferroni** correction across the family of pairwise tests — the
   paper claims significance but never corrected for multiple comparisons.
6. Run on A1 (glm-5p2, 42 incidents, 3 seeds) and A2 (deepseek-v4-pro, 30 incidents,
   5 seeds) cached pass@k JSONs; cross-check against A2's own rex-vs-control mcnemar.

## Files to create (all task-namespaced under B2/)
- `artifacts/mcnemar.py` — the standalone tool (stdlib only, no scipy).
- `artifacts/test_mcnemar.py` — unit tests (stdlib unittest).
- `artifacts/mcnemar_pairwise_report.json` — real output on A1+A2.

## Files to modify
- None. Do NOT edit `rex/*.py` (A2's `run_ablation_v2.py` already has an embedded,
  narrower mcnemar; B2 is a complementary standalone full-matrix tool).

## Dependencies
- Python 3 stdlib only (`math.comb` for exact binomial). No scipy/statsmodels —
  keeps it runnable in this env and matches A2's dependency-free choice.

## Risks
- Reward-threshold mismatch: must use each file's own `threshold` (0.8) so binary
  pass/fail matches the pass@k definition. Mitigated by reading it from the file.
- Alignment bug: if condition vectors are not in identical (incident,seed) order
  the pairing is wrong. Mitigated by iterating one canonical incident list + seed
  index and unit-testing alignment.
- Multiple-comparison inflation: 10 pairs x 4 families x 2 models = many tests.
  Mitigated by Holm correction + reporting raw and corrected flags separately.

## Success criteria
- `mcnemar.py` parses real A1/A2 JSONs and emits a complete 10-pair table per family.
- Unit tests pass (binary thresholding, exact binomial vs hand calc, Holm, alignment).
- rex-vs-control discordant counts reproduce A2's existing mcnemar artifact exactly.
- Real p-values reported, with honest discussion of where significance survives Holm.
