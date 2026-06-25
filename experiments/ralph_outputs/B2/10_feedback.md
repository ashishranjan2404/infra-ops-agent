# B2 — Step 10: Feedback for the next task

The pass@k result JSONs (A1/A2 `*_pass_at_k_*.json`) are the canonical paired-evaluation
substrate on this repo: `by_condition[c].per_incident_rewards[incident] = [r_per_seed]`,
plus `threshold`/`seeds`/`incidents_by_family`. Any paired statistic (McNemar here; a
seed-clustered or incident-collapsed test, Wilcoxon on rewards, or bootstrap CIs next)
should ingest that same shape read-only rather than re-running evals. Two real reuse
lessons: (1) cross-validate new stats against an existing artifact — A2 already had a
narrower mcnemar, and reproducing its discordant counts exactly was the fastest proof the
new tool was correct; do this whenever a prior task overlaps. (2) The headline REx-vs-control
effects are huge and direction-clean (b10=0), so they survive almost any correction, but the
*weak-baseline* orderings are fragile — Holm already flipped one (best_of_n vs zero_shot on
deepseek). The biggest open methodological gap for a follow-up is **seed correlation**: 3-5
seeds of one incident are not independent, so the honest next step is an incident-level
(collapse-seeds) or clustered variant — that's where marginal significance claims will move.
