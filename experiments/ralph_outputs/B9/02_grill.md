# B9 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take
- **SMR:** A bootstrap on n=15 binary outcomes is mostly theater unless you respect the
  design. The data is 5 incidents × 3 seeds. The seeds within an incident are near-
  deterministic replicates — look at the rex row, it's 3/3 or 0/3 per incident. The
  *effective* sample size is ~5, not 15. A vanilla bootstrap will quietly pretend n=15.
- **PSRE:** From an ops view I don't care about CI width, I care: "does REx actually beat
  baseline on incidents I'd be paged for?" If the interval includes the baseline, the
  claim is dead regardless of which CI you pick.
- **REV:** If you submit Wilson AND a bootstrap that mostly agrees, a reviewer asks "why
  show two intervals that say the same thing?" The bootstrap only earns its place if it
  reveals something Wilson hides. Otherwise cut it.
- **RLE:** Make it reproducible — fixed RNG seed, 10k resamples, percentile method. And
  reuse the existing `wilson_ci` so we're not comparing against a re-derived formula.
- **DVO:** Stdlib only. No numpy in the critical path or it won't run in every worker env.
  And write the results to a JSON artifact, not just stdout.

## Round 2 — react to another persona BY NAME (forced disagreement)
- **SMR → REV:** I disagree with REV's "cut it if it agrees." The *point* of a robustness
  check is to test whether Wilson holds. If the cluster bootstrap diverges (and on this
  clustered data it will), that's the headline finding, not redundancy. Agreement would
  also be a result: "Wilson is fine here." You don't cut a control because it passed.
- **REV → SMR:** Fine, but then you MUST run the cluster bootstrap, not just the i.i.d.
  one. An i.i.d. bootstrap on clustered data is wrong in the *same direction* as Wilson,
  so showing it alongside Wilson is the redundancy I'm attacking. Show the cluster one or
  you've proven nothing.
- **PSRE → RLE:** RLE is worried about RNG hygiene; I'm worried we're polishing a CI on 5
  incidents and calling it science. The honest sentence is "n is tiny, here's the
  interval, don't oversell." Reproducibility of a fragile number is still a fragile number.
- **RLE → DVO:** Disagree that stdlib-only is just convenience — it's correctness
  insurance. numpy's `percentile` has multiple interpolation modes; if a reviewer reruns
  with a different default they get different bounds. A hand-written linear-interp
  percentile that we test is *more* defensible here.
- **DVO → PSRE:** PSRE says the number is fragile so why bother — but the deliverable is
  exactly to quantify that fragility. The cluster bootstrap's blown-up interval IS the
  ops-relevant message: "we don't have enough distinct incidents to make a tight claim."

## Round 3 — synthesis
Consensus reached:
1. Run **both** an i.i.d. percentile bootstrap **and** a cluster (block) bootstrap that
   resamples whole incidents. The cluster one is the real robustness test (SMR+REV).
2. The bootstrap earns its keep by exposing the divergence on clustered conditions
   (rex), not by agreeing on the degenerate 0/15 conditions (REV satisfied).
3. Stdlib only, fixed seed, 10k resamples, hand-written tested percentile (RLE+DVO).
4. Reuse shipped `wilson_ci`/`binary_pass`; assert point estimates match (RLE).
5. Lead the writeup with the honesty caveat: n≈5 effective; report, don't oversell
   (PSRE). Frame the wide cluster CI as the ops-actionable finding (DVO).
