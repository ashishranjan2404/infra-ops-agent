# D1 — 08 Verification

## Success criteria (from 01) vs outcome
| Criterion | Status | Evidence |
|-----------|--------|----------|
| Runnable, syntax-valid 50-step launcher reusing the unmodified v2 trainer | MET | `run_rft_50.sh`, `bash -n` PASS; `exec`s `train_rft_v2.py --steps 50` |
| Analyzer quantifies trend + projects to 50-step horizon | MET | `analyze_curve.py`, 4/4 unit tests PASS |
| Live-backend smoke (rollout→reward→fwd/bwd) | MET | smoke "SMOKE OK", job id logged |
| Real (possibly partial) 50-step curve OR documented blocker | MET (both) | 9 real steps in `train_d1_50step.jsonl` + compute blocker in 07/09 |
| No edits to shared core files | MET | only new files under `D1/artifacts/`; `git status` shows no core diffs from D1 |

## Are outputs real, not placeholder?
- `train_d1_50step.jsonl` — **real**: 9 steps, n=60 rollouts each, distinct
  mean/std per step, produced by the live Tinker backend (not synthesized).
- `run_rft_50.sh`, `analyze_curve.py` — **real & runnable**: syntax-checked,
  unit-tested, executed against actual data.
- Smoke output — **real**: includes a live `hud.ai/jobs/<id>` URL.

## Does it answer the task question?
Task D1 = "run 50+ steps to see if the +0.037 trend continues." Answer delivered:
the trend is **reproducible in sign but `flat`/within-noise** (slope +0.0012/step,
projects to ~0.57 at step 50). The full 50-step completion is compute-blocked and
left as an unattended-run launcher — no fabricated steps. This is a completed
deliverable with an honest, partly-negative scientific result.

## Parallel-safety check
All artifacts are under `experiments/ralph_outputs/D1/`. No write to `rex/*`,
`sim/*`, `agent/*`, `experiments/*.py`, `ralph_status.json`, `train_rft_v2.py`,
`hud_env_v2.py`, or any other task's directory. The training run only *appended* to
a D1-namespaced JSONL.
