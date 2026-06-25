# Wenji GRPO Branch — Expected Payload Manifest

Repo: `git@github.com:ashishranjan2404/infra-ops-agent.git`
Unblocks: **Claim 2 (Fireball transfer beats OpenSRE-only GRPO on cascade incidents).**

## What ALREADY exists in-repo (do NOT re-push — see `grpo_inventory.json`)
- GRPO drivers: `opensre-traj/train_rft.py`, `opensre-traj/train_rft_v2.py`
- Training envs: `opensre-traj/hud_env_static.py`, `opensre-traj/hud_env_v2.py`
- Deterministic judge / parity reference: `rex/scoring.py`, `hud_env_v2.py`
- Cascade eval entrypoint: `rex/eval_pass_at_k.py`
- Existing run logs: `opensre-traj/runs/train_qwen3-8b*.jsonl`, `train_qwen3-30b.jsonl`
  (these are **mean_reward scalars only** — NOT enough to verify reward parity).

So the branch only needs to ADD what is genuinely missing below.

## Minimal sufficient payload (required to replicate Claim 2)
| key | required | accept-either | notes |
|-----|----------|---------------|-------|
| **Fireball corpus** | ✅ | — | the D&D/Fireball trajectory SFT data (`incidents.jsonl` or external pointer + `sha256`). Use Git LFS / pointer if > 25 MB. |
| **Parity payload** | ✅ | raw trajectories **OR** grader | EITHER per-rollout trajectories so we re-grade with `rex/scoring.py`, OR your grader source. A scalar `mean_reward` log alone is **insufficient**. |
| **Model provenance** | ✅ | — | base model id (e.g. `Qwen/Qwen3-8B`) + the fireball-trained HUD slug **and** a re-fork/adapter-export recipe (slugs are ephemeral). |
| **GRPO run log** | ✅ | — | the run `*.jsonl` (step, reward, spread) for the Fireball run and the OpenSRE-only baseline run you compared against. |

## Nice-to-have (fast-follow, don't block the push)
- Your GRPO driver script (we have an equivalent; include for diff).
- Repro metadata: seed, step count, lr, group size, data sha256.

## Drop-in manifest the verifier reads
Add `E1_MANIFEST.json` at repo root (or `opensre-traj/`) so verification is filename-agnostic:
```json
{
  "base_model": "Qwen/Qwen3-8B",
  "fireball_slug": "<hud-fork-slug>",
  "checkpoint_pointer": "<lfs path or url, optional if slug live>",
  "parity_payload": "trajectories",
  "parity_path": "opensre-traj/fireball/rollouts.jsonl",
  "run_log": "opensre-traj/runs/train_fireball_qwen3-8b.jsonl",
  "grpo_driver": "opensre-traj/train_fireball.py",
  "fireball_corpus": "opensre-traj/fireball/incidents.jsonl",
  "fireball_corpus_sha256": "<hash>",
  "seed": 0, "steps": 30, "group": 6, "lr": 1e-5
}
```

## Parity reference (pinned)
`hud_env_v2.py` + `rex/scoring.py` (the v2 / deterministic path). v1 `train_rft.py` used a
different reward and is **not** the parity reference.
