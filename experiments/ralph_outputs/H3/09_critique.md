# 09 — Honest Critique

## What a reviewer will attack
1. **Not actually built.** No Docker on host → `docker build`/`docker run`
   never executed. Structural validation + native smoke runs are strong
   proxies, but a reviewer can rightly say "show me the image." This is the
   single biggest weakness. Mitigation: every COPY source verified to exist,
   deps are cp313 manylinux wheels, entrypoint/smoke run green natively.
2. **Reproducibility is range-based, not pinned.** Deps follow
   `requirements-rex.txt` ranges (`pyyaml>=6`, `numpy>=1.24`, ...). A rebuild
   months later may pull different minor versions. For a *paper artifact* the
   SMR persona's hard-pin concern is legitimate. Documented as a known limit;
   a `pip freeze`-derived lockfile or digest-pinned base would close it.
3. **Base image not digest-pinned.** `python:3.13-slim` is a moving tag.
   Stronger reproducibility would pin `python:3.13-slim@sha256:...`.
4. **Single-stage, no HEALTHCHECK, no SBOM.** Fine for H3 scope but a
   production reviewer would want a multi-stage build and a scan step.
5. **Results persistence.** The live eval writes to
   `experiments/results/` *inside* the container; without a bind mount those
   results vanish on `--rm`. Documented in 06, but easy to miss.

## What's genuinely solid
- Correct, minimal, CPU-only image grounded in the right requirements file.
- Cache-friendly layer ordering; non-root; secrets runtime-injected only.
- The default `docker run` is a real offline health check that exercises the
  live eval's import graph and the real scenario corpus — not a toy.

## Negative/blocked results (stated honestly)
- BLOCKED: actual image build/run (no daemon). Everything else completed.

## If I had more time
- Add `python:3.13-slim@sha256:<digest>` and a committed `requirements.lock`.
- Add a multi-stage build + `HEALTHCHECK CMD python3 smoke_eval.py`.
- Add a GitHub Actions job that builds the image and runs `smoke` on push.
