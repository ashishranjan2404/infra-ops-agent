# G4 — SUMMARY

**Task:** Compare our trap-action labels vs SREGym's; ground our trap-action concept in
`rex/scoring.py` + scenario YAMLs; research whether SREGym (and neighbors) has trap/unsafe-
action labeling; write a comparison report highlighting our novelty.

## Result: COMPLETED
A grounded, cited comparison plus a re-runnable data artifact extracted from the live repo.

## Grounding (real)
- Trap mechanics: `rex/scoring.py` — `_traps_in` (:175-182), `TRAP_PENALTY=0.60`
  (:22, :206-209), per-trap `why` feedback (:243-252), trap-vs-BLOCKED distinction (:254-257).
  Schema: `Scenario.trap_actions` (`rex/harness.py:229`, built :307-308).
- Data: 51/51 generated scenarios carry a trap; tool distribution
  `scale_deployment x48, restart_pod/rollback_deployment/restart_service x1` each.

## Research finding
SREGym (arXiv 2605.07161), AIOpsLab (2502.05352), and ITBench all use end-state "resolved?"
oracles (ITBench + SREGym add anti-reward-hack guards against alert suppression). None
maintains a per-incident set of plausible-but-causally-wrong actions carrying a reward
penalty. Safe-RL (Safety-Gym) penalizes unsafe actions but as unconditional state hazards,
not mechanism-conditional remediation errors.

## Scoped novelty
A per-incident, mechanism-conditional trap-action labeling scheme with a graded reward
penalty (trap strictly worse than abstaining) and per-trap natural-language `why` feedback —
absent from contemporary SRE-agent benchmarks; distinct from Safe-RL constraint costs by its
mechanism conditioning.

## Honest caveats
Tool monoculture (48/51 = scale_deployment) -> "labeling scheme + seed taxonomy," not a rich
taxonomy. Competitor side is paper/doc-grounded (SREGym source not audited); claim is dated.
No behavior-change ablation (out of scope).

## Artifacts
- artifacts/extract_trap_taxonomy.py — read-only extractor (AST + YAML), runnable
- artifacts/trap_taxonomy.json — 51-record taxonomy generated from real data
- artifacts/test_extract_trap_taxonomy.py — 6 pytest cases, all pass
- artifacts/comparison_report.md — the deliverable comparison
- 01..10 step files

No shared core files were edited.
