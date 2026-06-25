# D9 — 01 Plan

## Objective
Run curriculum learning (easy→hard ordering) over the CIDG incident set. Reuse
the A12 difficulty ordering, build a **curriculum-scheduled training config** and
a **curriculum-vs-random comparison harness**, under a ~15 min compute cap.

## Approach
1. Reuse `experiments/ralph_outputs/A12/artifacts/curriculum_order.json` (51
   incidents, non-decreasing static-structural difficulty 0.9 → 17.0). Do NOT
   recompute difficulty — A12 owns that signal.
2. `curriculum_schedule.py` — turn the order into a concrete training schedule:
   band the incidents into stages, progressive unlock + rehearsal weighting,
   and emit a GRPO-style `training_config.json` that a real RFT loop can consume.
   Provide three orderings (curriculum / random / anti) sharing one sample budget.
3. `curriculum_vs_random.py` — comparison harness. REAL gradient training is
   blocked (no GPU, frozen-LLM project), so run a transparent, deterministic
   **competence-vs-difficulty simulation** (Bengio 2009 / Graves 2017 ATPG style)
   to demonstrate the *mechanism* and give the real run a falsifiable hypothesis
   + reusable metric/plot code. Numbers explicitly labeled "simulated".
4. `test_curriculum_schedule.py` — pytest over schedule invariants + the harness.

## Files to create (all task-namespaced under D9/artifacts/)
- `curriculum_schedule.py`, `curriculum_vs_random.py`, `test_curriculum_schedule.py`
- emitted: `training_config.json`, `comparison.json`

## Dependencies
- A12 artifact (present, validated), stdlib only (json/math/statistics/random),
  pytest. No network, no model calls, no GPU.

## Risks
- Risk: simulation mistaken for measured model reward → mitigate with loud
  "SIMULATED" labels + a clean seam to swap in real eval.
- Risk: editing shared core → avoided; everything lives under D9/artifacts/.

## Success criteria
- Reuses A12 order; config + comparison are real, runnable, deterministic.
- Tests pass; curriculum ≥ random ≥ anti in the simulation (correct mechanism).
- Training blocker documented honestly.
