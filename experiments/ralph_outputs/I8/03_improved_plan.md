# 03 — Improved Plan (post-grill)

## What changed vs 01

| # | Change | From which critique | Accepted? |
|---|---|---|---|
| 1 | Add a 6th framing axis up front — **"domain of applicability / does a verifier exist"** — and a dedicated **"where code-as-policy loses"** section. | REV (R1/R3) | ✅ Accepted |
| 2 | State explicitly that **verifiability is task-conferred, not method-conferred**; the oracle exists because incident-response has an SLO, and does not transfer to tone/harmlessness. | REV vs PSRE (R2) | ✅ Accepted |
| 3 | **Precisely name the mechanism**: code-as-policy here = *verifier-guided inference-time search over a frozen policy + rejection safety gate*, NOT policy-gradient / not "RL" loosely. | RLE (R1/R2) | ✅ Accepted |
| 4 | Frame sample efficiency as **amortized capex (labels+GPU, cheap inference) vs per-call opex (no labels, costly inference)** instead of "incomparable currencies." | SMR vs DOL (R2/R3) | ✅ Accepted |
| 5 | Add **interpretability ↔ reversibility coupling**: weight-baked knowledge is opaque/un-patchable; code knowledge is `git`-diffable and roll-backable. | DOL (R2/R3) | ✅ Accepted |
| 6 | Keep all three in one table but **scope each column's domain** to avoid the category error. | RLE vs REV (R2) | ✅ Accepted (compromise) |

## Rejected / deferred
- **PSRE's "verifiability is the only axis that matters."** Rejected for the doc's framing — adopting
  it would bias the comparison toward the home team (REV's objection is correct). Verifiability is
  *one* axis, reported honestly in both directions.
- **PSRE's "practitioners will call it RL anyway, so loosely is fine."** Rejected for a *rigorous*
  doc; we use the precise label and note the colloquial usage in a footnote only.

## Final structure of `comparison.md`
0. TL;DR + the unifying frame ("where does normative knowledge live").
1. One-paragraph precise definition of each paradigm (with citations).
2. The grounding: this repo's actual code-as-policy stack (named files).
3. The 5 axes, each a subsection: knowledge / verifiability / sample-efficiency / safety /
   interpretability — each comparing all 3, each scoped by domain.
4. Summary matrix (mirrors `axes_matrix.json`).
5. **Where code-as-policy LOSES** (honest limits).
6. Synthesis: they are complementary, not rivals.

## Artifacts unchanged from 01
`comparison.md`, `axes_matrix.json`, `validate_matrix.py`.
