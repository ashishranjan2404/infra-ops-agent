"""D3 unit tests for same-scenario GRPO group batching."""
import math

from same_scenario_groups import (
    ScenarioGroup,
    grpo_advantages,
    group_rollouts_by_scenario,
    gradient_variance_reduction_factor,
)


class _Run:
    """Minimal stand-in for a HUD Run: has .task_id and .reward."""
    def __init__(self, task_id, reward):
        self.task_id = task_id
        self.reward = reward


def test_partition_groups_by_scenario():
    batch = [_Run("A", 1.0), _Run("B", 0.0), _Run("A", 0.5), _Run("B", 0.2), _Run("A", 0.9)]
    groups = group_rollouts_by_scenario(batch)
    by_id = {g.scenario_id: g for g in groups}
    assert set(by_id) == {"A", "B"}
    assert by_id["A"].size == 3
    assert by_id["B"].size == 2
    # first-seen ordering is deterministic
    assert [g.scenario_id for g in groups] == ["A", "B"]


def test_advantages_are_within_scenario():
    g = ScenarioGroup("A", [_Run("A", 1.0), _Run("A", 0.0), _Run("A", 0.5)])
    adv = g.advantages()
    assert math.isclose(sum(adv), 0.0, abs_tol=1e-9)         # GRPO baseline -> zero mean
    assert math.isclose(adv[0], 0.5) and math.isclose(adv[1], -0.5)


def test_degenerate_group_has_no_signal():
    g = ScenarioGroup("flat", [_Run("flat", 0.7), _Run("flat", 0.7)])
    assert g.is_degenerate
    assert all(a == 0.0 for a in g.advantages())


def test_normalized_advantages():
    adv = grpo_advantages([1.0, 0.0], normalize=True)
    # mean-centered then /std: +/- 1.0
    assert math.isclose(adv[0], 1.0) and math.isclose(adv[1], -1.0)


def test_drop_singletons():
    batch = [_Run("A", 1.0), _Run("A", 0.0), _Run("solo", 0.3)]
    groups = group_rollouts_by_scenario(batch, drop_singletons=True, min_group=2)
    assert {g.scenario_id for g in groups} == {"A"}


def test_variance_reduction_removes_between_scenario_term():
    # Two scenarios with IDENTICAL within-spread but very different difficulty.
    # easy scenario ~0.9, hard scenario ~0.1; within-spread 0.05 each.
    per_scenario = {
        "easy": [0.95, 0.85],   # mean 0.90
        "hard": [0.15, 0.05],   # mean 0.10
    }
    r = gradient_variance_reduction_factor(per_scenario)
    # mixed baseline (global mean 0.5) carries the 0.8 difficulty gap -> huge E[A^2];
    # same-scenario baseline removes it -> small E[A^2].
    assert r["same_msq"] < r["mixed_msq"]
    assert r["reduction_factor"] > 5.0
    # between-scenario var should equal Var(scenario means) = ((0.4)^2+(0.4)^2)/2 = 0.16
    assert math.isclose(r["between_scenario_var"], 0.16, abs_tol=1e-6)
    # within-scenario var = 0.05^2 = 0.0025
    assert math.isclose(r["within_scenario_var"], 0.0025, abs_tol=1e-6)


def test_advantage_sign_corruption_under_mixing():
    """The mechanism, made concrete: a WORSE rollout on the easy scenario still
    gets a POSITIVE advantage under a mixed baseline, and a BETTER rollout on the
    hard scenario gets a NEGATIVE advantage — the gradient pushes the wrong way."""
    pooled = [0.85, 0.95, 0.05, 0.15]      # easy:[0.85,0.95], hard:[0.05,0.15]
    global_mu = sum(pooled) / len(pooled)  # 0.5
    mixed_adv = [r - global_mu for r in pooled]
    # easy-scenario worse rollout (0.85) -> mixed adv +0.35 (WRONG: it's the weaker of the two)
    assert mixed_adv[0] > 0
    # hard-scenario better rollout (0.15) -> mixed adv -0.35 (WRONG: it's the stronger of the two)
    assert mixed_adv[3] < 0
    # same-scenario fixes both signs:
    easy_adv = grpo_advantages([0.85, 0.95])
    hard_adv = grpo_advantages([0.05, 0.15])
    assert easy_adv[0] < 0 and easy_adv[1] > 0     # 0.85 worse than 0.95 -> negative
    assert hard_adv[0] < 0 and hard_adv[1] > 0     # 0.15 better than 0.05 -> positive
