# E10 — Plan: Write the Fireball Transfer Section of the Paper

## Objective
Produce a complete, honest, submission-grade draft of the **Cross-Domain Transfer
(Fireball → SRE)** section of the SRE-Degrees paper. The section must:
- State the transfer hypothesis precisely and ground it in the actual project framing.
- Describe the methodology (FIREBALL-schema trajectories, GRPO on the opensre env,
  the deterministic root-cause-aware reward).
- Lay out the experiment family **E3–E9** (already enumerated in
  `experiments/NEXT_100_TASKS.md`) as a coherent experimental design.
- Carry a **clearly-marked "results pending data" placeholder** structure — with
  pre-registered tables whose cells are explicitly `PENDING` — and NOT fabricate any
  numbers.

## Why this task is "currently blocked" (and what that means for the deliverable)
Per `experiments/results/P7_fireball_status.md` and `experiments/CLAIMS_EVIDENCE.md`,
the transfer **claim (C2)** cannot be *measured* in this repo right now: the FIREBALL
D&D source corpus (`incidents.jsonl`) is not present, and Wenji's GRPO branch / the
Fireball-trained Qwen slug has not been pushed (tasks E1, E2). The harness, the
42-incident benchmark, the pass@k engine (`rex/eval_pass_at_k.py`), and the
deterministic reward (`rex/scoring.py`) are all ready — **only the trained model and
source data are missing.**

Therefore the *writing* task (E10) is fully doable and is the right thing to unblock:
a paper section can be written honestly with a pre-registered design and explicit
placeholders, so that the moment E1/E2 land, the experiments E3–E9 drop straight into
labeled table cells.

## Approach
1. Read the real grounding: `ARCHITECTURE.md` (thesis + reward), `PAPER_OUTLINE.md`
   (§2.3 C2, §3.5 Transfer+RLVR, §5.3), `opensre-traj/SCHEMA.md` (FIREBALL trajectory
   shape), `NEXT_100_TASKS.md` E1–E10, `P7_fireball_status.md` (the blocker).
2. Write the section as standalone markdown (`artifacts/fireball_transfer_section.md`)
   with numbered subsections matching the paper outline numbering (5.3-style), an
   explicit **Hypotheses** block (H1–H4), a **Methodology** block, an **Experiment
   table** (E3–E9, each with: question, design, metric, control, status), and
   **pre-registered result tables** with `PENDING` cells + a falsification criterion.
3. Validate the markdown parses (headers, tables well-formed) and that NO numeric
   result is asserted (grep for fabricated digits in result tables).

## Files to create (task-namespaced, no shared edits)
- `experiments/ralph_outputs/E10/artifacts/fireball_transfer_section.md` — the deliverable.
- `experiments/ralph_outputs/E10/01..10_*.md`, `SUMMARY.md`, `result.json`.

## Dependencies
- Source-of-truth docs listed above (read-only). No code execution required beyond a
  markdown parse-check.

## Risks
- **Fabrication risk** (highest): the temptation to invent transfer numbers. Mitigation:
  every result cell is literally the token `PENDING`; a grep gate in step 07 fails the
  build if a results table contains a stray decimal.
- **Drift from project framing**: the global memory warns the project is *code-as-policy /
  auto-harness* with a **frozen** LLM, NOT fine-tuning. But C2/transfer is the *one*
  place the paper does fine-tune (GRPO after FIREBALL pretraining). Mitigation: scope the
  section honestly as the *training-data* contribution (C2), and explicitly contrast it
  with the frozen-policy + REx spine (C1/C3) so the framing is consistent, not muddled.
- **Over-claiming transfer**: D&D→SRE is a bold claim. Mitigation: frame H1 as a
  *falsifiable* hypothesis with a stated null and a "does it hurt?" guardrail (E4).

## Success criteria
- A standalone paper section that a co-author could paste into the draft.
- E3–E9 each appear as a designed experiment with metric + control.
- Result tables present but every data cell marked `PENDING` (zero fabricated numbers).
- Blocker (E1/E2 missing model+data) stated in-section as the gating dependency.
- Markdown parses; no shared core file touched.
