# I5 — 01 Plan

## Objective
Formalize the relationship between **SME (subject-matter-expert) override feedback** and
**RLVR (RL from Verifiable Rewards)**. Treat SME feedback as a signal that *reshapes the
reward/advantage*, and derive conditions under which it improves **sample efficiency**
versus RLVR alone. Deliver: assumptions, a proposition, and a small runnable simulation.

## Why this matters (SRE-Degrees context)
In the REx / opensre setting the verifier is cheap but **coarse**: a binary "incident
resolved?" check collapses many distinct remediation trajectories to the same reward.
This is the well-known *flat-reward / no within-group spread* pathology that starves
GRPO-style advantage estimation. An on-call SME can supply denser ordinal judgments
("plan B was closer than plan A even though both failed the check"), but SME time is
scarce and SMEs are sometimes wrong. We want a principled answer to: **when is it worth
spending SME labels, and how much should we trust them?**

## Approach
1. Abstract one RLVR optimization step as a **grouped bandit**: prompt → K candidate
   trajectories, each with a latent true value `q(tau)`.
2. Model the verifier as a **coarse binary** reward `r_V` with limited correlation `rho_V`
   to `q`.
3. Model SME feedback as a **dense ordinal** signal `s_hat` ≈ `q` + noise, corrupted by an
   **override error rate `eps`** (SME occasionally inverts the right answer), available
   only for a labeling-budget fraction `p` of groups.
4. Combine into a reshaped reward `r = (1-λ) r_V + λ s_hat` on labeled groups.
5. Define a **useful-gradient proxy** `G = Corr(A, q_centered) · Std(A)` where `A` is the
   group-centered advantage. This captures both *alignment* (does the advantage point at
   truth?) and *magnitude* (is there spread to learn from?).
6. State a **proposition**: SME helps iff the alignment gain outweighs the magnitude
   change — concretely, iff `eps` is below a crossover that depends on `rho_V` and `λ`.
7. **Simulate**: numpy world, compute G for RLVR-only vs RLVR+SME, a toy learning curve
   (steps-to-target), and a `(λ × eps)` sweep showing the crossover. Run it.

## Files to create (all task-namespaced — NO shared-core edits)
- `artifacts/sme_rlvr_model.py` — model + simulation (numpy only).
- `artifacts/test_sme_rlvr_model.py` — invariant + proposition tests.
- `artifacts/sim_results.json` — captured run output.
- `01..10` step docs + `SUMMARY.md` + `result.json`.

## Dependencies
- Python 3.13, numpy 2.x (present). No GPU, no network, no shared imports.

## Risks
- **Toy-model risk**: the abstraction may be too clean to be convincing to a reviewer.
  Mitigate by being explicit about assumptions and showing a *crossover* (not just a win).
- **Metric risk**: `G` is a proxy, not a true sample-efficiency bound. Mitigate with a
  learning-curve sim and honest framing in `09_critique.md`.
- **Over-claiming**: must show SME can *hurt* (high eps) to be credible.

## Success criteria
- A stated proposition with explicit assumptions and a derived crossover condition.
- A runnable sim that (a) shows SME helps for good SMEs, (b) shows it hurts for bad SMEs,
  (c) reproduces the crossover in a sweep.
- Tests pass, including a zero-budget/zero-λ no-op check and the bad-SME-hurts check.
