# G6 — 10 Feedback for the next task

For competitor/claims-analysis tasks, the highest-leverage move is to make citations
*machine-checkable* early: a `sources.json` + `claims_table.csv` + a hard `validate.py` turns
"be sourced" from a vibe into a passing test, and forces the fairness taxonomy (capability /
quant / acknowledged_limit / not_disclosed / structural) that keeps the analysis from sliding
into a straw-man. The grill's most useful output was the discipline of separating "they didn't
publish X" from "they can't do X" — bake that distinction into the data model, not just the
prose. Differentiators must quote real repo constants verbatim (e.g. the `0.30/0.25/0.45/0.60`
reward weights from `rex/scoring.py`) and assert the cited files exist in the validator; that
single check catches the most credibility-damaging error (citing code that isn't there). Watch
the persisted-shell-cwd trap: relative path checks silently mislead — resolve repo paths
absolutely. Finally, always state the no-empirical-head-to-head caveat up front so the artifact
is never mistaken for a benchmark.
