# C5 — 10 Feedback for the next task

Comparing a *learned data rule-set* to *hand-written code* is most credible as a behavioral diff over
the SAME labeled examples plus an explicit clause→rule map — run both decision functions, don't read
source. The biggest fairness trap is charging a shared limitation (here `trap_action`, which neither
harness has a generic clause for) to the synthesized side; always report `missed_by_synth` AND
`missed_by_handwritten` per hazard. Also check the train/held-out split FIRST: a hazard that lives only
in held-out (here `last_ready_node`) is structurally unlearnable, so a "miss" is partly a split-design
issue, not a search failure — report both honestly. Everything was deterministic and needed no
API/GPU; importing `rex.harness_synth` read-only and reusing its `labeled_examples`/`handwritten_pred`
gave an apples-to-apples comparison for free without touching any shared core file.
