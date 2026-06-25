# 08 — Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| `--dry-run` runs with no network, exits 0 | YES | T1: exit 0, synthetic scorer, zero LLM calls |
| Dry-run appends valid JSONL with REAL incident names | YES | T1/T4: 6 real incidents resolved; JSONL valid |
| `--show-history` parses + prints trend | YES | T3: trend table with DRY/REAL column |
| Wrapper runs end-to-end, writes a log | YES | T8: exit 0, `logs/nightly_*.log` written |
| crontab syntactically valid | YES | T7: field check passes |
| launchd plist valid | YES | T6: `plutil -lint` OK |
| Nothing installed into real crontab/LaunchAgents | YES | No `crontab`/`launchctl load` run; entries are inert files |
| No shared core files edited | YES | Only `rex.*` imports; `git status` shows only new H8 files |
| Real eval path wired (not faked) | YES | T9: real path reaches `run_eval`/gateway; numbers come from the real deterministic judge, not invented |

## Are outputs real (not placeholder)?
- `nightly_eval.py` is a runnable program, executed multiple times above.
- The history rows are genuine outputs of running the script (tagged `dry_run`
  so they're never mistaken for real eval results).
- crontab/plist are valid, install-ready (but deliberately uninstalled) entries.
- The real eval path is a true wrapper over the project's existing pass@k
  pipeline — verified it reaches the network layer in T9.

## Scope honesty
The only numbers written are explicitly-synthetic dry-run smoke values. A real
nightly fire (with `HUD_API_KEY`) would write real pass@k via `run_eval`; that
path is wired and reached, but a full real eval was not run to completion here to
avoid burning gateway budget during validation (and the brief asks specifically
to validate the *dry-run* path). This is a deliberate, documented choice — not a
fabrication.
