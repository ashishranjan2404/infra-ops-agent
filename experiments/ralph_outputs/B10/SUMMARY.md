# B10 — SUMMARY: RFT learning curve (pass@1 vs training steps)

## Deliverable
A reusable matplotlib harness that extracts pass@1 per GRPO training step from real opensre RFT
logs and plots the learning curve, plus tidy CSV exports. Grounded in opensre-traj/train_rft.py
and train_rft_v2.py (the JSONL schema they emit) and run against the 3 real logs in
opensre-traj/runs/.

## Artifacts (all under experiments/ralph_outputs/B10/artifacts/)
- learning_curve.py — parser + pass@1 derivation + Wilson-CI plotter + CSV export + CLI.
- test_learning_curve.py — 5 self-tests, all passing.
- learning_curve.png / .csv — tau=0.8 (canonical "incident resolved").
- learning_curve_t065.png / .csv — tau=0.65 ("substantially-correct diagnosis").

## How pass@1 is defined
Logs record a continuous weighted reward in [0,1], not binary pass/fail. pass@1 is derived with the
repo-canonical threshold (rex/eval_pass_at_k.py:43, compute_pass_at_k.binary_pass):
pass@1(step) = (#rollouts with reward >= 0.8) / n — a batch-level single-sample pass rate over the
step's GRPO rollouts (not per-incident; the log lacks per-rollout scenario ids).

## Key findings (real data)
- tau=0.8 (operational): pass@1 flat at 0 for all runs — max reward ~0.78-0.80 never clears the bar.
  Honest null headline: trained Qwen checkpoints resolve zero incidents at the resolution threshold.
- tau=0.65 (partial credit): curves separate — v2 deterministic-reward run CLIMBS 0.375->0.525,
  original 8b baseline DECLINES 0.375->0.208, 30b FLAT 0.167. Consistent with the flat-baseline
  diagnosis in train_rft_v2.py. Suggestive, not significant (n=24-40/step).

## Status
COMPLETED — real plan + spec + tested runnable harness + real curves from real logs. No shared core
file edited. The flat-zero result at the 0.8 bar is an honest property of the data, not a tooling
blocker; a longer GPU run pushing rollouts past 0.8 is the documented follow-up (blocked: needs HUD
Tinker GPU + forked Qwen slug).
