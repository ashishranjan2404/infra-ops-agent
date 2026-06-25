# 06 — Implementation

## What I built (all under experiments/ralph_outputs/H8/artifacts/)

### 1. `nightly_eval.py` (entry point, ~290 lines)
- Resolves `REPO_ROOT` from `__file__` (4 dirs up) so it imports `rex.*` /
  `agent.*` regardless of the cwd cron launches it in.
- `--dry-run`: deterministic synthetic scorer. Resolves REAL incidents via
  `rex.harness.scenarios_by_family`, seeds a synthetic pass count on
  `sha256(model)`, appends a `dry_run:true` record. NO network, NO LLM.
- default (real) path: thin wrapper over `rex.eval_pass_at_k.run_eval` with
  conditions `["zero_shot","rex"]`, compacted to a trend summary.
- `--show-history`: parses the JSONL and prints a `DRY/REAL` trend table.
- `append_history`: locked (`_FileLock`, fcntl) append of one JSON line.
- `run`: wraps eval in try/except → records `status:"error"` (never a fake 0.0)
  and `main` returns 1 so cron surfaces failures.
- Record schema carries `schema_version=2`, `ts`, `finished`, `host`, `model`,
  `dry_run`, `status`, `error`, `result`.

### 2. `run_nightly_eval.sh` (scheduler wrapper)
- `set -euo pipefail`; overridable `REPO_ROOT`.
- `load_env()`: prefers a dedicated `.env` (`NIGHTLY_ENV_FILE`); else extracts
  only `export NAME=...` lines from `~/.zshrc` and evals just those — it does
  **not** `source ~/.zshrc` (which aborts under bash). This was a real fix: the
  first version sourced zshrc and the wrapper died silently mid-run (see 07).
- `cd $REPO_ROOT`; runs the python entry, appending stdout+stderr to a
  timestamped `logs/nightly_<UTC>.log`.

### 3. `crontab.txt` (NOT installed)
- `30 2 * * *` real smoke + `0 6 * * *` `--dry-run` self-test.
- Header comments give exact install/verify/remove commands. We did NOT run
  `crontab` — per the task, nothing is installed.

### 4. `com.sre.nightly-eval.plist` (NOT installed)
- launchd native equivalent. `StartCalendarInterval` 02:30, `RunAtLoad=false`,
  logs under `logs/`. Header gives load/start/unload commands.

### 5. Produced by validation
- `nightly_eval_history.jsonl` — 3 real sample rows from dry-run validation.
- `logs/nightly_<stamp>.log` — wrapper output.

## Proposed change to shared core files
**None.** This task is purely additive orchestration on top of
`rex/eval_pass_at_k.py`; no core file needed editing, so no `.patch` was
required. The script imports the core pipeline read-only.

## How the "latest model" is handled
Model is a CLI arg (default `glm-5p2`, the project's primary gateway slug). The
scheduler entries pin it; an operator updates one string to point the nightly at
a newer slug. (A fancier "auto-detect latest checkpoint" was deliberately left
out — this project is code-as-policy over a frozen LLM, not checkpoint training,
so "latest model" = the configured slug.)
