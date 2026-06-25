# I5 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the metric is gameable"
**Finds:** `G = Corr·Std` can be inflated by magnitude alone. If SME blending merely adds
*spread* without alignment, `Std(A)` rises and `G` can go up even when the SME is useless,
producing a false "helps". This would make the proposition's crossover spurious.
**Severity:** high.
**Fix:** the sweep must show `delta_G` going *negative* as `eps` grows (it does:
eps≥0.25 rows are all negative). Also added `test_bad_sme_can_hurt`. The negative regime
proves magnitude alone does not rescue a bad SME — alignment is doing the work. Documented
the proxy caveat in `04_spec §1.5` and `09_critique`.

## Engineer B — "the learning-curve sim is a tautology"
**Finds:** `learning_curve()` updates `theta ← theta + lr·G·(1−θ)`. Since `theta` is driven
*by* `G`, of course higher-`G` (SME) reaches target faster — the steps-to-target result is
baked in, not evidence. Also `final_value` saturates at 1.0 for both, so the curve only
distinguishes via the early steps; with the default good-SME params the gap is tiny
(7 vs 6 steps).
**Severity:** medium-high.
**Fix:** reframed honestly: the learning curve is an *illustration that `G` maps
monotonically to steps-to-target under a standard diminishing-returns update*, NOT
independent proof. The real evidence is the **sweep crossover** (sign change of `delta_G`),
which is not tautological. Said so explicitly in `08`/`09`. Did not overclaim the 1.17x.

## Engineer C — "edge cases & determinism"
**Finds:** (1) `_safe_corr` divides by std — if a group's reward is constant, `Std=0` and a
naive corr is NaN; need the guard (present, returns 0). (2) `p_label` rounding: small `N`
with tiny `p` could round to 0 labeled groups and silently behave like `p=0`; acceptable
but should be tested (covered by `test_zero_budget_is_noop` at `p=0`). (3) the per-step
`rng.integers(1<<30)` reseeding in `learning_curve` — verify it's deterministic given the
top seed (it is; derived from `wp.seed+777`). (4) `s_hat` min-max comment in code says
"min-max per group" but implementation only clips — comment is stale.
**Severity:** low-medium.
**Fix:** kept the std guard and NaN protection (tested by `test_flat_verifier_has_low_signal`).
Confirmed determinism by running twice and diffing (see `07`). Noted the stale comment as a
cosmetic cleanup; the behavior (clip to [0,1]) is correct and intended.

## Final filtered spec (deltas applied)
- Metric kept but **explicitly proxy**, validated by the **sign-change crossover** (not the
  learning curve, which is illustrative only).
- Hurt-regime is load-bearing evidence; tests enforce it.
- All numerical guards (zero-std, zero-budget, zero-λ) retained and tested.
- Determinism asserted by a double-run diff in `07_test_results.md`.
