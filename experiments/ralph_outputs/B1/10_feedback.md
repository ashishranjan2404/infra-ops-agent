# B1 — 10 Feedback for the next task

The binding constraint on any pass@k task is the ~15-min model-run cap, not the code: at
~2.8–2.9 s/episode on glm-5p2, you get ~300 episodes per capped window. Budget BACKWARD from
that — pick `incidents × conditions × seeds ≤ ~300` and prefer COVERAGE (hit every family,
keep all conditions) over seed depth, because the thesis result (rex ≫ zero_shot) is already
disjoint at low n and extra seeds just reconfirm a saturated rex (mean ~0.98, std ~0.08).
Always ship the FULL runnable grid as a `--per-family 0` script with the in-pipeline
`.partial` checkpoint so the full run is resumable off-cap, and reference A1's full-42×3-seed
JSON instead of trying to re-run it. Reuse `rex.eval_pass_at_k.run_eval` /
`compute_pass_at_k` verbatim — never re-implement the estimator. Headline pass@1 ± Wilson CI
only; flag pass@5-from-few-seeds as optimistic; never claim per-family results off a thin
subset (n≈10/family). And keep every write under `<TASK_ID>/artifacts/` — the read-only
import of core modules is the safe pattern under parallel workers.
