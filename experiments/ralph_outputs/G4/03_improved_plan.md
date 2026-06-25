# 03 — Improved Plan

## What changed after the grill
1. **Scoped the novelty claim** (REV, SMR). The report will NOT say "we invented penalizing
   unsafe actions." It will claim: *a per-incident, mechanism-conditional trap-action
   taxonomy with a graded reward penalty and per-trap NL feedback, for an SRE-agent
   diagnosis benchmark.* Safe-RL constraint costs and ITBench reward-hacking guards are
   cited as related-but-distinct prior art.
2. **Added an honesty finding** (REV): 48/51 traps are `scale_deployment`. The taxonomy is
   currently shallow (one dominant anti-pattern). I will surface this from the data, not
   hide it, and frame it as both an empirical observation (scaling is THE reflex
   anti-pattern) and a limitation.
3. **Document matching semantics** (RLE): the extractor + report will record tool + optional
   target and call out the `target: None` wildcard false-positive risk.
4. **Threshold justification** (DEV): report states 0.60 is a design choice that makes a
   trap strictly worse than abstaining (it exceeds the 0.25 fix + makes net-negative
   contribution), not an optimized value.
5. **Measurable payoff** (SMR): note (without over-claiming a full experiment, which is out
   of scope for a comparison task) that the penalty produces finer within-group spread than
   a binary resolved-oracle and that `why` text is a per-action learning signal.

## Critiques accepted
- Scope the claim (REV). Document matching semantics (RLE). Report tool-monoculture (REV).
- Threshold-as-design-choice framing (DEV).

## Critiques rejected (with reason)
- SMR's push to *demonstrate* behavior change with a live RL run: **rejected for this task.**
  G4 is a comparison/grounding task, not a training run; fabricating a behavior-change
  number would violate the no-fake-results rule. I instead state the mechanism by which the
  penalty creates spread and cite the existing scoring math. A real ablation is a separate
  task.
- REV's implication that monoculture undermines the contribution: **partially rejected.** A
  shallow-but-real taxonomy that no competing benchmark has at all is still a delta; I keep
  the claim but down-weight "taxonomy" to "trap-action labeling scheme + seed taxonomy."

## Deliverables (unchanged shape, sharper content)
- `artifacts/extract_trap_taxonomy.py` (+ test), `artifacts/trap_taxonomy.json`,
  `artifacts/comparison_report.md`.
