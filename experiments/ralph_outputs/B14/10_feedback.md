# B14 — Feedback for the next task

The highest-leverage learning: **the eval harness drops token usage on the floor**, which forces
every cost analysis to be an estimate. `agent/llm.py:call` returns only text and discards the
provider's `usage` block from `r.json()`; `rex/eval_pass_at_k.py` never captures per-call tokens.
Any future cost/efficiency/budget task is stuck modelling cost from `max_tokens` budgets until
someone threads `usage` through `call` → `make_proposer` → the result JSON (a small, well-scoped
shared-file edit that the parallel-safety rule currently blocks — worth proposing as a dedicated,
serialized task). Second: the call-shape is cleanly knowable from the code (`N=4`,
zero_shot=1 / best_of_n=rex=rex_no_oracle=4, deterministic P0 judge = no LLM call), so iso-cost
comparisons (rex-vs-best_of_n) are far more defensible than absolute-dollar ones — frame
cost findings around equal-budget comparisons, not raw $/pass, to dodge the "zero_shot looks
cheapest" misread. Also note A2's result JSON has `n_incidents: null`; always fall back to summing
`incidents_by_family`. Keep prices flagged real-vs-assumed — only the Claude tier is real;
everything else in the roster is fictional.
