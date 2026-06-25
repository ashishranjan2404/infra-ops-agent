# E10 — Ouroboros: self-critique of the spec as 3 different engineers

## Engineer A — "Documentation pedant"
**Problems found:**
1. The spec mandates header text `## 5.x.1 …` but a literal `5.x` will read as a typo in a
   real paper. **Fix:** keep the `5.x` numbering but add a one-line note at the top of the
   artifact that the number is a placeholder to be set when the section lands in the draft.
2. The validation gate "no decimal in T1–T3 cells" is too broad — incident *counts* (14
   cascades, 8 simple, 10 novel) and reward *weights* (0.30, 0.25…) are legitimate integers/
   decimals that appear in prose and SHOULD remain. **Fix:** scope the grep gate to the
   *result-table cell positions only* (the `| … |` rows of T1/T2/T3 whose intent is a
   measured value), not the whole document. Implement by checking that every result-table
   data cell is exactly `PENDING`.
3. No explicit statement that the section is *standalone* (no undefined cross-refs). **Fix:**
   add a "this section assumes §3.5 Setup and §4 Benchmark are defined elsewhere; all other
   refs are self-contained" note.

## Engineer B — "Skeptical empiricist"
**Problems found:**
1. H4 (transfer beats synthetic augmentation) needs a **matched budget** definition or it's
   unfalsifiable — "more data" must be controlled by token/trajectory count. **Fix:** in
   5.x.3 E9 design cell, state the control is *equal trajectory budget* (same N as the
   Fireball corpus used), and reference E8's data-scaling so the budget is principled.
2. The headline "trap-avoidance-rate" is asserted but never *defined operationally*. **Fix:**
   define it in 5.x.2 as `1 − (fraction of rollouts where the −0.60 trap action fires)`,
   computed by the same deterministic grader (`rex/scoring.py`) — so it's grounded, not a vibe.
3. E5 "novel incidents" risks contamination if the novel set overlaps training families.
   **Fix:** add a one-line note that the novel set is *held-out by failure-family*, matching
   how the curriculum already separates generated single-leaf from reconstructed cascades.

## Engineer C — "Reviewer-2 simulator"
**Problems found:**
1. The biggest reject risk: the paper's spine says **frozen LLM, no fine-tuning**
   (ARCHITECTURE + global memory), yet this section *fine-tunes* (GRPO). If unaddressed, a
   reviewer calls it an internal contradiction. **Fix (critical):** add an explicit
   reconciliation paragraph in 5.x.2 — the *deployed* policy + REx loop is frozen and
   model-agnostic (C1/C3); the transfer contribution (C2) is a *separate, optional* study of
   whether cross-domain *training data* improves the base policy you then freeze. Both can be
   true; the harness/reward is the constant. State this tension as a *design choice*, owned.
2. Over-engineering risk: 7 experiments (E3–E9) for a section with *zero current data* may
   look like a wish-list. **Fix:** mark a clear **MVP subset** — E3 (the headline claim) and
   E4 (no-harm) are the *required* experiments for the claim; E5–E9 are labeled
   *strengthening / future*. Honest about what's load-bearing.
3. Under-specified failure mode: what if E1/E2 never land before submission? **Fix:** add a
   fallback line in 5.x.5 — if the model isn't pushed, the section ships as a *pre-registered
   protocol* and C2 moves from "claim" to "stated future experiment" in the contributions
   list. The paper survives either way.

## Filtered final spec (deltas applied)
- Placeholder-number note + standalone note added (A1, A3).
- Result-cell grep gate scoped to table cells; integers/weights in prose allowed (A2).
- E9 control = **equal trajectory budget**; E8 referenced (B1).
- **trap-avoidance-rate** defined operationally via the grader (B2).
- E5 novel set **held out by failure-family** (B3).
- **Frozen-vs-finetuned reconciliation** paragraph added — the most important fix (C1).
- **MVP subset (E3, E4)** vs strengthening (E5–E9) marked explicitly (C2).
- **Fallback if E1/E2 never land** (section ships as pre-registered protocol) (C3).

These deltas are folded into the artifact written in step 06.
