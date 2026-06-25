# F11 — 03 Improved Plan (post-grill)

## What changed vs 01
The grill converged on a **two-tier** appendix and a numeric reproduction tolerance. Concrete
revisions:

1. **Two evaluation tiers (NEW, central).**
   - **Tier A — Functional (offline, free, deterministic):** scenario-registry load + `floor_check`
     + `pytest tests/test_rex_deterministic_judge.py`. No credentials. This is the badge an
     evaluator can grant on a laptop in <1 min. Encoded in `smoke_ae.sh`.
   - **Tier B — Reproduced (online, costs API $, stochastic):** the full
     `python3 -m rex.eval_pass_at_k --conditions ... --frontier` sweep.
   Accepted RLE+DEV critique: do not sell the expensive stochastic sweep as the only/cheap repro.

2. **Numeric reproduction tolerance (NEW).** "Reproduced" = per-condition pass@1 lands inside the
   paper's reported Wilson 95% CI, *or* the two CIs overlap. Appendix states the exact seeds /
   per-family used so the CI width is comparable. Accepted REV+RLE.

3. **Honest substrate disclosure (NEW).** World = `sim/engine.py`, **deterministic given a fixed
   plan** (verified: identical plan → identical reward, see 07). Scenarios modeled on real
   postmortems but executed in-sim → an evaluator needs NO live cluster. Accepted PSRE+REV; I
   *reframed* "it's a sim" from a weakness (PSRE) to a reproducibility feature (REV).

4. **Availability via GitHub release → Zenodo DOI (CHANGED).** Pin a tag/commit; recommend minting
   a DOI from a tagged release rather than demanding a hand-built tarball. Accepted SR over REV's
   strict "Zenodo-only."

5. **Declared threats to reproduction (NEW section).** Gateway model drift (version the slug),
   API cost & wall-clock, sampling noise. Accepted PSRE+RLE.

6. **Self-checking artifacts (NEW).** `badge_claim_map.json` + `test_badge_map.py` assert the
   referenced repo files/flags exist, so the appendix can't silently rot. Accepted Round-3 ask.

## Rejected / deferred
- **Full Dockerfile (DEV).** Rejected as the *primary* hermeticity story: a container pins Python
  deps but NOT the LLM behind `agent/llm.call`, giving false hermeticity (PSRE's point). We pin
  `requirements-rex.txt` + Python 3.13 + the model slug instead, and note a container is optional
  for Tier A only. Documented, not built — out of scope and would over-engineer this appendix task.
- **Committing a Zenodo upload.** Out of scope for a worker; appendix gives the procedure.

## Unchanged from 01
File set, no-shared-core-edit rule, success criteria (1–4).
