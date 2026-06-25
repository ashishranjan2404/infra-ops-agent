# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Honest framing.** The job is a **regression tripwire**, not a statistically
   powered eval. Documented in the script docstring and SUMMARY. (REV, RLE)
2. **Dry-run rows are unmistakably tagged.** Every record carries `dry_run:true`
   and the synthetic result carries an explicit `note` that it's a synthetic
   scorer. `--show-history` prints a `DRY`/`REAL` column so the two can never be
   silently mixed in a plot. (REV)
3. **Env loading hardened.** Wrapper no longer `source`s `~/.zshrc`. It tries a
   dedicated `.env` (NIGHTLY_ENV_FILE), else greps only `export NAME=...` lines
   out of zshrc and evals just those. (SRE, DO)
4. **Errors recorded as `status:error`, never as a fake 0.0.** The run() wrapper
   catches eval exceptions, stores the message, and exits non-zero — it does not
   invent a score. (SR, SRE)
5. **Locking + schema_version + JSONL** confirmed in the spec. (SRE, SR)
6. **launchd plist added** alongside crontab, with `RunAtLoad=false` so loading
   the agent doesn't fire a real eval. (DO)

## Critiques accepted
- "Don't reinvent scoring" → real path is a thin wrapper over `run_eval`.
- "No-network test path" → `--dry-run`.
- "Don't source zshrc" → export-line extraction.
- "Don't conflate failure with zero" → `status:error`.
- "Small N is not a result" → explicit tripwire framing.

## Critiques rejected (with reason)
- REV's implied push to make N large enough for a tight CI: **rejected** for the
  nightly job. The whole value proposition is cheap + frequent. A heavy eval is a
  separate, on-demand concern (`rex.eval_pass_at_k --frontier`), and the operator
  can bump `--per-family/--seeds` if they want a heavier nightly. We keep the
  default smoke small and *labelled*.
- DO's "require a dedicated .env": **rejected as a hard requirement**; made it the
  preferred-but-optional path with a safe fallback, so zero extra setup is needed
  to run.

## Final shape (unchanged from 01 otherwise)
`nightly_eval.py` (dry-run + real + show-history), `run_nightly_eval.sh`,
`crontab.txt`, `com.sre.nightly-eval.plist`, history JSONL. No core files
edited.
