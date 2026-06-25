# A1 — 10 Feedback for the next task

The full-42 pass@k was almost entirely a *plumbing + scale* job, not new science: the existing
`rex/eval_pass_at_k.py` already supports the whole set via `per_family=None` and already ships
the Chen estimator + Wilson CI + floor check + per-incident reward vectors. The right move under
the Ralph parallel-safety rules was a ~60-line task-namespaced wrapper that imports the core
unmodified and redirects the checkpoint/output into `A1/artifacts/`, rather than re-running the
shared CLI (which writes to `experiments/results/` and would race other workers). Two gotchas for
the next worker: (1) a deeply-nested runner needs an explicit `sys.path.insert(REPO)` — the repo
isn't auto-importable from `experiments/ralph_outputs/<TASK>/artifacts/`; (2) the core sweep is
**condition-major** in its job ordering, so the thesis condition `rex` runs LAST and a timeout
leaves it empty — if you need a specific condition guaranteed, invoke with
`--conditions zero_shot,rex` so the anchors complete first. Always run `floor_check` OFFLINE
(no API) before spending ~3.5k LLM calls; it caught nothing here (floor_ok over all 42) but it's
free insurance. Headline metric should be pass@1 ± Wilson CI; pass@5 is degenerate below ~5 seeds.
