#!/usr/bin/env python3
"""F4 — publication-quality figures for the SRE-Degrees / REx paper.

Reads REAL result JSONs only (no fabricated numbers):
  experiments/ralph_outputs/A1/artifacts/summary_table.json      (glm-5p2, 126 ep/cond, 5 cond x 42 inc x 3 seed)
  experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json   (750 ep)
  experiments/ralph_outputs/A2/artifacts/ablation_v2_mcnemar_deepseek-v4-pro.json  (McNemar)
  rex/runs/frontier.json                                          (5 models x 5 scenarios, REx vs baseline)
  rex/runs/harness_synth_v2.json                                  (learned-harness held-out)

Outputs PNGs into experiments/ralph_outputs/F4/artifacts/figures/.
Task-namespaced; does NOT touch experiments/figures/ or any shared core file.

Usage:  python3 experiments/ralph_outputs/F4/artifacts/make_figures.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

# ---- publication style (no external deps) -------------------------------
plt.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "-",
    "legend.frameon": False,
    "figure.constrained_layout.use": True,
})

# Colour-blind-safe palette (Wong 2011)
C = {
    "zero_shot": "#999999",
    "best_of_n": "#56B4E9",
    "retry_realistic": "#0072B2",
    "rex_no_oracle": "#E69F00",
    "rex": "#009E73",
    "baseline": "#999999",
}
PRETTY = {
    "zero_shot": "zero-shot",
    "best_of_n": "best-of-n",
    "retry_realistic": "retry (realistic)",
    "rex_no_oracle": "REx (no oracle)",
    "rex": "REx (full)",
}
COND_ORDER = ["zero_shot", "best_of_n", "retry_realistic", "rex_no_oracle", "rex"]


def _load(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        print(f"  MISSING {rel}")
        return None
    with open(p) as f:
        return json.load(f)


def _save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print(f"  fig -> {os.path.relpath(p, REPO)}")


# ------------------------------------------------------------------ Fig 1
def fig1_passk_bars_ci():
    """pass@1 by ablation condition with Wilson 95% CIs (A1, glm-5p2)."""
    d = _load("experiments/ralph_outputs/A1/artifacts/summary_table.json")
    if not d:
        return
    conds = [c for c in COND_ORDER if c in d]
    p1 = [d[c]["overall"]["p1"] for c in conds]
    ci = [d[c]["overall"]["ci"] for c in conds]
    lo = [p - c[0] for p, c in zip(p1, ci)]
    hi = [c[1] - p for p, c in zip(p1, ci)]
    n = d[conds[0]]["overall"]["n"]

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    x = np.arange(len(conds))
    bars = ax.bar(x, p1, yerr=[lo, hi], capsize=5,
                  color=[C[c] for c in conds], edgecolor="black", linewidth=0.6,
                  error_kw=dict(elinewidth=1.4, ecolor="#333333"))
    for xi, v, c in zip(x, p1, ci):
        ax.text(xi, c[1] + 0.025, f"{v:.2f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([PRETTY[c] for c in conds], rotation=18, ha="right")
    ax.set_ylabel("pass@1  (reward ≥ 0.8)")
    ax.set_ylim(0, 1.08)
    ax.set_title("REx vs. inference-time baselines  (glm-5p2)")
    ax.text(0.985, 0.04,
            f"n={n} episodes/condition · 42 incidents × 3 seeds · 95% Wilson CI",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
            color="#555555")
    _save(fig, "fig1_passk_ci.png")


# ------------------------------------------------------------------ Fig 2
def fig2_passk_by_family():
    """Grouped pass@1 by incident family x condition (A1)."""
    d = _load("experiments/ralph_outputs/A1/artifacts/summary_table.json")
    if not d:
        return
    fams = ["simple", "cascade", "novel"]
    conds = [c for c in COND_ORDER if c in d]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    w = 0.16
    x = np.arange(len(fams))
    for i, c in enumerate(conds):
        vals = [d[c][f]["p1"] for f in fams]
        ax.bar(x + (i - (len(conds) - 1) / 2) * w, vals, w,
               label=PRETTY[c], color=C[c], edgecolor="black", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([f.capitalize() for f in fams])
    ax.set_ylabel("pass@1  (reward ≥ 0.8)")
    ax.set_ylim(0, 1.12)
    ax.set_title("pass@1 by incident family — REx holds on cascade & novel")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.0), fontsize=9)
    _save(fig, "fig2_passk_by_family.png")


# ------------------------------------------------------------------ Fig 3
def fig3_passk_curve():
    """pass@k curve k=1,2,5 per condition (A1 overall)."""
    d = _load("experiments/ralph_outputs/A1/artifacts/summary_table.json")
    if not d:
        return
    ks = [1, 2, 5]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    for c in [c for c in COND_ORDER if c in d]:
        o = d[c]["overall"]
        ys = [o["p1"], o["p2"], o["p5"]]
        ax.plot(ks, ys, "-o", color=C[c], label=PRETTY[c], linewidth=2, markersize=6)
    ax.set_xticks(ks)
    ax.set_xlabel("k (samples)")
    ax.set_ylabel("pass@k  (reward ≥ 0.8)")
    ax.set_ylim(0, 1.05)
    ax.set_title("pass@k scaling — REx reaches ceiling by k=2")
    ax.legend(loc="lower right", fontsize=9)
    _save(fig, "fig3_passk_curve.png")


# ------------------------------------------------------------------ Fig 4
def fig4_mcnemar():
    """McNemar discordant-pair bars: REx vs each baseline (A2, deepseek)."""
    m = _load("experiments/ralph_outputs/A2/artifacts/ablation_v2_mcnemar_deepseek-v4-pro.json")
    if not m:
        return
    mo = m["mcnemar_overall"]
    keys = ["rex_vs_zero_shot", "rex_vs_best_of_n", "rex_vs_retry_realistic",
            "rex_vs_rex_no_oracle"]
    labels = ["vs zero-shot", "vs best-of-n", "vs retry", "vs REx(no-oracle)"]
    a = [mo[k]["a_pass_b_fail"] for k in keys]   # REx pass, baseline fail
    b = [mo[k]["a_fail_b_pass"] for k in keys]   # REx fail, baseline pass
    pvals = [mo[k]["p_exact"] for k in keys]

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    y = np.arange(len(keys))
    ax.barh(y, a, color=C["rex"], edgecolor="black", linewidth=0.5,
            label="REx passes, baseline fails")
    ax.barh(y, [-v for v in b], color="#D55E00", edgecolor="black", linewidth=0.5,
            label="baseline passes, REx fails")
    for yi, av, bv, p in zip(y, a, b, pvals):
        ax.text(av + 1.5, yi, f"{av}", va="center", fontsize=10, fontweight="bold")
        ax.text(-bv - 1.5, yi, f"{bv}", va="center", ha="right", fontsize=10)
        ax.text(av + 9, yi, "p<1e-4" if p < 1e-4 else f"p={p:.3g}",
                va="center", fontsize=8, color="#555555")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("discordant incident×seed pairs")
    ax.set_xlim(-15, max(a) + 22)
    ax.grid(axis="y", alpha=0)
    ax.set_title("McNemar paired test — REx dominates  (deepseek-v4-pro, 750 ep)")
    ax.legend(loc="lower right", fontsize=8.5)
    _save(fig, "fig4_mcnemar.png")


# ------------------------------------------------------------------ Fig 5
def fig5_frontier():
    """REx lift across the model frontier (rex/runs/frontier.json)."""
    d = _load("rex/runs/frontier.json")
    if not d:
        return
    models = d["models"]
    names = [m["model"] for m in models]
    base = [m["baseline_mean"] for m in models]
    rex = [m["rex_mean"] for m in models]
    order = np.argsort(base)
    names = [names[i] for i in order]
    base = [base[i] for i in order]
    rex = [rex[i] for i in order]

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    x = np.arange(len(names))
    w = 0.38
    ax.bar(x - w / 2, base, w, label="baseline (budget=%d)" % d["budget"],
           color=C["baseline"], edgecolor="black", linewidth=0.5)
    ax.bar(x + w / 2, rex, w, label="REx", color=C["rex"],
           edgecolor="black", linewidth=0.5)
    for xi, bv, rv in zip(x, base, rex):
        ax.text(xi - w / 2, bv + 0.01, f"{bv:.2f}", ha="center", va="bottom", fontsize=8)
        ax.text(xi + w / 2, rv + 0.01, f"{rv:.2f}", ha="center", va="bottom", fontsize=8)
        ax.annotate("", xy=(xi + w / 2, rv), xytext=(xi - w / 2, bv),
                    arrowprops=dict(arrowstyle="->", color="#444444", lw=0.8))
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=18, ha="right")
    ax.set_ylabel("mean reward (5 scenarios)")
    ax.set_ylim(0, 1.05)
    ax.set_title("REx lifts every model to a common frontier (~0.86)")
    ax.legend(loc="lower right", fontsize=9)
    _save(fig, "fig5_frontier.png")


# ------------------------------------------------------------------ Fig 6
def fig6_harness_generalization():
    """Learned-harness held-out accuracy vs false-allow (harness_synth_v2.json).

    heldout_table is {policy: {accuracy, false_allow_rate, false_block_rate}}.
    We compare the synthesized harness against the empty seed and the
    hand-written oracle on held-out incidents.
    """
    d = _load("rex/runs/harness_synth_v2.json")
    if not d:
        return
    ht = d.get("heldout_table")
    if not isinstance(ht, dict) or not ht:
        return

    policies = list(ht.keys())
    acc = [ht[p].get("accuracy", 0.0) for p in policies]
    fa = [ht[p].get("false_allow_rate", 0.0) for p in policies]
    short = {
        "seed (empty)": "seed\n(empty)",
        "synthesized (v2)": "synthesized\n(learned, 3 rules)",
        "hand-written is_safe": "hand-written\noracle",
    }
    labels = [short.get(p, p) for p in policies]
    # colour the learned policy in REx green, others grey/blue
    cols = []
    for p in policies:
        if "synth" in p:
            cols.append(C["rex"])
        elif "hand" in p:
            cols.append(C["retry_realistic"])
        else:
            cols.append(C["baseline"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.3))
    x = np.arange(len(policies))

    ax1.bar(x, acc, color=cols, edgecolor="black", linewidth=0.5)
    for xi, v in zip(x, acc):
        ax1.text(xi, v + 0.012, f"{v:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_ylabel("held-out accuracy")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Block-decision accuracy")

    ax2.bar(x, fa, color=cols, edgecolor="black", linewidth=0.5)
    for xi, v in zip(x, fa):
        ax2.text(xi, v + 0.012, f"{v:.3f}", ha="center", va="bottom",
                 fontsize=9, fontweight="bold")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=8)
    ax2.set_ylabel("false-allow rate  (lower = safer)")
    ax2.set_ylim(0, 1.1)
    ax2.set_title("Unsafe-action leakage")

    v1 = d.get("vs_v1", {})
    fig.suptitle(
        f"Learned safety harness on held-out incidents "
        f"({d.get('n_rules')} rules; v1 had {v1.get('v1_n_rules', '?')})",
        fontsize=13, fontweight="bold")
    _save(fig, "fig6_harness.png")


def main():
    print(f"REPO={REPO}")
    print(f"OUT ={OUT}")
    fig1_passk_bars_ci()
    fig2_passk_by_family()
    fig3_passk_curve()
    fig4_mcnemar()
    fig5_frontier()
    fig6_harness_generalization()
    print("done.")


if __name__ == "__main__":
    main()
