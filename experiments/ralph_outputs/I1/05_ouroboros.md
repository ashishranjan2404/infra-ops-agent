# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Formal-methods skeptic

**Problems found:**
- **P1 (real):** `EarnedAutonomy(π,T,S) ≡ ∀T'≤T: graduated(π,T',B_{S,T'})` says batches are
  drawn *per tier*. But a single eval batch can't simultaneously satisfy the per-tier `n_min`
  AND restrict to "incidents whose safe fix lives at tier T'". The spec is ambiguous about
  whether `B_{S,T'}` is the same batch filtered or a fresh draw. → **Fix:** define `B_{S,T'}`
  as the held-out batch filtered to incidents whose *minimal sufficient action tier* ≤ T', so
  one draw serves all tiers; `n_min(T')` is then a constraint on |SOLV| within that filter.
- **P2 (real):** `esc_rate` returns 1.0 when `|UNSOLV|==0`. That lets a policy graduate the
  *escalation* requirement with zero evidence it can escalate. → **Fix:** require
  `|UNSOLV| ≥ 1` for any tier that gates on ε_T, else escalation is "untested" → block
  graduation (conservative). Document this.

## Engineer 2 — Production SRE / adversary

**Problems found:**
- **P3 (real):** `trap_unblocked` depends on `is_safe` catching traps. But the framework
  treats a *blocked* trap as harmless. A policy that *constantly proposes* destructive
  actions and only survives because the gate blocks them has NOT earned autonomy — it's
  pathological and one gate-bug away from a SEV1. → **Fix:** add a soft signal
  `trap_proposed_rate` (blocked OR not); make it a *revocation* trigger and a graduation
  warning, while keeping `trap_unblocked` the hard gate. (Documented as a known extension;
  hard gate stays on unblocked, the actually-harmful event.)
- **P4 (real):** Worked examples use the ARCHITECTURE.md *mean reward* (0.86), but graduation
  needs per-scenario clean-win/escalation *counts*, not the mean. 0.86 = (4×1.0+0.30)/5 is a
  reward mean, and I must not silently equate "mean 0.86" with "4 clean wins + 1 correct
  escalation". → **Fix:** in the worked example, reconstruct the per-scenario outcome vector
  the project actually reports (4 clean wins, 1 escalation, 0 traps) from `rex/numbers.py`'s
  `escalated_unsolvable` + clean-win accounting, and be explicit it's a small n (the live
  sweep is n=5) → so the *live* numbers graduate only a provisional/low tier; full
  graduation needs the larger held-out set. Honesty about n.

## Engineer 3 — RL/eval methodologist

**Problems found:**
- **P5 (real):** "Held-out, disjoint from tuning" is asserted but unenforced — nothing in the
  predicate references the tuning set. A reviewer can't verify non-contamination from the
  predicate alone. → **Fix:** make `S` carry a provenance tag and assert `S ∩ tuning = ∅` as
  a *precondition* documented next to the predicate (it's a dataset-construction obligation,
  not a runtime check — state that plainly rather than pretending to enforce it).
- **P6 (over-engineering):** Three Wilson bounds + three escalation thresholds + three n_min +
  floors = a lot of knobs for a framework with n=5 live data. → **Decision:** keep the tier
  thresholds (they're the substance) but mark the specific numeric defaults as *illustrative,
  calibration-pending*; the framework's value is the *structure* (conjunctive, Wilson-gated,
  hard-zero-trap, asymmetric revocation), not the exact 0.70/0.85/0.95. Documented.
- **P7 (real):** `grant = max{T: EarnedAutonomy}` with monotone tiers is fine, but if the
  per-tier filtered batches have very different n, a policy could graduate T2 but not T1
  purely from sample-size noise, violating the "∀T'≤T" intent. → The `∀T'≤T` quantifier
  already prevents *granting* T2 without T1; but I'll add a note that thresholds must be
  monotone (θ_{T+1} ≥ θ_T) so the conjunction is well-behaved — which the defaults satisfy.

## Final filtered spec deltas (carried into implementation)
- `B_{S,T'}` = held-out batch filtered by *minimal sufficient action tier ≤ T'* (P1).
- Escalation gate requires `|UNSOLV| ≥ 1`, else graduation blocked (P2).
- `trap_unblocked` = hard graduation gate; `trap_proposed` = revocation trigger + warning (P3).
- Worked examples use per-scenario outcome vectors, not the reward mean; explicitly flag small
  live n and "provisional tier" (P4).
- Non-contamination is a documented dataset precondition, not a runtime check (P5).
- Numeric thresholds labelled illustrative / calibration-pending; structure is the contribution (P6).
- Thresholds required monotone in tier (P7).
