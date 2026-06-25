# B15 — 09 Critique (honest)

## Where a reviewer attacks

1. **The comparison is fundamentally apples-to-oranges, and no amount of caveats fixes that.**
   A skeptic can say: if the benchmarks share no substrate, no tasks, no grader, and no models,
   then putting the numbers in one table is itself misleading — readers anchor on the digits and
   skip the prose. Fair. Mitigation is framing (no-ranking TL;DR, regime column), but the
   underlying critique stands: this is *contextualization*, not measurement.

2. **SREGym numbers are transcribed, not independently reproduced.** I pulled them from the paper
   HTML + leaderboard via web fetch. If those numbers are revised (it's a *live* benchmark), our
   frozen JSON goes stale. There's a `version_note` with a retrieval date, but no programmatic
   freshness check. A live re-fetch path would be more robust (deliberately omitted for repro).

3. **Our pass@1 is on cheaper/older models (glm-5p2, deepseek-v4-pro), SREGym's on frontier
   models (Sonnet-4.6, GPT-5.4).** So even the "our baselines are below SREGym" conclusion is
   confounded by model strength — a stronger model on our sim might close the gap. We disclose
   this (caveat 7) but cannot correct it without re-running, which needs API budget.

4. **The family↔partition analogy adds little and risks misreading.** Even labeled "loose," it
   invites exactly the per-partition comparison we say not to make. A reviewer could argue Table 2
   should be cut. I kept it only because the novel↔New collapse is a genuinely shared signal; it's
   the weakest part of the deliverable.

5. **"E2E-ish" reward claim is asserted, not proven.** I read `rex/scoring.py` semantics
   (SLO + root + collateral) and called it E2E-ish, but I did not formally show our reward's pass
   bar aligns with SREGym's E2E oracle. The 0.8 threshold could be stricter or looser than "correct
   diagnosis AND mitigation." Honest gap.

## What's genuinely solid
- The metric-semantics bridge (SREGym success-rate-over-3-runs == pass@1) is correct and useful.
- The fair-comparator reframing (use best_of_n/rex_no_oracle, not rex, vs single-attempt agents)
  is the right methodological move and yields a defensible, non-self-flattering conclusion.
- All our numbers are real and reproducible from disk; all SREGym numbers are cited.

## Blocked / out of scope (honest)
- Running our pipeline on Sonnet-4.6 to remove the model confound: needs API budget + time;
  not done. Running on SREGym's actual live cluster: needs their harness + a K8s cluster; not done.
- These are documented as non-equivalence axes rather than faked.
