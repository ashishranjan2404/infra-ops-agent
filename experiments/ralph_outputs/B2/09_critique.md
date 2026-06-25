# B2 — Step 9: Honest Critique

## What a reviewer will attack

1. **Within-incident seed pairs are not independent.** McNemar assumes the discordant
   pairs are independent Bernoulli(0.5) trials. But 3-5 seeds of the *same* incident are
   correlated (same scenario, same difficulty). The effective sample size is closer to
   #incidents than #(incident,seed). This inflates significance — our n_disc treats each
   seed as independent. **Honest impact:** the strong REx results (n_disc 70-100, b10=0)
   survive even a brutal correction (a clean sweep where REx wins every incident is
   significant at the incident level too), but the *marginal* calls (best_of_n vs zero_shot,
   p_holm 0.065) are the ones a clustered/incident-level test would most change. The tool
   does not currently offer an incident-level (collapse-seeds) mode — a real limitation.

2. **The 0.8 reward "cliff."** Pass/fail at threshold 0.8 is brittle near the boundary; a
   0.79 vs 0.81 difference flips a discordant pair on noise. We expose `--threshold` to probe
   this but did not run a sensitivity sweep in this deliverable. A reviewer can ask "do your
   REx-vs-control conclusions hold at 0.7 and 0.9?" — unanswered here.

3. **Underpowered per-family novel cells.** In the novel family, several pairs have
   n_disc as low as 0-2; the minimum achievable two-sided exact p there is 1.0, so "not
   significant" is meaningless (it's "no power"), not evidence of no effect. The report shows
   n_disc so a careful reader sees this, but a skim reader could over-read it. SUMMARY flags it.

4. **Two models, not a population.** We ran A1 (glm-5p2) and A2 (deepseek-v4-pro) — these
   are the only cached pass@k JSONs available with per-incident rewards. Conclusions are
   per-model; no cross-model meta-analysis. More models would strengthen generality.

5. **McNemar tests difference, not direction-of-practical-importance.** A statistically
   significant b01=16/b10=2 (best_of_n>zero_shot) is a small absolute effect. We added
   `pass_rate_a/b` so effect size is visible, but McNemar p-values alone overstate how much
   a reader should care about the weak-baseline orderings.

## What is genuinely solid
- REx >> all controls is robust, large, and direction-clean (b10=0 almost everywhere),
  significant under Holm for both models. This is not a marginal result.
- The tool independently reproduces A2's pre-existing mcnemar counts — the arithmetic is
  trustworthy.
- Holm correction demoted one raw-significant result (best_of_n vs zero_shot, deepseek),
  which is exactly the kind of over-claim the paper risked by claiming-but-not-running McNemar.

## Not blocked
Nothing was blocked. All data was available locally; the deliverable is a real, tested,
cross-validated tool plus real p-values. The honest caveats above (seed-correlation,
threshold sensitivity, novel power) are limitations of the *analysis*, documented, not
fabrications or gaps in the deliverable.
