# H8 — Automated Nightly Eval — SUMMARY

## Goal
A cron/launchd-driven nightly pass@k smoke against the latest model that appends
results to a history file for trend tracking. Real script + scheduler entry (as
artifacts, not installed), with the dry-run path validated. No core files edited,
no cron installed.

## Delivered (experiments/ralph_outputs/H8/artifacts/)
- nightly_eval.py — entry point. --dry-run (no-network synthetic smoke), default
  real path wrapping rex.eval_pass_at_k.run_eval, --show-history, locked JSONL
  history append, status:error on failure (never a fake 0.0).
- run_nightly_eval.sh — scheduler wrapper: robust env load (.env or extract
  export lines from zshrc — never source it), cd repo, log to logs/.
- crontab.txt — cron entries (02:30 real smoke, 06:00 dry-run self-test) +
  install/remove instructions. Not installed.
- com.sre.nightly-eval.plist — launchd native equivalent. Not installed.
- nightly_eval_history.jsonl — 3 real sample rows (all dry_run:true).
- logs/ — wrapper output.

## Design decisions (from the grill)
- Tripwire, not experiment: small N is intentional + tunable, and labelled.
- Wrap the project's single source of truth for pass@k; don't reinvent scoring.
- No-network --dry-run for CI/cron self-test, unmistakably tagged.
- Robust env loading (the v1 wrapper died silently sourcing zshrc — fixed).
- Failures recorded as status:error, not a fabricated zero score.
- Locked, schema-versioned, JSONL history; both cron + launchd shipped.

## Validation
9/9 checks pass (07): dry-run exit 0 with real incident names, model arg plumbed,
show-history, JSONL valid, bash syntax, plutil -lint OK, crontab field check,
wrapper end-to-end with log, real-path resilience with no key. One real bug found
and fixed (zshrc sourcing).

## Honesty
Only synthetic, clearly-tagged dry-run numbers are written. The real eval path is
wired and reaches the gateway but was not run to completion (budget + the task's
dry-run focus). No core files touched; crontab/launchctl never invoked.

## Status: completed
