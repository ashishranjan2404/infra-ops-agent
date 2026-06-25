# F11 — 10 Feedback for the next task

Grounding the appendix in *executed* repo calls (running `scenarios_by_family()`, `floor_check`,
the deterministic-judge tests, and a same-plan determinism probe) was the highest-leverage move —
it turned vague claims into checked facts and caught a real subtlety the draft missed: over the full
registry `trap_max_reward` is `0.1`, not `0.0`, so a "floor is exactly zero" claim would have been
wrong. Lesson: for any doc/appendix task, build a tiny self-checking harness (a schema test + an
offline smoke) so the doc can't silently rot, and run the *full* dataset not a convenience subset
when asserting integrity properties. For LLM-in-the-loop benchmarks, separate the deterministic
grading path (free, reproducible, demoable now) from the stochastic proposer path (paid, deferred) —
ship and demonstrate the former, give an exact recipe + CI-overlap tolerance for the latter, and
never invent the headline number. Finally: verify "no shared-core edits" via mtimes against the
session start, since a branch's pre-existing `git status` diff can otherwise look like your doing.
