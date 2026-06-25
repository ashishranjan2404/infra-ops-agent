# 01 — Plan (F9: Supplementary material — full incident catalog)

## Objective
Produce the paper's supplementary material: a complete, auto-generated catalog of
every CIDG incident spec, enumerating its key fields (id, title, root cause, fix,
source). The catalog must be *generated from the YAML ground truth*, not hand-typed,
so it stays in sync as specs are added.

## Approach
1. Enumerate `scenarios/cidg/generated/*.yaml` (the CIDG ground-truth specs).
2. Parse each with PyYAML; tolerate missing/extra keys.
3. Extract: `meta.id`, `meta.title`, `meta.failure_class`, `meta.source`,
   `meta.urls`, `root_cause.{location,kind,severity,hidden}`,
   `canonical_fix.{ordering_notes,steps[]}`, `assertions.cascades`, topology size.
4. Render two outputs:
   - `incident_catalog.md` — supplementary markdown (summary stats + full table +
     per-incident detail blocks).
   - `incident_catalog.json` — machine-readable index for diffing / regeneration.
5. Ship a no-dependency test verifying every real YAML parses and every id round-trips
   into the markdown.

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/F9/artifacts/gen_incident_catalog.py` (generator)
- `experiments/ralph_outputs/F9/artifacts/test_catalog.py` (tests)
- `experiments/ralph_outputs/F9/artifacts/incident_catalog.md` (generated)
- `experiments/ralph_outputs/F9/artifacts/incident_catalog.json` (generated)

## Dependencies
- Python 3.13, PyYAML (already installed, 6.0.3). No network, no cluster, no LLM.

## Risks
- Schema drift across YAMLs (some specs may omit `urls`, `assertions`, etc.) →
  mitigate with defensive `.get()` extraction.
- Markdown pipe-escaping for titles/sources containing `|`.
- Duplicate ids across files (e.g. two `80-*`, `81-*`, `82-*`) → key on filename, not id.

## Success criteria
- Generator runs clean over all ~33+ specs (actual: 51 files).
- Every incident appears in both MD and JSON.
- Tests pass.
- No shared core file edited.
