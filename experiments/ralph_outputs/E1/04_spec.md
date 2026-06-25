# 04 — Technical Spec

## A. Inventory data structure (`grpo_inventory.json`)
```json
{
  "generated": "<ISO8601>",
  "repo": "git@github.com:ashishranjan2404/infra-ops-agent.git",
  "head_commit": "<sha>",
  "in_repo_grpo_assets": [
    {"path": "opensre-traj/train_rft.py",    "role": "GRPO/RFT driver v1 (HUD Tinker, rollouts->fwd/bwd)", "tracked": "untracked"},
    {"path": "opensre-traj/train_rft_v2.py", "role": "GRPO v2 driver (P0 judge in reward, within-group spread logging, --reset-head)", "tracked": "untracked"},
    {"path": "opensre-traj/hud_env_static.py","role": "training env for v1", "tracked": "untracked"},
    {"path": "opensre-traj/hud_env_v2.py",   "role": "training env w/ deterministic-judge reward (v2)", "tracked": "untracked"},
    {"path": "opensre-traj/runs/train_qwen3-8b.jsonl",     "role": "v1 run log (mean_reward only)", "tracked": "untracked"},
    {"path": "opensre-traj/runs/train_qwen3-8b_v2.jsonl",  "role": "v2 run log (mean_reward + reward_std)", "tracked": "untracked"},
    {"path": "opensre-traj/runs/train_qwen3-30b.jsonl",    "role": "v1 30B run log", "tracked": "untracked"},
    {"path": "rex/scoring.py",        "role": "in-repo deterministic judge (reward parity reference)", "tracked": "tracked"},
    {"path": "rex/eval_pass_at_k.py", "role": "cascade pass@k eval entrypoint (the claim-gate runner)", "tracked": "tracked"}
  ],
  "missing_for_claim2": ["fireball_training_corpus", "fireball_trained_model_slug_or_checkpoint", "fireball_run_trajectories_or_grader", "repro_metadata"],
  "branch_search": {"local": [...], "remote": [...], "grpo_named": []}
}
```

## B. Expected payload from Wenji's branch (manifest schema)
Two tiers. **Minimal sufficient** = everything needed to replicate Claim 2.
| key | required | accept-either | description |
|-----|----------|---------------|-------------|
| `fireball_corpus` | yes | — | the D&D/Fireball trajectory SFT data (`incidents.jsonl` or pointer + sha256) |
| `parity_payload` | yes | trajectories **OR** grader | raw per-rollout trajectories (re-gradable by `rex/scoring.py`) OR Wenji's grader source |
| `model_provenance` | yes | — | base model id + fireball-trained slug + re-fork/adapter export recipe |
| `run_log` | yes | — | the GRPO run jsonl (step, reward, spread) |
| `grpo_driver` | no | — | her training script (we have an equivalent shape; include for diff) |
| `repro_metadata` | fast-follow | — | seed, step count, lr, group size, data sha256 |

## C. Verifier contract (`verify_grpo_push.py`)
- Signature: `python3 verify_grpo_push.py [--repo-root PATH]` → exit 0 if gate-1 passes, 2 if blocked (branch not present / payload incomplete), 1 on internal error.
- Pure stdlib, **read-only** (no writes outside stdout, no network, no git mutation).
- Checks:
  1. `branch_present`: any local/remote ref or directory matching `*grpo*`/`*fireball*` beyond what inventory recorded as pre-existing.
  2. `corpus_present`: a file matching `*fireball*`/`incidents.jsonl` exists and is non-empty.
  3. `parity_payload_present`: trajectories file (has per-rollout records) OR a grader `.py`.
  4. `model_provenance_present`: a manifest/README naming a base model + slug.
  5. `secret_scan`: grep candidate added files for `HUD_API_KEY`, `sk-`, `AKIA`, `-----BEGIN`.
  6. `size_scan`: warn on any added file > 25 MB not under Git LFS.
- Prints a per-check table + overall PASS/BLOCKED + the gate-2 next command.
- Test cases:
  - T1 (today / nothing pushed): all data checks fail → exit 2, message "branch not pushed yet".
  - T2 (synthetic fixture w/ corpus+trajectories+manifest, no secrets): gate-1 PASS → exit 0.
  - T3 (fixture containing `HUD_API_KEY=...`): secret_scan FAIL → exit 2.

## D. File formats
- All `.md` deliverables: GitHub-flavored markdown.
- `grpo_inventory.json`: valid JSON (parseable by `json.load`).
- `verify_grpo_push.py`: importable + `python3 -m py_compile` clean.

## E. API contract — gate-2 (documented, not run here)
`python3 -m rex.eval_pass_at_k` over the cascade scenarios, three policies
(fireball-trained / opensre-trained / zero-shot), compare pass@1 by incident family.
Owned by us, runs *after* the push.
