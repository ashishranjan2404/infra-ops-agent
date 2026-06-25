# 07 — Test Results

All commands run from `experiments/ralph_outputs/H8/artifacts/`.

## T1 — dry-run path (PASS)
`python3 nightly_eval.py --dry-run --history-file ./nightly_eval_history.jsonl`
→ exit **0**. Output record:
```
"dry_run": true, "status": "ok",
"result": { "incidents": ["auth_cert_expiry","bad_deploy_leaf",
  "aws_dynamodb_dns","aws_kinesis_cell_manager","azure_leapyear_cert",
  "cloudflare_leap_second"], "n_incidents": 6, "seeds": 2,
  "summary": {"zero_shot": {"n": 12, "pass@1": 0.75, "passes": 9}},
  "note": "synthetic deterministic scorer — no LLM/network calls" }
```
Resolves REAL incident names from the registry. No network used.

## T2 — model arg is plumbed (PASS)
Second dry-run with `--model minimax-m3` → different pass@1 (0.9167 vs 0.75),
confirming the synthetic score is model-dependent (seeded on the model slug).

## T3 — show-history (PASS)
`--show-history` output:
```
2026-06-25T08:17:48+00:00 glm-5p2        DRY   zero_shot pass@1=0.75
2026-06-25T08:17:48+00:00 minimax-m3     DRY   zero_shot pass@1=0.9167
-- 2 run(s) in history
```
DRY/REAL column present so dry-run rows can never be silently mixed with real.

## T4 — history JSONL validity (PASS)
`python3 -c "import json;[json.loads(l) for l in open('nightly_eval_history.jsonl') if l.strip()]"`
→ `JSONL valid`.

## T5 — wrapper bash syntax (PASS)
`bash -n run_nightly_eval.sh` → `wrapper syntax OK`.

## T6 — launchd plist validity (PASS)
`plutil -lint com.sre.nightly-eval.plist` → `com.sre.nightly-eval.plist: OK`.

## T7 — crontab field check (PASS)
Entry lines have 5 time fields + command; `=`-assignment lines skipped →
`crontab entries OK`.

## T8 — wrapper end-to-end (PASS, after a fix)
- **First attempt FAILED:** `bash -x run_nightly_eval.sh` aborted right after
  `source /Users/mei/.zshrc` (exit unknown, no log written). Root cause: the
  user's zshrc has zsh-only/interactive content that aborts a `source` under
  bash, killing the wrapper before the python call.
- **Fix applied:** replaced `source ~/.zshrc` with `load_env()` — prefer a
  dedicated `.env`, else extract only `export NAME=...` lines and eval those.
- **Re-run:** `REPO_ROOT=/Users/mei/rl ./run_nightly_eval.sh --dry-run ...` →
  exit **0**, log `logs/nightly_20260625T081829Z.log` written containing the
  full JSON record.

## T9 — real path resilience, no usable key (PASS)
`python3 nightly_eval.py --model __nonexistent__ --per-family 1 --seeds 1` did
NOT crash. `run_eval` catches per-episode API failures internally and returns a
result with `n_errors`; the nightly script recorded `status:"ok"` with the error
count surfaced in `result.n_errors`. (A *hard* exception in run() would instead
record `status:"error"` and exit 1 — that branch is covered by the try/except in
`run()`.)

## Summary
9/9 checks pass. One real bug found and fixed during validation (zshrc sourcing
aborting the wrapper). No fabricated eval numbers: the only numbers in history
are explicitly-tagged synthetic dry-run rows.
