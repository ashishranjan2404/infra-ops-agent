# J4 — 01 Plan

## Objective
Measure the **real MTTR improvement** from agent assistance: how much does an
LLM/agent-in-the-loop reduce Mean-Time-To-Resolve for SRE incidents vs an
unassisted human? Deliver (a) a rigorous experiment **protocol**, (b) the
**metrics + statistics** definition, (c) a runnable **analysis harness**, and
(d) a **simulation** that exercises the harness on synthetic timing data with a
known ground-truth effect (because real human-in-the-loop measurement is the
documented blocker).

## Approach
1. Reuse A9 `mttr_labels.json` as the **baseline** distribution: real incident
   MTTRs (Cloudflare 27m … Roblox 4380m) give the right-skew + scale for
   synthetic baselines, so the simulation is grounded, not invented from a flat prior.
2. Support **both** experiment designs:
   - **within-subjects (paired)**: same incident resolved unassisted & assisted
     (matched operators / replayed scenario). Higher power, controls for
     incident difficulty. Risk: learning/order effects.
   - **between-subjects (A/B)**: incidents/operators randomized to one arm.
     No order effects; needs larger n.
3. Analyze in **log space** (durations are ~160x-skewed): primary endpoint is
   the multiplicative **speedup = GM(unassisted)/GM(assisted)**, with bootstrap
   CI, paired/Welch t-test, and nonparametric backups (Wilcoxon / Mann-Whitney /
   Cliff's delta). scipy optional with permutation fallback.

## Files to create (all task-namespaced under J4/artifacts/)
- `mttr_analysis.py` — the analysis harness (load → analyze → JSON report) + self-test + power calc.
- `simulate_trials.py` — synthetic trial generator grounded in A9 labels.
- generated: `trials_within.csv`, `trials_between.csv`, `report_*.json`.

## Dependencies
- numpy/scipy present (verified scipy 1.17.1); harness degrades to stdlib
  permutation tests if scipy absent. A9 `mttr_labels.json` (read-only).

## Risks
- **Blocker**: no real operators / no controlled incident-replay env in a batch
  job → cannot collect real timing. Mitigation: deliver protocol + harness +
  simulation; document blocker honestly.
- Simulation could be circular (validate stats on data the stats assume).
  Mitigation: plant a realistic effect (operator random effects + no-benefit
  fraction + per-trial noise) and verify recovery AND a null case.

## Success criteria
- Harness self-test passes; recovers planted speedup within tolerance; null case
  is correctly non-significant; CI brackets ground truth. Both designs run.
- Protocol covers randomization, blinding, confounds, power/sample-size, endpoints.
