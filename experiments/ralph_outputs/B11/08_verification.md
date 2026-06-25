# 08 — Verification against success criteria

| Criterion (from 01) | Met? | Evidence |
|---|---|---|
| Ground threshold in `rex/scoring.py` | YES | scoring has no threshold (graded reward); located the real cutoff at `compute_pass_at_k.binary_pass` / `eval_pass_at_k.THRESHOLD=0.8`. Documented in 04/06. |
| Script sweeps threshold over real score data | YES | `threshold_sweep.py` reads real `rex/runs/ablation.json` (15 graded rewards/arm) and re-binarises at {0.70,0.80,0.86,0.90}. |
| Emits a robustness table | YES | ASCII table printed + `robustness.json` written with per-arm pass-rate, Wilson CI, gap, verdict. |
| Script was actually run | YES | 07 shows real stdout; robustness.json exists on disk. |
| Tests pass | YES | 3/3 pytest + standalone runner. |
| No shared core file edited | YES | only new files under `experiments/ralph_outputs/B11/artifacts/`; estimators copied, not imported/patched. |

## Outputs are real, not placeholder
- `robustness.json` is generated from real `ablation.json` reward data
  (claude-haiku-4-5, deterministic judge), not hand-written. Re-running reproduces it
  byte-for-byte (pure function of fixed input).
- Numbers are internally consistent: e.g. `best_of_n` pass-rate 0.07 at thr>=0.80 =
  1 pass / 15 (the single 1.0-reward attempt); REx 0.40 = 6/15.

## Headline finding
REx beats the best fair control at EVERY threshold; the gap is +0.20 at 0.70 and
WIDENS to +0.33 at 0.80/0.86/0.90. The win is therefore robust to (and strengthened
by) a stricter pass gate — the opposite of "tuned to win at 0.80." `robust = True`.
