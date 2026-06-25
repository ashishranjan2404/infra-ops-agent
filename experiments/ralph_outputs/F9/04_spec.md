# 04 — Technical Spec

## Inputs
- Source dir: `scenarios/cidg/generated/*.yaml` (CIDG ground-truth specs).
- Relevant YAML schema (subset used):
  ```yaml
  meta: {id, title, source, urls[], failure_class, clouds[]}
  topology: {nodes[], edges[]}
  root_cause: {location, kind, severity, hidden, persistent, reset_by[]}
  canonical_fix: {ordering_notes, steps[{tool, args{target, ...}}]}
  assertions: {cascades, loudest_alert_not_cause, fix_resolves, ...}
  ```

## Outputs
- `incident_catalog.md` — supplementary markdown: header, Summary, Full catalog
  table, Per-incident detail blocks.
- `incident_catalog.json` — list of row dicts (machine-readable index).

## Data structure (one row)
```python
{
  "file": str,                 # YAML filename (stable sort + dedup key)
  "id": str,                   # meta.id (fallback path.stem)
  "title": str,
  "failure_class": str,
  "source": str,
  "urls": list[str],
  "root_cause": str,           # "<kind> @ <location> (sev <s>) [hidden]"
  "root_cause_kind": str,
  "root_cause_location": str,
  "root_cause_hidden": bool,
  "fix": str,                  # "1. `tool` → target (k=v) <br> 2. ..."
  "fix_ordering_notes": str,
  "cascades": bool,
  "n_nodes": int,
}
```

## Function signatures
```python
def _fmt_fix_steps(canonical_fix: dict) -> str
def extract(spec: dict, path: Path) -> dict
def collect(src: Path) -> list[dict]          # parses + skips bad files with warning
def render_md(rows: list[dict], src: Path) -> str
def main(argv=None) -> int                     # CLI: --src --out-md --out-json
```

## CLI contract
- Defaults resolve from `__file__` (repo root = parents[4]); runnable from anywhere.
- Exit codes: 0 ok; 1 no specs parsed; 2 src dir missing.
- Deterministic: files processed in `sorted()` order.

## Test cases (`test_catalog.py`, stdlib only)
1. `test_extract_minimal` — full spec → all fields populated, fix string ordered.
2. `test_extract_missing_keys` — `{}` spec → no crash, fix == "(none)".
3. `test_real_yamls_all_parse` — collect() over real dir → >=33 rows, each has id + "@".
4. `test_generated_outputs_consistent` — every JSON id appears in the MD; count header matches.

## Failure handling
- Per-file try/except in `collect()`: malformed YAML is logged to stderr and skipped,
  run continues. `extract()` never raises on missing keys (all `.get()` with defaults).
