# C5 — 03 Improved Plan

## What changed after the grill

1. **Three views, not one** (accepted SMR + PSRE + DEV). The report now emits:
   - per-example behavioral diff (agree / hand-only-block / synth-only-block),
   - a **false-allow gap list** as the headline number (PSRE/DEV — unsafe-action-through is the
     metric that matters operationally),
   - an explicit **clause → synth-rule mapping** naming the missing safety invariant.
2. **Report false-BLOCKS / over-blocks too** (accepted SMR). Added the `synth_only_blocks` column so
   we don't only count synth's misses but also where it is *more* conservative than the human.
3. **Tag each gap by type** (accepted RLE, with REV's guardrail): each missed hazard is labeled either
   `over-fit` or `unseen-in-train (OOD)`. We do NOT use OOD to dismiss a safety hole — we report
   `last_ready_node` as a genuine missing guardrail AND note it is single-incident/held-out-only
   (so the synthesis design literally couldn't learn it).
4. **Fairness on `trap_action`** (accepted REV). The analysis distinguishes hazards that BOTH harnesses
   miss (trap_action — neither `is_safe` nor the synth rules have a generic trap clause) from
   synth-specific gaps. Charging trap_action only to synth would be a rigged comparison.

## Rejected
- **SMR's "ignore source lines entirely."** Rejected — the clause map is how we name *which* invariant
  is missing (PSRE's point). We keep both behavioral and structural diffs.
- **REV's "the split itself is the bug, rewrite it."** Rejected for THIS task: C5 is a *comparison*
  task over the existing artifact, not a re-synthesis. We surface the split limitation in `09_critique.md`
  rather than changing core files (also forbidden by the brief).

## Final method
Run `artifacts/gap_analysis.py` over all 10 incidents using the saved synth rule-set + the in-repo
`handwritten_pred`. Emit `gap_report.json` + console summary. Interpret in `08`/`09`.
