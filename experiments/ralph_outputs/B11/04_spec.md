# 04 — Technical spec

## Inputs
`rex/runs/ablation.json` (real):
```
{
  "model": "claude-haiku-4-5", "N": 4, "seeds": [0,1,2],
  "incidents": [5 hard cascades],
  "per_incident": { arm: { incident: [r_seed0, r_seed1, r_seed2] } }   # r in [0,1]
}
```
Arms: `zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle`. 5 incidents x 3
seeds = 15 graded rewards per arm.

## Threshold semantics (grounded)
`binary_pass(reward, thr) = 1 if reward >= thr else 0` — identical to
`experiments/compute_pass_at_k.py:39` and the `THRESHOLD=0.8` gate in
`rex/eval_pass_at_k.py`. We sweep `thr in {0.70, 0.80, 0.86, 0.90}`.
- 0.70: lenient — diag(0.30)+resolved(0.45)=0.75 passes; partial-fix combos near here.
- 0.80: the canonical published cutoff (the value under attack).
- 0.86: strict — just ABOVE diag+fix+partial-resolved (0.30+0.25+... bands); needs
  near-complete credit. Stress point.
- 0.90: very strict — effectively requires diag+fix+resolved. Strictest stress point.

## Function signatures (`threshold_sweep.py`)
```python
def binary_pass(reward: float, threshold: float) -> int        # copied, canonical math
def wilson_ci(p: float, n: int, z: float = 1.96) -> tuple      # copied, canonical math
def arm_rewards(per_incident: dict) -> dict                    # {arm: [all rewards]}
def sweep(per_incident: dict, thresholds: list) -> dict        # rows keyed by "%.2f"
def render_table(rows: dict, arms: list) -> str
```

## Output contract (`robustness.json`)
```
{
 "_source": "rex/runs/ablation.json",
 "model","seeds","N","incidents","n_attempts_per_arm","thresholds","arms",
 "rows": { "0.70": {
     "per_arm": { arm: {"n","passes","pass_rate","wilson95":[lo,hi]} },
     "best_control": <best non-rex arm>,
     "rex_pass_rate", "best_control_pass_rate",
     "rex_minus_best_control", "rex_wins": bool
   }, "0.80": {...}, "0.86": {...}, "0.90": {...} },
 "robust": all(rows[t].rex_wins),
 "table": "<rendered ascii>"
}
```
`best_control` = argmax pass-rate over arms NOT starting with "rex" (the fair-control
set the headline claim is measured against).

## Test cases (07)
1. `python3 -c "import ast; ast.parse(open(script).read())"` parses (syntax).
2. Run end-to-end → `robustness.json` exists, has 4 rows, each with 5 arms.
3. Estimator equivalence (offline): `binary_pass(0.7,0.8)==0`, `binary_pass(0.8,0.8)==1`,
   `wilson_ci(0.4,15)` ≈ hand value from the canonical formula (matches
   `compute_pass_at_k.wilson_ci` math).
4. Semantic: `rows["0.80"].rex_pass_rate > rows["0.80"].best_control_pass_rate`
   (REx beats best control at the published cutoff).
5. `robust == True` iff REx wins at all four.

## Non-goals
No new rollouts, no LLM calls, no edits to scoring/eval. Pure re-thresholding of
existing real reward data.
