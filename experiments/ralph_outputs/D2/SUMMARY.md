# D2 — SUMMARY

**Task:** Run RFT with Qwen-14B on the opensre incident env (8B may be too small). Ground in
`opensre-traj/train_rft*.py`. ~15-min compute cap; deliver config/launcher + documented
blocker if backend/GPU unreachable; no fabricated metrics; no core edits.

## Outcome: COMPLETED deliverable + documented hard blocker
A literal Qwen-14B run is **impossible on this backend**: the HUD Tinker gateway exposes no
Qwen-14B (verified live via `hud models list`). Trainable Qwen rungs are dense 4B / 8B / 27B
and MoE 30B-A3B / 35B-A3B / 397B-A17B / 235B-A22B. So I delivered the runnable RFT launcher +
config for the **closest dense upgrade (Qwen3.6-27B)**, with a preflight that fails loud on a
missing base, plus the documented blocker.

## Artifacts (all task-namespaced; zero shared-core edits)
- `artifacts/train_rft_qwen14b.py` — additive launcher; imports `train_rft_v2` (untouched),
  adds base-selection + live gateway preflight. Exit-code-correct across 4 scenarios.
- `artifacts/qwen14b_train.config.yaml` — canonical flags + blocker record (requested
  `Qwen/Qwen3-14B`, available `false`, substitute `Qwen/Qwen3.6-27B`, MoE alt `Qwen3-30B-A3B`).
- `artifacts/runs/` — empty (no real run: blocker + compute cap).

## Evidence (real, reproducible)
- T4 `--preflight` -> exit 0, confirms substitute `Qwen/Qwen3.6-27B` IS trainable.
- T5 `--preflight --base Qwen/Qwen3-14B` -> exit 2, confirms 14B absent + prints BLOCKER.
- T1/T2/T3 compile / help / YAML-parse all PASS. Core trainer files unmodified (`git status`).

## Blocker (verbatim)
No Qwen-14B on the HUD Tinker gateway (2026-06-25); a real 30-step GRPO on the 27B substitute
is paid Tinker forward/backward (hours), outside the ~15-min cap. Launcher is one
`hud models fork Qwen/Qwen3.6-27B` away from a real run. No metrics fabricated.
