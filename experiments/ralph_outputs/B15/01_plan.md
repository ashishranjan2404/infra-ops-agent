# B15 — 01 Plan

## Objective
Compare our measured **pass@1** (from the A1 full-42 run and the A2 ablation) directly
against **SREGym's** reported leaderboard numbers, and deliver an honest comparison that is
explicit about the fact that the two benchmarks are **not equivalent** — different substrate
(real K8s vs. a state-machine simulator), different success definition (multi-axis SLO+root
reward >= 0.8 vs. diagnosis/mitigation/E2E oracle), different task counts, different models.

## Why this is hard (and why caveats dominate)
A naive "our pass@1 = 0.90 beats SREGym's 0.61 E2E" headline would be **misleading**. Our
strong number is REx (a multi-attempt tree search with oracle feedback) on a *simulator*; the
SREGym numbers are single-shot agent loops on *live containerized faults*. The deliverable's
real value is the comparison table **plus** a rigorous caveat section that names every axis of
non-equivalence so a reviewer can't accuse us of cherry-picking.

## Approach
1. Pull SREGym's reported numbers from the paper (arXiv 2605.07161) and the public leaderboard
   (sregym.com/leaderboard). Record diagnosis / mitigation / E2E success per agent-model pair,
   the 90-problem partition (Ported 34 / Similar 43 / New 13), and their "3 runs per problem,
   single attempt per run" = pass@1 methodology.
2. Pull our pass@1 from existing A1/A2 artifacts (do NOT re-run anything):
   - A1: `full_pass_at_k_glm-5p2.json` — full 42 incidents, 3 seeds, 5 conditions, glm-5p2.
   - A2: `ablation_pass_at_k_deepseek-v4-pro.json` — 30 incidents, 5 seeds, deepseek-v4-pro.
3. Map our families (simple/cascade/novel) onto SREGym's partitions (Ported/Similar/New) as a
   *loose analogy only*, flagged as such — novel<->New is the most defensible mapping.
4. Build a small, dependency-light Python script that ingests both data sources (our JSON +
   a checked-in `sregym_reported.json` of cited numbers) and emits a Markdown comparison table.
5. Write the report (`comparison_report.md`) with the table, the family<->partition mapping,
   and a numbered caveats list.

## Files to create (all task-namespaced)
- `artifacts/sregym_reported.json` — SREGym numbers with per-row source citations.
- `artifacts/our_pass_at_1.json` — distilled pass@1 from A1/A2 (generated, not hand-typed).
- `artifacts/gen_comparison.py` — reads both, writes the table + report. Pure stdlib.
- `artifacts/comparison_report.md` — the rendered report (the primary deliverable).
- `artifacts/comparison_table.md` — the standalone table (script output).

## Dependencies
- Python 3.13 stdlib only (json, argparse, pathlib). No network at run time (SREGym numbers are
  frozen into a checked-in JSON with citations; web research done once, here).
- Read-only consumption of A1/A2 artifacts. No edits to shared core files.

## Risks
- **Apples-to-oranges**: the central risk. Mitigated by a dedicated caveats section + clearly
  labeling our headline number as REx-with-oracle, and also reporting our *zero_shot* pass@1
  (0.23) which is the more honest single-shot comparator to SREGym's single-shot agents.
- **SREGym has no "pass@1" column literally** — they report success *rates* over 3 runs, single
  attempt each. That IS pass@1 semantics; I document the equivalence rather than inventing a number.
- **Model mismatch**: SREGym uses Sonnet-4.6 / GPT-5.4 / Kimi; we use glm-5p2 / deepseek-v4-pro.
  Flagged; not correctable without re-running (out of scope, would cost API + a live cluster).

## Success criteria
- Comparison table renders from the script (no hand-edits) and pulls our numbers from real A1/A2 JSON.
- Every SREGym number has a cited source.
- Caveats section enumerates >= 6 concrete non-equivalence axes.
- Script parse-checks and runs clean on Python 3.13; output committed.
