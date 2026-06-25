# D1 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/D1/artifacts/`, no core edits)

### 1. `run_rft_50.sh` — 50-step RFT launcher
Thin, env-overridable wrapper over the **unmodified** `opensre-traj/train_rft_v2.py`.
Defaults: `MODEL=opensre-qwen3-8b-1e439a`, `STEPS=50`, `GROUP=6`, `LR=1e-5`,
`TASKS=0..9`, append-only `OUT`. Hardened with `set -euo pipefail`. Syntax-checked
with `bash -n` (PASS). Does NOT modify `train_rft_v2.py`, `hud_env_v2.py`, or any
`rex/*` / `sim/*` / `agent/*` file — it only re-invokes the existing trainer with
`--steps 50`.

### 2. `analyze_curve.py` — trend analyzer (pure stdlib)
Reads any run JSONL and emits delta, OLS slope/step, early/late means, a
horizon projection, and a falsifiable `verdict` (`continuing-up`/`flat`/
`reversed-down`). This is the tool that actually answers "does the +0.037 trend
continue?". No network, no HUD dependency.

### 3. `train_d1_50step.jsonl` / `.log` — REAL partial training curve
The actual per-step output of a live 50-step run I launched against the HUD/Tinker
backend (model `opensre-qwen3-8b-1e439a`, group 6, lr 1e-5, tasks 0–9, n=60
rollouts/step). Real numbers, not fabricated; the run is capped by compute (see 07/09).

## Live-backend proof (smoke, before the full run)
```
$ ../.venv-hud/bin/python train_rft_v2.py --model opensre-qwen3-8b-1e439a \
      --tasks 0,1 --group 2 --steps 1 --smoke
v2  model=opensre-qwen3-8b-1e439a  tasks=[0, 1]  group=2  steps=1  lr=1e-05
env=hud_env_v2.py (P0 deterministic mechanism reward)  reset_head=False
job: https://hud.ai/jobs/874077aeb4374c108d1e582e143de9ed
[smoke] rollouts=4 rewards=[0.588, 0.704, 0.252, 0.312] spread=0.188
step   0  mean_reward=0.4640  spread=0.188  n=4  loss=None
SMOKE OK: rollouts -> reward (v2 grader) -> forward/backward -> logged.
```
This proves the full pipeline (rollout → v2 deterministic reward → Tinker
forward/backward → logged) works end-to-end against the live GPU backend.

## Proposed core change (NOT applied — parallel safety)
None required. D1 is achievable purely by re-invoking the existing `train_rft_v2.py`
with more steps; no core file needs editing. (If one ever wanted true mid-run
resume rather than append, that would be a change to `train_rft_v2.py` — left as a
documented future patch, not applied here.)
