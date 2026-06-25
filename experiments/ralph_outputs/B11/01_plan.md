# 01 — Plan (B11: threshold-robustness ablation)

## Objective
Show that the headline ablation result ("REx lifts the model over fair controls") is
NOT an artifact of a single, arbitrary pass cutoff. Re-binarise the SAME real graded
rewards at thresholds {0.70, 0.80, 0.86, 0.90} and emit a robustness table.

## Grounding (where the threshold lives)
- `rex/scoring.py` produces a **graded** reward in `[0,1]`:
  `0.30*diag + 0.25*fix + 0.45*resolved - 0.60*trap` (see `score_plan`). There is no
  threshold INSIDE scoring — the reward is continuous.
- The threshold is applied DOWNSTREAM at the pass/fail boundary:
  - `experiments/compute_pass_at_k.py:39` `binary_pass(reward, threshold=0.8)`
  - `rex/eval_pass_at_k.py:48` `THRESHOLD = 0.8`
  - so "pass" = `reward >= THRESHOLD`. 0.80 is the parameter B11 must sweep.

## Data (real, already on disk)
`rex/runs/ablation.json` → `per_incident[arm][incident] = [reward_seed0..]`, graded
rewards from `python3 -m rex.ablation` (claude-haiku-4-5, N=4, 3 seeds, 5 hard
cascades, deterministic P0 judge). 5 arms: zero_shot, best_of_n, retry_realistic,
rex, rex_no_oracle. 15 attempts/arm.

## Approach
1. New script `artifacts/threshold_sweep.py` reads `ablation.json`, re-applies
   `binary_pass` at each threshold, computes per-arm pass-rate + Wilson 95% CI.
2. Report the REx-vs-best-control GAP at every threshold and whether REx still wins.
3. Emit `artifacts/robustness.json` + a printed table.

## Files
- CREATE `experiments/ralph_outputs/B11/artifacts/threshold_sweep.py` (script)
- CREATE `experiments/ralph_outputs/B11/artifacts/robustness.json` (output)
- DO NOT edit `rex/*.py`, `experiments/*.py` (shared core). Estimators are copied
  into the script, not imported, to keep it self-contained and parallel-safe.

## Risks
- The dataset is small (n=15/arm) → wide Wilson CIs; the claim is "ordering stable",
  not "statistically separated at every cutoff". Report CIs honestly.
- 0.86 is an odd cutoff; justify it (it sits between the 0.85 [diag+fix+partial] and
  full-resolution reward bands, so it is a meaningful stress point).

## Success criteria
- Script runs, parses real data, emits a table over all 4 thresholds.
- Robustness verdict computed (does REx beat best control at every threshold?).
- No shared core file modified.
