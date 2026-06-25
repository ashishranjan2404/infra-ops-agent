"""D3 — Same-scenario GRPO group batching for opensre RFT.

THE FIX (third fix from Table 1): construct each GRPO group from rollouts of a
*single* scenario, so the group-relative advantage A_i = r_i - mean_group(r)
measures "which rollout was better on THIS incident" rather than soaking up
per-scenario difficulty.

Grounding (real code this addresses):
  opensre-traj/train_rft_v2.py docstring, lines 11-13:
    "(likely) GRPO groups spanning DIFFERENT scenarios so the advantage reflects
     per-scenario difficulty, not which rollout was better."
  opensre-traj/train_rft_v2.py:89-100 — the training loop does
    `ts.run(agent, group=args.group, job=session)` over a multi-task Taskset, then
    `trainer.step(batch, ..., group_size=args.group)`. When the Taskset holds K
    scenarios and the harness fills a group by drawing across the taskset, a group
    of size G can contain rollouts from different incidents. The advantage baseline
    (group mean) then mixes an easy scenario's high reward with a hard scenario's
    low reward, so the sign of the advantage tracks *scenario difficulty*, not
    rollout quality. That injects bias + variance into the policy gradient.

This module is ADDITIVE and imports nothing HUD-specific at module load, so it is
unit-testable without the .venv-hud / a live trainer. The training driver
(train_rft_same_scenario.py) imports HUD lazily.

Core API
--------
group_rollouts_by_scenario(batch, key=...) -> list[ScenarioGroup]
    Partition a flat list of rollouts into per-scenario groups.
grpo_advantages(rewards) -> list[float]
    Group-relative (mean-centered, optionally std-normalized) advantages.
gradient_variance_reduction_factor(per_scenario_rewards) -> dict
    Quantify how much same-scenario grouping shrinks the advantage baseline's
    variance vs a mixed-scenario baseline (the explanation, made numeric).
"""
from __future__ import annotations

import statistics as st
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Sequence


def _default_key(rollout: Any) -> str:
    """Best-effort scenario id from a HUD run / rollout / dict.

    Tries, in order: .task.id, .task_id, ["scenario"], ["task_id"], .scenario,
    falling back to a stable repr. Real HUD `Run` objects expose `.task`.
    """
    for attr in ("scenario_id", "scenario"):
        v = getattr(rollout, attr, None)
        if v is not None:
            return str(v)
    task = getattr(rollout, "task", None)
    if task is not None:
        for attr in ("id", "name"):
            v = getattr(task, attr, None)
            if v is not None:
                return str(v)
    tid = getattr(rollout, "task_id", None)
    if tid is not None:
        return str(tid)
    if isinstance(rollout, dict):
        for k in ("scenario_id", "scenario", "task_id", "id"):
            if k in rollout:
                return str(rollout[k])
    return repr(rollout)


def _reward_of(rollout: Any) -> float:
    if isinstance(rollout, dict):
        return float(rollout.get("reward", 0.0))
    return float(getattr(rollout, "reward", 0.0))


@dataclass
class ScenarioGroup:
    scenario_id: str
    rollouts: list = field(default_factory=list)

    @property
    def rewards(self) -> list[float]:
        return [_reward_of(r) for r in self.rollouts]

    @property
    def size(self) -> int:
        return len(self.rollouts)

    @property
    def mean_reward(self) -> float:
        rs = self.rewards
        return sum(rs) / len(rs) if rs else 0.0

    @property
    def reward_std(self) -> float:
        rs = self.rewards
        return st.pstdev(rs) if len(rs) > 1 else 0.0

    def advantages(self, normalize: bool = False, eps: float = 1e-8) -> list[float]:
        return grpo_advantages(self.rewards, normalize=normalize, eps=eps)

    @property
    def is_degenerate(self) -> bool:
        """A group with zero within-group spread yields all-zero advantages —
        no learnable signal. Same-scenario grouping does NOT fix a flat scenario;
        it only stops *cross*-scenario difficulty from masquerading as advantage."""
        return self.reward_std == 0.0


