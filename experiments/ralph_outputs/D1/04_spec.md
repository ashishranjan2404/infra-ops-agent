# D1 — 04 Spec

## Artifact 1: `run_rft_50.sh` (launcher)
Thin wrapper over the **unmodified** `opensre-traj/train_rft_v2.py`.

Env-overridable vars (defaults):
| var | default | meaning |
|-----|---------|---------|
| `MODEL` | `opensre-qwen3-8b-1e439a` | forked trainable Qwen3-8B slug |
| `STEPS` | `50` | training steps (the point of D1) |
| `GROUP` | `6` | GRPO group size (== 15-step run) |
| `LR`    | `1e-5` | learning rate (== 15-step run) |
| `TASKS` | `0,1,2,3,4,5,6,7,8,9` | same 10-task v2 set |
| `OUT`   | `runs/train_qwen3-8b_v2_50step.jsonl` | append-only per-step log |

Contract: `cd`s into `opensre-traj`, sources `~/.zshrc` for `HUD_API_KEY`,
`exec`s `../.venv-hud/bin/python train_rft_v2.py` with the above. Output JSONL
schema is whatever `train_rft_v2.py` already emits:
`{"step":int,"mean_reward":float,"reward_std":float,"n":int,"rewards":[float],"loss":null}`.

## Artifact 2: `analyze_curve.py` (analyzer, pure stdlib)
```
analyze(path: str, horizon: int, flat_eps: float=0.005) -> dict
ols_slope(xs: list[float], ys: list[float]) -> float
```
Reads the JSONL, sorts by `step`, computes:
- `step0`, `stepN`, `delta = stepN - step0`
- `ols_slope_per_step` (least-squares fit of mean_reward vs step)
- `early_mean` / `late_mean` (first/last k=min(5,n//2) steps)
- `projected_at_horizon = step0 + slope*horizon`
- `verdict`: `continuing-up` if slope>flat_eps, `reversed-down` if slope<-flat_eps,
  else `flat`.

CLI: `python3 analyze_curve.py <jsonl> --horizon 50 [--flat-eps 0.005]` → JSON to stdout.

### Test cases
- T1 (existing v2, 15 steps): delta ≈ +0.0371, slope ≈ +0.00174, verdict `flat`
  (slope < eps) — proves the +0.037 is real but within-noise. **PASS expected.**
- T2 (existing v1, 25 steps): slope < 0, verdict `reversed-down`/`flat`,
  delta ≈ −0.03 — proves the analyzer distinguishes the two runs.
- T3 (<2 lines): raises `SystemExit`. (guards empty/partial files)
- T4 (synthetic strictly-increasing run): verdict `continuing-up`.

## Artifact 3: real partial curve
`train_d1_50step.jsonl` / `.log` — the actual per-step output of the live
50-step run, however many steps complete within the compute cap.

## Non-goals (explicit)
- No edit to `train_rft_v2.py`, `hud_env_v2.py`, or any `rex/*`, `sim/*`, `agent/*`.
- No reward redesign. No multi-seed (deferred to a follow-up task).
