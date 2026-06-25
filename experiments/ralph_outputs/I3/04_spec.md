# I3 — Technical spec

## Data contract (inputs)
A1/A2 result JSON: `by_condition[cond].per_incident_rewards` is
`Dict[incident_id -> List[float]]` (one reward per seed). Per-condition episode
vector = flatten all incidents' lists. Sizes: A1 = 126/condition, A2 = 150.
`rex/runs/diagnostic_probe_*.jsonl`: each line has float `score`; pool all.

Reward atoms observed: {0.0, 0.3, 0.4, 0.45, 0.75, 1.0} (partial-credit rubric).

## `dip_test.py`
```python
def dip_test(samples: Sequence[float], n_boot=10000, seed=0) -> tuple[float, float]:
    """(D, p). Primary engine: diptest.diptest(x, boot_pval=False) (AS 217,
    analytic interpolation p). Fallback (no pkg): numpy statistic + Uniform MC p."""

def dip_statistic(samples) -> float          # D only
def _dip_statistic_fallback(samples) -> float # numpy GCM/LCM, statistic only
```
D in [0, 0.25]. n<4 -> (0.0, 1.0).

## `run_dip_on_rewards.py`
```python
collect_condition_rewards(path) -> (model: str, {cond: List[float]})
collect_rex_runs(repo) -> List[float]
describe(rewards) -> {n, mean, std, frac_low(<=0.1), frac_high(>=0.9), frac_mid}
run_one(name, rewards) -> {name, dip_statistic, p_value, alpha, conclusion, **describe}
main() -> writes dip_results.json, prints table
```
Conclusion rule (alpha=0.05): p<0.05 -> "REJECT unimodality (multimodal/bimodal)";
0.05<=p<0.10 -> "marginal"; else "fail to reject unimodality".

## `dip_results.json` (output)
```json
{"test":"...","engine":"diptest v0.11 (AS 217 ...)","null":"Uniform(0,1)...",
 "alpha":0.05,
 "results":[{"name":"A1/glm-5p2::zero_shot","dip_statistic":0.143,"p_value":0.0,
   "alpha":0.05,"conclusion":"...","n":126,"mean":0.429,"std":0.384,
   "frac_low(<=0.1)":..,"frac_high(>=0.9)":..,"frac_mid":..}, ...]}
```

## Test cases (`test_dip_test.py`)
- D in [0,0.25] for random inputs.
- Uniform: majority p>0.05 (not rejected).
- Gaussian(300): D<0.05 and p>0.05.  [the gate]
- Two-spike (N(0,.05)+N(1,.05)): D>0.1 and p<0.01.
- Pass/fail rewards [0]*60+[1]*60+middle: p<0.05.
- Determinism: dip_test(x) == dip_test(x).
