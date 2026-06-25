# B10 — 04 Spec

## Log format contract (input)
One JSON object per line (JSONL), as emitted by `train_rft.py` / `train_rft_v2.py`:
```
{"step": int,            # GRPO step index (0-based)
 "mean_reward": float,   # optional; mean of `rewards`
 "reward_std": float,    # optional (v2 only)
 "n": int,               # optional; len(rewards)
 "rewards": [float,...], # REQUIRED; per-rollout graded reward in [0,1]
 "loss": float|null}     # optional
```
Required keys for this tool: `step`, `rewards`. Lines lacking either are skipped with a warning.

## Constants
- `THRESHOLD = 0.8` — repo-canonical (`rex/eval_pass_at_k.py:43`, `compute_pass_at_k.binary_pass`).
- `_DEFAULT_RUNS = <repo>/opensre-traj/runs` — auto-discovery root.

## Function signatures (`artifacts/learning_curve.py`)
```python
def wilson_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]
    # Wilson score 95% CI; mirrors compute_pass_at_k.wilson_ci. n==0 -> (0.0,0.0).

def parse_log(path: str, threshold: float = THRESHOLD) -> list[dict]
    # -> rows sorted by step, each:
    #   {"step":int, "n":int, "passes":int, "pass1":float,
    #    "ci_lo":float, "ci_hi":float, "mean_reward":float}
    # pass1 = sum(r >= threshold for r in rewards) / n.
    # Robust to: blank lines, JSONDecodeError, missing step/rewards, empty rewards.

def write_csv(series: dict[str, list[dict]], path: str) -> None
    # columns: run, step, n, passes, pass1, ci_lo, ci_hi, mean_reward

def plot(series: dict[str, list[dict]], out: str, threshold: float, title: str) -> None
    # one pass@1 line + Wilson band + faint mean_reward dashed line per run;
    # horizontal threshold line; matplotlib Agg backend; dpi=130.

def label_for(path: str) -> str    # basename without extension
def main() -> int                  # CLI; 0 ok, 2 = blocker (no logs / no parseable steps)
```

## CLI
```
python3 learning_curve.py [--log P]... [--threshold 0.8] [--out PNG] [--csv CSV] [--title T]
# no --log -> auto-discover opensre-traj/runs/*.jsonl
```

## pass@1 semantics (the contract that matters)
`pass@1(step)` is the empirical single-sample success rate over that step's GRPO rollouts:
each rollout is one i.i.d. attempt at the (mixed) task batch; a rollout succeeds iff
`reward >= threshold`. This equals the mean of the per-rollout 0/1 indicator. It is a
**batch-level** pass@1 over rollouts, NOT a per-incident pass@1 (the log does not carry the
scenario id per rollout).

## Test cases (`artifacts/test_learning_curve.py`)
1. `test_pass1_threshold` — `[0.9,0.8,0.79,0.1]` @0.8 → passes=2, pass1=0.5.
2. `test_threshold_boundary` — reward == threshold counts as pass (`>=`).
3. `test_robust_to_garbage` — blank / malformed JSON / missing-rewards / empty-rewards lines
   skipped; valid lines returned sorted by step.
4. `test_wilson_ci_bounds` — CI brackets p and lies in [0,1]; n==0 → (0,0).
5. `test_real_logs_parse` — every real `runs/*.jsonl` parses; pass1∈[0,1]; steps sorted.

## Outputs
- `learning_curve.png` / `.csv` (τ=0.8 headline).
- `learning_curve_t065.png` / `.csv` (τ=0.65 companion, labeled).
