# E9 — 03 Improved Plan

## What changed after the grill

| # | Critique (persona) | Decision | Rationale |
|---|---|---|---|
| 1 | Score BOTH arms on one metric vector (AAAI) | **Accepted (modified)** | Shared vector `{n_traj, label_coverage, within_group_spread, domain_match, floor_check}`, but `null` where undefinable (Fireball spread) — never a faked number. |
| 2 | Don't fake symmetric numbers (RLE) | **Accepted** | Fireball arm reports `status:blocked`, `domain_match:0`, spread `null`; brief forbids fabrication. |
| 3 | Verdict must not claim "beat a real number" on spread (AAAI) | **Accepted** | `verdict.caveat` states the spread comparison is vacuous on the Fireball side. |
| 4 | Positives end on canonical fix; negatives use real traps; graded (PSRE/RLE) | **Accepted** | Augmenter reads `canonical_fix.steps[0]` and `trap_actions` from each YAML; emits 1 positive + (trap, wrong-fix, empty) negatives. |
| 5 | Perturb surface form, seeded (DOL) | **Accepted** | Paraphrase table + read-only tool-order shuffle, all driven by a per-(scenario,variant) SHA1-seeded RNG → deterministic. |
| 6 | Low reasoning diversity is the synthetic arm's weakness (SMR/PSRE) | **Accepted into 09** | Logged as the headline limitation in the critique; verdict scoped to *seeding*, not final accuracy. |

## Rejected / deferred
- **Reject:** forcing a non-null SRE spread onto the Fireball arm — would be fabrication.
- **Defer:** measuring reasoning diversity quantitatively (e.g. tool-sequence entropy across
  positives). Worth doing but out of scope for one worker; noted as future work in 10.

## Final approach (unchanged in spirit, sharper in detail)
1. `synth_sre_augmenter.py`: YAML → gold extraction → 1 positive + 3 negatives per variant,
   N variants per scenario, seeded perturbations, reward via mirrored `rex/scoring.py` weights.
2. `compare_arms.py`: load augmented JSONL → score synthetic arm; score Fireball arm (blocked
   unless a real export is dropped at `--fireball-jsonl`) → emit verdict with explicit caveat.
3. Run over all 51 scenarios; validate self-test, floor check, spread > 0.
