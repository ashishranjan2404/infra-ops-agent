# 09 — Honest Critique

## What's weak / what a reviewer attacks
1. **The smoke is statistically thin.** per_family=2 × seeds=2 = 12 episodes for
   a tripwire. A reviewer correctly notes this can't detect small regressions;
   it catches *breakage* (model swap, scenario import error, gateway down) and
   gross drops, not a 3-point pass@1 dip. Mitigation is framing (tripwire, not
   experiment) + tunable `--per-family/--seeds`, not statistical power.
2. **Real path not run to completion here.** I validated the dry-run path (as the
   task asked) and confirmed the real path *reaches the gateway*, but did not
   execute a full real nightly eval (budget + the brief's dry-run focus). So the
   real-path history record schema is verified by code, not by a green real run.
3. **zshrc `export`-line extraction does an `eval`.** Low risk (user's own file,
   only `export NAME=...` lines match), but it is eval-of-file-content. The
   preferred `.env` path avoids it; the fallback is a pragmatic convenience.
4. **No log rotation.** `logs/` grows one file per fire forever. A real deploy
   needs logrotate or a `find -mtime +30 -delete` in the wrapper. Left as a
   documented gap.
5. **History lives under a task scratch dir by default.** Fine for the demo;
   production should point `--history-file` at a durable location (it's a CLI
   arg precisely for this).
6. **"Latest model" is a pinned slug, not auto-detected.** Justified by the
   project being code-as-policy over a frozen LLM (no checkpoint training loop),
   but if the team later adds checkpoints, the nightly would need a resolver.

## What's missing
- An alerting hook (Slack/email beyond cron MAILTO) on a regression threshold.
- A tiny dashboard/plot over the JSONL (out of scope; the format is plot-ready).
- A `.env.example` to make the preferred env path turnkey.

## What's genuinely solid
- Correct separation of a no-network self-test path from the real eval.
- Does not reinvent scoring — wraps the project's single source of truth.
- Records failures as `status:error`, never as a fake 0.0 — trend stays honest.
- Locked, schema-versioned, JSONL history; both cron and launchd shipped.
- A real bug (zshrc sourcing aborting the wrapper) was found and fixed during
  validation, not papered over.

## Blocked / negative results
None blocked. The only deliberate non-execution is a full *real* nightly eval,
documented above and consistent with the task's "validate the dry-run path"
instruction and the brief's "don't burn budget / don't fake numbers" guidance.
