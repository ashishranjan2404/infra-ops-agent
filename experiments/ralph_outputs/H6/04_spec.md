# H6 — 04 Spec

## Module: `ci_validate_scenarios.py`

### Constants (stage identifiers, ordered)
```
STAGE_LOAD        = "load"         # YAML parse + dataclass build
STAGE_SCHEMA      = "schema"       # sim.spec.validate() returned errors
STAGE_INSTANTIATE = "instantiate"  # World.from_spec raised
STAGE_APPLY       = "apply_fix"    # apply_action over canonical_fix raised
STAGE_SETTLE      = "settle"       # world.run(sustain) raised
```

### Functions
```python
def default_globs() -> list[str]
    # [scenarios/cidg/*.yaml, scenarios/cidg/generated/*.yaml] (abs paths under REPO)

def resolve_paths(patterns: list[str]) -> list[str]
    # de-dup + sorted absolute paths; abs patterns honored, rel patterns joined to REPO

def check_one(path: str) -> dict
    # runs the 5 stages; returns a record (see schema below)

def main(argv: list[str] | None = None) -> int
    # CLI; returns the process exit code (0|1|2)
```

### Per-scenario record (also the JSON `scenarios[]` element)
```json
{
  "file": "scenarios/cidg/generated/44-search-cpu-starve.yaml",
  "id": "search-cpu-starve",
  "ok": true,
  "failed_stage": null,
  "schema_errors": [],
  "error": null,
  "traceback": ["...last 3 lines..."]   // only present on an exception stage
}
```

### Report file (`--json`)
```json
{
  "summary": {
    "total": 61, "pass": 61, "fail": 0, "all_pass": true,
    "failures_by_stage": {}            // e.g. {"schema": 2, "load": 1}
  },
  "scenarios": [ <record>, ... ]
}
```

### CLI contract
```
--glob PATTERN   repeatable; overrides default corpus
--json PATH      write full report (dirs created); path may be rel (joined to REPO) or abs
--quiet          suppress per-OK lines; failures + summary still print
```

### Exit codes (the CI contract)
| code | meaning |
|------|---------|
| 0 | every matched scenario passed all 5 stages |
| 1 | ≥1 scenario failed (load/schema/instantiate/apply_fix/settle) |
| 2 | harness/usage: no scenarios matched, or sim engine import failed |

### Acceptance test cases (in `test_ci_validate.py`)
- `test_all_real_scenarios_pass` → `main(...) == 0` over the real corpus.
- `test_malformed_yaml_fails_at_load` → `check_one(bad_yaml).failed_stage == "load"`.
- `test_bad_schema_fails_at_schema` → schema stage + non-empty `schema_errors`.
- `test_unknown_slo_victim_caught_before_engine` → schema stage (never a runtime KeyError).
- `test_exit_code_nonzero_on_failure` → `main(bad_*) == 1`.
- `test_exit_code_two_on_no_match` → `main(__none__*) == 2`.

### Negative fixtures (committed under artifacts/)
- `bad_yaml.yaml` — unparseable YAML (load stage).
- `bad_schema.yaml` — unknown node kind, dangling edge, bad rc kind, bad SLO direction (schema).
- `bad_engine.yaml` — SLO names a nonexistent victim node (schema rejects pre-engine).

### Invariants
- No shared-core file is written. `sim/spec.py` and `sim/engine.py` are imported read-only.
- Each stage is wrapped so one bad scenario never aborts the sweep.
- `validate()` raising is reclassified as a schema failure (not an uncaught crash).
