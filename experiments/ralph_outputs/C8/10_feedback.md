# C8 — 10 Feedback for the next task

The most reusable lesson: in this REx harness-synthesis setup, **a held-out accuracy
ceiling is almost always a TRAIN-COVERAGE problem, not a search/rule problem.** Before
proposing new rules, inspect which `FEATURES` are unused by the synthesized set and
*count how many TRAIN examples activate each* — if a hazard's feature is True for zero
train labels (here `last_ready_node_op` and `at_replica_limit`), the Thompson/haiku
search is mathematically blind to it and any "fix" you add is human-injected
hindsight, not generalization. The honest framing for such tasks is two-sided:
"expressible + effective on held-out, but undiscoverable from the train signal." Two
concrete gotchas for whoever touches this next: (1) the v2 baseline already carries 2
TRAIN rollback false-blocks — when asserting "no regressions," always test the *delta*
vs baseline, never an absolute zero; (2) `confusion()` rounds accuracy to 3 dp and the
held-out set is only 39 labels, so gains move in ~2.5-point chunks — distrust any
sub-rounding "improvement." The clean, cheap, deterministic move is to fix the rule-set
and inject one rule offline (no LLM, no core edits); re-running the actual haiku search
to test whether a re-balanced split lets it *discover* the rule is the natural,
higher-cost follow-up.
