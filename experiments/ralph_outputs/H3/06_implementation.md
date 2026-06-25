# 06 — Implementation

## Artifacts built (all under `experiments/ralph_outputs/H3/artifacts/`)
| File | Purpose |
|------|---------|
| `Dockerfile` | `python:3.13-slim`, installs `requirements-rex.txt`, copies the eval packages, non-root, `PYTHONPATH=/app`, exec-form `ENTRYPOINT` + `CMD ["smoke"]`. |
| `.dockerignore` | Shrinks build context; excludes VCS/venv/secrets/heavy trees + the GPU-stack `requirements.txt`; negation exceptions for the H3 entrypoint+smoke. |
| `entrypoint.sh` | `smoke | eval [args] | shell | <exec>` dispatch; warns when `eval` runs without a model key. |
| `smoke_eval.py` | Offline, no-key health check: imports the real eval module surface, loads the real bundled CIDG scenarios, exercises the pass@k / Wilson-CI math. |

## Grounding (no fabrication)
- Deps come straight from `requirements-rex.txt` (pyyaml, requests,
  matplotlib, numpy). The GPU/SFT stack (`requirements.txt`: unsloth/trl) is
  deliberately excluded.
- The live eval is `python3 -m rex.eval_pass_at_k`
  (`--model --conditions --per-family --seeds --frontier`), confirmed by
  reading `rex/eval_pass_at_k.py:242-250`. Its imports
  (`agent.llm`, `rex.harness/loop/scoring/tree/ablation`,
  `experiments/compute_pass_at_k.py`) dictate the COPY set.
- `__init__.py` at repo root is gone (git status) → NOT copied.

## How to use the image
```bash
# Build from repo root:
docker build -f experiments/ralph_outputs/H3/artifacts/Dockerfile -t rex-eval:latest .

# Offline health check (no secret needed; this is the default CMD):
docker run --rm rex-eval:latest               # == rex-eval:latest smoke

# Real eval (inject the gateway key at runtime; persist results via a volume):
docker run --rm -e HUD_API_KEY="$HUD_API_KEY" \
  -v "$PWD/experiments/results:/app/experiments/results" \
  rex-eval:latest eval --model glm-5p2 --per-family 2 --seeds 3
```

## Shared-core safety
No shared core file was edited. Everything new lives under the task-namespaced
`experiments/ralph_outputs/H3/` tree. (The `.dockerignore` excludes
`experiments/results/` from the *build context* only — that runtime dir is
recreated by the eval inside the container, or bind-mounted to persist.)
