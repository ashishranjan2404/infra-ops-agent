# I5 — 04 Spec (formal model + technical contract)

## 1. Formal model

### 1.1 Setting (grouped bandit abstraction of one RLVR step)
For a prompt `x`, the policy emits `K` candidate trajectories `tau_1..tau_K`. Each has a
latent **true task value** `q(tau) in [0,1]` (e.g. true remediation quality). We sample
`q ~ Beta(2,2)` i.i.d. per candidate across `N` groups.

### 1.2 Verifier (RLVR signal) — coarse & binary
The verifier returns `r_V(tau) in {0,1}`. We construct a latent
`ℓ = rho_V · z(q) + sqrt(1−rho_V²) · ξ`, with `z(q)` the standardized true value,
`ξ ~ N(0,1)`, and threshold `ℓ` at a quantile (`verifier_threshold`). Thus `r_V` is
correlated with `q` only through `rho_V in [0,1]`; **small `rho_V` ⇒ coarse reward** and
frequently flat within a group.

### 1.3 SME feedback — dense, ordinal, occasionally wrong
For a labeling-budget fraction `p` of groups, an SME supplies
`s_hat(tau) = clip(q(tau) + N(0, sme_noise²), 0, 1)`, except that with probability
`eps_override` (the **override error rate**) the SME *inverts* the candidate:
`s_hat = 1 − q`. This models the SME confidently overriding the correct ranking.

### 1.4 Reward reshaping (advantage reshaping)
On labeled groups:  `r = (1−λ) r_V + λ s_hat`,  λ ∈ [0,1] the **trust weight**.
On unlabeled groups: `r = r_V`. The **advantage** is the group-centered reward
`A(tau) = r(tau) − (1/K) Σ_j r(tau_j)`. (Reshape reward → recompute advantage.)

### 1.5 Useful-gradient proxy (the optimization quantity)
`G = Corr(A, q_c) · Std(A)`, where `q_c` is centered true value. *Alignment*
`Corr(A, q_c)` measures whether the advantage points toward truth (controls gradient
**bias**); *magnitude* `Std(A)` measures whether there is spread to learn from (controls
gradient **signal-to-noise** under the flat-reward pathology). `G` is a **proxy**, not a
bound; §3 validates it against a learning curve.

## 2. Proposition (when SME feedback helps)

**Assumptions.**
- (A1) `q` is the ground truth and the only thing we ultimately care about.
- (A2) Verifier coarseness: `Corr(r_V, q) ≈ rho_V < 1` (binary, lossy).
- (A3) SME signal is `q + noise` with inversion probability `eps`; its correlation with
  `q` is approximately `c_S(eps, sme_noise) = (1 − 2·eps_eff)·κ`, decreasing in `eps`.
- (A4) Frozen-LLM policy-gradient step; sample efficiency is monotone in `G` (validated
  empirically, §3).

**Proposition.** Let `G_V` be the RLVR-only proxy and `G_mix(λ)` the reshaped proxy under
trust `λ` and budget `p`. Then to first order

> SME feedback improves sample efficiency (`G_mix(λ) > G_V`) **iff** the blended signal's
> correlation with truth exceeds the verifier's by enough to offset any magnitude change,
> i.e. iff `c_S(eps) > rho_V` on the labeled mass. There exists a crossover override rate
> `eps* ` (increasing in `rho_V`'s *deficit* and decreasing in λ): for `eps < eps*` the SME
> **helps** (`delta_G > 0`); for `eps > eps*` it **hurts** (`delta_G < 0`).

**Corollaries.**
- C1 (no-op): `λ = 0` ⇒ `G_mix = G_V` (no effect).
- C2 (no-op): `p = 0` ⇒ `G_mix = G_V` (no labels, no effect).
- C3 (monotone trust): for a *good* SME (`c_S > rho_V`), `delta_G` increases in `λ`; for a
  *bad* SME (`c_S < rho_V`), `delta_G` decreases in `λ`. Hence the optimal λ is bang-bang
  in the idealized model: trust fully a good SME, ignore a bad one.

## 3. Technical contract

### Data structures
```python
@dataclass
class WorldParams:
    K:int=8; n_groups:int=4000; rho_V:float=0.35; verifier_threshold:float=0.55
    p_label:float=0.30; eps_override:float=0.10; sme_noise:float=0.20
    lam:float=0.5; seed:int=0
```

### Function signatures
- `evaluate(wp) -> dict` with keys `rlvr_only`, `rlvr_plus_sme`, `delta_G`, `helps`, `params`.
- `signal_quality(rewards, q) -> {align, magnitude, G}`.
- `reshaped_reward(q, r_V, s_hat, labeled_mask, lam) -> ndarray`.
- `learning_curve(wp, steps, target) -> (curve_rlvr, curve_sme, steps_rlvr, steps_sme)`.
- `sweep(wp) -> {lams, epss, delta_G_grid}`.

### Test cases (8)
1. centering yields zero per-group mean.
2. perfect reward (`r=q`) ⇒ alignment ≈ 1, `G>0`.
3. flat reward ⇒ magnitude 0, `G=0`.
4. good SME (low eps/noise, λ=0.5) ⇒ `helps=True`, `delta_G>0`.
5. bad SME (eps=0.5, λ=1.0) ⇒ does not help.
6. `λ=0` ⇒ `delta_G=0` (C1).
7. `p=0` ⇒ `delta_G=0` (C2).
8. sweep monotone: mean `delta_G` at eps=0 ≥ at eps=0.5.

### File formats / API
- `sim_results.json`: `{headline, learning_curve:{steps_to_target_*, speedup_x}, sweep:{lams,epss,delta_G_grid}}`.
- CLI: `python3 sme_rlvr_model.py --out sim_results.json [--seed N]`.
