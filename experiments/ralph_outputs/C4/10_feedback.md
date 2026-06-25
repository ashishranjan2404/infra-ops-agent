# C4 — 10 Feedback for the next task

When a task references "the N synthesized rules," check BOTH run files first
(`rex/runs/harness_synth.json` is v1 with 10 rules; `rex/runs/harness_synth_v2.json` is v2 with
exactly 3) — the count in the task disambiguates which artifact is canonical, and the v1→v2 delta
is itself the most quotable evidence (10→3 rules while accuracy *rose*). The biggest time-saver was
writing a tiny validator that re-applies the rules through the *real* interpreter
(`rex.harness_synth.is_safe_synth` + `confusion` + `labeled_examples`) and asserts against the
published JSON: it turned every report claim into a reproduced number and surfaced subtleties for
free (first-match ordering, the broadening of the leak rule, the 0-synthesis-quality-miss split of
held-out false-allows). Import `rex.harness_synth` read-only and NEVER call its `main()` — that
rewrites a shared core JSON. Finally, for interpretability claims, commit to explicit yardsticks up
front (1:1 mapping / simulability / sparsity) so the analysis is scored, not vibed; and frame a
safety harness's over-blocking as deliberate conservatism only after checking the held-out
false-block rate is actually 0.
