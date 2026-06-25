# F11 — 01 Plan: Artifact Evaluation Appendix (AAAI Artifact Track)

## Objective
Write a real, submission-ready **Artifact Appendix** for the AAAI artifact-evaluation
(AE) track covering the SRE-Degrees / REx benchmark + evaluation harness. It must let a
third-party evaluator: (1) obtain the artifact, (2) build/install it, (3) run the
benchmark + eval with concrete commands grounded in the *actual* repo, (4) know the
expected outputs and hardware, and (5) see a **badge-claim mapping** that ties each
AAAI/ACM badge (Available / Functional / Reproduced) to a runnable check.

## Why this matters
A paper claiming "REx beats best-of-N on novel SRE incidents" is only as credible as the
reviewer's ability to *re-run the number*. The appendix is the contract between the paper's
claims and the repo's commands. AAAI 2025+ uses the ACM-style badge taxonomy
(Artifacts Available, Artifacts Evaluated — Functional, Results Reproduced).

## Grounding (verified in repo)
- Eval entrypoint: `rex/eval_pass_at_k.py` — `python3 -m rex.eval_pass_at_k` with
  `--model --conditions --per-family --seeds --frontier`. THRESHOLD=0.8, pass@k + Wilson CI.
- Deterministic judge: `rex/scoring.py` (`REX_JUDGE_MODE=deterministic` default) → **no LLM
  needed for grading**, so the *grading* path is fully reproducible offline.
- Benchmark substrate: `scenarios/cidg/generated/*.yaml` (~33 registered scenarios across
  families `simple=12 / cascade=20 / novel=10`, verified via `scenarios_by_family()`).
- Pass@k estimator + Wilson CI: `experiments/compute_pass_at_k.py` (single source of truth).
- Floor check (`floor_check()`): empty-plan & trap both score < 0.8 → confirms no reward leak.
- Deps: `requirements-rex.txt` (pyyaml, requests, matplotlib, numpy). Python 3.13 verified.
- Offline-capable checks: floor_check, deterministic-judge unit tests
  (`tests/test_rex_deterministic_judge.py` — 12 passed), scenario registry load.
- Network-capable check: full pass@k sweep needs an LLM proposer via `agent/llm.call`
  (HUD_API_KEY / gateway). This is the only part that needs credentials.

## Files to create (all task-namespaced — NO shared-core edits)
- `experiments/ralph_outputs/F11/artifacts/APPENDIX.md` — the appendix itself.
- `experiments/ralph_outputs/F11/artifacts/badge_claim_map.json` — machine-readable
  badge→claim→command→expected mapping.
- `experiments/ralph_outputs/F11/artifacts/smoke_ae.sh` — a runnable, **offline** AE smoke
  script (registry load + floor check + deterministic-judge tests) that an evaluator can run
  with zero credentials to earn the *Functional* badge.
- `experiments/ralph_outputs/F11/artifacts/test_badge_map.py` — pytest that validates the
  badge map JSON schema + cross-checks that the commands it names point at real repo files.

## Dependencies
None new. Uses existing repo modules + stdlib + pytest (already used by repo tests).

## Risks
- **Fabricated numbers**: the appendix must NOT claim specific pass@1 figures (those require
  a paid LLM run). Mitigation: appendix states *where* the number is produced and gives the
  exact reproduction command; "Reproduced" badge instructions point to the live sweep, the
  "Functional" badge is satisfiable offline.
- **Drift**: commands could go stale. Mitigation: `test_badge_map.py` asserts the referenced
  files/flags exist, so the appendix is self-checking.

## Success criteria
1. APPENDIX.md has all AE-required sections (Abstract, Availability, Dependencies/HW,
   Setup, Evaluation workflow with real commands, Expected results, Badge mapping).
2. badge_claim_map.json validates against its own schema test (pytest green).
3. smoke_ae.sh runs offline and exits 0 on this machine.
4. No shared core file edited (git status shows only F11/ additions).
