# A14 — 10 Feedback for the next task

The cleanest way to add a constraint to the frozen REx env is to wrap the **proposer**
(`propose_fn`) rather than the loop: `refine_loop`/`rex_tree` already expose `propose_fn`,
`log=`, and `budget=`, so you can meter cost, capture every completed iteration, and cut the
rollout off — all without editing a single `rex/*.py` file (satisfying the parallel-safety
rule). Two gotchas worth carrying forward: (1) raising an exception inside `propose_fn` aborts
the loop and discards its internal aggregation, so always capture iterations through the
loop's `log=` hook and rebuild the result with the SAME aggregation logic the loop uses
(best=argmax score, clean_win=any iter with no failed_checks); (2) make any time/cost axis
*injectable* (`cost_fn`, `clock`) so tests stay deterministic and offline — the real `oom_kill`
scenario + `run_plan` + deterministic judge run with no network once the LLM call is mocked,
which makes a "real loop, fake model" test both fast and faithful. Finally, when you add an
outcome-changing knob (here, budget), **label the induced outcomes** (`budget_truncated`,
`truncation_reason`) — reviewers immediately ask how a constraint-induced escalation is
distinguished from a genuine one, and the label is the answer.
