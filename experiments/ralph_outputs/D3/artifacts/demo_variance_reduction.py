"""D3 demo: quantify gradient-variance reduction from same-scenario GRPO groups.

Uses a synthetic-but-grounded reward distribution that mirrors the flat-baseline
diagnosis in train_rft_v2.py: ~0.5 mean reward, ~0.17 within-group spread, but
scenarios differ in difficulty. We show that pooling scenarios into one baseline
(mixed) inflates the advantage second moment (a proxy upper bound on per-sample
policy-gradient variance) vs same-scenario baselining.

Writes demo_variance_reduction.json. Pure stdlib; no HUD / network needed.
"""
import json
import os
import random

from same_scenario_groups import gradient_variance_reduction_factor, grpo_advantages

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_variance_reduction.json")


def main():
    random.seed(0)
    # 10 scenarios (matching train_rft_v2 --tasks 0..9), group size 6.
    # Each scenario has its own difficulty (mean), shared within-group std ~0.17
    # (the spread the v2 docstring reports was already present).
    n_scen, group = 10, 6
    within_std = 0.17
    # difficulties spread across [0.2, 0.8] -> realistic per-scenario reward means
    difficulties = [0.2 + 0.6 * i / (n_scen - 1) for i in range(n_scen)]

    per_scenario = {}
    for s, mu in enumerate(difficulties):
        rs = []
        for _ in range(group):
            r = max(0.0, min(1.0, random.gauss(mu, within_std)))
            rs.append(round(r, 4))
        per_scenario[f"scenario_{s}"] = rs

    metrics = gradient_variance_reduction_factor(per_scenario)

    # Illustrate sign corruption rate: fraction of rollouts whose advantage SIGN
    # flips between mixed-baseline and same-scenario-baseline.
    pooled = [r for rs in per_scenario.values() for r in rs]
    gmu = sum(pooled) / len(pooled)
    flips = 0
    total = 0
    for rs in per_scenario.values():
        same_adv = grpo_advantages(rs)
        for r, a_same in zip(rs, same_adv):
            a_mixed = r - gmu
            if a_same != 0.0 and (a_mixed > 0) != (a_same > 0):
                flips += 1
            total += 1
    sign_flip_rate = flips / total if total else 0.0

    result = {
        "setup": {
            "n_scenarios": n_scen,
            "group_size": group,
            "within_scenario_std_target": within_std,
            "difficulties": [round(d, 3) for d in difficulties],
        },
        "metrics": {k: (round(v, 6) if isinstance(v, float) else v)
                    for k, v in metrics.items()},
        "sign_flip_rate_mixed_vs_same": round(sign_flip_rate, 4),
        "interpretation": (
            f"Same-scenario grouping removes the between-scenario advantage "
            f"variance ({metrics['between_scenario_var']:.4f}), shrinking the "
            f"advantage second moment by {metrics['reduction_factor']:.2f}x "
            f"(from {metrics['mixed_msq']:.4f} to {metrics['same_msq']:.4f}). "
            f"{sign_flip_rate:.0%} of rollouts had their advantage SIGN corrected "
            f"— under mixed baselining their gradient pushed the wrong direction."
        ),
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
