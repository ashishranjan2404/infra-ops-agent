# D4 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — correctness / safety semantics
**Problem found:** `gate_plan` builds a fresh `World` but never advances it, while
`rex.harness.run_plan` advances the world before gating. Does that change `is_safe`'s
decisions? Audit: the Layer-2 traps depend on `build_state`, which derives signals from
the *scenario* + `applied_tools` (mem_leak_active, draining_last_ready_node,
at_replica_limit, recent_deploy) — NONE read settled world metrics. Layer-1 reads
`forbidden_categories` (static). So gating is independent of world settling. **Resolution:**
correct as-is; documented in the docstring. `rollout_reward` still uses the full `run_plan`
for the base reward so the resolution signal is real.

## Engineer B — training/reward design
**Problem found:** the penalty could be gamed — a model could propose ZERO actions to dodge
any penalty (reward = base, safe_fraction = 1.0). Is that a reward hack? Audit: an empty plan
gets `base_reward` from the env, which for an UNRESOLVED incident is low/0. So doing nothing
is only "rewarded" when nothing is the correct answer (the escalation case), which is exactly
right. The penalty never *exceeds* the value of actually solving the incident.
**Problem found:** if `unsafe_penalty` is large relative to the resolve bonus, the model
learns excessive caution. **Resolution:** default 0.25 << resolve weight (~0.45 in
rex.scoring); knob is tunable; documented in YAML + critique.

## Engineer C — integration / reproducibility
**Problem found:** the `.patch` assumes `run.plan` and `run.scenario_name` exist on a HUD
run object — they may not. If absent, `_shape` silently falls back to `run.reward`, which
would silently disable the whole feature. **Resolution:** `_shape` wraps in try/except and
documents the integration dependency explicitly (the env must surface the plan); flagged in
07/09 as the real wire-in risk, not hidden.
**Problem found:** path math — file is 4 dirs below repo root; an off-by-one breaks standalone
import. **Resolution:** fixed to `*([os.pardir]*4)` and tested both standalone + via pytest.

## Final filtered spec deltas
- Keep `gate_plan` world-free; document why it's sound. (A)
- Keep default `unsafe_penalty=0.25 << resolve weight`; document anti-hack reasoning. (B)
- `_shape` try/except + explicit integration-dependency note; verify both import paths. (C)
