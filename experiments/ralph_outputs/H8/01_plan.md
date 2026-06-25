# 01 — Plan (H8: Automated nightly eval)

## Objective
Stand up an automated **nightly eval**: a cron/launchd-driven job that runs a
pass@k *smoke* against the latest model and appends results to a history file
so we can watch the metric trend over time. Deliver a real, runnable script + a
scheduler entry (as an artifact, **not installed**), and validate the script's
dry-run path. Do **not** actually install cron. Do **not** edit shared core
files.

## Approach
Be a thin orchestration layer on top of the project's existing single source of
truth for pass@k: `rex/eval_pass_at_k.py` (`run_eval`, deterministic judge,
unbiased pass@k estimator). The nightly job should NOT re-implement scoring; it
should:
1. Resolve the "latest" model (CLI arg, default `glm-5p2`).
2. Pick a small, family-balanced set of incidents (the smoke).
3. Call `run_eval` for a couple of conditions/seeds.
4. Compact the result to a trend-friendly summary.
5. Append one JSON line to a history file under a file lock.
6. Provide a `--dry-run` path that exercises the WHOLE pipeline with a
   deterministic synthetic scorer — no network, no LLM, always green — so cron
   can self-test and CI can validate.

## Files to create (all task-namespaced)
- `artifacts/nightly_eval.py` — the entry point (dry-run + real paths, history).
- `artifacts/run_nightly_eval.sh` — cron/launchd wrapper (env load, cd, log).
- `artifacts/crontab.txt` — crontab entry (install instructions in comments).
- `artifacts/com.sre.nightly-eval.plist` — launchd entry (macOS native).
- `artifacts/nightly_eval_history.jsonl` — produced by validation (sample rows).
- `artifacts/logs/` — produced by the wrapper.

## Files to modify
None. Per the brief, no shared core files touched. We only *import*
`rex.eval_pass_at_k` / `rex.harness`.

## Dependencies
- Python 3.13 stdlib (argparse, json, fcntl, socket, hashlib, datetime).
- For the *real* path: `rex.eval_pass_at_k`, `rex.harness`, `HUD_API_KEY`.
- The dry-run path has zero external dependencies beyond the scenario registry
  (and even degrades gracefully if that can't load).

## Risks
- cron/launchd run with a bare env → `HUD_API_KEY` missing. Mitigation: wrapper
  loads env; dry-run needs no key.
- Overlapping fires corrupting history. Mitigation: advisory file lock.
- Sourcing `~/.zshrc` under bash can abort the wrapper. Mitigation: don't source
  it; extract only `export` lines (or use a dedicated `.env`).
- Faking eval numbers. Mitigation: real path calls the real pipeline; dry-run is
  explicitly labelled synthetic and only used for plumbing validation.

## Success criteria
- `nightly_eval.py --dry-run` runs with no network, exits 0, appends a valid
  JSONL record resolving REAL incident names.
- `--show-history` parses and prints the trend.
- Wrapper runs end-to-end and writes a log.
- crontab and plist are syntactically valid (`plutil -lint`, field check).
- Nothing installed into the user's real crontab/LaunchAgents.
