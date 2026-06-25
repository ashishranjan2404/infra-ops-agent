# H3 — Containerize the eval pipeline — SUMMARY

**Status: completed** (real Dockerfile + .dockerignore + entrypoint + offline
smoke delivered and validated; actual `docker build` blocked — no Docker
daemon on host).

## What was delivered
A reproducible CPU-only Docker image spec for the REx SRE-Degrees eval
pipeline, grounded in `requirements-rex.txt` (pyyaml, requests, matplotlib,
numpy — the GPU/SFT stack in `requirements.txt` is deliberately excluded).

Artifacts (`experiments/ralph_outputs/H3/artifacts/`):
- `Dockerfile` — `python:3.13-slim`, requirements-first cache ordering,
  non-root user, `PYTHONPATH=/app`, exec-form `ENTRYPOINT` + `CMD ["smoke"]`.
- `.dockerignore` — trims context (VCS/venv/secrets/heavy trees + the GPU
  `requirements.txt`); negation chain so the build can read the H3
  entrypoint/smoke.
- `entrypoint.sh` — `smoke | eval [args] | shell | <exec>` dispatch; `eval`
  runs `python3 -m rex.eval_pass_at_k`; warns when no model key is set.
- `smoke_eval.py` — offline, no-key health check: imports the live eval module
  surface and loads the 42 real CIDG scenarios; the default `docker run`.

## Usage
    docker build -f experiments/ralph_outputs/H3/artifacts/Dockerfile -t rex-eval:latest .
    docker run --rm rex-eval:latest                         # offline smoke
    docker run --rm -e HUD_API_KEY="$HUD_API_KEY" \
      -v "$PWD/experiments/results:/app/experiments/results" \
      rex-eval:latest eval --model glm-5p2 --per-family 2 --seeds 3

## Validation (no Docker daemon -> structural + native)
- Offline smoke: exit 0, real imports, 42 scenarios, pass@k math correct.
- `bash -n entrypoint.sh`: OK; `py_compile smoke_eval.py`: OK.
- hadolint-style structural: 10/10 PASS; all COPY sources exist.

## Blocker
`docker build`/`docker run` not executed — Docker absent on host. Image is
structurally validated and the entrypoint/smoke run green natively.

## Shared-core safety
No shared core file edited. All artifacts are task-namespaced under
`experiments/ralph_outputs/H3/`.
