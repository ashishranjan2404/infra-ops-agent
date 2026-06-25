# F8 — Reproducibility Checklist · 01 Plan

## Objective
Produce a real, AAAI/NeurIPS-style reproducibility checklist for the SRE-Degrees /
REx project, grounded in the **actual** repo layout (`rex/`, `scenarios/`,
`opensre-traj/`, `experiments/`). Honestly state, per item: what is **available**,
what is **seeded/deterministic**, and what is **blocked** (and why). No aspirational
claims — every "yes" must be backed by a file path or command that exists today.

## Approach
1. Inventory the four axes a reviewer cares about:
   - **Code** — is the pipeline runnable from a fresh clone? deps pinned? entrypoints?
   - **Data** — are the scenarios / trajectories committed and versioned? provenance?
   - **Model weights** — closed APIs vs. open fine-tuned checkpoints; are forks reproducible?
   - **Randomness** — seeds, deterministic judges, sources of nondeterminism (LLM sampling).
2. Map each axis to concrete repo evidence already verified:
   - Seeds: `rex/tree.py:30` (`random.Random(seed)`), `rex/eval_pass_at_k.py` (`--seeds`),
     `rex/ablation.py` (`SEEDS`, 3 seeds).
   - Deterministic scoring: `rex/scoring.py:79` `deterministic_judge`, `mechanism_score`.
   - Data: `opensre-traj/out/hud_trajectories.jsonl` is **committed**; the 53
     `scenarios/cidg/generated/*.yaml` are **untracked** (gap).
   - Weights: closed models (Claude/GPT/Gemini via `agent/models.py` roster) are
     API-pinned by version string but not weight-reproducible; open training is
     `opensre-traj/train_rft.py` (HUD Tinker / Qwen fork) — needs HUD_API_KEY + GPU.
   - Env: Python 3.13.7, `requirements-rex.txt` (runtime) vs `requirements.txt` (GPU/SFT).
3. Fill out a standard checklist (the NeurIPS "Reproducibility Checklist" + AAAI
   reproducibility-policy items) as a markdown artifact with explicit
   AVAILABLE / SEEDED / BLOCKED tags and evidence pointers.
4. Add a small `verify_repro.py` scaffold that mechanically checks the *claimed*
   facts (deps importable, seeded modules present, committed-data check, env vars),
   so the checklist is self-auditing rather than prose-only.

## Files to create (all task-namespaced — no shared-core edits)
- `experiments/ralph_outputs/F8/artifacts/REPRODUCIBILITY_CHECKLIST.md` — the deliverable.
- `experiments/ralph_outputs/F8/artifacts/repro_manifest.json` — machine-readable per-axis status.
- `experiments/ralph_outputs/F8/artifacts/verify_repro.py` — runnable self-audit.
- The 10 step files + SUMMARY.md + result.json.

## Files to modify
- NONE. Per brief, do not touch `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`,
  or `ralph_status.json`. Where a real fix is needed (e.g. committing generated scenarios),
  document it as a recommendation, do not perform it.

## Dependencies
- Read-only repo inspection + `python3`/`git`/`yaml`. No network, no GPU, no live cluster.

## Risks
- **Overclaiming**: easy to mark "seeded" green when LLM sampling makes runs
  non-bit-reproducible. Mitigation: separate *control-flow determinism* (seeded)
  from *output determinism* (NOT reproducible for sampled LLMs) explicitly.
- **Stale evidence**: a path I cite could move. Mitigation: `verify_repro.py` checks
  paths at run time and the checklist records the git SHA it was generated against.
- **Scope creep**: a checklist can balloon. Keep to the standard item set.

## Success criteria
- Checklist covers code / data / weights / seeds, each item tagged AVAILABLE | SEEDED |
  PARTIAL | BLOCKED with a real file/command pointer.
- `repro_manifest.json` parses as valid JSON; `verify_repro.py` runs and emits a
  pass/fail report against the live repo.
- Every BLOCKED item names the concrete blocker (no GPU, no HUD key, closed weights,
  untracked data) rather than hand-waving.
