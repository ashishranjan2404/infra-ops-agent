# 05 — Ouroboros (self-critique, 3 engineers)

## Engineer A — "the portability skeptic"
**Problems found:**
- A1. `$(abspath $(dir ...)/../../../..)` is brittle: if someone moves the
  Makefile, REPO silently points elsewhere and recipes `cd` into the wrong tree.
- A2. `cd $(REPO) && ...` in each recipe means a `cd` failure (typo'd REPO)
  still runs the second half in the *current* dir. Should be `&&` (it is) — but
  REPO itself is unchecked.
- A3. No guard that `python3`/`pytest` exist.

**Resolution:** Keep auto-detect but make REPO overridable (`REPO ?=`) so a user
can pin it — done. A `&&` already short-circuits on a failed `cd`. Tool-presence
guards are out of scope for a thin wrapper (the underlying scripts error
clearly); documented as a known limitation in 09 rather than gold-plated.

## Engineer B — "the reproducibility hawk"
**Problems found:**
- B1. `eval` defaults route through the HUD gateway → not runnable offline / in
  CI without a key. A reviewer typing `make eval` gets an auth error, not a
  result.
- B2. `figures` depends on data files (`rex/runs/curriculum.json`) that may not
  exist yet → `make figures` can crash on a fresh checkout.
- B3. `train` requires a forked slug that doesn't exist by default.

**Resolution:** These are inherent to the *operations*, not the Makefile — the
Makefile's job is to expose the real command, not to fake infra. Mitigations:
(a) the header documents `set -a; source ~/.zshrc; set +a` for the key;
(b) `eval-smoke` is the cheapest real path; (c) `validate-scenarios` and `test`
are fully offline and are the targets actually executed in 07. B2/B3 documented
as ordering prerequisites in 09, not hidden.

## Engineer C — "the make pedant"
**Problems found:**
- C1. `make -n figures` shows two `cd $(REPO) && ...` lines — fine, but if the
  first (`rex.chart`) fails in a real run, make aborts before the table PNGs.
  Acceptable (fail-fast) but worth stating.
- C2. The `help` awk/grep depends on every documented target having a `## `
  comment exactly once; an undocumented target silently vanishes from `help`.
- C3. `.PHONY` list must include every target or a stray file named like a
  target would shadow it.

**Resolution:** C1 accepted as intended fail-fast. C2: all targets carry a
single `## ` doc — verified by `make help` listing all 11. C3: `.PHONY`
enumerates all targets — verified.

## Final filtered spec
No structural change from 04. Confirmed: auto-REPO with override, offline
targets (`test`, `validate-scenarios`) are the proof path, gateway/infra targets
are honestly exposed + documented (not faked), all targets `.PHONY` + `## `
documented. Known limits (no tool guards, data/slug prerequisites) go in 09.
