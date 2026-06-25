# 02 — Ralph Loop Grill (5 personas × 3 rounds)

Personas: **SR** Senior ML Researcher · **SRE** Principal SRE · **REV** AAAI
Reviewer · **RLE** RL Engineer · **DO** DevOps Lead.

## Round 1 — initial takes
- **SR:** A nightly pass@k is only useful if it's *comparable* night to night.
  Pin the threshold, the incident set, and seed count, or trend is noise. Record
  schema_version so old rows stay parseable.
- **SRE:** This is a cron job that calls an LLM gateway at 02:30. It WILL fail
  intermittently (key rotation, gateway 5xx). The job must never crash the box,
  must log, and must surface failures (MAILTO / non-zero exit). Idempotency and a
  lock on the history file are non-negotiable.
- **REV:** "Smoke" with per_family=2, seeds=2 = 12 episodes. That's far too few
  for a meaningful pass@k CI. Don't dress this up as an experiment; it's a
  regression *tripwire*, not a result. Say so explicitly or a reviewer will
  attack the statistics.
- **RLE:** Don't re-implement scoring. `rex/eval_pass_at_k.py` already has the
  unbiased estimator + deterministic judge. Wrap it. Also: how do you test this
  without burning API budget every CI run? You need a no-network path.
- **DO:** cron is half-deprecated on macOS. Ship a launchd plist too. And cron
  runs with `PATH=/usr/bin:/bin` and no env — your script must load its own
  environment or it'll fail silently every night.

## Round 2 — react to another persona by name (forced disagreement)
- **RLE → REV:** I disagree with framing 12 episodes as worthless. The point
  isn't a tight CI; it's *catching a regression* (model swap, prompt change,
  scenario breakage). A cheap tripwire that runs every night beats a rigorous
  eval that runs never. But you're right it must be *labelled* a smoke, not a
  result — I'll take that.
- **REV → RLE:** Then your synthetic dry-run scorer is dangerous. If the dry-run
  produces a "pass@1" number and it lands in the SAME history file as real runs,
  someone WILL plot them together and report garbage. Hard objection: dry-run
  rows must be unmistakably tagged (`dry_run: true`) and ideally separable.
- **SRE → DO:** Sourcing `~/.zshrc` to "load env" is how you get a nightly job
  that silently dies — zshrc has interactive guards and zsh-only syntax that
  abort under bash/sh. I'd refuse a wrapper that does `source ~/.zshrc`. Use a
  dedicated env file, or grep out only `export` lines.
- **DO → SRE:** Fair, but a dedicated `.env` adds a setup step the brief didn't
  ask for. Compromise: try `.env` first, fall back to extracting `export` lines
  from zshrc — never execute arbitrary zshrc logic. (This is what we built.)
- **SR → SRE:** Your "never crash the box" and my "comparability" collide: if you
  swallow all errors to stay alive, a broken eval looks like a *0.0 pass@1* and
  pollutes the trend. Disagreement: errors must be recorded as `status:error`,
  NOT as a zero score. Don't conflate "model failed" with "model scored 0".

## Round 3 — synthesis
Consensus the build adopts:
1. **Tripwire, not experiment.** Document the small N honestly (REV/RLE).
2. **Wrap, don't reinvent** `rex.eval_pass_at_k` (RLE).
3. **No-network `--dry-run`** with a deterministic synthetic scorer for CI/cron
   self-test, **unmistakably tagged** `dry_run:true` (RLE + REV).
4. **Robust env load**: `.env` first, else extract `export` lines; never
   `source ~/.zshrc` (SRE + DO).
5. **Resilience without lying**: catch eval errors, record `status:error` with
   the message, exit non-zero — do NOT record a fake 0.0 (SR + SRE).
6. **File lock** on history append; **schema_version**; JSONL so old + new rows
   coexist (SRE + SR).
7. Ship **both** crontab and launchd (DO).
