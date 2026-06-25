"""Render reward histograms with dip D / p annotations (matplotlib, no display)."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_dip_on_rewards import collect_condition_rewards, A1  # noqa: E402
from dip_test import dip_test  # noqa: E402

_, conds = collect_condition_rewards(A1)
order = ["zero_shot", "best_of_n", "retry_realistic", "rex_no_oracle", "rex"]
order = [c for c in order if c in conds]
fig, axes = plt.subplots(1, len(order), figsize=(3.2 * len(order), 3), sharey=True)
if len(order) == 1:
    axes = [axes]
for ax, c in zip(axes, order):
    r = np.asarray(conds[c])
    D, p = dip_test(r)
    ax.hist(r, bins=np.linspace(0, 1, 11), color="#3b6ea5", edgecolor="white")
    verdict = "BIMODAL" if p < 0.05 else "unimodal"
    ax.set_title(f"{c}\nD={D:.3f} p={p:.3f}\n{verdict}", fontsize=9)
    ax.set_xlabel("reward")
axes[0].set_ylabel("episodes")
fig.suptitle("A1/glm-5p2 per-episode reward distributions — Hartigan dip test", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.92])
out = os.path.join(HERE, "reward_dip_histograms.png")
fig.savefig(out, dpi=120)
print("wrote", out)
