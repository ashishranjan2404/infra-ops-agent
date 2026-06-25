# 01 — Plan (Task I7: Trap-action taxonomy)

## Objective
Create a taxonomy of trap actions (restart-trap, scale-trap, rollback-trap,
failover-trap), grounded in `rex/scoring.py` and the scenario YAMLs. Deliver a
structured taxonomy doc + a script that classifies each scenario's trap into the
taxonomy and reports counts per category. Run it. Be honest about skew.

## Approach
1. Read `rex/scoring.py` to learn how a trap is *defined* (it's `(tool, target)`
   matched in `_traps_in()`, penalised `0.60` in `score_plan`) and what the
   `why`-table in `format_feedback` says about each trap tool.
2. Reuse G4's `trap_taxonomy.json` (already extracts per-scenario trap tools) as the
   input set; fall back to scanning YAMLs directly if absent.
3. Map trap *tool* → one of 4 named categories + an `other-trap` catch-all.
4. Write `classify_traps.py` (read-only), a self-test, and a taxonomy doc.
5. Run it, report counts, be honest about the scale-trap skew.

## Files to create (all task-namespaced, no shared edits)
- `artifacts/trap_taxonomy_doc.md` — the taxonomy
- `artifacts/classify_traps.py` — classifier
- `artifacts/test_classify_traps.py` — tests
- `artifacts/trap_classification.json` — generated output

## Dependencies
`pyyaml` (already in repo), stdlib only otherwise. No network, no LLM.

## Risks
- Distribution may be skewed (anticipated by the task) → report honestly.
- failover tools may not exist in the corpus → map them anyway, report 0 coverage.

## Success criteria
- 4 named categories defined and grounded in scoring.py + YAMLs.
- Script runs, emits counts per category, exit 0.
- Tests pass.
- Honest write-up of skew + empty categories.
