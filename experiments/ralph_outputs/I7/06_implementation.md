# 06 — Implementation

## Artifacts created (all under `experiments/ralph_outputs/I7/artifacts/`)
- `classify_traps.py` — read-only classifier. Reuses G4's `trap_taxonomy.json` as the
  input record set (falls back to a direct YAML scan of
  `scenarios/cidg/generated/*.yaml` if G4 is absent). Maps each scenario's trap
  *tool* → one of `scale-trap | restart-trap | rollback-trap | failover-trap`, with
  an `other-trap` catch-all. Emits `trap_classification.json` and an ASCII bar chart.
- `test_classify_traps.py` — 4 tests (tool mapping, unknown→other, real-repo build
  invariants, skew reporting). Runs under pytest or standalone.
- `trap_taxonomy_doc.md` — the structured taxonomy: 4 families with mechanism, trap
  tools, gold-fix contrast, grounding in `rex/scoring.py`, the measured distribution
  table, and an honest assessment of the skew.
- `trap_classification.json` — generated output (committed for inspection).

## Grounding (no shared files edited)
- Trap *definition*: `rex/scoring.py::_traps_in()` matches applied actions against a
  scenario's `trap_actions` on `(tool, target)`; `score_plan` subtracts a flat
  `TRAP_PENALTY = 0.60`. → tool is the classification axis.
- Per-trap rationale: reused from the `why`-table inside
  `rex/scoring.py::format_feedback` (scale / restart / clear_cache explanations).
- Per-scenario trap data: `scenarios/cidg/generated/*.yaml` `trap_actions:` blocks,
  via G4's already-extracted `trap_taxonomy.json`.

## Did NOT touch
`rex/*.py`, `sim/*.py`, scenario YAMLs, ralph_status, dashboard, other task dirs.
Any future scoring change (e.g. severity-weighted penalties) is left as a doc
suggestion, not a patch.
