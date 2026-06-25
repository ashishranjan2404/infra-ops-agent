# 10 — Feedback for the next task

The biggest reusable lesson: **never `source ~/.zshrc` from a cron/launchd
wrapper** — a zsh interactive/zsh-only construct silently aborts the script
under bash before it does any work, and `|| true` won't save you because a parse
error or `exit` inside the sourced file isn't a catchable non-zero. Prefer a
dedicated `.env` or extract only `export NAME=...` lines. Second lesson for any
"automation" task here: lean hard on `rex/eval_pass_at_k.py` as the single source
of truth (unbiased pass@k + deterministic judge) and build a *thin* wrapper —
re-implementing scoring is both wasted work and a way to introduce a metric that
disagrees with the rest of the repo. Third: for anything that appends to a shared
history/log, ship a no-network `--dry-run` that exercises the whole plumbing
(resolution → append → lock → parse) with a deterministic synthetic scorer and
tag those rows unmistakably (`dry_run:true`) so they can never be mixed into a
real trend. Record eval failures as an explicit error status, not a fake 0.0.
Finally, remember this project is code-as-policy over a *frozen* LLM, so "latest
model" means a configured gateway slug, not a training checkpoint.
