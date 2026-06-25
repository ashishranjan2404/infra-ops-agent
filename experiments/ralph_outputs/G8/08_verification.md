# 08 — Verification

## Against the success criteria (from 01_plan.md)

1. **One page, scannable (wedge / moat / proof / honest-caveat / ask).** ✅ 657 words, all five
   sections present (T2). Scannable: short declarative lines, bolded leads, one reward formula.

2. **Every numeric claim traceable to a real repo file.** ✅ `proof_points.json` enumerates 12
   claims (C1–C12), each with a source path; T3/T4 confirm the two counts (19, 51) empirically;
   T5/T6 confirm the cited files and run logs exist.

3. **Honest: includes the ablation caveat.** ✅ The "What we do NOT claim" block states plainly
   that REx's raw lift was largely oracle-feedback leakage (0.25 ≈ 0.24) and that the defensible
   contributions are the environment and the searched verifier. Also declines to claim
   uncontaminated substrate.

4. **`proof_points.json` valid JSON; one-pager valid Markdown.** ✅ T1 passes; Markdown renders
   (headers, table-free prose, fenced code block balanced).

## Are the outputs real (not placeholder)?
Yes. The one-pager is finished investor/partner copy, not a stub. Numbers are read from
`ARCHITECTURE.md` and `docs/headline_insights.md`, not invented — and the two scale numbers were
counted from the filesystem live. The honest-caveat block is the strongest evidence the doc is
real synthesis: a placeholder would not surface its own ablation.

## Shared-core safety verification
All artifacts under `experiments/ralph_outputs/G8/`. No edits to `rex/`, `sim/`, `agent/`,
`experiments/*.py`, `ralph_status.json`, or any other task directory.

**Verdict: meets all success criteria.** Deliverable is real, cited, and honest.
