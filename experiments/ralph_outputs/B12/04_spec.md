# 04 — Spec

## Input contract (per source JSON, A1/A2 schema)
```
{
  "model": str, "label": str, "threshold": float (e.g. 0.8),
  "seeds": int,                       # number of reps per incident
  "incidents_by_family": { "simple"|"cascade"|"novel": [incident_id, ...] },
  "by_condition": {
     "<cond>": {
        "per_incident_rewards": { "<incident_id>": [float, ...] }   # len == reps
     }, ...
  }
}
```
Validation: a file lacking `by_condition` or `incidents_by_family` raises `ValueError`
in `load_source`; `main` catches it, prints `[skip] <path>: <reason>`, continues.

## Data structures

`row` (one per (source_model, incident)):
```
{
  "incident": str, "family": str, "source_model": str, "source_label": str,
  "threshold": float, "best_pass@1": float,
  "solvability": "solvable" | "partially" | "unsolvable",
  "by_condition": {
     "<cond>": {"n": int, "passes": int, "pass@1": float,
                "pass@<k>": float, "k": int, "mean_reward": float}
  }
}
```

`summary`:
```
{ "n_rows": int,
  "counts": {flag: int},
  "unsolvable": ["<model>:<incident>", ...],   # sorted
  "partially":  ["<model>:<incident>", ...],
  "by_family": {family: {flag: int}} }
```

## Function signatures
- `_pass_at_k(n, c, k) -> float` — unbiased estimator (imported or fallback).
- `binary_pass(reward, threshold) -> int`
- `load_source(path) -> dict`           # validates schema
- `incident_family_map(d) -> dict`      # incident -> family
- `build_rows(sources: list, k_override) -> list[row]`
- `summarize(rows) -> summary`
- `render_md(rows, summary) -> str`
- `main(argv=None) -> int`              # 0 ok, 2 no valid inputs

## CLI
```
per_incident_breakdown.py --inputs A.json B.json --out-json out.json --out-md out.md [--k 2]
```
Default k = per-source sample count n (so pass@k uses the full rep budget).

## Solvability rule
`best_p1 = max over conditions of (passes/n)`.
`>=1.0 -> solvable`; `>0 -> partially`; `==0 -> unsolvable`.

## Test cases (test_per_incident_breakdown.py)
1. `_pass_at_k` bounds: c=0→0, c=n→1, (n=3,c=1,k=1)→1/3, monotonic in c.
2. `binary_pass` threshold boundary (0.8→1, 0.79→0).
3. `incident_family_map` correctness.
4. solvability flags: crafted solvable/partially/unsolvable incidents classify right.
5. summary counts + unsolvable list format `model:incident`.
6. multi-source: same incident, two models → two rows, independent flags.
7. `--k` override honored in cell keys.
