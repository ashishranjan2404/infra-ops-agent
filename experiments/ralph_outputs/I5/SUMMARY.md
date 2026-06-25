# I5 — SUMMARY: When does SME feedback help RLVR?

## Question
Formalize SME (subject-matter-expert) override feedback as a signal that reshapes the
RLVR reward/advantage, and derive when it improves sample efficiency vs RLVR alone.

## The model (one paragraph)
Abstract one RLVR step as a grouped bandit: prompt -> K candidates with latent true value
`q`. The verifier gives a coarse binary reward `r_V` correlated with `q` only through
`rho_V<1` (the flat-reward pathology). An SME supplies, for a budget fraction `p` of
groups, a dense ordinal signal `s_hat ~= q + noise` that is inverted with override-error
probability `eps`. Reshape: `r = (1-lam)r_V + lam s_hat` on labeled groups; the learning
signal is the group-centered advantage `A`. Sample efficiency is proxied by
`G = Corr(A, q_c) * Std(A)` (alignment x spread).

## Proposition
SME feedback helps (`delta_G>0`) iff the SME's correlation with truth exceeds the
verifier's (`c_S(eps) > rho_V`). There is a crossover override rate `eps*`: below it the
SME helps and help grows with trust lam; above it the SME hurts and harm grows with lam
(bang-bang optimal trust). No-op corollaries: `lam=0` or `p=0` => no effect.

## Result (real run, seed 0, numpy 2.4.5)
- Good SME (eps=0.10, lam=0.5): alignment 0.281->0.318, delta_G=+0.0026, helps.
- Crossover sweep delta_G over (eps x lam): positive for eps<=0.10, flips sign between
  eps=0.10 and 0.25, negative and growing for eps>=0.25 - monotone in both eps and lam,
  matching the corollaries. This sign-change is the load-bearing evidence.
- Learning curve: 1.17x fewer steps-to-target (illustrative only, not independent proof).
- Tests: 8/8 pass (pytest + script); output deterministic across runs.

## Artifacts
- artifacts/sme_rlvr_model.py — model + simulation (numpy-only, CLI, seeded).
- artifacts/test_sme_rlvr_model.py — 8 invariant/proposition tests.
- artifacts/sim_results.json — captured run output.

## Honest scope
G is a proxy, not a variance/PAC bound; the world model is clean (single scalar SME error,
no verifier false positives); not yet validated against real CIDG reward flatness. The
crossover itself is solid and reproducible. No shared-core files were edited.
