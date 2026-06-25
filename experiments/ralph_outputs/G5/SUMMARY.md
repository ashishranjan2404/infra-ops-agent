# G5 — SUMMARY

**Task:** Positioning matrix — us (SRE-Degrees / REx) vs SREGym vs Komodor vs Datadog Bits AI —
across open benchmark, trap-action safety, training method, deployment posture, evaluation rigor,
with honest, sourced claims.

## Deliverable
A 5-dimension x 4-column markdown positioning matrix with per-dimension prose, a category
disclaimer, an explicit "where we are honestly weaker" section, 11 dated/cited sources, and a
runnable validator enforcing citation hygiene + a vendor-marketing-flag guard.

## Artifacts (under experiments/ralph_outputs/G5/)
- artifacts/positioning_matrix.md — the matrix (primary deliverable)
- artifacts/sources.json — 11 sources S1-S11 (url/who/claim/verification/as_of)
- artifacts/validate_matrix.py — validator, main + --selftest (T1-T4), all passing

## Key honest findings
- We are a benchmark/data engine; Komodor + Datadog are deployed products; SREGym is a benchmark.
  The matrix compares posture, not a single ranking.
- We LOSE deployment posture (no prod, no customers) and TIE open-benchmark with SREGym (ahead on
  scale: 90 problems, 38.9-72.6% diagnosis).
- Our one defensible "first" claim: frozen policy emitting reward-shaped trajectories with a
  quantified -0.60 trap penalty — none of the other three publicly do this.
- Eval rigor split honestly: we lead on WHAT is graded (root cause + trap, not "came back up");
  SREGym leads on HOW MUCH (larger n, external benchmark). Not head-to-head.
- Vendor numbers (Komodor 95%/40%/80%, Datadog 2,000+ envs, "2x faster") are real but
  vendor-stated and flagged unverified.

## Validation
python3 validate_matrix.py -> EXIT 0. --selftest -> T1-T4 all PASS. sources.json parses.

## Shared-core safety
No shared core file edited. ARCHITECTURE.md read-only. All outputs namespaced under G5/.

## Status: completed
