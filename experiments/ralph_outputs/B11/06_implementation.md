# 06 — Implementation

## Artifacts created (all under experiments/ralph_outputs/B11/artifacts/)
- `threshold_sweep.py` — standalone sweep. Reads `rex/runs/ablation.json`, re-applies
  `binary_pass(reward, thr)` at thresholds {0.70, 0.80, 0.86, 0.90}, computes per-arm
  pass-rate + Wilson 95% CI, the REx-vs-best-control gap, and a `robust` verdict.
  Estimators (`binary_pass`, `wilson_ci`) are COPIED (not imported) so the script is
  self-contained and never touches `agent.llm` / network (DEVOPS). Includes a
  load-time shape assert on `per_incident` (05_ouroboros Engineer A).
- `test_threshold_sweep.py` — offline tests: (1) copied `binary_pass` matches the
  canonical `reward>=thr` rule; (2) copied `wilson_ci` matches the hand-computed
  canonical Wilson formula within 1e-3 (estimator-drift guard, PSRE/DEVOPS); (3)
  sweep on real data has 4 thresholds x 5 arms, REx beats best control at 0.80, and
  REx wins at all thresholds.
- `robustness.json` — emitted output (the robustness table + per-arm CIs).

## Grounding
- Threshold parameter located in `experiments/compute_pass_at_k.py:39`
  (`binary_pass(reward, threshold=0.8)`) and `rex/eval_pass_at_k.py:48`
  (`THRESHOLD = 0.8`). `rex/scoring.py` itself has NO threshold — its reward is the
  graded `0.30*diag + 0.25*fix + 0.45*resolved - 0.60*trap` (score_plan). The sweep
  therefore operates at the downstream pass/fail gate, exactly where 0.80 lives.

## Real data used
`rex/runs/ablation.json` — `claude-haiku-4-5`, N=4, seeds [0,1,2], 5 hard cascades,
deterministic P0 judge. 15 graded rewards/arm across 5 arms.

## Shared-core safety
No edit to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`. Only new files
under the task-namespaced B11 artifacts dir. Estimators copied, not monkey-patched.

## Result (real output)
```
arm                 thr=0.70    thr=0.80    thr=0.86    thr=0.90
zero_shot               0.20        0.00        0.00        0.00
best_of_n               0.20        0.07        0.07        0.07
retry_realistic         0.20        0.00        0.00        0.00
rex                     0.40        0.40        0.40        0.40
rex_no_oracle           0.20        0.00        0.00        0.00
REx - best ctrl        +0.20       +0.33       +0.33       +0.33
REx wins?                yes         yes         yes         yes
robust = True
```
Observed reward bands (RLE prediction confirmed): {0.0, 0.10, 0.125, 0.25, 0.30,
0.40, 0.425, 0.55, 0.70, 1.0}. Nothing lands in (0.70, 1.0), so 0.80/0.86/0.90 give
identical pass-rates — the discriminating cut is 0.70 vs >0.70. REx is the only arm
that reaches the 1.0 band (on aws_dynamodb_dns and railway_gcp_suspension), which is
why its pass-rate is invariant across the strict thresholds while every control
collapses above 0.70.
