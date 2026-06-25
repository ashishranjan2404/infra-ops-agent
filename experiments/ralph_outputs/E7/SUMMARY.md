# E7 — SUMMARY: Cross-Domain Transfer (game domains beyond D&D)

## Goal
Test transfer of REx-style diagnose-then-act policies to OTHER interactive game
domains (text adventures). Survey candidate datasets, design a domain-agnostic
trajectory adapter, write a transfer-experiment plan with a generic adapter +
unit test on a synthetic fixture.

## Delivered
- Survey: TextWorld, Jericho (Z-machine IF), ALFWorld (embodied text), + SRE/REx
  reference (01_plan).
- Domain-agnostic adapter artifacts/trajectory_adapter.py: one CanonicalTrajectory
  schema + registry of 4 pluggable adapters. to_sre_scoring_inputs() projects any
  episode into the exact kwargs of rex/scoring.deterministic_judge, so game
  trajectories are scorable by the existing SRE eval stack with zero core edits.
- Synthetic fixtures (artifacts/synthetic_fixtures.json): 1 episode per domain.
- Unit test (artifacts/test_trajectory_adapter.py): 12 cases, all PASS, incl. a
  real call into rex/scoring.py on an adapted TextWorld trajectory.
- Transfer plan (artifacts/TRANSFER_PLAN.md): H1/H0, 4 baseline conditions, 4
  metrics, 2 ablations, caveats, and a proposed un-applied rex/transfer_eval.py.

## Result
Plumbing + runnable transfer protocol verified (12/12 green, real judge import).
Transfer claim itself is honestly unproven & blocked: live run needs
textworld/jericho/alfworld installs + ROMs/network, unavailable in sandbox.
Scaffold delivered; numbers run documented as the blocker. No core files modified.

## 10-step files
01_plan 02_grill 03_improved_plan 04_spec 05_ouroboros 06_implementation
07_test_results 08_verification 09_critique 10_feedback
