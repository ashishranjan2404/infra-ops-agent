# A12 — 10 Feedback for the next task

The richest, cheapest difficulty signal already lives **inside the scenario YAMLs**
(`assertions.{cascades,loudest_alert_not_cause,buried_gun_exists,hysteresis,
monitoring_degrades}`, `root_cause.hidden`, `smoking_guns[].buried_under`, topology
size) plus `registry.json` (`family`, `red_herrings`) — you can build a principled
static curriculum/feature vector with zero model calls, which keeps the artifact
deterministic and re-runnable. Two practical gotchas: (1) `scenarios/cidg/generated/`
is being grown by **parallel workers**, so the incident count drifts between runs —
make any generator idempotent and re-run it as the final step, and join on the yaml
basename since some new yamls aren't in `registry.json` yet (`family="unknown"`).
(2) Use **registry keys** as canonical incident ids (`redis_cache_flush`,
`slack_tgw_fd_exhaustion`) because that's what `rex/harness.py:load_scenario`
consumes — `meta.id` uses hyphens and won't round-trip. The one thing this static
approach can't give you is *learner-perceived* difficulty; the clean next task is to
correlate the structural score against empirical pass@k (`rex/eval_pass_at_k.py`) and
refit the weights — that turns the prior into a measured curriculum.
