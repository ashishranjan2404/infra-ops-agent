# A9 — 06 Implementation

## What I built (real artifacts, all under `experiments/ralph_outputs/A9/artifacts/`)

### 1. `mttr_labels.csv` — the labels (source of truth)
51 rows (one per scenario YAML in `scenarios/cidg/generated/`), 9 columns:
`incident_id, yaml_file, title, is_real_incident, mttr_minutes, mttr_basis,
source_citation, confidence, notes`.

- **30 real** incidents (dated public postmortems), **21 synthetic/benchmark/novel**.
- **18 real incidents carry a sourced MTTR** (minutes) with citation + confidence.
- **12 real incidents are marked `unknown`** (no reliable public MTTR, or
  date/signature conflation, or future-dated, or security-disclosure rather than a
  timed outage). MTTR was never invented.
- **21 synthetic rows** are `not_applicable`.

Representative documented labels (high confidence): Cloudflare WAF 2019-07-02 = 27m;
Knight Capital 2012 = 45m; Monzo 2019-07-29 = 99m; Fastly 2021-06-08 = 49m; AWS S3
2017-02-28 = 283m; Reddit Pi-Day 2023 = 314m; Facebook BGP 2021-10-04 = 373m; GitHub
2018-10-21 = 1451m; GitLab DB-deletion 2017 = ~1080m; Roblox 2021 = 4380m (73h).

### 2. `build_mttr_json.py` — validator + JSON renderer
`python3 build_mttr_json.py [--check]`. Reads the CSV, type-coerces, runs invariants
(unique ids, confidence enum, MTTR range, MTTR<->confidence linkage, not_applicable
=> not real), and writes `mttr_labels.json` with a `summary` block. `--check`
validates only and exits non-zero on any problem.

### 3. `mttr_labels.json` — generated sidecar (consumed by analysis)
`schema_version:1`, `summary{...}`, `incidents[...]` with unknown MTTR as JSON `null`.

### 4. `correlate_mttr.py` — correlation-analysis stub
stdlib-only Pearson + tie-averaged Spearman. Joins MTTR labels to a difficulty
signal: `--scores <json|csv>` (real pass@k / step-count when available) or, by
default, a **structural proxy** read directly from the YAML (node count +
3*cascade + 2*buried-gun) so it runs on repo assets alone. Drops unknown-MTTR rows and
prints every drop with a reason; requires >=2 paired points.

## Parallel-safety / race handling
Other Ralph workers were generating new YAMLs *during* this task (A5 added the 80-89
real-incident set; A11 added `a11-pair-*` synthetic minimal pairs). I detected the new
files via the id<->YAML cross-check and labelled all of them too, reaching 51/51
coverage. No shared core files were edited. If still more YAMLs land after this run,
re-running `build_mttr_json.py --check` will flag the gap (see 09).

## Files NOT touched
No edits to `rex/*`, `sim/*`, `agent/*`, existing YAMLs, `registry.json`, or any other
task's directory.
