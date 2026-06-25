# 04 — Technical Spec

## Components
1. `nightly_eval.py` — Python entry point.
2. `run_nightly_eval.sh` — bash wrapper for the scheduler.
3. `crontab.txt` — cron entry (not installed).
4. `com.sre.nightly-eval.plist` — launchd entry (not installed).
5. `nightly_eval_history.jsonl` — append-only trend log.

## nightly_eval.py — function signatures
```python
SCHEMA_VERSION = 2
REPO_ROOT: str            # resolved from __file__ (4 dirs up)
DEFAULT_HISTORY: str      # artifacts/nightly_eval_history.jsonl

class _FileLock:          # POSIX fcntl advisory lock; no-op fallback
    def __init__(self, path: str) -> None
    def __enter__(self) -> "_FileLock"
    def __exit__(self, *exc) -> bool

def _now_iso() -> str                                   # UTC, second precision
def _pick_smoke_incidents(per_family: int) -> list|dict # family-balanced names
def _dry_run_eval(model, per_family, seeds) -> dict     # synthetic, no network
def _real_eval(model, per_family, seeds, max_workers) -> dict  # wraps run_eval
def append_history(history_file: str, record: dict) -> None    # locked append
def show_history(history_file: str) -> int
def run(args) -> dict                                   # one nightly cycle
def build_parser() -> argparse.ArgumentParser
def main(argv=None) -> int                              # 0 ok / 1 on error
```

## CLI contract
```
--model STR          default glm-5p2     ("latest" model under test)
--per-family INT     default 2           incidents per family for the smoke
--seeds INT          default 2
--max-workers INT    default 4
--history-file PATH  default DEFAULT_HISTORY
--dry-run            flag  -> synthetic deterministic scorer, no network
--show-history       flag  -> print trend and exit
```

## History record schema (JSONL, one object per line)
```json
{
  "schema_version": 2,
  "ts": "<ISO8601 UTC start>",
  "finished": "<ISO8601 UTC end>",
  "host": "<hostname>",
  "model": "<slug>",
  "dry_run": true|false,
  "status": "ok"|"error",
  "error": null|"<Type: msg>",
  "result": { ... }            // dry-run summary OR compacted run_eval summary
}
```
`result` (real path) holds a compacted per-condition summary:
`{cond: {pass@1, pass@5, mean_reward, reward_std, n}}`, plus `floor_check`,
`n_errors`, `elapsed_s`. `result` (dry-run) holds `{incidents, n_incidents,
summary: {zero_shot: {pass@1, n, passes}}, note}`.

## Dry-run scorer (deterministic, no network)
- Resolve real incidents via `rex.harness.scenarios_by_family`.
- Seed a synthetic pass count on `sha256(model)` so the smoke is reproducible
  yet model-dependent (proves the model arg is wired). `pass@1 = passes / n`.
- Never calls `agent.llm.call`; never touches the gateway.

## Concurrency / durability
- `append_history` wraps the write in `_FileLock` (fcntl LOCK_EX) so overlapping
  cron fires can't interleave/corrupt lines. Each write is a single
  newline-terminated JSON object → partial-line risk minimized.

## Error semantics
- Any exception in eval → `status:"error"`, `error` set, `result` minimal; the
  record is STILL appended (so failures are visible in trend), and `main`
  returns 1 so cron's MAILTO surfaces it. No fake 0.0 score is ever written.

## run_nightly_eval.sh contract
- `set -euo pipefail`; `REPO_ROOT` overridable (default /Users/mei/rl).
- Loads env: `.env` first, else extract `export` lines from `~/.zshrc`.
- `cd $REPO_ROOT`; runs `python3 nightly_eval.py "$@"`, appending stdout+stderr
  to `logs/nightly_<UTCstamp>.log`.

## Scheduler entries
- crontab: `30 2 * * *` real smoke; `0 6 * * *` `--dry-run` self-test.
- launchd: `StartCalendarInterval` H=2 M=30; `RunAtLoad=false`;
  Std{Out,Err}Path under `logs/`.

## Test cases
| # | command | expect |
|---|---------|--------|
| T1 | `--dry-run` | exit 0; record `dry_run:true,status:ok`; real incident names |
| T2 | `--dry-run --model X` then again `--model Y` | two rows, different pass@1 |
| T3 | `--show-history` | prints rows + count; DRY/REAL column |
| T4 | history file | every line valid JSON (JSONL) |
| T5 | `bash -n wrapper` | syntax OK |
| T6 | `plutil -lint plist` | OK |
| T7 | crontab field check | 5 time fields + command on entry lines |
| T8 | wrapper `--dry-run` | exit 0; log file written |
| T9 | real path, no key | does NOT crash; records errors (n_errors) |
