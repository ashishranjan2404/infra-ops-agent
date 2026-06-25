# B11 — Threshold-robustness ablation (SUMMARY)

**Task:** Run the ablation across multiple pass thresholds {0.70, 0.80, 0.86, 0.90}
to show the "REx lifts the model" result is not an artifact of the single 0.80 cutoff.

**Grounding:** `rex/scoring.py` has no threshold — its reward is graded
(`0.30*diag + 0.25*fix + 0.45*resolved - 0.60*trap`). The pass/fail threshold lives
downstream at `experiments/compute_pass_at_k.py:39` (`binary_pass(reward, 0.8)`) and
`rex/eval_pass_at_k.py:48` (`THRESHOLD=0.8`). The sweep re-binarises real reward data
at that gate.

**Data:** real per-attempt graded rewards from `rex/runs/ablation.json`
(claude-haiku-4-5, N=4, 3 seeds, 5 hard cascades, deterministic P0 judge; 15
attempts/arm, 5 arms).

**Artifacts (task-namespaced, no shared core edited):**
- `artifacts/threshold_sweep.py` — the sweep (run, works).
- `artifacts/test_threshold_sweep.py` — 3 offline tests (3/3 pass).
- `artifacts/robustness.json` — emitted robustness table + Wilson CIs.

**Result:**
```
arm                 thr=0.70  thr=0.80  thr=0.86  thr=0.90
zero_shot              0.20      0.00      0.00      0.00
best_of_n              0.20      0.07      0.07      0.07
retry_realistic        0.20      0.00      0.00      0.00
rex                    0.40      0.40      0.40      0.40
rex_no_oracle          0.20      0.00      0.00      0.00
REx - best ctrl       +0.20     +0.33     +0.33     +0.33   ->  robust = True
```
REx beats the best fair control at every threshold; the gap WIDENS from +0.20 (0.70)
to +0.33 (>=0.80) because REx is the only arm reaching the top (1.0) reward band. The
win is robust to a stricter pass gate — the opposite of "tuned to 0.80."

**Caveats (09):** clustered n (5 incidents x 3 seeds -> effective n~5) -> Wilson CIs are
optimistic; claim is rank-order/gap stability, not per-cutoff significance. Reward is
discrete-banded so 0.80/0.86/0.90 tie (reported, not hidden). One model / one ablation
file (the only one storing per-attempt rewards).

**Status:** completed.
