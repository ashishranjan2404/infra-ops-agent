# I5 — 09 Critique (honest)

## What a reviewer attacks

1. **`G = Corr·Std` is a heuristic, not a sample-efficiency bound.** This is the biggest
   weakness. There is no theorem here linking `G` to gradient variance or to PAC sample
   complexity. I label it a proxy and validate direction-of-effect empirically, but a
   skeptical AAAI reviewer can still say "you defined a quantity and showed it moves; so
   what?" A real contribution would derive `G` from the REINFORCE/GRPO gradient estimator
   variance under group normalization. I did not do that derivation.

2. **The learning curve is partly tautological.** `θ` is updated *by* `G`, so "higher G ⇒
   faster to target" is built in. The 1.17x speedup is therefore illustrative, not
   evidence. I say so, but it weakens the headline.

3. **The world model is clean to the point of being friendly.** `q ~ Beta(2,2)`,
   gaussian SME noise, a single scalar `eps` for SME error. Real SME error is structured
   (correlated with hard cases, systematically over/under-confident), and real verifiers
   have *false positives* (reward hacking), which I don't model. The crossover would shift
   and possibly distort under those.

4. **`c_S(eps)` in the proposition is stated approximately, not derived in closed form.**
   I assert `c_S = (1−2eps_eff)·κ` decreasing in eps; I verify the *consequence*
   (monotone, sign-changing `delta_G`) numerically but do not pin `eps*` analytically. The
   proposition is therefore "semi-formal": rigorous in structure, empirical in the exact
   threshold.

5. **No connection to the actual REx/opensre pipeline.** This is a standalone abstraction.
   I did not plug it into `rex/scoring.py` or the real CIDG scenarios, so the claim that
   the flat-reward pathology it models is *the* one REx suffers is asserted, not measured.

## What's weak / missing
- No variance-reduction or PAC bound (the thing that would make it a paper).
- No false-positive-verifier (reward-hacking) term.
- Budget `p` is present but its *cost/benefit tradeoff* (label cost vs `delta_G`) is not
  optimized — I show `p=0` is a no-op but never answer "what `p` is worth it".
- Single random family; no sensitivity analysis over `K`, `verifier_threshold`, or the
  Beta shape.

## What is genuinely solid
- The **crossover is real and non-tautological**: `delta_G` changes sign as SME quality
  degrades, monotonically in both `eps` and `λ`, matching the corollaries. That is the one
  clean, defensible result.
- The no-op corollaries (λ=0, p=0) are exact and tested — the model degenerates correctly.
- Fully reproducible, numpy-only, seeded, no shared-core edits.

## Honest verdict
A **correct, well-scoped, reproducible toy model** that crisply answers "when does SME
feedback help RLVR?" with a falsifiable crossover — but it is a *proxy-level* result, not a
theorem, and it is not yet validated against the real REx reward signal. Completed
deliverable; the natural follow-up (derive `G` from gradient variance, and measure
`rho_V`/flatness on real CIDG groups) is flagged for the next task.
