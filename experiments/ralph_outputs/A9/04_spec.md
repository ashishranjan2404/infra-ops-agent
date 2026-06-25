# A9 — 04 Spec

## File: `artifacts/mttr_labels.csv` (source of truth)
Header (exact order, validated):
```
incident_id,yaml_file,title,is_real_incident,mttr_minutes,mttr_basis,source_citation,confidence,notes
```
Field contracts:
- `incident_id` (str, unique): equals `meta.id` in the scenario YAML.
- `yaml_file` (str): filename under `scenarios/cidg/generated/`.
- `title` (str): `meta.title`.
- `is_real_incident` (bool): true iff derived from a dated public postmortem.
- `mttr_minutes` (float|""): real-world resolution time in minutes; "" => unknown/NA.
- `mttr_basis` (enum): documented | approximate | unknown | synthetic |
  novel_synthetic | benchmark_synthetic.
- `source_citation` (str): org + report name + URL (or "none").
- `confidence` (enum): high | medium | low | unknown | not_applicable.
- `notes` (str): MTTR definition caveat / sourcing reasoning.

## File: `artifacts/build_mttr_json.py`
```python
load_rows() -> list[dict]            # reads CSV, asserts header == EXPECTED_COLS
to_records(rows) -> list[dict]       # typed: bool, float|None
validate(records) -> list[str]       # invariants, returns error list
summarize(records) -> dict           # counts + coverage_of_real_pct
main()                               # --check validates only; else writes JSON
```
Invariants enforced by `validate`:
- unique non-empty `incident_id`.
- `confidence ∈ VALID_CONFIDENCE`.
- `mttr_minutes` in (0, 100000] when present.
- present MTTR => confidence ∉ {unknown, not_applicable}.
- confidence == not_applicable => is_real_incident == false.

JSON output schema (`mttr_labels.json`):
```json
{"schema_version":1,"task":"A9-mttr-labels","description":"...",
 "summary":{"total_incidents":int,"real_incidents":int,"synthetic_incidents":int,
            "mttr_labeled":int,"real_but_unknown_mttr":int,"coverage_of_real_pct":float},
 "incidents":[{...row with mttr_minutes:float|null...}]}
```

## File: `artifacts/correlate_mttr.py`
```python
pearson(xs, ys) -> float|None
spearman(xs, ys) -> float|None       # via tie-averaged ranks
load_scores(path) -> dict[str,float] # json or csv(incident_id,score)
structural_proxy(id, yaml_file) -> int|None   # nodes + 3*cascade + 2*buried
main()  # --labels, --scores; joins, drops unknown-MTTR, prints r + per-incident
```
Behavior: only incidents with known `mttr_minutes` enter the correlation; all drops
are printed with a reason. Needs >=2 paired points or it reports "not enough".

## Test cases
- T1: `build_mttr_json.py --check` exits 0, summary has total_incidents == #YAMLs.
- T2: corrupt a confidence value -> validator exits 1 with a specific message.
- T3: every `incident_id` in CSV exists as a `meta.id` in the YAMLs (no typos).
- T4: `correlate_mttr.py` runs with no `--scores` and reports paired==#known-MTTR.
- T5: JSON unknown MTTR serializes as `null` (not 0, not "").
