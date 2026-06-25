# D4 — 03 Improved Plan

## What changed after the grill
1. **Added `reward_floor` knob + clamp test** (DOL, RLE). Catastrophic plans clamp to a
   finite floor so GRPO advantages stay well-conditioned. — ACCEPTED.
2. **Wired path is the SCALAR shaped reward**; the per-action breakdown is exposed as an
   extra, not claimed as the trained signal (RLE). The `.patch` makes this explicit. — ACCEPTED.
3. **Penalty is per *proposed* unsafe action** even if the safe sub-plan still resolves —
   a plan that proposes a trap is strictly worse (SMR/PSRE synthesis). — ACCEPTED.
4. **Scenario mix with within-group spread** incl. the held-out `singleton_node_notready`
   escalation case (SMR, PSRE) — so the penalty term is actually learnable. — ACCEPTED.
5. **Evidence over curves**: unit tests + a standalone demo that run the REAL `is_safe` on
   real scenarios and show the real block reason; NO fabricated training numbers (REV/RLE). — ACCEPTED.
6. **Both import paths tested** (repo-root pytest + standalone) — fixed path math (DOL). — ACCEPTED.

## Rejected / deferred
- **REV's demand for training curves** — REJECTED for this task. The backend is HUD/Tinker
  GRPO requiring a forked Qwen slug, HUD_API_KEY, and the `.venv-hud` (3.12) interpreter; a
  real run exceeds the ~15 min compute cap. Fabricating curves violates the no-fake rule.
  Deliverable is the tested reward path + the documented wire-in + an honest blocker.
- **PSRE's "penalty must bite even on resolved plans, always"** — PARTIALLY rejected as
  framing: we penalize the *proposed* unsafe action, but we do NOT penalize a clean resolving
  plan that proposed nothing unsafe (that would teach pathological under-action). The
  `singleton` case shows under-action is correct *only* when no safe fix exists, and `is_safe`
  already encodes that.

## Final shape
- `harness_in_loop_reward(plan, scenario, base_reward, cfg) -> ShapedReward`.
- `rollout_reward(plan, scenario_name, cfg, base_reward=None)` end-to-end convenience
  (runs the real sim for a base reward when none supplied).
- YAML config; 7 unit tests; documented `.patch` wire-in into `train_rft_v2.py`.
