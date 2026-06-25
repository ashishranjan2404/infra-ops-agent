# 06 — Implementation

## What I built (all under G4/artifacts/, no core files touched)

1. **`extract_trap_taxonomy.py`** — read-only extractor. Pulls trap-action labels from the 51
   `scenarios/cidg/generated/*.yaml`, and pulls `TRAP_PENALTY` / `W_*` weights and the per-
   trap `why` explanation table out of `rex/scoring.py` via `ast` (parsed, never imported —
   so no side effects and no edit to the core module). Emits `trap_taxonomy.json`.

2. **`trap_taxonomy.json`** — generated artifact. 51 records, one per scenario, each with
   `{scenario_id, file, failure_class, fault_node, trap{tool,target,replicas},
   contrasted_gold_fix, why_label}` plus top-level `trap_penalty=0.6`, weights summing to
   1.0, and the trap-tool distribution `{scale_deployment:48, restart_pod:1,
   rollback_deployment:1, restart_service:1}`.

3. **`test_extract_trap_taxonomy.py`** — 6 pytest cases validating the extractor against the
   real repo (constants, full coverage, modal tool, every trap contrasted with a real fix,
   why-table presence, JSON written to disk). All pass.

4. **`comparison_report.md`** — the G4 deliverable. Grounds our mechanism with file:line,
   summarizes SREGym / AIOpsLab / ITBench oracles and the Safe-RL precedent, gives a
   side-by-side table, states a *scoped* novelty claim, and lists honest limitations.

## Key grounded facts
- Trap mechanics live in `rex/scoring.py`: `_traps_in` (`:175-182`), penalty `−0.60`
  (`:22`, `:206-209`), per-trap `why` (`:243-252`), trap vs BLOCKED distinction (`:254-257`).
- Schema carrier: `Scenario.trap_actions` (`rex/harness.py:229`), built from
  `spec.trap_actions` (`:307-308`).
- Real data: 51/51 generated scenarios carry a trap; 48 are `scale_deployment`.

## Proposed core change (documented, NOT applied — per parallel-safety rules)
None required for this task. If we wanted to broaden the taxonomy, the change would be to
the YAML generator (`scenarios/cidg/...` generator) to emit more diverse `trap_actions` and
to extend the `why` table in `rex/scoring.py:243-252`. That is left as a proposal; no shared
file was edited.
