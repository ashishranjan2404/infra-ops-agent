# E1 — SUMMARY: Get Wenji's GRPO branch pushed to the repo

**Status: completed deliverable / downstream BLOCKED on a human action.**

This is a coordination task a repo worker cannot directly execute — I cannot push a branch that
lives only on Wenji's machine/HUD account. I delivered the maximal in-repo unblocking package.

## Key finding (verified, not assumed)
**No GRPO/Fireball/Wenji/RFT-named branch exists** locally or on `origin`
(`git@github.com:ashishranjan2404/infra-ops-agent.git`; remotes = origin/main,
origin/opensre-traj only). Confirmed via `git branch -a` + `git for-each-ref`. This is the
exact blocker for paper Claim 2 ("Fireball transfer beats OpenSRE on cascades"), corroborated
by `experiments/results/P7_fireball_status.md` and `PAPER_QUESTIONS.md` section 4.

## What GRPO already exists in-repo (so the push is additive only)
- GRPO/RFT drivers: `opensre-traj/train_rft.py` (v1), `train_rft_v2.py` (v2, deterministic-judge
  reward + within-group spread + `--reset-head`).
- Training envs: `hud_env_static.py`, `hud_env_v2.py`.
- Deterministic judge / parity reference: `rex/scoring.py`, `hud_env_v2.py`.
- Cascade eval entrypoint: `rex/eval_pass_at_k.py`.
- Run logs `runs/train_qwen3-8b*.jsonl` — mean_reward scalars only (insufficient for parity).

## What's genuinely missing (Wenji must push)
Fireball/D&D corpus, fireball-trained model slug/checkpoint, raw run trajectories OR her
grader (for reward parity), repro metadata.

## Deliverables (artifacts/)
- `grpo_inventory.json` — machine-generated inventory + branch search.
- `wenji_branch_manifest.md` — precise expected payload + `E1_MANIFEST.json` template.
- `integration_checklist.md` — two-gate merge checklist (push gate / claim gate) + hygiene.
- `request_message_to_wenji.md` — send-ready message + exact git recipe + expired-slug fallback.
- `verify_grpo_push.py` — read-only GATE-1 verifier; tested T1 (blocked/exit2 today),
  T2 (pass/exit0 on full fixture), T3 (secret leak/exit2).

## Verification
Verifier passed 3 scenarios; inventory JSON parses; verifier py_compiles; no shared-core files
edited (all output under `experiments/ralph_outputs/E1/`).
