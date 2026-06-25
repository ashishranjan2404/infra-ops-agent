# E10 — Improved Plan (post-grill)

## What changed vs `01_plan.md`

| # | Change | Source critique | Accept/Reject |
|---|---|---|---|
| 1 | Section now leads with a **narrow falsifiable empirical claim** (transfer helps cascades) and carries the "why would D&D help SRE" reasoning as an **explicitly-labeled mechanistic conjecture**, not a headline claim. | SMR vs REV (R2 compromise) | **Accepted** |
| 2 | **Headline metric = trap-avoidance-rate + correct-fix-rate on cascades**, with aggregate pass@1 demoted to secondary and *decomposed by incident family*. | PSRE (R1/R2) | **Accepted** |
| 3 | Added **E9 (transfer vs synthetic SRE augmentation)** and **E4 (does it hurt simple?)** as first-class controls in the design table, framed as "is it transfer or just more data?" and "no-harm guardrail". | REV (R1) | **Accepted** |
| 4 | Section now **cites** the reward weights and the GRPO group-construction recipe (within-group spread) rather than re-deriving them — pointer to §3.5/Setup. | RLE vs PSRE (R2) | **Accepted (scoped)** |
| 5 | Added an explicit **Status & Blockers** subsection naming **E1/E2**; all result cells say literal `PENDING`. | DEV (R1/R2) | **Accepted** |
| 6 | Added a stated **falsification criterion** (the null under which we report "no transfer / negative transfer"). | REV (R3) | **Accepted** |
| 7 | E7 (other source domains) framed as the **stated generalization frontier / future work**, not claimed. | SMR/REV (R3) | **Accepted** |

## Rejected / deferred

- **RLE's full GRPO derivation in-section** — *rejected for this section*. The derivation
  belongs in §3.5/Experimental Setup. The transfer section cites it. Keeping it here would
  bloat the section and duplicate the methods. (We keep the *recipe pointer*, per #4.)
- **SMR's pure representation-transfer framing with probing analysis** — *deferred*. We have
  no representation-similarity experiments run; claiming them would be fabrication. Recorded
  as future work alongside E7.

## Final section structure (to write in artifact)
1. **5.x.1 Motivation & hypothesis** — the transfer idea, grounded in the FIREBALL schema
   the repo already mirrors; H1–H4 with a stated null.
2. **5.x.2 Methodology** — FIREBALL SFT pretraining → GRPO on opensre env → frozen-policy
   evaluation through the *same* pass@k harness + deterministic reward; how this contribution
   (C2, the one place we fine-tune) relates to the frozen-LLM + REx spine (C1/C3).
3. **5.x.3 Experiment design (E3–E9)** — table: id, question, design, metric, control, status.
4. **5.x.4 Pre-registered results (PENDING)** — Tables T1–T3 with `PENDING` cells +
   falsification criterion.
5. **5.x.5 Status & blockers** — E1/E2 gating; exact command to run once unblocked.
6. **5.x.6 Threats to validity / limitations** — confounds, single-source-domain, frozen-vs-
   finetuned framing tension stated honestly.

## Success criteria (unchanged, sharpened)
- Zero fabricated numbers (grep-gated in step 07).
- E3–E9 each a designed experiment with metric + control.
- Headline metric is cascade trap-avoidance, not aggregate pass@1.
- Falsification criterion present. Blocker (E1/E2) named in-section.
