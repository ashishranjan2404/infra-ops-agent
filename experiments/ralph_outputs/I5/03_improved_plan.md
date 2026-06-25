# I5 — 03 Improved Plan (post-grill)

## What changed vs 01_plan
1. **Advantage definition pinned (accepted RLE).** We reshape the *reward* and then
   recompute the group-centered advantage `A = r − mean_group(r)`. This is option (a); we
   do NOT add a separate SME advantage term. Stated up front to remove ambiguity.
2. **`G` relabeled a proxy (accepted AAAI + SMR).** `G = Corr(A, q_centered)·Std(A)` is
   explicitly a *first-order useful-gradient proxy*, not a theorem-grade bound. We back it
   with an empirical **learning-curve / steps-to-target** simulation so the central claim
   is validated, not asserted.
3. **Budget `p` kept but de-emphasized (PSRE/RLE compromise).** `p` stays a parameter
   (default 0.3) with an explicit `p=0` no-op test, but the **headline sweep is `λ × eps`**
   to give a legible crossover.
4. **Proposition must include a hurt-regime (accepted AAAI).** The proposition derives a
   crossover: SME helps only when `eps` is below a `λ`,`rho_V`-dependent threshold; above
   it, `delta_G < 0`. The sim and a test (`test_bad_sme_can_hurt`) enforce this.
5. **Determinism/CI (accepted DOL).** numpy-only, every entry-point seeded, results dumped
   to `sim_results.json`.

## Critiques accepted
- Couple alignment AND magnitude in the metric (SMR).
- Make `eps` (override error) a first-class crux variable (PSRE).
- Operationalize "helps" and force a falsifiable hurt-regime (AAAI).
- Pin the advantage semantics (RLE).
- Runnable + seeded + diffable (DOL).

## Critiques rejected (with reason)
- **AAAI's demand for a PAC/variance bound** — rejected as out of scope for a one-day,
  frozen-LLM artifact; replaced by the proxy-plus-learning-curve compromise SMR proposed.
  A formal bound would be a separate task and would not change the qualitative crossover.
- **RLE's "drop `p` entirely"** — rejected; the budget is the SRE-actionable lever
  (PSRE's point). Kept as a parameter with a no-op test instead of deleting it.

## Final deliverable shape
- `sme_rlvr_model.py`: `WorldParams`, `evaluate()`, `signal_quality()`,
  `reshaped_reward()`, `learning_curve()`, `sweep()`.
- `test_sme_rlvr_model.py`: 8 invariant/proposition tests.
- `sim_results.json`: captured numbers.
- Docs `04`/`05` carry the formal model; `07` carries the real run.
