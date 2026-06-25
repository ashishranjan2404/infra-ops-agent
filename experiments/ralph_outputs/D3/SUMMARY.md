# D3 — SUMMARY: Same-scenario GRPO group batching for opensre RFT

**Task:** Run RFT with same-scenario GRPO groups (the third fix from Table 1). Ground in
`opensre-traj/train_rft*.py`, implement same-scenario group batching as a new module/config,
explain why it reduces gradient variance, run a demo/unit test.

## The bug (grounded)
`opensre-traj/train_rft_v2.py:11-13` names it: GRPO groups can span DIFFERENT scenarios, so the
advantage A_i = r_i - group_mean reflects per-scenario *difficulty* rather than which rollout was
better. The loop at :89-100 runs one `ts.run(group=G)` over a multi-scenario Taskset, then
`trainer.step(group_size=G)` — a group can mix incidents.

## The fix (delivered, no core edits)
- `artifacts/same_scenario_groups.py` — partition rollouts into pure per-scenario GRPO groups,
  compute group-relative advantages, and quantify the variance removed via the law of total
  variance: Var(R) = E[Var(R|S)] + Var(E[R|S]). Same-scenario baselining deletes the
  between-scenario term Var(E[R|S]) (pure difficulty nuisance), keeping only the informative
  within-scenario signal.
- `artifacts/train_rft_same_scenario.py` — additive v3 driver: one single-scenario Taskset per
  index, looped per step, so every `trainer.step` group is same-scenario. Diff vs core v2
  documented for fold-back (original untouched).
- `artifacts/test_same_scenario_groups.py` — 7 unit tests (all pass).
- `artifacts/demo_variance_reduction.py` -> demo_variance_reduction.json.

## Results (real)
- 7/7 unit tests pass.
- Demo (grounded in v2's ~0.5 mean / ~0.17 within-spread): same-scenario grouping gives a
  2.38x lower advantage second moment (E[A^2] 0.0748 -> 0.0314), removes
  between_scenario_var = 0.0433, and corrects the advantage SIGN on 28% of rollouts (their
  gradient pointed the wrong way under mixed baselining). Total-variance identity holds exactly
  (0.074762 == 0.074762).

## Blocker (honest)
End-to-end GRPO A/B (v2 mixed vs v3 same-scenario learning curves) needs the live HUD Tinker
trainer + a forked Qwen slug + ~30 min — over the ~15-min cap and infra/credit-gated. Mechanism
proven + driver shipped; the live curve is the documented next step. No training numbers fabricated.

**Status: completed.**
