# 04 — Technical Spec

## Module: `artifacts/root_cause_accuracy.py`

### Data structures
- `KIND_CATEGORY: dict[str,str]` — mirrors `rex/harness.py:_KIND_CATEGORY`
  (16 kinds -> 8 categories: resource_exhaustion, bad_deploy, config_error,
  network_fault, node_failure, saturation, dependency_failure, +unknown).
- `_CATEGORY_TERMS: dict[str, list[str]]` — discriminative keyword vocab/category.
- `_CATEGORY_STEMS: dict[str, set[str]]` — vocab stemmed via `rex.scoring._stems`.
- `CATEGORIES: list[str]` — the 7 keyworded categories + "unknown".

### Function signatures
```python
classify_root_cause(stated: str) -> str
    # max discriminative keyword overlap; tie or no-signal -> "unknown". Pure.

gold_category_from_kind(kind: str) -> str
    # KIND_CATEGORY.get(kind, "unknown")

evaluate(records: list[dict]) -> RCAResult
    # record needs model text ('answer' or 'root_cause') + gold
    # ('true_category', else 'root_cause_kind' -> gold_category_from_kind).

load_jsonl(path: str) -> list[dict]
main(argv=None) -> int   # CLI: --traj PATH [--json]
```

### RCAResult (dataclass)
```
n: int                       # records scored
accuracy: float              # correct / n
correct: int
confusion: dict              # gold -> {predicted -> count}
per_category_acc: dict       # gold -> recall
rc_vs_resolved_disagree: float | None   # decoupling statistic
n_with_resolved: int
```

### Gold/pass-fail contract
- gold = `true_category` if present, else derived from `root_cause_kind`.
- pass/fail (`_resolved_flag`): `resolved` bool if present, else `reward >= 0.5`,
  else None (skipped from decoupling stat). This is ONLY used to demonstrate
  decoupling — it never enters the accuracy number.

### Test cases (`test_root_cause_accuracy.py`)
1. classify resource_exhaustion / network_fault / bad_deploy / config_error.
2. empty + signal-free answer -> "unknown".
3. phrasing-robustness: "leaking memory" == "memory leak" category.
4. `gold_category_from_kind` for mem_leak/cache_flush/dep_revoked/unknown.
5. evaluate perfect (acc 1.0); mixed (acc 0.5 + confusion entry).
6. decoupling: diagnosis correct but reward<0.5 -> disagree==1.0.
7. YAML-kind grounding path (no true_category).
8. records without gold are skipped.

### File formats
- Input: JSONL, one trajectory/line.
- Output: human table (default) or `--json` (RCAResult as JSON).
