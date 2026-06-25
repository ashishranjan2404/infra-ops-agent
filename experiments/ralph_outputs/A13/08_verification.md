# A13 — Verification against success criteria

| Success criterion (from 01_plan.md) | Met? | Evidence |
|---|---|---|
| 3 new uniquely-named YAMLs, each 2 distinct independently-clearable faults | YES | `80/81/82-multi-*.yaml`; `test_two_distinct_fault_locations` passes (2 distinct locations each) |
| All 3 pass `python -m sim.spec validate` (0 errors) | YES | 07 §1: all `OK`; 07 §2: 51/51 suite valid |
| Each primary root_cause engine-valid (builds, cascades, primary fix clears it) | YES | `test_primary_runs_and_clears_in_unpatched_engine` passes |
| `test_multifault.py` passes under pytest | YES | 07 §3: 6 passed |
| No shared core file edited | YES | 07 §5: `diff -q` engine.py & spec.py vs snapshots → identical |
| (Stretch) mechanism is real, not a label | YES | `engine_multifault.patch` verified conjunctive on copy (07 §4) |

## Are outputs real, not placeholder?
- The 3 YAMLs are full, schema-valid specs with real topology, edges, two faults, two SLO victims,
  two smoking guns, traps, and two-step canonical fixes — not stubs. They load through the actual
  `sim.spec.load_spec` and validate with 0 errors.
- The test file runs the **real** `sim.engine.World` / `apply_action` / `is_resolved` and passes.
- The patch is a real unified diff that applies cleanly to copies of the actual core files and was
  executed to confirm the conjunctive-resolution behavior; it was deliberately NOT applied to the
  repo (no-edit rule).

## Spot checks
- `82` trap fidelity: in the unpatched engine, `apply_action(scale_deployment@conn-router)` does
  NOT clear fd_exhaust (scale_deployment ∉ REMEDIATION['fd_exhaust']); `restart_service` does. This
  preserves the "right-tool/wrong-fault" trap the suite is built around.
- Masking fidelity (`81`): secondary cache_flush smoking gun has `buried_under: 80` vs the primary's
  25, modeling that the cold-cache signature only surfaces once the loud bad rollout is rolled back.

Verdict: all stated success criteria met; deliverables are real and validated.
