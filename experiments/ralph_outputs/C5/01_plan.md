# C5 — 01 Plan

## Objective
Compare the **synthesized** safety rules (the searched data rule-set produced by
`rex/harness_synth.py`, saved in `rex/runs/harness_synth.json`) against the
**hand-written** rules (`rex/harness.py:is_safe`), line-by-line / clause-by-clause,
and produce a concrete gap analysis: *what does the synthesized harness miss that the
human baseline catches (and vice-versa)?*

## Inputs (read-only; shared core — do NOT edit)
- `rex/harness.py` — hand-written `is_safe()` (the human baseline). 4 enforcement clauses:
  L1 category-block, L2a leak-restart, L2b last-ready-node, L2c replica-limit, L2d rollback-no-deploy.
- `rex/harness_synth.py` — feature extraction, `ground_truth()`, the rule interpreter
  `is_safe_synth()`, and `handwritten_pred()`.
- `rex/runs/harness_synth.json` — the *synthesized* rule-set (10 data rules) + the train/heldout
  accuracy table already computed by a real synthesis run.

## Approach
1. Enumerate the 5 distinct **clauses** of the hand-written `is_safe` (with line refs) — these are
   the "lines" we diff against.
2. Run BOTH harnesses (`handwritten_pred`, `is_safe_synth` over the saved rule-set) on the SAME
   labeled examples for all 10 incidents (train + held-out), using the existing ground-truth labels.
3. Diff per-example: agreement, hand-only-blocks (synth gaps = false-allows), synth-overblocks.
4. Map each hand-written clause -> the synthesized rule(s) that cover it (by shared feature). Report
   which clauses are NOT represented at all.
5. Hazard-coverage gap: per hazard, which incidents each harness blocks vs the ground truth.

## Files to create
- `artifacts/gap_analysis.py` — runnable analysis (imports core, never edits it).
- `artifacts/gap_report.json` — machine-readable diff (generated).
- `04_spec.md`, the rest of the 10 step files, `SUMMARY.md`, `result.json`.

## Dependencies / risks
- Depends on `rex/runs/harness_synth.json` existing (it does — real prior run, budget 8, haiku).
- Risk: `trap_action` hazard is labeled by the SPEC but neither harness has a generic trap clause —
  must report it as a *shared* limitation, not a synth-specific gap, to avoid an unfair comparison.
- No live API / GPU needed; pure deterministic comparison over saved artifacts.

## Success criteria
- Real per-example diff over all 10 incidents runs deterministically.
- Identifies the specific clause(s) the synthesized rule-set is missing, with incident-level evidence.
- Distinguishes synth-specific gaps from limitations shared with the hand-written baseline.
