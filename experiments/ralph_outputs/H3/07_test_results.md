# 07 — Test Results

Docker daemon is **absent** on this host (`docker not found`, `hadolint not
found`), so a real `docker build` could not be run. Validation was therefore:
(a) running the offline entrypoint/smoke natively, and (b) hadolint-style
structural checks + build-context existence checks. All passed.

## T1 — offline smoke, no API keys  → PASS
```
$ env -u HUD_API_KEY -u ANTHROPIC_API_KEY -u FIREWORKS_API_KEY \
      REX_REPO=$(pwd) python3 .../smoke_eval.py
[smoke] scenarios by family: {'simple': 12, 'cascade': 20, 'novel': 10}  (total=42)
[smoke] pass@2(n=4,c=2)=0.833  wilson95%=(0.150,0.850)
[smoke] OK — container healthy, deterministic eval path intact.
exit=0
```
Real imports of `rex.harness/scoring/loop` + `compute_pass_at_k` succeeded and
the 42 bundled CIDG scenarios loaded — the same module surface the live eval
uses.

## T2 — entrypoint syntax + dispatch  → PASS
`bash -n entrypoint.sh` → OK. Dispatch table routes
`smoke|eval|shell|<exec>` correctly.

## T3 — smoke compiles  → PASS
`python3 -m py_compile smoke_eval.py` → OK.

## T4 — hadolint-style structural (10 checks)  → 10/10 PASS
tagged base · deps from requirements-rex · `--no-cache-dir` · non-root USER ·
absolute WORKDIR · exec-form ENTRYPOINT · exec-form CMD · requirements copied
before source (cache) · GPU stack excluded in `.dockerignore` · no COPY of the
deleted root `__init__.py`.

## T5 — every COPY source exists  → PASS
`requirements-rex.txt, agent, rex, sim, experiments, scenarios` all present.

## Fixes applied during testing
- `wilson_ci` called with a proportion `p=0.5` (not a success count) after
  reading the real signature `wilson_ci(p, n, z=1.96)`.
- Removed `COPY __init__.py` (file deleted from repo root per git status).
- Added `.dockerignore` negation chain so the build can read the H3
  entrypoint/smoke despite excluding `experiments/ralph_outputs/`.
- Cleaned the stray `__pycache__` left by `py_compile`.

## Blocker
No Docker daemon → `docker build`/`docker run` not executed here. The Dockerfile
is structurally validated and the entrypoint+smoke run green natively; on any
host with Docker the documented `docker build`/`docker run` commands should work
unchanged.
