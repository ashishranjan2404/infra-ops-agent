# 06 — Implementation

This task is a **coordination/blocker** deliverable, not a model run. "Built" = a complete,
evidence-grounded coordination package plus a runnable, tested verifier.

## Artifacts created (all task-namespaced under `experiments/ralph_outputs/E1/artifacts/`)
1. **`grpo_inventory.json`** — machine-readable inventory of in-repo GRPO machinery, generated
   programmatically from `git` (tracked status, HEAD sha) + filesystem. Records that **no
   grpo/fireball/wenji/rft-named branch exists** on any local ref or on `origin`
   (confirmed via `git branch -a` and `git for-each-ref`; remotes = origin/main,
   origin/opensre-traj only).
2. **`wenji_branch_manifest.md`** — the precise minimal-sufficient + nice-to-have payload Wenji's
   branch must contain, parity-aware (trajectories OR grader), with a drop-in `E1_MANIFEST.json`
   template the verifier consumes. Pins parity to `hud_env_v2.py` + `rex/scoring.py`.
3. **`integration_checklist.md`** — two-gate merge checklist (push gate / claim gate) + secret &
   size hygiene + no-shared-core constraint.
4. **`request_message_to_wenji.md`** — send-ready message with an exact copy-paste git recipe and
   the expired-slug fallback path.
5. **`verify_grpo_push.py`** — read-only, stdlib-only GATE-1 verifier (presence, parse, secret
   scan, warn-only size scan), filename-agnostic via `E1_MANIFEST.json`, excludes pre-existing
   inventory + opensre target-domain trajectories. Documented exit codes (0 pass / 2 blocked /
   1 error).

## Inventory findings (the real state of GRPO in the repo)
- **GRPO/RFT drivers DO exist** (untracked on this branch): `opensre-traj/train_rft.py` (v1),
  `opensre-traj/train_rft_v2.py` (v2 w/ deterministic-judge reward, within-group spread,
  `--reset-head`). Training envs `hud_env_static.py` / `hud_env_v2.py` exist.
- **Existing run logs** (`runs/train_qwen3-8b*.jsonl`, `train_qwen3-30b.jsonl`) are
  **mean_reward scalars** — proof, in-repo, that a scalar log is insufficient for parity
  re-grading (motivates the trajectories-or-grader ask).
- **Eval entrypoint + deterministic judge are tracked & ready**: `rex/eval_pass_at_k.py`,
  `rex/scoring.py`.
- **Genuinely missing (the Fireball/Claim-2 gap):** the Fireball/D&D corpus, the
  fireball-trained model slug/checkpoint, the raw run trajectories (or Wenji's grader), and
  repro metadata. Corroborated by `experiments/results/P7_fireball_status.md` and
  `PAPER_QUESTIONS.md` §4 ("one run, not yet pushed").

## No shared-core edits
No file under `rex/`, `sim/`, `agent/`, `experiments/*.py`, or another task dir was modified.
Everything new lives under `experiments/ralph_outputs/E1/`. The proposed Wenji-side changes are
described in the manifest, not applied here.

## The honest blocker
This worker **cannot push a branch that exists only on Wenji's machine / HUD account**. The
deliverable is the maximal in-repo unblocking step: a verified inventory, a precise ask, a
mergeable checklist, a one-paste git recipe, and a verifier that gates the push when it lands.
