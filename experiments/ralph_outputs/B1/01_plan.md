# B1 — 01 Plan

## Objective
Run **pass@k on the full grid**: all **42 incidents × 5 conditions × 5 seeds = 1050**
model-driven episodes, graded by the P0 deterministic judge, reporting pass@1/2/5 with
Wilson 95% CIs overall and per family (simple/cascade/novel), plus reward spread (std)
and a floor check. Ground the implementation in `rex/eval_pass_at_k.py`.

## Conditions (the 5)
`zero_shot`, `best_of_n`, `retry_realistic`, `rex`, `rex_no_oracle` — exactly the
`CONDITIONS` dict in `rex/eval_pass_at_k.py`. The thesis comparison is `rex` vs
`zero_shot`; the other three are realistic baselines (parallel best-of-N, sequential
retry-with-realistic-feedback, REx without the oracle feedback).

## Approach
- Reuse the existing `run_eval` / `print_report` / `floor_check` pipeline — do NOT
  re-implement the estimator. The unbiased pass@k + Wilson CI live in
  `experiments/compute_pass_at_k.py` (single source of truth).
- Wrap it in a **task-namespaced** runner `artifacts/run_full_grid.py` (4-levels-up REPO
  path, writes only into `B1/artifacts/`). Add a `--per-family` knob so the SAME script
  is both the full grid (`--per-family 0`) and a representative capped subset.
- `--seeds 5` and all 5 conditions are fixed to match "the full grid."
- Crash-survival `.partial` checkpoint (already in `run_eval`) → resumable across capped
  windows toward the full 1050.

## Files to create (task-namespaced; no shared edits)
- `artifacts/run_full_grid.py` — the full + subset runner.
- `artifacts/grid_sub2_glm-5p2.json` — REAL subset result (6 incidents × 5 × 5 = 150 eps).
- `artifacts/run_sub.log` — real run log.
- `artifacts/summarize_grid.py` + `artifacts/summary_table.json` — table from the JSON.
- 01..10 + SUMMARY.md + result.json.

## Dependencies
`agent.llm.call` (glm-5p2 via HUD_API_KEY gateway), `rex.harness`, `rex.tree`,
`rex.scoring` (deterministic judge), `rex.ablation`, `experiments/compute_pass_at_k.py`,
~33–42 scenarios in `scenarios/cidg/generated/`.

## Risks
- **COMPUTE CAP (primary risk).** A1 measured ~2.5 s/episode → 630 eps in ~27 min.
  The full grid is 1050 eps ≈ **~45 min**, over the ~15-min model-run cap. Mitigation:
  run a representative subset (2 incidents/family, full 5 conditions × 5 seeds = 150 eps)
  as the real anchor and ship the full runnable grid script + checkpoint + documented
  blocker. Do NOT fabricate the missing 900 episodes.
- Transient gateway HTTP errors → handled by the in-pipeline retry + per-job try/except.
- pass@5 with 5 seeds is borderline-optimistic (Chen estimator); headline stays pass@1±CI.

## Success criteria
1. `run_full_grid.py` compiles, runs, asserts the floor invariant.
2. A REAL subset run (5 conditions × 5 seeds, all 42 incidents covered family-wise)
   completes with 0/low errors and `floor_ok`.
3. `rex.pass@1 > zero_shot.pass@1` with the thesis direction (ideally disjoint CIs),
   consistent with A1's full-42×3-seed anchor.
4. Full-grid command documented + runnable; blocker (cap) honestly recorded.
