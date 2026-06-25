# I2 — 06 Implementation

## What I built (all task-namespaced; NO shared-core edits)
1. `artifacts/bimodality_sim.py` — derivation (module docstring) + simulation:
   - `score()` mirrors the exact `rex/scoring.py` arithmetic incl. `clamp(.,0,1)`.
   - `Population.draw()` — synthetic agent population with realistic coupling
     (resolution gated on having a real fix; traps almost always block resolution).
   - `resolved_eligible_subpop()` — the **competent / C-conditioned** law where
     only the `trap` flag varies → the clean two-atom distribution.
   - bimodality diagnostics: `is_bimodal` (primary valley test), `bimodality_
     coefficient` (Sarle's BC, secondary), `two_cluster_separation`, `histogram`.
   - a TRAP_PENALTY sweep across the `W_RESOLVED=0.45` threshold.
   - emits `bimodality_result.json` and asserts mirrored constants == source.
2. `artifacts/test_bimodality.py` — 5 pytest cases (arithmetic, threshold,
   two-atom structure, causal sweep, drift guard).
3. `artifacts/bimodality_result.json` — REAL emitted results (N=20000 per cell).

## The math, restated (full derivation in 04_spec.md)
Condition on competent C = {diag=fix=resolved=1}. Then R is two-valued:
- success atom = MAX_CLEAN = **1.0**
- trap basin atom = clamp(MAX_CLEAN − TRAP_PENALTY) = clamp(1.0 − 0.60) = **0.40**

Two atoms separated by Δ = min(TRAP_PENALTY, 1.0) = 0.60 → a bimodal law whenever
`0 < p_trap < 1`. The **resolved-reward-nullifying** threshold is exactly
`TRAP_PENALTY ≥ W_RESOLVED`: the basin (0.40) drops to/below the unresolved-clean
reference MAX_CLEAN−W_RESOLVED = 0.55. Shipped 0.60 > 0.45 → nullified (0.40<0.55).

## Key real results (from bimodality_result.json)
- `gap_condition_holds`: **true** (0.60 > 0.45).
- competent subpopulation `values_seen`: **[0.4, 1.0]**, `is_bimodal`: **true**,
  separation gap **0.6**, mass 34.8% basin / 65.2% success.
- sweep: `is_bimodal` flips on at tp≈0.2 (valley appears), and
  `resolved_reward_nullified` flips on at **tp=0.45 (==W_RESOLVED)** exactly.
- `valley_present_at_shipped_penalty`: **true**;
  `nullification_threshold_is_W_RESOLVED`: **true**;
  `shipped_penalty_nullifies_resolved`: **true**.

## Proposed change to shared core (NOT applied — documented only)
None required. The task is a *proof/analysis* of existing constants. If one wanted
to make the basin carry *degree* information (avoid the clamp-to-0 caveat), a
proposed (un-applied) tweak would be to floor the trap term instead of the total,
e.g. `score = clamp(base, 0, 1) − min(TRAP_PENALTY, base)` so it never clamps a
distinct basin into 0. This is left as a `.patch`-style note, intentionally not
written to `rex/scoring.py` per the real-artifact rules.