def group_rollouts_by_scenario(
    batch: Iterable[Any],
    key: Callable[[Any], str] | None = None,
    min_group: int = 2,
    drop_singletons: bool = False,
) -> list[ScenarioGroup]:
    """Partition a flat batch of rollouts into per-scenario groups.

    Order of scenarios is first-seen (deterministic). `drop_singletons` removes
    groups smaller than `min_group` (a singleton group has advantage 0 for its
    only member and contributes no GRPO signal)."""
    key = key or _default_key
    buckets: dict[str, ScenarioGroup] = {}
    for r in batch:
        sid = key(r)
        if sid not in buckets:
            buckets[sid] = ScenarioGroup(scenario_id=sid)
        buckets[sid].rollouts.append(r)
    groups = list(buckets.values())
    if drop_singletons:
        groups = [g for g in groups if g.size >= min_group]
    return groups


def grpo_advantages(
    rewards: Sequence[float], normalize: bool = False, eps: float = 1e-8
) -> list[float]:
    """GRPO group-relative advantage. A_i = r_i - mean(r) [ / (std(r)+eps) ].

    With a SINGLE scenario in the group, mean(r) is that scenario's own baseline,
    so A_i is a clean within-scenario ranking signal."""
    rewards = list(rewards)
    if not rewards:
        return []
    mu = sum(rewards) / len(rewards)
    adv = [r - mu for r in rewards]
    if normalize and len(rewards) > 1:
        sd = st.pstdev(rewards)
        if sd > eps:
            adv = [a / sd for a in adv]
    return adv


def gradient_variance_reduction_factor(
    per_scenario_rewards: dict[str, Sequence[float]],
) -> dict:
    """Make the 'reduces gradient variance' claim NUMERIC.

    Two baselining schemes for the SAME pooled rollouts:
      mixed : every rollout is centered by the GLOBAL pooled mean (what a
              scenario-mixing group does on average).
      same  : every rollout is centered by ITS OWN scenario mean.

    The policy-gradient estimator is g = E[A * grad logpi]. The advantage's
    second moment E[A^2] upper-bounds the per-sample gradient variance (grad
    logpi held fixed across schemes). We report E[A^2] under each scheme; the
    ratio is the variance-reduction factor.

    Decomposition (law of total variance over the pooled reward R, with scenario S):
      Var_mixed(A) = Var(R)            = E[Var(R|S)] + Var(E[R|S])
      Var_same(A)  = E[Var(R|S)]                       (between-scenario term removed)
    So same-scenario grouping deletes exactly the BETWEEN-scenario variance
    Var(E[R|S]) — the part driven by scenario difficulty, not rollout quality.
    """
    pooled: list[float] = []
    for rs in per_scenario_rewards.values():
        pooled.extend(rs)
    if not pooled:
        return {"mixed_msq": 0.0, "same_msq": 0.0, "reduction_factor": 1.0,
                "between_scenario_var": 0.0, "within_scenario_var": 0.0}
    global_mu = sum(pooled) / len(pooled)

    mixed_sq, same_sq, n = 0.0, 0.0, 0
    within_accum = 0.0
    scenario_means = {}
    for sid, rs in per_scenario_rewards.items():
        rs = list(rs)
        if not rs:
            continue
        s_mu = sum(rs) / len(rs)
        scenario_means[sid] = (s_mu, len(rs))
        for r in rs:
            mixed_sq += (r - global_mu) ** 2
            same_sq += (r - s_mu) ** 2
            n += 1
        within_accum += sum((r - s_mu) ** 2 for r in rs)
    mixed_msq = mixed_sq / n
    same_msq = same_sq / n
    within_var = within_accum / n
    between_var = mixed_msq - same_msq  # = Var(E[R|S]) by the decomposition above
    reduction = (mixed_msq / same_msq) if same_msq > 0 else float("inf")
    return {
        "mixed_msq": mixed_msq,
        "same_msq": same_msq,
        "reduction_factor": reduction,
        "between_scenario_var": between_var,
        "within_scenario_var": within_var,
        "n_rollouts": n,
        "n_scenarios": len(scenario_means),
    }


__all__ = [
    "ScenarioGroup",
    "group_rollouts_by_scenario",
    "grpo_advantages",
    "gradient_variance_reduction_factor",
]
