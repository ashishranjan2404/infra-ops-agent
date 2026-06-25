# B15 — 10 Feedback for the next task

Cross-benchmark comparisons live or die on the caveats, not the table — the highest-value work
here was the *metric-semantics bridge* (SREGym "success rate over 3 runs, 1 attempt/run" == pass@1)
and the *fair-comparator reframing* (compare external single-attempt agents to our
best_of_n/rex_no_oracle band, never to oracle-fed REx). Two concrete reusables for downstream
tasks: (1) the A1 artifact nests per-family stats under `by_condition[cond]["by_family"][family]`
(NOT a flat key) and uses `pass@1`/`ci95` spellings, while summarizer outputs use `p1`/`ci` —
write tolerant readers and add a selftest assert on a known value (rex novel == 1.0) to catch
schema drift before it silently emits "—". (2) Freeze external/leaderboard numbers into a cited
JSON with a retrieval date rather than live-scraping, so the deliverable is reproducible; note the
staleness risk explicitly since SREGym is a *live* benchmark. The unremovable confound to flag for
anyone extending this: our pass@1 is on cheaper models (glm-5p2 / deepseek-v4-pro) vs SREGym's
frontier models, so "our baselines are below SREGym" is partly a model-strength gap — only a
matched-model re-run (API budget needed) can isolate the benchmark-difficulty effect.
