# 01 — Plan: H3 Containerize the eval pipeline

## Objective
Make the REx SRE-Degrees eval pipeline reproducible via Docker: a real
`Dockerfile`, `.dockerignore`, and a small entrypoint that runs the eval —
grounded in `requirements-rex.txt` (the CPU runtime stack, NOT the GPU/SFT
stack in `requirements.txt`).

## Approach
- Base image `python:3.13-slim` (matches host Python 3.13.7).
- Install only `requirements-rex.txt` (pyyaml, requests, matplotlib, numpy).
- Copy the exact packages the live eval imports: `agent/ rex/ sim/
  experiments/ scenarios/`.
- Entrypoint dispatches subcommands:
  - `smoke` (default) — offline, no-key health check.
  - `eval [args]` — `python3 -m rex.eval_pass_at_k` (the real pipeline).
  - `shell` — debugging.
- Non-root user, `PYTHONPATH=/app`, cache-friendly layer ordering.

## Files to create (all task-namespaced, no shared-core edits)
- `artifacts/Dockerfile`
- `artifacts/.dockerignore`
- `artifacts/entrypoint.sh`
- `artifacts/smoke_eval.py` (offline validator the image runs by default)

## Dependencies / grounding
- `rex/eval_pass_at_k.py` is the entrypoint (`python3 -m rex.eval_pass_at_k`,
  args: `--model --conditions --per-family --seeds --frontier`).
- It imports `agent.llm.call`, `rex.harness`, `rex.loop`, `rex.scoring`,
  `rex.tree`, `rex.ablation`, and `experiments/compute_pass_at_k.py`.
- Live models need `HUD_API_KEY` (gateway). The deterministic judge +
  scenario loading + pass@k math are 100% offline → basis for the smoke.

## Risks
- Docker not installed on host → can only structurally validate (mitigate:
  hadolint-style manual checks + run the entrypoint/smoke natively).
- `.dockerignore` excludes `experiments/ralph_outputs/` but the build COPYs
  files from there → need negation exceptions.
- Root `__init__.py` was deleted (git status) → must not COPY it.

## Success criteria
- Dockerfile passes hadolint-style structural checks (tagged base, non-root,
  exec-form CMD/ENTRYPOINT, pinned deps, cache-ordered layers).
- All build-context paths referenced actually exist.
- `smoke_eval.py` runs green offline with no API key.
- `entrypoint.sh` passes `bash -n`.
