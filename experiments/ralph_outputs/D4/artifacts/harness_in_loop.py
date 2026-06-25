"""D4 — Harness-in-the-loop RFT reward path (Wenji's ask: LLM + harness, not LLM alone).

The baseline RFT (opensre-traj/train_rft*.py) trains an open Qwen model on the
opensre incident env where the reward is computed AFTER the whole plan runs. Unsafe
actions (treating a ruled-out cause, draining the last Ready node, restarting through
an active mem leak, ...) only hurt via the downstream score. That is a weak,
delayed, and noisy training signal: a rollout can stumble into the right final state
while having proposed several dangerous actions along the way.

This module puts the REAL safety harness (rex/harness.py::is_safe) directly INSIDE
rollout collection. During a rollout we:

  1. dispatch each candidate action through `is_safe(action, state)` BEFORE it touches
     the world (exactly as `rex.harness.run_plan` already gates execution), and
  2. shape the reward so every blocked/unsafe action is PENALIZED, not silently
     dropped — the policy gradient sees the cost of proposing it.

The result is `harness_in_loop_reward(plan, scenario, base_score)`:

    shaped = base_score - UNSAFE_PENALTY * n_blocked   (clamped to >= floor)

plus a per-action breakdown so a training driver can do dense, per-step credit
assignment if its backend supports it (HUD/Tinker `trainer.step` consumes a scalar
reward per rollout; the scalar path is what we wire here, the breakdown is exposed
for backends that accept shaped/auxiliary signals).

It reuses the production harness verbatim — `is_safe`, `build_state`, `load_scenario`,
`run_plan` from rex.harness and `score_plan` from rex.scoring — so the safety
semantics in training are byte-identical to eval. No core file is modified.

Wire-in (documented, NOT executed here — training backend is HUD/Tinker, see blocker):

    from harness_in_loop import harness_in_loop_reward, HarnessInLoopConfig
    cfg = HarnessInLoopConfig(unsafe_penalty=0.25)
    shaped = harness_in_loop_reward(plan, scenario, base_score, cfg)
    # feed shaped.reward to trainer.step(...) instead of the raw env reward.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, asdict

# Make the repo importable when this file is run standalone from its artifacts dir.
# dirname(file)=.../D4/artifacts; +1 D4, +2 ralph_outputs, +3 experiments, +4 <repo root>.
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *([os.pardir] * 4)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from rex.harness import is_safe, build_state, load_scenario, run_plan, Scenario  # noqa: E402


@dataclass
class HarnessInLoopConfig:
    """Reward-shaping knobs for harness-in-the-loop training.

    unsafe_penalty   : reward subtracted per blocked/unsafe action proposed.
    reward_floor     : lower clamp so a catastrophic plan can't drive reward to -inf
                       (GRPO advantages stay well-conditioned).
    filter_unsafe    : if True, blocked actions are dropped before world execution
                       (the harness's native behavior); if False, they are still
                       counted/penalized but also dropped (is_safe never executes
                       an unsafe action regardless — this flag only documents intent).
    count_only_executed_block : if True, only actions the model actually proposed are
                       penalized (no penalty for actions never attempted).
    """
    unsafe_penalty: float = 0.25
    reward_floor: float = -1.0
    filter_unsafe: bool = True
    count_only_executed_block: bool = True


@dataclass
class ShapedReward:
    reward: float                 # the scalar fed to the trainer (shaped)
    base_reward: float            # the env/score reward before shaping
    n_proposed: int
    n_blocked: int
    n_applied: int
    penalty: float
    safe_fraction: float          # applied / proposed (1.0 == fully safe plan)
    per_action: list = field(default_factory=list)  # [{action, allowed, reason}]
    resolved: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def gate_plan(plan: dict, scenario: Scenario):
    """Run each action of a plan through the REAL is_safe harness, in order, against
    the same evolving state run_plan uses (so mem_leak_active etc. update as tools
    are applied). Returns (per_action, n_blocked, n_applied) WITHOUT needing the sim
    world to settle — this is the pure safety-gating decision the policy is graded on.

    NOTE: we rebuild state with `build_state` exactly like rex.harness.run_plan, but we
    do not advance the World here (gating is state-conditional on applied_tools, not on
    settled metrics), keeping this path cheap enough to run inside every rollout.
    """
    from sim.engine import World  # local import: only needed for state scaffolding
    world = World.from_spec(scenario.spec, inject=True)
    applied_tools: set = set()
    per_action = []
    n_blocked = n_applied = 0
    for a in plan.get("actions", []):
        ok, reason = is_safe(a, build_state(world, scenario, applied_tools))
        per_action.append({"action": a, "allowed": bool(ok), "reason": reason})
        if ok:
            applied_tools.add(a.get("tool", ""))
            n_applied += 1
        else:
            n_blocked += 1
    return per_action, n_blocked, n_applied


def harness_in_loop_reward(plan: dict, scenario: Scenario, base_reward: float,
                           cfg: HarnessInLoopConfig | None = None) -> ShapedReward:
    """Shape a rollout's reward using the in-loop safety harness.

    base_reward is whatever the env/score produced for the plan (e.g. rex.scoring
    .score_plan or the HUD env grader). We subtract `unsafe_penalty` per unsafe action
    the model PROPOSED, then clamp to `reward_floor`.
    """
    cfg = cfg or HarnessInLoopConfig()
    per_action, n_blocked, n_applied = gate_plan(plan, scenario)
    n_proposed = len(plan.get("actions", []))
    penalty = cfg.unsafe_penalty * n_blocked
    shaped = max(cfg.reward_floor, base_reward - penalty)
    safe_frac = (n_applied / n_proposed) if n_proposed else 1.0
    return ShapedReward(
        reward=shaped, base_reward=base_reward, n_proposed=n_proposed,
        n_blocked=n_blocked, n_applied=n_applied, penalty=penalty,
        safe_fraction=safe_frac, per_action=per_action,
    )


def rollout_reward(plan: dict, scenario_name: str,
                   cfg: HarnessInLoopConfig | None = None,
                   base_reward: float | None = None) -> ShapedReward:
    """End-to-end convenience: load the scenario, get a base reward (run the real
    sim via run_plan -> resolved as a 0/1 base if none supplied), then shape it.

    This is the function a training driver calls per rollout to obtain the scalar
    reward for `trainer.step`. It is deliberately self-contained and side-effect free.
    """
    cfg = cfg or HarnessInLoopConfig()
    scenario = load_scenario(scenario_name)
    if base_reward is None:
        result = run_plan(plan, scenario)
        base_reward = 1.0 if result["resolved"] else 0.0
        resolved = result["resolved"]
    else:
        resolved = base_reward >= 0.999
    shaped = harness_in_loop_reward(plan, scenario, base_reward, cfg)
    shaped.resolved = bool(resolved)
    return shaped


if __name__ == "__main__":
    # Tiny demo on a real scenario: a plan with one unsafe action gets penalized.
    demo = {"actions": [
        {"tool": "scale_deployment", "args": {"target": "service-control"}},  # trap
        {"tool": "modify_network_policy", "args": {"target": "service-control"}},  # fix
    ]}
    out = rollout_reward(demo, "gcp_service_control")
    import json
    print(json.dumps(out.to_dict(), indent=2, default=str))
