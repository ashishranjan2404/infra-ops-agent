# H2 — 10 Feedback for the next task

CI/eval-gate tasks in this repo should default to **deterministic, hermetic** checks: the
real value is guarding the substrate (`load_scenario` → `run_plan` → `score_plan` with the
default deterministic judge), not running a flaky per-PR model sweep. Reuse the real scoring
path — never mock the judge — and assert *falsifiable* invariants (separation between a good
and a trivial policy, plus a strict floor that the cheapest path can't pass) rather than
"it runs". Watch two repo-specific gotchas: (1) PyYAML parses the GitHub Actions `on:` key as
boolean `True`, so any YAML validator must check both keys; and (2) the scenario set is not
uniformly well-formed — at least two scenarios (`aws_dynamodb_dns`, `azure_ddos`) have
canonical-fix data that under-scores in the sim, so any "gold must be perfect" assertion is
brittle. Build tolerance for known-bad data into thresholds, and surface those data bugs as
findings for a dedicated scenario-repair task rather than editing shared core.
