# 08 — Verification against success criteria

| Criterion (from 01) | Met? | Evidence |
|---|---|---|
| Real Dockerfile grounded in `requirements-rex.txt` | YES | `artifacts/Dockerfile` installs exactly that file; GPU stack excluded. |
| Real `.dockerignore` | YES | `artifacts/.dockerignore`, 1.2 KB, excludes VCS/venv/secrets/heavy trees + negation exceptions. |
| Small entrypoint that runs the eval | YES | `artifacts/entrypoint.sh` dispatches `eval -> python3 -m rex.eval_pass_at_k`. |
| Dockerfile passes hadolint-style checks | YES | T4: 10/10 PASS. |
| All build-context paths exist | YES | T5: all 6 present. |
| Offline smoke runs green, no key | YES | T1: exit 0, 42 scenarios, real imports. |
| `entrypoint.sh` passes `bash -n` | YES | T2: OK. |
| No shared-core edits | YES | only new files under `experiments/ralph_outputs/H3/`. |

## Are outputs real (not placeholder)?
Yes. The Dockerfile, `.dockerignore`, entrypoint, and smoke are all real,
runnable files. The smoke actually imports the live eval's modules and loads
the 42 real CIDG scenarios off disk — it is not a stub. The only thing NOT
executed is `docker build` itself, because no Docker daemon exists on this host
(documented blocker, not a fabrication).

## Honest gap
The image was not *built*. Build-time risks that structural checks can't fully
catch: a transient PyPI resolution failure, or a slim-base missing a system lib
some wheel needs. The chosen deps (pyyaml/requests/matplotlib/numpy) all ship
manylinux wheels for cp313, so this risk is low but non-zero.
