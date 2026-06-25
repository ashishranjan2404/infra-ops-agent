# D4 — 09 Critique (honest)

## What a reviewer will attack
1. **No training curves.** The headline ask is "run RFT with the harness in the loop," and I
   did NOT produce a learning curve showing the in-loop harness improves safety/return. The
   backend (HUD/Tinker GRPO) needs a forked Qwen slug + HUD_API_KEY + `.venv-hud` and exceeds
   the ~15 min cap. Mitigation: a fully tested reward path + a documented wire-in, and an
   honest blocker instead of fabricated numbers. Still, this is the biggest weakness.

2. **The wire-in is unproven end-to-end.** `train_rft_harness_in_loop.patch` depends on the
   HUD run object exposing `run.plan` and `run.scenario_name`. If the env only returns a
   scalar reward, `_shape` silently falls back to the raw reward — the feature would be a
   no-op without anyone noticing. Honest gap: the env-side change to surface the plan is NOT
   implemented here (it's `hud_env_v2.py`, a core file I must not edit), only described.

3. **Reward shaping ≠ novelty.** A reviewer can call this "potential-based-ish penalty, not
   research." Fair. The contribution is operational, not algorithmic: the SAME production
   `is_safe` used for eval is now used inside rollout collection, so the model is trained
   against the exact safety constraint it's evaluated on — no proxy drift.

4. **Gating doesn't advance the world.** I argue (05) that `is_safe`'s decisions don't read
   settled metrics, so a world-free gate is sound. If a future Layer-3 trap DID read live
   metrics, `gate_plan` would diverge from `run_plan`. The `rollout_reward` path avoids this
   by using full `run_plan` for the base reward, but `gate_plan`'s shortcut is a latent
   coupling risk worth a regression test if the harness grows.

5. **Penalty calibration is unvalidated.** `unsafe_penalty=0.25` is a guess relative to the
   resolve weight; without a training run I can't show it's neither too weak (ignored) nor too
   strong (pathological under-action). Tunable, but untuned.

## What's genuinely solid
- The reward path is real, runs the production harness + sim, and is unit-tested incl. the
  trap-block, penalty-scaling, and floor-clamp edges.
- Honest about the blocker; no invented results.
- Zero shared-core edits; the proposed change is a reviewable `.patch`.

## If I had more compute
Fork the Qwen slug, apply the patch (+ the one-line `hud_env_v2.py` plan-surfacing change),
run `train_rft_v2.py --reset-head` for ~30 steps logging `reward_std` AND a new
`mean_unsafe_per_rollout`, and show the unsafe-action rate falling while return holds — the
curve that would close attack #1.
