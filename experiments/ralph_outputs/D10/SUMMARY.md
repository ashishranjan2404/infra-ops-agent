# D10 — SUMMARY

## Task
Run RFT with different reward weightings — sweep W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY.
Ground in rex/scoring.py. Build a non-invasive sweep harness, run it over real rollout data,
show how composite reward / ranking change. Do not edit core files.

## Grounding
rex/scoring.py:22 -> W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60.
score_plan = W_ROOT*diag + W_FIX*fix + W_RESOLVED*resolved (- TRAP_PENALTY if trap), clamped [0,1].

## What was built
- artifacts/reward_sweep.py — wrapper that recombines score_plan's four primitives under
  arbitrary weights. Imports rex.scoring/rex.harness; edits NEITHER.
- artifacts/sweep_results.json — 292 real sim-executed rollouts across all 42 scenarios,
  8 weightings. Deterministic (byte-identical across runs).

## Key results
weighting          mean   tau-vs-default  argmax-flips
default            0.319  1.000           0
diagnosis_heavy    0.405  0.766           0
fix_heavy          0.313  0.831           0
resolution_only    0.211  0.406           1
equal_thirds       0.335  0.832           0
no_trap_penalty    0.383  0.723           1
harsh_trap         0.280  0.671           0
diag_then_resolve  0.343  0.766           0

- Re-weighting reorders the optimization target. Dropping TRAP_PENALTY and resolution_only
  flip the top-ranked rollout (e.g. azure_ddos: best flips fix_wrong_target -> correct_full).
  The trap penalty and resolution weight are load-bearing for RANKING, not just magnitude.
- diagnosis_heavy raises mean reward (0.405) but mostly preserves ranking (tau 0.77).
- Selftest proves the wrapper == score_plan at default weights on all 292 rollouts.

## Honest boundary
This is the reward-design half of RFT (how the optimization target moves under each weighting)
over real sim rollouts. The GPU policy-gradient/GRPO update is NOT run (no GPU/API) and training
curves were deliberately not fabricated. Rollouts are synthetic candidate plans executed through
the real sim, so argmax-flip rate is an existence proof, not a population statistic. Global
spread metric is pinned at 1.0 (noted weakness; per-scenario std is the proper trainability signal).

## Status: completed (downstream GPU training step blocked, deliverable real).
