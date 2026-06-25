# I2 — 01 Plan

## Objective
Prove (theoretically, then demonstrate numerically) that in `rex/scoring.py` the
trap penalty being larger than the resolved reward induces a **bimodal** reward
distribution. State the exact condition on the constants and back it with a
runnable simulation on simulated reward draws.

## Grounding (rex/scoring.py)
```
W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60
score = W_ROOT*diag + W_FIX*fix + W_RESOLVED*resolved   (- TRAP_PENALTY if trap)
score = clamp(score, 0.0, 1.0)
```
- `diag ∈ {0,1}` (deterministic keyword judge), `fix ∈ {0, 0.5, 1.0}`,
  `resolved ∈ {0,1}`, `trap` boolean.
- A single boolean `trap` subtracts a large constant, then the score is clamped.

## Claim to prove
Under what condition does `TRAP_PENALTY > W_RESOLVED` induce bimodality?
- The clean (no-trap) optimum is `MAX_CLEAN = W_ROOT+W_FIX+W_RESOLVED = 1.0`.
- A trapped-but-otherwise-competent plan scores `clamp(MAX_CLEAN - TRAP_PENALTY)`.
- These two reward atoms are separated by `TRAP_PENALTY`. The *economically*
  meaningful separation — where a trapped, resolved plan scores **no better than
  an unresolved one** — is exactly `TRAP_PENALTY > W_RESOLVED`.

## Approach
1. Derive the two-atom (success peak / trap basin) structure analytically.
2. Build a synthetic agent population (Bernoulli diag/fix/resolved + trap rate),
   compute rewards with the exact `score` arithmetic.
3. Measure bimodality (largest-gap valley test, Sarle BC, two-cluster split).
4. Sweep `TRAP_PENALTY` across the threshold `W_RESOLVED=0.45` to show causality.
5. Unit-test the arithmetic and the threshold.

## Files to create (task-namespaced, no shared-core edits)
- `artifacts/bimodality_sim.py` — derivation in docstring + simulation + sweep.
- `artifacts/test_bimodality.py` — pytest validating arithmetic + threshold.
- `artifacts/bimodality_result.json` — emitted real results.

## Dependencies
Pure stdlib (`random`, `statistics`, `math`, `json`). Python 3.13. No network.

## Risks
- The FULL mixed population is multi-modal (partial-credit plans fill the middle),
  not a clean 2-mode law — must isolate the competent subpopulation for the clean
  theorem and report the full population honestly.
- "Bimodal" needs an operational definition (valley width + mass on both sides).

## Success criteria
- Math states the exact condition and matches the shipped constants (0.60 > 0.45).
- Simulation runs, emits JSON, shows a valley for tp > W_RESOLVED and confirms the
  nullification threshold == W_RESOLVED exactly.
- Tests pass.
