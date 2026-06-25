# D14 — 08 Verification

## Success criteria vs evidence

| Criterion | Met? | Evidence |
|---|---|---|
| Assembled task file uses all 42 incidents | YES | `tasks_42.json` count=42 (34 canonical + 8 variants); all 19 reals + 15 synthetic classes present |
| 42 unique scenario_ids, all real corpus keys | YES | assemble asserts uniqueness + membership; dry-run `missing=[]` against 319-record corpus |
| Runnable RFT config using the 42 as the task set | YES | `train_rft_42.yaml` (`tasks: all`) + launcher; live smoke produced a reward + step |
| Dataset-assembly script delivered | YES | `assemble_tasks.py`, deterministic, self-validating, re-runnable |
| Curriculum is real (not cosmetic) | YES | difficulty 3/4/5 = 9/15/18; dry-run shows easy ids first, hard reals last |
| No shared core file edited | YES | only additive imports of `hud_env_v2`/`hud_env`; stock `train_rft_v2.py` untouched |
| Compute cap ~15 min honored / blocker documented | YES | smoke proven; full 42×6×30 run is the compute-capped step; backend prereq documented |

## Are the outputs real (not placeholder)?
- `tasks_42.json` — generated from the actual 319-record corpus; every id verified present.
- `smoke_run.jsonl` — a real reward log from a live HUD Tinker rollout (mean 0.6586,
  spread 0.0562), not a hand-written number.
- The deterministic reward is the project's own `rex.scoring.mechanism_score` via
  `hud_env_v2._grade_v2` — no fabricated grading.

## The "10 -> 42" claim, verified
- Stock `train_rft_v2.py` default `--tasks 0,1,...,9` = **10** index-selected canonical tasks.
- D14 `tasks: all` = **42** explicit-id tasks, and crucially **8 are variants unreachable
  by the index path** — proven by the live smoke instantiating `001-oom_kill-s019` etc.
  So D14 genuinely expands the trainable surface beyond what the index-based runner can express.

## Residual (honest)
- A *complete* 42-task × group 6 × 30-step training run was not executed to convergence:
  it exceeds the ~15-min compute cap and, on the re-run, the shared trainable head was
  held by another concurrent worker (transient 409). The deliverable — config + assembled
  task file + runnable launcher + proven smoke — is complete; the long run is the
  documented compute-capped follow-on.
