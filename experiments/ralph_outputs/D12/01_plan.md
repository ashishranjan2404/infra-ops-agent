# D12 — 01 Plan

## Objective
Determine whether raising the RFT (GRPO) **group size from 4 to 8** helps the opensre
incident-diagnosis training run, and deliver: (a) a runnable group-size-8 config + launcher,
(b) a grounded analysis of the expected variance reduction.

## Grounding (real code & data)
- `opensre-traj/train_rft_v2.py` is the current trainer. The group-size param is `--group`
  (default 6 in v2; the **logged baseline run used 4**). It flows to 3 sites:
  - `Job.start(model, group=G)` — sizes the rollout job
  - `ts.run(agent, group=G, job=session)` — emits G rollouts per task per step
  - `trainer.step(batch, learning_rate, group_size=G)` — GRPO normalizes advantage within each group of G
- `opensre-traj/runs/train_qwen3-8b_v2.jsonl` — REAL baseline: 10 tasks × group 4 = **40 rollouts/step**,
  15 steps, mean per-step reward_std ≈ 0.183, **per-task within-group sigma ≈ 0.069**.
- `hud_env_v2.py` — P0 deterministic grader giving non-degenerate within-group spread.

## Approach
1. Read both trainers; confirm exactly how `group` is threaded (done).
2. Pull the empirical within-group reward sigma from the baseline jsonl (the quantity GRPO
   advantage rides on).
3. Project the GRPO baseline-estimator error (SEM = sigma/sqrt(G)) for G=4 vs G=8.
4. Emit a `--group 8` config + shell launcher that does NOT modify the shared trainer.

## Files to create (all task-namespaced)
- `artifacts/group8_config.yaml` — declarative config mirroring the trainer CLI, group=8.
- `artifacts/run_group8.sh` — launcher invoking `train_rft_v2.py --group 8` (+ `--smoke`).
- `artifacts/variance_analysis.py` — derives the variance numbers from the real baseline log.

## Dependencies / risks
- Real training needs `HUD_API_KEY` + a forked trainable Qwen slug + ~GPU minutes on HUD
  Tinker. **Compute cap ~15 min** → cannot complete a 30-step group-8 run here; expected blocker.
- Closed models (Claude/GPT) cannot be GRPO'd — group size only matters for the open trainee.
- Statistical claim must be honest: more rollouts reduce *baseline-mean* error by 1/sqrt(2),
  it does not change the *root cause* of the flat baseline.

## Success criteria
- group=8 config parses; launcher passes `bash -n`; analysis script runs on the real log and
  prints grounded sigma + SEM(4) vs SEM(8) + the 29.3% / 50% reduction figures.
- Honest verdict on "does more rollouts help?" with the training blocker documented.
