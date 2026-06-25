# 10 — Feedback for the next task

Best-effort instrumentation is the right default for this repo: wrap every tracker call so a
missing/offline backend degrades to a local JSONL artifact instead of killing a run, and make
the canonical record the local file (reproducible) with cloud dashboards as an optional
mirror. Two concrete lessons worth reusing: (1) when a deliverable touches a shared core file
under the parallel-safety rules, ship the change as a `git apply --check`-validated `.patch`
plus a snippet and leave the original untouched — verify with `git status` that the file shows
no diff. (2) Check actual env state before assuming a fallback path: `wandb` (0.27.2) turned
out to be installed here, so `auto` selects it; I had to exercise the fallback explicitly via
`EXPTRACK_BACKEND=jsonl` / `WANDB_DISABLED=true` to test the path we actually depend on. Next
task: if integration into `rex/eval_pass_at_k.py` is wanted as a real patch, first read the
exact keys of `out[cond]` on this branch so the diff applies.
