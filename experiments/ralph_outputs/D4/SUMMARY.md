# D4 — SUMMARY

**Task:** Run RFT with the harness in the loop (Wenji's ask: LLM + harness, not LLM alone).
Implement a training-loop variant where the harness filters/penalizes unsafe actions during
rollout collection, with a unit test on the harness-in-loop reward path.

## Delivered (all task-namespaced under experiments/ralph_outputs/D4/artifacts/)
- harness_in_loop.py — reward path that reuses the REAL rex/harness.py::is_safe inside
  rollout collection. gate_plan filters unsafe actions; harness_in_loop_reward shapes
  reward = max(floor, base - unsafe_penalty*n_blocked); rollout_reward runs the real
  sim/engine.py for a base reward then shapes. Both effects (filter + penalize) active.
- harness_in_loop.yaml — shaping knobs + safety layers + a training scenario mix (with the
  held-out escalation case) + HUD/Tinker backend params.
- test_harness_in_loop.py — 7 unit tests on the reward path; 7/7 pass.
- train_rft_harness_in_loop.patch — documented minimal wire-in into
  opensre-traj/train_rft_v2.py (NOT applied — shared core file).

## Evidence
- pytest: 7/7. Standalone demo on gcp_service_control: trap scale_deployment blocked by the
  real is_safe, fix applied, sim resolves, shaped reward 1.0->0.75. YAML parses; all 6
  scenarios load. Both import paths verified.

## Blocker (honest)
Live GRPO training NOT run: needs HUD/Tinker forked Qwen slug + HUD_API_KEY + .venv-hud
(3.12) and exceeds the ~15 min compute cap. No fabricated curves. The reward path + wire-in
are the deliverable; the GPU run is the only blocked piece. Wire-in also needs the HUD env to
surface the parsed plan + scenario id per rollout (one-line hud_env_v2.py change, described).

## No shared core files edited.
