# D11 — Verification against success criteria

| Success criterion (from 01_plan) | Status | Evidence |
|---|---|---|
| `seed_variance.py` runs on the 3 real logs, emits valid JSON + md with real numbers | **PASS** | `variance_report.json` (2.6 KB) + `variance_table.md` generated; plateau_std {0.0209, 0.0071, 0.0302}, within-step spread {0.172, 0.183, 0.168}, cross-config std 0.0269 — all from actual `opensre-traj/runs/*.jsonl` |
| `--seed` patch parses as a valid diff & is logically correct | **PASS** | `git apply --check` exit 0 ("applies cleanly"); patch seeds random/numpy + exports PYTHONHASHSEED/HUD_ROLLOUT_SEED and adds the CLI arg |
| `test_seed_variance.py` passes under pytest | **PASS** | 10 passed in 0.52s |
| Blocker documented honestly; no fabricated seed numbers | **PASS** | `seed_variance_status="NOT MEASURED ..."` is a machine-readable top-level field; real report carries NO seed-CI; CI path tested only on synthetic fixtures |
| No shared core files edited | **PASS** | `git status` shows `train_rft_v2.py` still untracked/unmodified; all new files live under `experiments/ralph_outputs/D11/` |

## Outputs are real, not placeholder
- `variance_report.json` / `variance_table.md` are tool-generated from the 3 genuine
  training logs (25/15/14 steps; n=24/40/24 per step) — not hand-written.
- The diff was generated mechanically and verified to apply; not a sketch.
- The pytest output is a real run (10 cases incl. a hand-computed Student-t check).

## Honest gaps (carried to 09)
- The headline "seed variance / CI across seeds" is **NOT MEASURED** — by construction
  (no prior seed control). The deliverable is the harness + the real observable-variance
  numbers + a valid patch to unblock it, plus an honest blocker. This matches the brief's
  "correct scaffold + honest blocker beats fabricated numbers."
- The within-step spread and plateau std ARE real variance measurements, just not the
  *seed* axis. They are the most rigorous variance numbers obtainable from existing data.
