# 04 — Technical Spec

## Image
- Base: `python:3.13-slim` (host is 3.13.7).
- WORKDIR `/app`; `PYTHONPATH=/app`; non-root `appuser` (uid 10001).
- Env: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PIP_NO_CACHE_DIR=1`.

## Layer order (cache contract)
1. `COPY requirements-rex.txt` → `pip install -r requirements-rex.txt`
2. `COPY agent/ rex/ sim/ experiments/ scenarios/`
3. `COPY entrypoint.sh, smoke_eval.py` → chmod +x
4. create user, chown, `USER appuser`

## Entrypoint contract (`entrypoint.sh`)
```
entrypoint.sh smoke                 # offline health check (default CMD)
entrypoint.sh eval [args...]        # -> python3 -m rex.eval_pass_at_k args...
entrypoint.sh shell | bash          # interactive shell
entrypoint.sh <other> [args...]     # exec verbatim (escape hatch)
```
- `eval`: if none of HUD_API_KEY / ANTHROPIC_API_KEY / FIREWORKS_API_KEY set,
  print a WARNING to stderr and still exec (let the run surface its own error).
- `set -euo pipefail`.

## smoke_eval.py contract
- Reads repo root from `REX_REPO` env (default `/app`), inserts it +
  `<repo>/experiments` on `sys.path`.
- Imports (must all succeed, network-free):
  `compute_pass_at_k.{pass_at_k,wilson_ci,binary_pass}`,
  `rex.harness.scenarios_by_family`, `rex.scoring.{score_plan,failed_checks}`,
  `rex.loop.{build_prompt,parse_plan}`.
- Asserts `sum(scenarios_by_family().values()) > 0`.
- Asserts `0 <= pass_at_k(4,2,2) <= 1` and `wilson_ci(0.5,4)` returns `lo<=hi`.
- Prints family counts + the computed values. Exit 0 on success.

## API signatures relied upon (verified in repo)
- `pass_at_k(n:int, c:int, k:int) -> float`
- `wilson_ci(p:float, n:int, z=1.96) -> tuple`
- `binary_pass(reward:float, threshold=0.8) -> int`
- `scenarios_by_family() -> dict[str, list]`
- live eval CLI: `--model --conditions --per-family --seeds --max-workers
  --frontier --out`

## .dockerignore (key rules)
- Exclude: `.git`, `.claude/.factory/...`, `__pycache__`, venvs, `.env*`,
  `*.pem/*.key`, `site/ docs/ research/ gcp-bench/ mreal/ opensre-traj/
  skills/ runs/ rex/runs/ experiments/results/ experiments/ralph_outputs/`,
  `requirements.txt` (GPU stack), media, editor cruft.
- Negation exceptions (build needs them): the parent-dir chain down to
  `experiments/ralph_outputs/H3/artifacts/entrypoint.sh` and `smoke_eval.py`.

## Validation tests (since no docker daemon)
- T1: `python3 smoke_eval.py` exits 0 offline with no API keys.
- T2: `bash -n entrypoint.sh` (syntax).
- T3: `python3 -m py_compile smoke_eval.py`.
- T4: hadolint-style structural assertions over the Dockerfile (10 checks).
- T5: every COPY source path exists in the repo.
