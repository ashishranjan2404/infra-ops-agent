# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the security/ops reviewer"
**Problems found:**
- A1. `eval "export ${line#export }"` over zshrc lines is an eval of file
  content. If zshrc has `export FOO=$(rm -rf ...)` it executes. Risk is low
  (it's the user's own zshrc) but it's still arbitrary command substitution.
- A2. The history file and its `.lock` sit in the artifacts dir; a real
  deployment should put history somewhere durable, not under a task scratch dir.
- A3. No log rotation — `logs/` grows unbounded (one file per fire).

**Resolutions:**
- A1: accepted as a documented limitation. The preferred path is a dedicated
  `.env` (no eval of arbitrary logic); the zshrc extraction is a *fallback* and
  only matches `export NAME=...` lines. Note added in SUMMARY/critique.
- A2: `--history-file` is a CLI arg precisely so the operator points it at a
  durable path; default is sensible for the demo. Keep.
- A3: out of scope for a tripwire; documented in 09 as a known gap (a logrotate
  snippet would be the fix).

## Engineer B — "the correctness reviewer"
**Problems found:**
- B1. `_pick_smoke_incidents` can return a `dict` (error) instead of a `list`;
  `_dry_run_eval` does `len(incidents) if isinstance(incidents, list) else 0` —
  good — but downstream JSON still serializes the dict, which is fine. Verify no
  `TypeError` when registry fails.
- B2. `pass@1 = passes/n` where `passes = h % (n+1)` can equal n → pass@1=1.0.
  Acceptable for a synthetic; just confirm it never divides by zero (n=max(1,..)).
- B3. Real path mixes `run_eval`'s progress prints onto stdout with the final
  JSON. A naive `json.load(stdout)` fails. The wrapper redirects to a log so
  it's fine, but `--show-history` is the supported parse path, not stdout.

**Resolutions:**
- B1: defended with `isinstance` guard and `max(1, n_inc)`; validated T1 with a
  working registry (6 incidents resolved). Graceful path exercised by code
  review.
- B2: `n = max(1, n_inc) * max(1, seeds)` guarantees n>=1. OK.
- B3: documented — history (JSONL) is the machine-readable interface; stdout is
  human/log. No change needed.

## Engineer C — "the over/under-engineering reviewer"
**Problems found:**
- C1. Is the `_FileLock` over-engineered for a once-nightly job? Overlap is rare.
- C2. `schema_version` bump to 2 with no v1 in the wild — premature?
- C3. The synthetic dry-run scorer is *extra code*. Could we just call `run_eval`
  with a stub? 

**Resolutions:**
- C1: keep — the 06:00 dry-run + 02:30 real fire CAN overlap if a real eval runs
  long, and an operator may fire manually. Cheap insurance. Keep.
- C2: keep — costs nothing and makes the very first row forward-compatible.
- C3: reject the stub idea — the whole point of dry-run is ZERO network/LLM
  dependency for CI. A stub of `run_eval` would still pull its import graph and
  risk touching `agent.llm`. The standalone synthetic scorer is the right call.

## Final filtered spec delta
No structural changes; all three reviewers' hard objections were either already
mitigated (B1/B2, env eval via fallback-only) or accepted as documented,
out-of-scope gaps (log rotation, durable history path). Recorded in 09.
