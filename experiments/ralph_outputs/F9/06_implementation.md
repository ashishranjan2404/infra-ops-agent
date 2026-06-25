# 06 — Implementation

## What I built
A self-contained supplementary-material generator plus its outputs, all under
`experiments/ralph_outputs/F9/artifacts/` (no shared core file touched).

### Artifacts
1. **`gen_incident_catalog.py`** — reads `scenarios/cidg/generated/*.yaml`, extracts
   key fields per incident, and writes:
   - `incident_catalog.md` (39 KB) — supplementary markdown: header + Summary
     (cascade/hidden/failure-class stats) + Full catalog table (51 rows) + 51
     Per-incident detail blocks.
   - `incident_catalog.json` (33 KB) — machine-readable index, one dict per incident.
   - Repo-root resolved from `__file__` (parents[4]); CLI flags `--src/--out-md/--out-json`.
   - Defensive `.get()` extraction; per-file try/except in `collect()` that warns+skips.
   - Deterministic (sorted by filename); exit codes 0/1/2.
2. **`test_catalog.py`** — stdlib-only test runner (4 tests), pytest-compatible.
3. **`incident_catalog.md`**, **`incident_catalog.json`** — the generated outputs.

## Key implementation decisions (from grill/ouroboros)
- Rows keyed on **filename**, not `meta.id` (id prefixes 80/81/82 repeat across files).
- Pipe-escaping (`\|`) and `<br>`-joined ordered fix steps for valid markdown tables.
- Aggregate Summary surfaces realism honestly: **40/51 cascade, 40/51 hidden root
  cause, 15 distinct failure classes** — no fabricated citations.
- Source shown verbatim (incl. "Synthetic simple incident (...)").

## Run
```
$ python3 experiments/ralph_outputs/F9/artifacts/gen_incident_catalog.py
Parsed 51 incident specs from .../scenarios/cidg/generated
Wrote markdown catalog: .../incident_catalog.md
Wrote JSON index:       .../incident_catalog.json
```

## Shared-core safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, or any other
task's directory. The generator only *reads* `scenarios/cidg/generated/`.
