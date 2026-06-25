# B10 — 08 Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| Script extracts pass@1 per training step | YES | `parse_log` derives `pass1=sum(r>=τ)/n` per step; `test_pass1_threshold` pins the math |
| Grounded in train_rft.py / train_rft_v2.py | YES | Parses the exact JSONL schema those scripts emit (`step`,`rewards`,`mean_reward`,`reward_std`) |
| Uses REAL run logs under opensre-traj/runs | YES | 3 real logs parsed: train_qwen3-8b, _v2, -30b (54 total steps) |
| Plots a learning curve (matplotlib PNG) | YES | `learning_curve.png` (τ=0.8) + `learning_curve_t065.png` (τ=0.65), visually verified |
| Self-tests pass | YES | 5/5, incl. real-log parse + robustness |
| No shared core files edited | YES | All output under `B10/artifacts/`; logs read-only; compute_pass_at_k mirrored not modified |
| pass@1 threshold consistent with repo | YES | τ=0.8 reused verbatim from `rex/eval_pass_at_k.py:43` / `compute_pass_at_k.binary_pass` |

## Outputs are REAL, not placeholder
- CSV rows are computed from the actual reward arrays (e.g. v2 step 14: 21/40 ≥0.65 → pass1=0.5250).
- PNG is a rendered matplotlib figure (78 KB / 151 KB), not a stub.
- The flat-zero τ=0.8 result is a genuine property of the data (reward max ≈0.78–0.80), reproducible
  by re-running the script — it is not an artifact of the harness.

## Honest caveats surfaced (not hidden)
- pass@1 is **derived** by thresholding a continuous reward, not logged natively — stated everywhere.
- It is a **batch-level** pass@1 over GRPO rollouts, not per-incident (the log lacks per-rollout
  scenario ids).
- Steps are autocorrelated; CIs are wide (n=24/40). No statistical-significance claim is made on the
  small per-step trends.

## Verdict
All success criteria met. Deliverable is a real, tested, reusable pass@1-vs-step harness producing
real curves from real RFT logs, with an honest negative headline result (no incident resolved at the
operational 0.8 bar) and a labeled partial-credit companion that exposes the v2 reward's learning
signal.
