# F5 — Feedback for the next task

The most valuable move on this task was treating `docs/headline_insights.md` and the raw
`rex/runs/*.json` aggregates as the source of truth and the `PAPER_OUTLINE.md` abstract as
a *draft to be corrected against them* — the two disagreed in several places (89.7/94.9 vs
0.90/0.95 verifier accuracy; "≥2× lift" vs the oracle-leakage collapse), and the honest
numbers were always the smaller, JSON-backed ones. Future writing tasks should re-derive
every cited number from a run artifact before committing it (a 30-second `python3 -c`
read of the JSON caught that `rex_no_oracle=0.250` is genuinely in the data, upgrading the
claim from doc-only to repo-backed). Also: keep an explicit "omitted as unsupported" list
(C2 transfer, McNemar p-value) so the gap between the paper's *ambition* (three claims,
42 incidents, cross-model) and its *current evidence* (two defensible claims, 5-incident
single-model ablation) is documented, not silently papered over. Whoever writes the
Introduction or Results next should expect the same tension and resolve it the same way.
