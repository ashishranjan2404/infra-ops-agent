"""
sme_rlvr_model.py — Formal model of SME feedback as an advantage-reshaping signal
on top of RLVR (Reinforcement Learning from Verifiable Rewards).

Task I5: Formalize the relationship between SME (subject-matter-expert) override
feedback and RLVR. Derive conditions under which SME feedback improves sample
efficiency vs RLVR alone, and provide a small illustrative simulation.

Self-contained: depends only on numpy. No shared-core imports, no network.

------------------------------------------------------------------------------
THE MODEL (see SUMMARY.md / 04_spec.md for the prose derivation)
------------------------------------------------------------------------------
Setting: a bandit/contextual-policy abstraction of one RLVR step. For a prompt x
the policy proposes K candidate trajectories. A *verifier* V (the RLVR signal)
returns a binary correctness r_V(tau) in {0,1} that is cheap but COARSE: many
distinct trajectories collapse to the same r_V, so within a group the verifiable
reward has little spread (the "flat-reward" pathology that kills REINFORCE/GRPO
advantage signal).

An SME provides *override* feedback: for a fraction p of groups (a labeling
budget) the SME supplies a denser, ordinal preference signal s(tau) in [0,1] that
is correlated with the TRUE task value q(tau) but is itself noisy / occasionally
wrong (override error rate eps).

We combine them into a reshaped reward:
    r(tau) = (1 - lambda) * r_V(tau) + lambda * s_hat(tau)     when SME labeled
           =                  r_V(tau)                          otherwise
where s_hat is the (noisy) SME signal and lambda in [0,1] is the trust weight.

The learning signal per group is the *advantage* A(tau) = r(tau) - mean_group(r).
GRPO-style updates have variance/efficiency governed by the within-group spread
(std of advantages) and by the BIAS of the advantage relative to true value q.

We measure sample efficiency by the expected per-step *useful gradient signal*
proxy:  G = Corr(A, q_centered) * Std(A)      (alignment x magnitude),
and by a simulated learning curve (steps to reach a target true-value).

The proposition (derived in the docs, checked numerically here) gives the
condition under which adding SME feedback raises G over RLVR-alone.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict

import numpy as np


# ----------------------------------------------------------------------------
# Core abstractions
# ----------------------------------------------------------------------------
@dataclass
class WorldParams:
    """Generative parameters for the synthetic RLVR-with-SME world."""
    K: int = 8                 # candidates per group (group size)
    n_groups: int = 4000       # number of prompt-groups sampled
    # Verifier coarseness: fraction of true-value variance the binary verifier
    # captures. rho_V in [0,1]; low rho_V => flat/coarse reward.
    rho_V: float = 0.35
    verifier_threshold: float = 0.55   # q above this => r_V = 1 (binary)
    # SME signal quality.
    p_label: float = 0.30      # labeling budget: fraction of groups SME labels
    eps_override: float = 0.10 # SME override error rate (flips ordering noise)
    sme_noise: float = 0.20    # gaussian noise std on SME ordinal signal
    lam: float = 0.5           # trust weight lambda on SME signal
    seed: int = 0


def _make_groups(rng: np.random.Generator, wp: WorldParams):
    """Sample true values q for each candidate in each group, in [0,1]."""
    q = rng.beta(2.0, 2.0, size=(wp.n_groups, wp.K))  # true task value
    return q


def _verifier_reward(q: np.ndarray, wp: WorldParams, rng) -> np.ndarray:
    """Binary verifiable reward: coarse thresholded view of q with limited
    correlation rho_V (we blend q with noise then threshold)."""
    noise = rng.normal(0, 1, size=q.shape)
    # blend so that correlation of the latent with q equals ~rho_V
    a = wp.rho_V
    latent = a * (q - q.mean()) / (q.std() + 1e-9) + np.sqrt(max(1e-9, 1 - a * a)) * noise
    # threshold the latent at a quantile matching verifier_threshold on q
    thr = np.quantile(latent, wp.verifier_threshold)
    return (latent >= thr).astype(float)


def _sme_signal(q: np.ndarray, wp: WorldParams, rng) -> np.ndarray:
    """Dense ordinal SME signal in [0,1]: q + gaussian noise, with an
    eps fraction of candidates getting an adversarial 'override' flip
    (value pushed toward the opposite extreme) to model SME being wrong."""
    s = q + rng.normal(0, wp.sme_noise, size=q.shape)
    flip = rng.random(q.shape) < wp.eps_override
    s = np.where(flip, 1.0 - q, s)
    # clip and min-max per group to [0,1] for a comparable scale with r_V
    s = np.clip(s, 0.0, 1.0)
    return s


def _centered(x: np.ndarray) -> np.ndarray:
    """Subtract the per-group (row) mean => advantage-style centering."""
    return x - x.mean(axis=1, keepdims=True)


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    af = a.ravel()
    bf = b.ravel()
    sa, sb = af.std(), bf.std()
    if sa < 1e-9 or sb < 1e-9:
        return 0.0
    return float(np.mean((af - af.mean()) * (bf - bf.mean())) / (sa * sb))


# ----------------------------------------------------------------------------
# Signal-quality metric G = Corr(A, q_centered) * Std(A)
# ----------------------------------------------------------------------------
def signal_quality(rewards: np.ndarray, q: np.ndarray) -> dict:
    """Given a per-candidate reward matrix and true values q, compute the
    advantage A (group-centered reward), its alignment with true centered
    value, its magnitude, and the composite useful-gradient proxy G."""
    A = _centered(rewards)
    qc = _centered(q)
    align = _safe_corr(A, qc)        # how well advantage points toward truth
    mag = float(A.std())             # within-group spread (gradient magnitude)
    G = align * mag
    return {"align": align, "magnitude": mag, "G": G}


def reshaped_reward(q, r_V, s_hat, labeled_mask, lam):
    """r = (1-lam) r_V + lam s_hat on labeled groups; r_V elsewhere."""
    r = r_V.copy()
    blend = (1.0 - lam) * r_V + lam * s_hat
    r[labeled_mask] = blend[labeled_mask]
    return r


# ----------------------------------------------------------------------------
# One realization of the world -> compare RLVR-alone vs RLVR+SME signal quality
# ----------------------------------------------------------------------------
def evaluate(wp: WorldParams) -> dict:
    rng = np.random.default_rng(wp.seed)
    q = _make_groups(rng, wp)
    r_V = _verifier_reward(q, wp, rng)
    s_hat = _sme_signal(q, wp, rng)

    # labeling budget: choose a fraction of groups to receive SME feedback
    n = wp.n_groups
    labeled_mask = np.zeros((n, 1), dtype=bool)
    n_lab = int(round(wp.p_label * n))
    idx = rng.choice(n, size=n_lab, replace=False)
    labeled_mask[idx, 0] = True
    labeled_mask = np.broadcast_to(labeled_mask, q.shape)

    base = signal_quality(r_V, q)
    r_mix = reshaped_reward(q, r_V, s_hat, labeled_mask, wp.lam)
    mixed = signal_quality(r_mix, q)

    return {
        "rlvr_only": base,
        "rlvr_plus_sme": mixed,
        "delta_G": mixed["G"] - base["G"],
        "helps": mixed["G"] > base["G"],
        "params": asdict(wp),
    }


# ----------------------------------------------------------------------------
# Illustrative learning-curve simulation:
# A toy policy parameter theta drifts up the gradient implied by the advantage.
# We model "true value reached at step t" as proportional to cumulative useful
# gradient signal. Steps-to-target is the sample-efficiency readout.
# ----------------------------------------------------------------------------
def learning_curve(wp: WorldParams, steps: int = 200, target: float = 0.7):
    """Returns (curve_rlvr, curve_sme, steps_to_target_rlvr, steps_to_target_sme).
    Each step resamples a fresh batch (online RL). theta_value starts at 0.5
    (random policy) and increases by a learning rate * useful-gradient G, with
    diminishing returns as it approaches 1.0."""
    rng = np.random.default_rng(wp.seed + 777)
    lr = 0.6

    def run(use_sme: bool):
        theta = 0.5
        curve = []
        hit = None
        for t in range(steps):
            sub = WorldParams(**{**asdict(wp), "n_groups": 256, "seed": int(rng.integers(1 << 30))})
            r = evaluate(sub)
            G = r["rlvr_plus_sme"]["G"] if use_sme else r["rlvr_only"]["G"]
            # diminishing-returns update toward 1.0
            theta = theta + lr * G * (1.0 - theta)
            theta = float(np.clip(theta, 0.0, 1.0))
            curve.append(theta)
            if hit is None and theta >= target:
                hit = t + 1
        return curve, hit

    c_rlvr, h_rlvr = run(False)
    c_sme, h_sme = run(True)
    return c_rlvr, c_sme, h_rlvr, h_sme


# ----------------------------------------------------------------------------
# Sweep: where does SME help? vary trust lambda and override error eps.
# ----------------------------------------------------------------------------
def sweep(wp: WorldParams):
    lams = [0.0, 0.25, 0.5, 0.75, 1.0]
    epss = [0.0, 0.1, 0.25, 0.4, 0.5]
    grid = []
    for eps in epss:
        row = []
        for lam in lams:
            sub = WorldParams(**{**asdict(wp), "lam": lam, "eps_override": eps})
            res = evaluate(sub)
            row.append(round(res["delta_G"], 4))
        grid.append(row)
    return {"lams": lams, "epss": epss, "delta_G_grid": grid}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write JSON results to path")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    wp = WorldParams(seed=args.seed)
    res = evaluate(wp)
    c_rlvr, c_sme, h_rlvr, h_sme = learning_curve(wp)
    sw = sweep(wp)

    out = {
        "headline": evaluate(wp),
        "learning_curve": {
            "steps_to_target_rlvr": h_rlvr,
            "steps_to_target_sme": h_sme,
            "final_value_rlvr": round(c_rlvr[-1], 4),
            "final_value_sme": round(c_sme[-1], 4),
            "speedup_x": (round(h_rlvr / h_sme, 3) if (h_rlvr and h_sme) else None),
        },
        "sweep": sw,
    }
    print(json.dumps(out, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    main()
