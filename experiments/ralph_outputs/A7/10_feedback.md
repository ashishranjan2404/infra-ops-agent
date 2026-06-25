# A7 — 10 Feedback for the next task

The CIDG corpus is being written concurrently by parallel Ralph workers — it
grew from 33 → 48 YAMLs mid-task. Treat `scenarios/cidg/generated/*.yaml` as a
moving target: glob + count at run time, never hard-code a count, and keep any
derived artifact a pure read-only sidecar so it can't race the generators (the
brief's parallel-safety rule is not theoretical — it bit this task). When a
task asks for a "score"/"rate"/"probability" but the corpus has no labels, build
a transparent heuristic that emits its own per-component breakdown and call it a
*prior* loudly; don't fake validation you can't do — an auditable ordinal score
plus an honest calibration-deferred note is the correct, reviewable deliverable.
Finally, structural fields (`assertions.cascades`, `loudest_alert_not_cause`,
`smoking_guns[].buried_under`, topology size) are the discriminating difficulty
signals in this schema; `severity`/`flap_prob` are near-constant and weak.
