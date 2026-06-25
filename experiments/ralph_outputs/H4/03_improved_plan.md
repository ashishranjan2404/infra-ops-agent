# 03 — Improved plan

## What changed after the grill
1. **JSONL is the canonical record** (AAAI/SMR). The shim ALWAYS produces a parseable
   local file in the fallback path; W&B/Trackio is treated as an optional mirror, not the
   source of truth. -> Implemented: `JsonlRun` writes a complete typed log independent of
   any cloud backend.
2. **Typed JSONL schema** with a `_type` discriminator in {`meta`,`metric`,`summary`}
   (SMR). -> Implemented exactly.
3. **`run.backend` is exposed on the handle** so a misconfig is visible (RLE/PSRE).
   `select_backend()` is also a public function and the tests assert its resolution.
4. **`none` backend added** for CI/prod where call sites should be no-ops (PSRE/DOL).
5. **Shim stays dumb** — no git/env introspection; caller passes a plain config dict (DOL).
6. **Best-effort everywhere** but `init()` chooses deterministically and never silently
   "pretends" — the chosen backend is on the handle for the caller to print/assert.

## Critiques accepted
- AAAI's JSONL-primary stance — accepted; it's the reproducible artifact reviewers need.
- PSRE's never-page rule — accepted; blanket try/except on all I/O + backend calls.
- SMR's typed schema — accepted.
- DOL's no-tendrils rule — accepted; the shim does not read git or scrape env beyond the
  two documented selection vars (`EXPTRACK_BACKEND`, `EXPTRACK_DIR`, `WANDB_DISABLED`).

## Critiques rejected (with reason)
- RLE wanted `init()` to *print* the backend unconditionally. **Rejected as a default** —
  a library that prints on import is noisy in test suites and notebooks. Compromise: the
  backend is exposed on `run.backend` so the *caller* can print it (the integration guide
  shows this), keeping the library quiet.
- SMR's "log reward version automatically." **Rejected** — that's introspection the shim
  must not do (DOL). The caller passes `env`/reward-version in the config dict instead;
  the train patch does exactly this (`"env": ENV`).

## Final shape
`init(project,name,config,directory) -> Run` with `Run.{log,summary,finish}` + context
manager; backends wandb|trackio|jsonl|none; jsonl typed + canonical; everything best-effort.
