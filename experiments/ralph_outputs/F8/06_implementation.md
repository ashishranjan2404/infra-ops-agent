# F8 · 06 Implementation

## What I built (all task-namespaced; no shared-core files touched)
1. **`artifacts/REPRODUCIBILITY_CHECKLIST.md`** — AAAI/NeurIPS-style checklist, two
   reproducibility tiers (replay vs generation), 5 axes (code / data / weights / seeds /
   compute-license) + summary table + reviewer-facing limitations + happy-path repro
   commands. Every row carries a real `path:line` evidence pointer and an honest note.
2. **`artifacts/repro_manifest.json`** — machine-readable, 21 items, valid JSON,
   `counts` = {AVAILABLE:13, SEEDED:4, PARTIAL:3, BLOCKED:1}, sum == n_items == 21,
   stamped with git SHA `8a12b41…` and Python 3.13.7. Defines the two tiers.
3. **`artifacts/verify_repro.py`** — pure-stdlib self-audit that checks the *claims*
   against the live repo: path existence, importability, `git ls-files` committed-state,
   substring evidence (e.g. `random.Random(seed)` in `tree.py`), and an **empirical**
   `replay_double_grade` that imports `rex.scoring.deterministic_judge` and grades the
   first committed trajectory twice to prove stability. PARTIAL/BLOCKED emit `WARN` and
   are tallied but never silently pass; `git` failures degrade to `UNKNOWN`.

## Grounding facts established by direct inspection (not assumed)
- `opensre-traj/out/hud_trajectories.jsonl` is **committed** and holds **197 rollouts**
  (claude-opus-4-8 ×68, claude-haiku-4-5 ×68, kimi-k2p5 ×61) — measured, and *richer
  than DATA.md states* (doc drift flagged).
- `scenarios/cidg/generated/` (53 YAMLs) is **untracked** (`git status` → `??`) — a real
  fresh-clone reproducibility gap.
- Seeds: `rex/tree.py:30,67`, `rex/eval_pass_at_k.py --seeds`, `rex/ablation.py SEEDS=3`.
- Judges: `rex/scoring.py:79 deterministic_judge`, `:100 hybrid_judge`, `:141 _llm_judge`.
- Roster: `agent/models.py` with dated version strings (closed) + open recipe
  `opensre-traj/train_rft.py`.
- No committed checkpoint (`*.safetensors/*.pt/*.bin` absent).

## Proposed change to a shared core file (NOT applied — documented only)
Per the brief, the real fix for the untracked-scenario gap is to commit the artifacts.
I did **not** run it. Recommended commands for the maintainer:
```bash
# Option A: commit the artifacts
git add scenarios/cidg/generated/*.yaml
# Option B (preferred): commit the deterministic generator + seed that produced them,
#   so the corpus is reproducible-by-construction (mirror rex/curriculum.py:generate_simple).
# Also refresh opensre-traj/DATA.md to the measured 197-rollout / 3-model reality.
```

## Why no fabricated numbers
This task is a meta/governance deliverable. The only "results" are facts about the repo,
each backed by a command whose output is shown in `07_test_results.md`. Nothing requires
a live cluster, API key, or GPU, so there is no blocker on the deliverable itself; the
BLOCKED rows describe blockers *in the project being audited*, reported honestly.
