# 01 — Plan (Task G4: Trap-action labels — ours vs SREGym)

## Objective
Ground our "trap-action" concept in the actual code (`rex/scoring.py`) and the scenario
YAMLs, then research whether SREGym (and the adjacent SRE-agent benchmarks AIOpsLab /
ITBench) have any comparable notion of trap / unsafe / counterproductive action labeling
and reward penalty. Produce a comparison report that honestly states where the line is
and what is genuinely novel here: a **per-scenario trap-action taxonomy with a graded
reward penalty and per-trap natural-language feedback**.

## Approach
1. Read `rex/scoring.py` — extract the exact trap mechanics: `_traps_in`, `TRAP_PENALTY`,
   the per-trap `why` feedback table, the BLOCKED-action channel.
2. Read the scenario schema (`rex/harness.py` `Scenario`, `ScenarioSpec.trap_actions`) and
   survey all `scenarios/cidg/generated/*.yaml` — count traps, tool distribution, targeting.
3. Web research SREGym (arXiv 2605.07161), ITBench, AIOpsLab — find how each scores
   mitigation and whether any penalize harmful / trap actions.
4. Write a structured comparison + a machine-readable taxonomy artifact extracted from OUR
   real YAMLs (so the "novelty" claim is backed by data, not assertion).

## Files to create (all task-namespaced — NO core edits)
- `artifacts/extract_trap_taxonomy.py` — reads the real YAMLs + scoring.py constants,
  emits the taxonomy JSON. Runnable, self-contained.
- `artifacts/trap_taxonomy.json` — generated taxonomy (per-scenario trap, tool, target,
  the gold fix it is contrasted against, the failure-class).
- `artifacts/comparison_report.md` — the deliverable comparison.
- `artifacts/test_extract_trap_taxonomy.py` — pytest validating the extractor against the
  real repo (counts, schema, that every trap names a tool).

## Dependencies
PyYAML (already in repo), the 51 generated YAMLs, `rex/scoring.py` constants. No network at
test time; research is captured as prose + citations in the report.

## Risks
- SREGym is a very recent (2026) live benchmark; their repo may evolve. Mitigation: cite the
  arXiv paper version + GitHub and date the claim; frame novelty as "as of the published
  oracle design," not "forever."
- Over-claiming novelty. ITBench DOES guard against reward-hacking (alert suppression). I
  must distinguish "reward-hacking guard" (don't credit fake fixes) from our "trap penalty"
  (actively subtract reward for a *plausible-but-wrong* action). They are different.

## Success criteria
- Trap mechanics grounded with exact file:line + constants.
- Taxonomy artifact generated from real data and validated by a passing pytest.
- Comparison report distinguishes our penalty from SREGym/ITBench oracles with citations.
- Honest statement of what is NOT novel.
