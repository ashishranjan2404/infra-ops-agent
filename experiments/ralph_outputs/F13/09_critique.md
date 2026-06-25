# 09 — Critique (honest)

## What's weak
1. **No rendered proof of A0 fit.** I validated well-formedness and presence of print CSS, but
   I did not rasterize the poster to confirm the 3 columns actually fit one A0 page without
   vertical overflow. A real submission needs a `print-to-PDF` pass in a browser; conservative
   font sizing reduces but does not eliminate overflow risk.
2. **Two result sets coexist.** The poster shows both the optimistic frontier table (0.86) and
   the deflating ablation (lift ≈ leakage). This is honest, but a hurried reader could still
   anchor on 0.86 and miss the caveat despite equal styling. A poster cannot force reading
   order; a presenter must verbally connect them.
3. **No embedded figures.** The repo has real charts (`docs/curriculum_rewards.png`,
   `ablation.png`, `verifier_generalization.png`) that would strengthen the poster. I kept the
   HTML self-contained (no external assets) per the DevOps constraint, so figures are
   referenced by path, not embedded. A production version should inline them as base64 or ship
   them alongside.
4. **Numbers come from two summary docs, not re-run here.** I trusted `ARCHITECTURE.md` and
   `headline_insights.md` rather than re-executing `rex.frontier` (which needs `HUD_API_KEY`
   and live gateway calls). If those docs drifted from the code, the poster inherits the drift.

## What a reviewer attacks first
- "Your own ablation says the lift is leakage — so why is the frontier table on the poster at
  all?" Defense: it's a *deployment-wrapper* claim (frozen models converge + escalate safely),
  distinct from a *learning* claim, and it's labeled as such. A hostile reviewer may still call
  it mixed messaging.
- "0.86 = (4×1.0+0.30)/5 is a designed ceiling, not evidence." True, and the poster now says
  *designed*. But it means the headline number is partly definitional, which weakens its punch.
- "Tier-B is one cluster, mechanism-only." Acknowledged on the poster; still a single-cluster
  validation, not a statistical fidelity claim.

## What's missing
- A figure/diagram of the cascade (currently prose-only); an embedded chart.
- Author names / affiliation / venue (placeholders) — a real poster needs them.
- A rendered PDF artifact.

## Honest bottom line
The deliverable is a **real, valid, honestly-framed poster source** (md + print-styled HTML +
passing validator), grounded entirely in existing repo results. It is submission-*shaped* but
not submission-*final*: it needs a browser PDF render, embedded figures, and author metadata
before it could go on a board.
