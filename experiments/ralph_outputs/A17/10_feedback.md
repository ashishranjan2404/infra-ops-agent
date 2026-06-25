# A17 — Feedback for the next task

The `scenarios/cidg/generated/` corpus is a **live, concurrently-written artifact** — it grew
from 35 to 51 YAMLs while I worked, and individual files appeared/disappeared mid-run as
parallel Ralph workers generated scenarios. Any task that reports counts over the corpus MUST
derive them with a script at run time and stamp the result with a timestamp + git commit; do
not hand-type or trust a number more than a few minutes old. Two concrete reusable facts:
(1) `registry.json` lags the YAML corpus badly (32 indexed vs 51 on disk) — registry-driven
harnesses silently skip ~37% of scenarios, so the registry should be regenerated before any
coverage or eval claim; (2) the reproducible reward path is `rex/scoring.py`'s
`deterministic_judge` with `REX_JUDGE_MODE=deterministic` — the `hybrid`/`llm` modes call an
LLM and break determinism, so any "reproducible result" claim must pin the judge mode. The
artifact `experiments/ralph_outputs/A17/artifacts/compute_stats.py` is a ready-made,
dependency-light corpus profiler the next task can reuse for composition/coverage stats.
