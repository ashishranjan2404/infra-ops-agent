# B1 — 08 Verification

## Success criteria (from 01_plan, post-grill)
1. **`run_full_grid.py` compiles, runs, asserts the floor invariant** — MET. py_compile OK;
   the run exited 0 with `assert floor_ok` (floor_ok=true).
2. **REAL subset run, all 5 conditions × 5 seeds, all families covered, low errors** — MET.
   150 episodes, 0 errors, 430 s; simple/cascade/novel each represented.
3. **rex.pass@1 > zero_shot.pass@1, thesis direction, ideally disjoint CIs** — MET. rex
   0.967 [0.83,0.99] vs zero_shot 0.333 [0.19,0.51]; CIs DISJOINT. Matches A1's full-42 anchor.
4. **Full-grid command runnable + cap blocker honestly recorded** — MET. `run_full_grid.py
   --per-family 0 --seeds 5` produces the full 1050-episode JSON (resumable); blocker
   (~50 min > 15-min cap) documented in 07/09. The 900 unrun episodes are not fabricated.

## Outputs are REAL, not placeholder
- `grid_sub2_glm-5p2.json` — real model episodes graded by the deterministic judge
  (0 errors, 430 s wall logged); reward arrays per incident present.
- `summary_table.json` — derived from the real JSON by `summarize_grid.py` (re-runnable).
- `run_sub.log` — real progress lines (50/100/150 @ 128/257/430 s) + final report.
- `run_full_grid.py`, `summarize_grid.py` — compile + run; no shared core file touched
  (only `experiments/ralph_outputs/B1/artifacts/` written).

## Parallel-safety verification
All writes are under `B1/artifacts/`. The runner imports `rex.eval_pass_at_k` /
`compute_pass_at_k` read-only; nothing in `rex/`, `sim/`, `agent/`, `experiments/*.py`,
`ralph_status.json`, or another task's dir was modified.

## Cross-check vs A1
Direction and magnitude agree with A1's independent full-42×3-seed run (rex ≫ zero_shot,
disjoint CIs, floor_ok). The subset is a faithful, smaller window onto the same grid.
