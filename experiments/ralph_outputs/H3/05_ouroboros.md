# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "Build Reproducibility"
**Problems found:**
- A1. Spec copied root `__init__.py` originally — but git status shows it was
  **deleted**. COPYing a missing file fails the build. → REMOVE that COPY.
- A2. `.dockerignore` excludes `experiments/ralph_outputs/` yet the Dockerfile
  COPYs `entrypoint.sh`/`smoke_eval.py` from there. Without negation
  exceptions the build can't find them. → ADD parent-chain `!` exceptions.
- A3. No reproducibility caveat surfaced to a user who only reads the
  Dockerfile. → Header comment documents the deps source + the GPU-stack
  exclusion.

## Engineer B — "Runtime / Security"
**Problems found:**
- B1. If `eval` is run with no key the container could hard-crash with an
  opaque traceback. → entrypoint prints an explicit WARNING naming the three
  accepted env vars, then execs.
- B2. Non-root user can't write bytecode into `/app` if perms wrong → set
  `PYTHONDONTWRITEBYTECODE=1` and `chown -R appuser /app`. Both present.
- B3. `experiments/results/` excluded from context, but the live eval *writes*
  results there at runtime inside the container (`RESULTS = .../results`).
  Excluding it from the *build context* is correct (don't bake host results);
  the dir is recreated at runtime by the eval. Confirmed not a bug, but
  noted: results are ephemeral unless a volume is mounted → document.

## Engineer C — "Reviewer / Scope"
**Problems found:**
- C1. The smoke must import the *same* modules the live eval imports, else a
  green smoke gives false confidence (the AAAI concern). → smoke imports
  `rex.harness`, `rex.scoring`, `rex.loop`, `compute_pass_at_k`. Done.
- C2. `wilson_ci` takes a *proportion* `p`, not a success count — an early
  draft passed `successes=2`. → fixed to `wilson_ci(p=0.5, n=4)`; verified
  against the real signature.
- C3. Over-engineering risk: no need for multi-stage build / healthcheck for
  H3's scope. Kept single-stage. Acceptable.

## Final filtered spec changes applied
- Removed `COPY __init__.py`. (A1)
- Added `.dockerignore` negation chain for the H3 entrypoint+smoke. (A2)
- Dockerfile header documents deps source + GPU-stack exclusion. (A3)
- entrypoint warns (not crashes) on missing key. (B1)
- smoke imports the real eval module surface; fixed `wilson_ci` call. (C1,C2)
- Document that `experiments/results/` is runtime-ephemeral (mount a volume to
  persist). (B3)
