# B1 — 06 Implementation

## What I built (all task-namespaced; NO shared core files edited)
1. **`artifacts/run_full_grid.py`** — the literal full grid runner. Thin wrapper around
   `rex.eval_pass_at_k.run_eval` (imported, unmodified). `--per-family 0` = all 42 incidents
   = the full 42×5×5=1050-episode grid; `--per-family N` = a representative capped subset
   with the SAME 5 conditions × 5 seeds. Resumable `.partial` checkpoint; asserts the floor
   invariant; tags output `grid_full_*` vs `grid_subN_*` and records `grid.full_grid`.
2. **`artifacts/summarize_grid.py`** — reads a result JSON, prints the overall table + a
   thesis line (rex vs zero_shot, disjoint-CI check), writes `summary_table.json`.
3. **`artifacts/grid_sub2_glm-5p2.json`** — REAL subset result: 6 incidents (2/family) ×
   5 conditions × 5 seeds = 150 episodes on glm-5p2, deterministic judge, 0 errors, 430s.
4. **`artifacts/summary_table.json`** — compact table derived from (3).
5. **`artifacts/run_sub.log`** — real run log (progress + final report).

## The full grid (1050 episodes) — runnable command (off-cap)
```
set -a; source ~/.zshrc; set +a
python3 experiments/ralph_outputs/B1/artifacts/run_full_grid.py --model glm-5p2 --seeds 5
# -> artifacts/grid_full_glm-5p2.json   (42 incidents x 5 conditions x 5 seeds)
# resumable: re-run the same command after a cap kill; the .partial checkpoint skips done episodes
```

## What actually ran under the cap
The 150-episode subset (`--per-family 2 --seeds 5`), which fits the ~15-min cap (~7 min
wall). It exercises the entire pipeline end-to-end (all 5 conditions, full 5-seed depth,
all three families represented, deterministic judge, floor check) and reproduces the
thesis direction. The remaining 900 episodes of the full grid are deferred to the off-cap
command above + A1's full-42×5-condition×3-seed reference JSON.

## Grounding
Built directly on `rex/eval_pass_at_k.py` (`run_eval`, `print_report`, `floor_check`,
`summarize`) and `experiments/compute_pass_at_k.py` (`pass_at_k`, `wilson_ci`,
`binary_pass`) — the single source of truth for the estimator. No core file modified.
