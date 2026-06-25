# F9 — Summary: Supplementary Material (full incident catalog)

## Deliverable
An auto-generated supplementary catalog enumerating every CIDG incident spec with its
key fields (id, title, root cause, fix, source), produced by a runnable script that
reads the YAML ground truth.

## Artifacts (all under `experiments/ralph_outputs/F9/artifacts/`)
- `gen_incident_catalog.py` — generator: parses `scenarios/cidg/generated/*.yaml`,
  emits markdown + JSON. CLI flags, defensive extraction, deterministic, exit codes.
- `test_catalog.py` — 4 stdlib tests (incl. a real-corpus parse test). All PASS.
- `incident_catalog.md` — supplementary markdown (650 lines): Summary + 51-row table +
  51 per-incident detail blocks.
- `incident_catalog.json` — machine-readable index (51 rows) for diffing/CI.

## Results
- 51/51 incident specs parsed, 0 skipped.
- Aggregate: 40/51 cascade, 40/51 hidden root cause, 15 failure classes.
- Tests: 4/4 PASS, byte-compile OK, JSON valid.

## Honesty notes
The catalog truthfully reports the substrate is synthetic-heavy (40/51 are
"Synthetic simple incident (...)" with empty URLs) and severity is near-constant 0.7.
Strengthening real-postmortem grounding would require editing the source YAMLs — a
shared-core change deliberately not made (documented in 09/10).

## Shared-core safety
No shared core files edited; the generator only reads the scenarios dir. Status: completed.
