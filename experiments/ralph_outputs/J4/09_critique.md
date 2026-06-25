# J4 — 09 Critique (honest)

## The headline weakness
**There is no real MTTR measurement here, only a validated way to measure it.**
The speedup numbers (1.5x within, 1.87x between) are artifacts of a simulation
where *I planted the effect myself*. They demonstrate the harness recovers a known
effect; they say NOTHING about whether a real agent helps a real on-call engineer.
A reviewer is right to discount every speedup figure as circular until fed real data.

## Where a reviewer attacks
1. **Simulation circularity.** The generator uses lognormal noise; the analysis
   assumes log-normality. Mitigated by nonparametric backups (Wilcoxon, Mann-
   Whitney, Cliff's delta, bootstrap) and a null negative-control, but the data-
   generating process still flatters the chosen test. Real MTTR may be bimodal
   (quick-fix vs deep-dive) — untested here.
2. **External validity of staged replays (the REV/DOL fight in `02`).** You can
   only run controlled A/B on *known, scripted* incidents — exactly where LLMs
   look best (the answer is in their training distribution / the runbook). Measured
   speedup on staged incidents will OVER-state production benefit on novel incidents.
   The `no_benefit_frac` knob gestures at this but cannot substitute for real novel data.
3. **n and power.** A9 gives only 18 real MTTR labels. Real human studies will be
   small (operators are expensive); the harness can run at n≈30–40 pairs, but
   that's underpowered for speedups below ~1.3x. `required_n_paired` makes this
   explicit but doesn't conjure operators.
4. **`resolved=False` not excluded.** Timed-out / abandoned attempts currently
   count at face value — could bias either arm. Field is captured; exclusion is a
   one-line follow-up, not done.
5. **MTTR segment mismatch.** A9 labels are *outage-level* customer-facing
   durations; the protocol wants *diagnosis-to-resolution* segments. Using A9 as
   the baseline distribution conflates scales — fine for exercising the math,
   wrong for a real baseline.
6. **Operator confound only modeled, not solved.** Matched pairs / random effects
   are recommended in the protocol but the harness's analysis is a fixed-effects
   t-test, not a mixed model. With strong operator variance and few operators,
   the CI may be optimistic.
7. **Percentile bootstrap**, not BCa — mildly biased for small skewed n.

## What's genuinely solid
- Log-space GM-ratio endpoint is the statistically correct choice for ~160x-skewed
  durations and is defensible.
- Both designs implemented; scipy-optional with hermetic permutation fallback.
- Negative control (null case) included — rare and important.
- Honest about the blocker rather than fabricating a human study.

## Blocked result (stated plainly)
Real human-in-the-loop MTTR collection is **blocked**: no operator pool, no
controlled incident-replay lab, and production A/B is unethical (can't withhold a
helpful tool during customer impact). Deliverable is the protocol + harness +
grounded simulation that will analyze that data the moment it exists.
