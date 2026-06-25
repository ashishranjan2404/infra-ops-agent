# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Default `docker run` is now the offline smoke** (`CMD ["smoke"]`), and the
   smoke imports the *real* eval modules + loads the *real* bundled CIDG
   scenarios. (AAAI+PSRE — this is load-bearing for reviewability.)
2. **Explicit reproducibility caveat** added to the README block in the
   Dockerfile / SUMMARY: image is reproducible *modulo PyPI dependency drift*
   because deps follow `requirements-rex.txt` ranges. (SMR+DOL compromise.)
3. **Secrets strictly runtime-injected** via `-e HUD_API_KEY=...`; the
   entrypoint warns (not crashes) when no key is present for `eval`. (PSRE.)
4. Kept **explicit per-package COPY** rather than `COPY . .`; `.dockerignore`
   is the safety net with negation exceptions for the H3 entrypoint/smoke.
   (RLE.)

## Critiques accepted
- Offline default smoke must use real imports/scenarios (AAAI/PSRE). ✔
- Tag base image, requirements-first caching, non-root (DOL/PSRE). ✔
- CPU-only, no GPU/SFT stack (RLE). ✔
- README must disclose dependency-range reproducibility limit (SMR). ✔

## Critiques rejected (with reason)
- **Hard `==` pins / digest-pinned base as a hard requirement (SMR R1).**
  Rejected as default for H3 scope: `==` pins rot and break rebuilds when a
  version is yanked; this is a research repo. Mitigation: the deps come
  straight from `requirements-rex.txt` (single source of truth) and the
  reproducibility caveat is documented. A future hardening note is left in
  `09_critique.md`. (Aligns with DOL R2.)

## Final deliverables
- `artifacts/Dockerfile` — tagged slim base, req-first layers, non-root,
  PYTHONPATH, exec-form ENTRYPOINT + `CMD ["smoke"]`.
- `artifacts/.dockerignore` — excludes VCS/venv/secrets/heavy trees; negation
  exceptions for H3 entrypoint + smoke.
- `artifacts/entrypoint.sh` — `smoke | eval | shell | <exec>` dispatch.
- `artifacts/smoke_eval.py` — offline, no-key health check (real imports).
