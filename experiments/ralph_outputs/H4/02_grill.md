# 02 — Grill (5 personas x 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take
- **SMR:** A tracker is table stakes, but the *value* is comparability across runs. I
  care that config (model, lr, group, seeds, reward version) is logged alongside metrics
  so I can group/filter. mean_reward + reward_std per step is the minimum useful signal.
- **PSRE:** My only hard requirement: instrumentation must never page me. If the tracker
  is the reason a training job died at step 27, that's an outage I caused for nothing.
  Best-effort, swallow-everything semantics are non-negotiable.
- **AAAI:** For a paper, the local JSONL artifact matters more than the W&B dashboard —
  reviewers need a reproducible file, not a login-walled URL. The fallback should be the
  *canonical record*, W&B a convenience mirror.
- **RLE:** I want one call site. If I have to learn wandb's API in train and a different
  one in eval, I won't instrument eval at all. Same 3 methods everywhere or it rots.
- **DOL:** Zero new hard dependencies. Our boxes don't all have wandb and I won't add it
  to the critical path. An env var to force the backend per environment is mandatory.

## Round 2 — react to another persona (genuine disagreement)
- **AAAI vs SMR:** I disagree with SMR's framing that W&B is the point. If the metric of
  record is the W&B project, your experiment is *not reproducible* — accounts get deleted,
  projects go private. The JSONL must be primary; treat W&B as lossy.
- **RLE vs PSRE:** PSRE's "swallow everything" worries me. If every error is silently
  eaten, I'll think I'm logging to W&B for a week and have nothing. I want best-effort on
  *log()*, but `init()` should at least *report* (print) which backend it actually chose,
  so a misconfig is visible without being fatal.
- **DOL vs SMR:** SMR wants rich config including "reward version". Fine, but don't let the
  shim try to introspect git SHAs or env — that's how trackers grow tendrils into core.
  The caller passes a plain dict; the shim stays dumb.
- **PSRE vs DOL:** DOL's per-env env var is right, but I push further: there must be a
  `none` backend for prod/CI where I want the call sites to exist but write nothing.
- **SMR vs AAAI:** I'll concede JSONL-primary, but then the JSONL schema must be *typed*
  (a `_type` discriminator) so I can parse meta vs metric vs summary without guessing.

## Round 3 — synthesis
Consensus landed on:
1. **JSONL is canonical**, W&B/Trackio is an optional mirror (AAAI + SMR).
2. **Best-effort on log/summary/finish**, but `init()` resolves and *exposes* the backend
   name on the handle (`run.backend`) and may print it (RLE + PSRE).
3. **One 3-method API** across train and eval (RLE), backed by env-var selection incl.
   `none` (DOL + PSRE).
4. **Typed JSONL** with `_type` in {meta, metric, summary} (SMR).
5. Shim stays **dumb**: caller passes config dicts; no git/env introspection (DOL).
