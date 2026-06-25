# C12 — Step 10: Feedback for the next task

The single highest-value move was writing the runnable witness BEFORE finalizing the
proof — it converted a comfortable "3 rules suffice (QED)" into the true, more
interesting result: 3 rules saturate the *fixed 6-feature space* (99.6% of the
feature-expressible traps), but 37 topology-dependent explicit `trap_action`s and 2
rollback feature-collisions prove the real limiting resource is *features, not rules*.
Lesson for the next worker: in this repo, "sufficiency"/"coverage" claims about the
harness almost always hinge on `harness_synth.FEATURES` (the 6 signals `is_safe` reads)
and the `ground_truth` branch table — ground any such claim in those two, then run
`labeled_examples` over all of `_SCENARIOS` to get a real accuracy number instead of
asserting one. Beware that `rex.harness_synth` imports `agent.llm.call` at module load,
so import only the pure-data helpers (`load_scenario`, `_SCENARIOS`, `labeled_examples`)
to stay offline. Most importantly: when the empirical witness contradicts the nice
claim, report the negative result and re-scope the theorem to what's actually true — the
honest, narrower result was stronger and more publishable than the clean lie.
