# D12 — 06 Implementation

## Artifacts created (all under `experiments/ralph_outputs/D12/artifacts/`)

### 1. `group8_config.yaml`
Declarative config for a group=8 RFT run. Mirrors `train_rft_v2.py`'s CLI exactly
(`model_slug, tasks=0..9, group=8, steps=30, lr=1e-5, reset_head, out`). Comments document the
3 sites where `group` is threaded (Job.start / ts.run / trainer.step) and the 2× rollout cost
(40 → 80 rollouts/step). Parses cleanly under `yaml.safe_load`.

### 2. `run_group8.sh`
Launcher that invokes the **existing, unmodified** `train_rft_v2.py --group 8`. Supports a
`--smoke` fast path (`--tasks 0,1 --group 8 --steps 1 --smoke`) and a full run. Sources
`~/.zshrc` for `HUD_API_KEY` (guarded with `|| true`), `MODEL` overridable. `bash -n` clean,
`chmod +x` applied. **Does NOT edit any shared core file.**

### 3. `variance_analysis.py`
Reads the REAL baseline log `opensre-traj/runs/train_qwen3-8b_v2.jsonl` (10 tasks × group 4,
15 steps), derives per-task within-group reward sigma, and projects the GRPO baseline-estimator
error for G=4 vs G=8. Output (verified, see `07`):

```
within-group sigma   : mean=0.0689  median=0.0349
G=4:  rollouts/step= 40   SEM=0.0345   Var=0.00119
G=8:  rollouts/step= 80   SEM=0.0244   Var=0.00059
4 -> 8:  baseline-mean std error -29.3%   variance -50.0%   rollout compute +100%
```

## Proposed core change (NOT applied — documented per parallel-safety rules)
No edit to `train_rft_v2.py` is required: `--group 8` is already a supported CLI value. The only
"change" to run group-8 is the config + launcher above. If one wanted group=8 to be the *default*,
the one-line diff would be `train_rft_v2.py:119  default=6 -> default=8` — recorded here, **not
applied**, to avoid touching a shared file under parallel execution.

## How to actually run (when compute is available)
```
bash experiments/ralph_outputs/D12/artifacts/run_group8.sh --smoke   # < 1 min model time
bash experiments/ralph_outputs/D12/artifacts/run_group8.sh           # full 30-step group-8 run
```
