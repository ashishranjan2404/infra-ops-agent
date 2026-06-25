# E8 — 09 Critique (honest)

## What a reviewer will attack
1. **The headline question is unanswered.** "1k? 10k? 50k?" has no number, because the
   Fireball corpus is 319 records and no fireball-trained model / source corpus is in repo.
   I deliver a harness + power-analysis N + blocker, not a scaling curve. A harsh reviewer
   calls this "infrastructure, not a result." Fair — but the alternative (a curve fit to
   319 real + ~50k imaginary points) would be fabrication, which the brief forbids.

2. **Power N answers a *different* N.** `required_n_for_effect` gives the **eval-rollout**
   budget to detect a reward gap, not the **training-trajectory** count. They are linked
   (you can't detect a small data-efficiency gap without enough eval rollouts) but they are
   not the same quantity. I separated them in 05/08, but a skim reader could conflate them.

3. **sd=0.22 is borrowed.** It comes from a HUD eval of *frozen* models
   (`opensre-traj/DATA.md`), not from policies trained on N-sized subsets. The true
   per-policy reward sd at small N is likely *higher* (noisier), so 304 eval rollouts/arm is
   a floor, not a ceiling. Labelled as an estimate, but still a soft spot.

4. **Nesting is approximate.** Largest-remainder apportionment shifts a stratum's quota by
   ±1 across N, so subset(N1)⊄subset(N2) exactly. I assert >0.8 overlap, not 100%. For
   strict rollout reuse this matters; documented, not hidden.

5. **The curve fitter is unvalidated on real data.** It's tested on synthetic points only;
   its grid is coarse (no CI on a,b,c) and the demo knee was 56M — which I use to *argue*
   the data is insufficient, but a careless user could mis-fit a real-looking curve. Gated
   to ≥4 points and never written to result.json, but it ships untested-on-real.

## What's genuinely solid
- The subsetter is deterministic, stratified, and strata-preserving (tested <0.05 dev).
- The anti-fabrication gates are real and tested: no curve without a real fit callback.
- The blocker is concretely demonstrated (every requested N caps at 319), not just asserted.
- Zero shared-core edits; the fit-callback seam is pre-defined for a future PR.

## What's missing / future work
- A real `FitCallback` wiring subset→train→eval (needs shared-core edits + the Fireball
  data + compute). Until then the training curve stays blocked.
- A bootstrap CI on the curve fit, and an SD measured from actual small-N training runs.
- Generation path to lift the corpus above 319 (re-run `opensre-traj/generate.py --n …`)
  if synthetic Fireball data at volume is acceptable — but that conflates "synthetic data
  scaling" with "real Fireball data needed," so it was out of scope here.
