# A9 — 10 Feedback for the next task

Label-quality tasks live or die on an anti-fabrication discipline: keep one CSV as the
source of truth, make a `--check` validator the gate, and let "unknown" be a
first-class value (JSON `null`) so missing data never silently becomes a fake zero. Two
concrete gotchas worth carrying forward: (1) the `scenarios/cidg/generated/` directory
is being written by multiple parallel Ralph workers simultaneously — your artifact set
can grow under you mid-run, so always end with a dynamic cross-check
(incident_id <-> YAML meta.id) rather than a hardcoded count, and re-validate. (2) When
a task feeds a downstream analysis you don't own (here: a difficulty score), don't
block on it — ship a runnable stub with a clean plug-in seam (`--scores`) and a repo-only
fallback, and label the fallback loudly as a placeholder so nobody mistakes it for a
result. Finally, several scenario titles use dates/signatures that don't match the
canonical public incident (AWS Kinesis 2024 vs 2020, future-dated 2025 events); flag
these as unknown with the suspected conflation rather than attaching a famous number.
