# D12 — 04 Spec

## A. The group-size param (verified in `opensre-traj/train_rft_v2.py`)
`--group G` (argparse, line ~119) threads to:
| site | line | role |
|------|------|------|
| `Job.start(args.model, group=args.group)` | ~82 | sizes the rollout job |
| `ts.run(agent, group=args.group, job=session)` | ~91 | emits G rollouts / task / step |
| `trainer.step(batch, learning_rate=args.lr, group_size=args.group)` | ~99 | GRPO within-group advantage normalization |
Rollouts/step = `len(tasks) * G`. Logged baseline: 10 tasks × 4 = 40 (matches `n=40` in jsonl).

## B. Artifacts

### `group8_config.yaml`
Keys: `run_name, env, model_slug, tasks, group(=8), steps, lr, reset_head, out`.
Declarative mirror of the CLI; comments document the 3 threading sites + 2× cost + smoke command.

### `run_group8.sh`
- `cd` to `opensre-traj`, `source ~/.zshrc` for `HUD_API_KEY`.
- `MODEL` env override (default `opensre-qwen3-8b`).
- `--smoke` → `--tasks 0,1 --group 8 --steps 1 --smoke`.
- default → `--tasks 0..9 --group 8 --steps 30 --lr 1e-5 --reset-head --out runs/train_qwen3-8b_group8.jsonl`.
- Does NOT modify `train_rft_v2.py`.

### `variance_analysis.py`
```
within_group_sigma(log_path, base_g=4) -> (list[sigma_per_group], n_steps)
  # rollouts are task-major: base_g consecutive rewards == one task's group
main():
  sigma = mean(per-group pstdev)
  for G in (4,8): SEM[G] = sigma / sqrt(G); Var = SEM**2
  report: reduction_sd = 1 - SEM[8]/SEM[4]  (== 1 - 1/sqrt(2) = 0.293)
          reduction_var = 1 - Var[8]/Var[4] (== 0.5)
```

## C. Statistical contract
- GRPO advantage `A_i = r_i - mean_g(r)`. The baseline `mean_g` is a G-sample estimator of the
  group's true mean; its standard error is `sigma/sqrt(G)`.
- 4→8: SEM ×0.707 (−29.3%), Var ×0.5 (−50%), rollout cost ×2.
- Claim scope: improves *gradient/baseline quality*, NOT the reward ceiling.

## D. Test cases
1. `yaml.safe_load(group8_config.yaml)` → dict with `group == 8`. PASS criterion.
2. `bash -n run_group8.sh` → exit 0.
3. `python3 variance_analysis.py` on the real log → prints `reduction_sd ≈ 29.3%`,
   `reduction_var = 50%`, with `n=40`-derived sigma > 0.
4. Negative: missing log → script exits with a clear "baseline log not found" message.

## E. Blocker contract
Real run requires HUD_API_KEY + forked slug + GPU minutes; 80 rollouts/step × 30 steps ≫ 15-min
cap. Deliverable = config + smoke path + projection; `07`/`09` document the blocker explicitly.
