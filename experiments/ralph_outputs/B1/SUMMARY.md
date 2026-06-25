# B1 — SUMMARY

**Task:** Run pass@k on the full grid — 42 incidents × 5 conditions × 5 seeds = 1050
episodes — grounded in `rex/eval_pass_at_k.py`. Compute cap: ~15 min per model run.

## Outcome: completed (full grid script shipped + real subset anchor + documented cap blocker)
The full grid is ~1050 episodes ≈ ~50 min, over the 15-min cap. Per the brief's COMPUTE CAP
rule I delivered the **full runnable grid script** and ran a **representative subset** as a
real anchor — no fabricated episodes.

## What ran for real (glm-5p2, deterministic P0 judge, HUD gateway)
Subset = 6 incidents (2 per family) × **5 conditions × 5 seeds = 150 episodes**, 0 errors,
430 s, `floor_ok` (empty=0.0, trap=0.0 < 0.8).

| condition | pass@1 | 95% CI | mean | std |
|---|---|---|---|---|
| zero_shot | 0.333 | [0.19,0.51] | 0.52 | 0.42 |
| best_of_n | 0.400 | [0.25,0.58] | 0.69 | 0.32 |
| retry_realistic | 0.433 | [0.27,0.61] | 0.78 | 0.25 |
| **rex** | **0.967** | **[0.83,0.99]** | 0.98 | 0.08 |
| rex_no_oracle | 0.333 | [0.19,0.51] | 0.69 | 0.29 |

**Thesis: rex 0.967 [0.83,0.99] vs zero_shot 0.333 [0.19,0.51] — Wilson CIs DISJOINT.**
Consistent with A1's independent full-42×3-seed run (rex 0.897 vs zero_shot 0.230, disjoint).

## Full grid (off-cap, resumable)
```
python3 experiments/ralph_outputs/B1/artifacts/run_full_grid.py --model glm-5p2 --seeds 5
# -> grid_full_glm-5p2.json (42×5×5=1050 eps); .partial checkpoint resumes after a cap kill
```

## Artifacts (all under B1/artifacts/, no shared core edited)
- `run_full_grid.py` — full grid + subset runner (wraps `rex.eval_pass_at_k.run_eval`).
- `grid_sub2_glm-5p2.json` — real 150-episode subset result.
- `summarize_grid.py` + `summary_table.json` — table + disjoint-CI thesis line.
- `run_sub.log` — real run log.

## Blocker
Full 1050-episode grid (~50 min) exceeds the ~15-min model-run cap. Shipped: full runnable
grid script + resumable checkpoint + 150-episode real subset anchor + A1 full-42 reference.

## Honest caveats
rex is near-saturated (std 0.08 → little trainable spread; this measures its ceiling).
No per-family claims from the thin subset (n≈10/family). Hardest multi-fault cascades only
covered by the full-grid script. pass@5-from-5-seeds is optimistic; headline is pass@1±CI.
