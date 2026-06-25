# I2 — 04 Spec

## 1. The reward function (exact, from rex/scoring.py)
For a plan with `diag ∈ {0,1}`, `fix ∈ {0, 0.5, 1.0}`, `resolved ∈ {0,1}`,
`trap ∈ {0,1}`:

    R = clamp( W_ROOT·diag + W_FIX·fix + W_RESOLVED·resolved − TRAP_PENALTY·trap,
               0, 1 )

with `(W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY) = (0.30, 0.25, 0.45, 0.60)` and
`MAX_CLEAN = W_ROOT+W_FIX+W_RESOLVED = 1.0`.

## 2. The theorem (bimodality condition)

**Setup.** Condition on the *competent* event `C = {diag=1, fix=1, resolved=1}`.
On `C`, the only remaining randomness is `trap ~ Bernoulli(p_trap)`. Then R takes
exactly two values:

    R | (C, trap=0) = MAX_CLEAN                      = 1.0   ("success atom")
    R | (C, trap=1) = clamp(MAX_CLEAN − TRAP_PENALTY) = 0.40 ("trap basin atom")

So `R | C` is a two-point (Bernoulli-scaled) law — a *bimodal* distribution with
mass `1−p_trap` at the success atom and `p_trap` at the basin atom, separated by

    Δ = MAX_CLEAN − clamp(MAX_CLEAN − TRAP_PENALTY) = min(TRAP_PENALTY, MAX_CLEAN).

**Bimodality (valley) condition.** `R|C` is bimodal (two separated atoms with a
real valley) iff `Δ > 0`, i.e. `TRAP_PENALTY > 0`, *and* both atoms carry mass
(`0 < p_trap < 1`). With a width threshold `ε` for "separated," need `Δ ≥ ε`.

**The economically meaningful threshold (the task's question).** A trapped,
competent, *resolved* plan should not outscore an unresolved plan. The
unresolved-clean reference scores `MAX_CLEAN − W_RESOLVED`. Thus the trap basin
sits at or below it iff

    MAX_CLEAN − TRAP_PENALTY ≤ MAX_CLEAN − W_RESOLVED
    ⇔  **TRAP_PENALTY ≥ W_RESOLVED**     (strict > for strictly worse).

This is the precise condition that makes the trap penalty *dominate* the resolved
reward, collapsing "resolved-but-trapped" into the low mode. Shipped: `0.60 > 0.45`
→ holds. The basin atom (0.40) is below the unresolved-clean reference (0.55),
proving the trap penalty nullifies the resolved reward.

## 3. Data structures / signatures (bimodality_sim.py)
```python
W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60
MAX_CLEAN = 1.0

def score(diag: bool, fix: float, resolved: bool, trap: bool,
          trap_penalty: float = TRAP_PENALTY) -> float            # exact arithmetic

@dataclass
class Population:                # p_diag, p_fix_full, p_fix_half, p_resolved,
    def draw(n, trap_penalty) -> list[float]   # p_trap, seed

def resolved_eligible_subpop(pop, n, trap_penalty) -> list[float] # the C-conditioned law
def bimodality_coefficient(xs) -> float        # Sarle's BC (secondary)
def largest_gap(xs) -> (gap, lo, hi)
def two_cluster_separation(xs) -> dict          # split_at, left/right frac+mean, gap
def is_bimodal(xs, gap_thresh=0.12) -> bool     # PRIMARY valley test
def histogram(xs, bins=20) -> str
```

## 4. Test cases (test_bimodality.py)
- `score(1,1.0,1,0)==1.0`; `score(1,1.0,1,1)==0.40`; `score(0,0,0,1)==0.0` (clamp).
- trapped-resolved ≤ unresolved-clean **iff** `TRAP_PENALTY > W_RESOLVED`.
- competent subpop has exactly two distinct values `{0.4, 1.0}` and is bimodal.
- tiny penalty (0.05) → subpop NOT bimodal (no valley); 0.60 → bimodal.
- mirrored constants == `rex/scoring.py` (drift guard).

## 5. Output format (bimodality_result.json)
Keys: `constants`, `gap_condition`, `gap_condition_holds`,
`baseline_full_population`, `competent_subpopulation`, `sweep_competent_subpop`
(list of {trap_penalty, trap_atom, success_atom, atom_gap, bc, is_bimodal,
resolved_reward_nullified}), `valley_present_at_shipped_penalty`,
`nullification_threshold_is_W_RESOLVED`, `shipped_penalty_nullifies_resolved`.
