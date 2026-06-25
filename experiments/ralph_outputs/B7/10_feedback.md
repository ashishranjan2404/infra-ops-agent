# 10 — Feedback for the next task

The repo already has two clean grounding seams worth reusing: `rex.scoring._stems`
(hermetic, phrasing-robust tokenizer — import it instead of re-rolling regex) and
the `_KIND_CATEGORY` taxonomy in `rex/harness.py`, which the HUD trajectory export
(`opensre-traj/out/hud_trajectories.jsonl`, 197 records with `answer`,
`true_category`, `subscores`, `reward`) already conforms to — that JSONL is the
best consolidated REAL dataset for any metric/eval task and lets you produce a real
number without a live model run. Key lesson: when adding a metric "separate from
pass/fail", PROVE the separation by computing the disagreement between the new
metric and the reward on real data (here 43.1%) — that single statistic is what
justifies the metric's existence to a reviewer. Also note the trajectory `answer`
is a verbose multi-cause narrative, so single-label classification under-counts;
if a task needs cleaner diagnosis text, prefer REx plan logs' structured
`root_cause` field over the narrative `answer`. Keep new code under
`experiments/ralph_outputs/<TASK>/artifacts/` and document any core wiring as a
proposal rather than editing `rex/*.py`.
