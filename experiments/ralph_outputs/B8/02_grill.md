# 02 — Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**AAAI** (AAAI Reviewer), **RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial takes
- **SMR:** Right instinct. But be precise: `pass@1` is a Bernoulli proportion, so Cohen's
  *h* (arcsine) is correct; Cohen's *d* belongs on the continuous mean-reward. Don't
  conflate them. Also report sample sizes — h/d alone hide power.
- **PSRE:** I care whether the lift survives at the incident level, not the pooled blob.
  A pooled n=126 d=1.7 can be one family carrying everything. Want a per-family breakdown.
- **AAAI:** Effect size without a CI is half a result. d=1.5 on n=126 is real, but the
  paper still needs to say so. And state the baseline explicitly — h is asymmetric near 1.
- **RLE:** The reward values are bounded [0,1] and clumpy (0.0, 0.25, 0.55...). Pooled SD
  assumes roughly comparable spread; rex std (0.17) vs zero_shot std (0.38) are unequal.
  Cohen's d with pooled SD is then slightly optimistic — Glass's Δ (base SD only) is safer.
- **DVO:** Make it a one-command CLI that eats our existing JSON and never touches core.
  If it needs me to hand-edit a results file it's dead on arrival.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that h fully closes the issue. h fixes the *near-boundary*
  distortion but it's still a point estimate. The honest headline is h *plus* the n. SMR's
  "just use h" understates the unequal-variance problem on the d side.
- **SMR → RLE:** Pushing back. Glass's Δ throws away the treatment group's information and
  is noisier; for an *effect-size summary* (not a hypothesis test) pooled-SD d is the
  conventional, reproducible choice. I'll *report* both SDs so the reader can see the
  inequality, but the headline stays Cohen's d. Switching estimators to chase the variance
  ratio is over-engineering for B8's scope.
- **AAAI → PSRE:** Agree the per-family cut matters scientifically, but disagree it belongs
  in B8. B8's deliverable is *the effect-size machinery + numbers on claimed lifts*. The
  claimed lifts in the JSONs are the **overall** lifts. Per-family is a separate slice
  (that's A-series work). Scope-creeping B8 into a full breakdown weakens the deliverable.
- **PSRE → AAAI:** Fine, but then the SUMMARY must *say* "overall, not per-family" so nobody
  over-reads a pooled d. I'll concede scope if the caveat is loud.
- **DVO → SMR/RLE:** I don't care which estimator wins the theology war as long as the tool
  is deterministic and self-tested. Add `--selftest` so CI can prove the math.

## Round 3 — synthesis
Consensus:
1. **h for proportions, d for means** — keep both, report side by side (SMR, accepted).
2. **Pooled-SD Cohen's d as headline, but print both group SDs** so the unequal-variance
   concern (RLE) is visible without changing estimator — rejected Glass's Δ swap as
   over-engineering for scope.
3. **Overall lifts only in B8**, with an explicit "not per-family" caveat in SUMMARY
   (AAAI/PSRE) — per-family deferred.
4. **State baseline + n on every row** (AAAI/SMR) and ship a `--selftest` (DVO).
5. CIs on the effect sizes themselves are noted as a known limitation (09), not built —
   the source JSONs already carry Wilson CIs on pass@1.
