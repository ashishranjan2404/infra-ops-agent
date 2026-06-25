# I2 — 08 Verification

## Against the success criteria (from 01_plan.md)

| Criterion | Met? | Evidence |
|---|---|---|
| Math states the exact condition | YES | 04_spec.md §2: bimodal two-atom law on C; nullification iff `TRAP_PENALTY ≥ W_RESOLVED` |
| Matches shipped constants (0.60>0.45) | YES | `gap_condition_holds: true`; basin 0.40 < unresolved-clean ref 0.55 |
| Simulation runs + emits JSON | YES | exit 0; `bimodality_result.json` valid (JSON_OK) |
| Valley for tp > W_RESOLVED | YES | `valley_present_at_shipped_penalty: true` |
| Nullification threshold == W_RESOLVED | YES | `nullification_threshold_is_W_RESOLVED: true` (sweep flips at 0.45) |
| Tests pass | YES | 5 passed |
| No shared-core edits | YES | only files under `experiments/ralph_outputs/I2/artifacts/` written |

## Are outputs real (not placeholder)?
- `bimodality_result.json` is machine-emitted from a 20,000-draw simulation per
  cell — not hand-written. Re-running reproduces it (seeded RNG).
- The arithmetic is asserted equal to the live `rex/scoring.py` via
  `test_constants_match_source` (would fail if constants drifted).
- Numbers are internally consistent and hand-checkable:
  - success atom = W_ROOT+W_FIX+W_RESOLVED = 0.30+0.25+0.45 = **1.0** ✓
  - basin atom = clamp(1.0 − 0.60) = **0.40** ✓
  - unresolved-clean ref = 1.0 − 0.45 = **0.55**; 0.40 < 0.55 → nullified ✓
  - Δ = 0.60; with p_trap≈0.35 the two-atom mass split is ≈35/65, matching the
    emitted 34.8% / 65.2%.

## Honest scope note
- The *full mixed* population is multi-modal (partial-credit plans), NOT a clean
  2-mode law; we condition on the competent subpopulation for the headline claim
  and label the full population accordingly. This is stated, not hidden.
- A weak valley exists already at tp≈0.2; the *meaningful* threshold the task asks
  about — penalty dominating the resolved reward — is `tp > W_RESOLVED`, confirmed
  exactly. Both facts reported separately.

Verdict: **success criteria met**; deliverables real and reproducible.
