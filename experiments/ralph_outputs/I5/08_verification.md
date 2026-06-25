# I5 — 08 Verification

## Success criteria (from 01_plan) vs outcome

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Stated proposition with explicit assumptions | ✅ | `04_spec §2`: assumptions A1–A4, proposition with crossover `eps*`, corollaries C1–C3 |
| Derived crossover condition | ✅ | `c_S(eps) > rho_V` ⇒ helps; crossover override rate `eps*`; reproduced numerically in the sweep |
| Sim shows SME *helps* for good SME | ✅ | headline `delta_G=+0.00256`, `helps=True`; eps≤0.10 rows positive |
| Sim shows SME *hurts* for bad SME | ✅ | eps≥0.25 rows negative; `test_bad_sme_can_hurt` passes |
| Crossover reproduced in a sweep | ✅ | sign flip between eps=0.10 and eps=0.25 in `delta_G_grid` |
| Tests pass incl. zero-budget/zero-λ no-op | ✅ | 8/8 pytest; `test_zero_lambda_is_noop`, `test_zero_budget_is_noop` |
| Runnable, deterministic, diff-able | ✅ | double-run diff identical; JSON written to `sim_results.json` |

## Are the outputs real (not placeholder)?
Yes. Every number in `07` / `sim_results.json` is produced by executing
`sme_rlvr_model.py` on this machine (numpy 2.4.5, Python 3.13.7), seeded and reproduced
across two runs. The tests genuinely exercise the model (a deliberately bad SME makes a
test fail if the hurt-regime disappears).

## What the proposition concretely says (plain language)
SME override feedback improves RLVR sample efficiency **only when the SME's signal is more
correlated with ground truth than the verifier is** (`c_S(eps) > rho_V`). For a coarse
verifier this is an easy bar when the SME is reliable, but there is a hard **override-error
crossover `eps*`**: past it, blending in SME judgments *poisons* the advantage and you are
better off with RLVR alone. Trust (λ) is a multiplier on whichever side of the crossover
you are on — so the idealized optimal policy is bang-bang: fully trust a good SME, ignore a
bad one. The actionable SRE reading: page the expert only if you believe their override
accuracy clears the verifier's coarseness; otherwise the page is net-negative.

## Honest limitation flagged here (full detail in 09)
`G` is a proxy, and the learning-curve speedup (1.17x) is illustrative, not independent
proof. The load-bearing, non-tautological evidence is the **sign-change crossover** in the
sweep.
