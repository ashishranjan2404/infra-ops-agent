# E10 — Spec

This is a *writing* deliverable; the "API contract" is the document structure, the table
schemas, and the validation gates. No runtime code is produced.

## Deliverable
`experiments/ralph_outputs/E10/artifacts/fireball_transfer_section.md`

## Document contract

### Front matter
- A single H1 `# 5.x Cross-Domain Transfer: FIREBALL → SRE` (placeholder numbering noted).
- A one-paragraph abstract of the section.

### Required subsections (H2), in order
1. `## 5.x.1 Hypothesis & motivation`
2. `## 5.x.2 Methodology`
3. `## 5.x.3 Experiment design (E3–E9)`
4. `## 5.x.4 Pre-registered results`
5. `## 5.x.5 Status & blockers`
6. `## 5.x.6 Threats to validity`

### Hypotheses block (in 5.x.1)
Each hypothesis is a row with: id, statement, null, primary metric.
- **H1** transfer helps **cascades** (correct-fix + trap-avoidance ↑ vs OpenSRE-only).
- **H2** transfer does **not hurt** simple incidents (no-harm guardrail; E4).
- **H3** the *full trajectory* (state+action+state) carries the transfer, not state- or
  action-only (mechanistic; E6).
- **H4** transfer beats an equal budget of synthetic SRE augmentation (E9) — i.e. the gain
  is *transfer*, not merely *more data*.
- **Stated null (falsification):** if Fireball-trained ≤ OpenSRE-trained on cascade
  correct-fix-rate within the benchmark's Wilson 95% CI, report **no / negative transfer**.

### Experiment-design table schema (5.x.3)
Columns: `ID | Question | Design | Primary metric | Control / comparison | Status`.
Rows: **E3, E4, E5, E6, E7, E8, E9** — taken verbatim-in-spirit from
`experiments/NEXT_100_TASKS.md` §E. Status column ∈ {`pending (needs E1/E2)`}.

Mapping (must match repo source):
- E3 — Fireball vs OpenSRE vs zero-shot on **cascade** incidents (14), pass@1 by family.
- E4 — Fireball vs OpenSRE on **simple** incidents (8) — does it hurt? (no-harm guardrail)
- E5 — Fireball transfer on **novel** incidents (10) — generalization.
- E6 — Ablate Fireball: full vs state-only vs action-only (mechanism / H3).
- E7 — transfer from **other** source domains (text-adventure), not just D&D (frontier).
- E8 — data-scaling: 1k / 10k / 50k trajectories (how much is needed).
- E9 — Fireball transfer **vs** synthetic SRE augmentation (transfer-vs-more-data / H4).

### Pre-registered result tables (5.x.4) — ALL cells `PENDING`
- **T1 (E3) — cascade pass@1 by family:** rows = incident families (DNS/control-plane/
  config-crash/dependency/resource); cols = {Fireball-trained, OpenSRE-trained, zero-shot};
  cells = `PENDING`. Plus a **trap-avoidance-rate** row group (headline).
- **T2 (E4/E5) — no-harm + generalization:** rows = {simple (E4), novel (E5)}; cols =
  {Fireball-trained, OpenSRE-trained}; cells = `PENDING`.
- **T3 (E6/E8/E9) — ablations & controls:** rows = {full, state-only, action-only (E6);
  1k/10k/50k (E8); Fireball vs synthetic-aug (E9)}; metric col = cascade correct-fix-rate;
  cells = `PENDING`.

### Methodology contract (5.x.2) — must reference REAL repo objects
- FIREBALL trajectory shape `state_before → action/fix → state_after`
  (cite `opensre-traj/SCHEMA.md`).
- Reward weights: `0.30·diagnosis + 0.25·correct_fix + 0.45·resolved − 0.60·trap`
  (cite `rex/scoring.py`, `ARCHITECTURE.md`).
- Eval harness: `rex/eval_pass_at_k.py` (pass@k engine) on the 42-incident benchmark.
- Training: FIREBALL SFT pretraining → GRPO on the opensre env, group sizes for
  within-group reward spread (cite §3.5 of `PAPER_OUTLINE.md`, `opensre-traj/hud_env_v2.py`).
- The frozen-LLM + REx spine (C1/C3) vs this fine-tuned transfer contribution (C2):
  explicitly reconcile the two framings.

### Status & blockers (5.x.5)
- Name **E1** (Wenji's GRPO branch / Fireball-trained slug not pushed) and **E2**
  (FIREBALL `incidents.jsonl` source corpus absent). Cite `P7_fireball_status.md`,
  `CLAIMS_EVIDENCE.md`.
- Give the one-command run recipe to slot results in once unblocked (three policies through
  `rex.eval_pass_at_k` on the cascade benchmark).

## Validation gates (executed in step 07)
1. **Markdown structure:** all 6 H2 subsections present, in order.
2. **No fabricated numbers:** in the result tables (T1–T3), no decimal-number literal
   appears as a cell value — every data cell is `PENDING`. (grep gate.)
3. **E3–E9 all present** in the design table.
4. **Real-object citations present:** `rex/scoring.py`, `rex/eval_pass_at_k.py`,
   `opensre-traj/SCHEMA.md` all referenced.
5. **Falsification criterion present** (literal "null" / "falsif").

## Test cases (assertions for step 07 script)
- `assert section has >= 6 "## 5.x." headers`
- `assert "E3".."E9" all substrings present`
- `assert count of "PENDING" >= 12`
- `assert no result-table cell matches regex \b0\.\d+\b inside T1/T2/T3 blocks`
- `assert "rex/scoring.py" in text and "eval_pass_at_k" in text and "SCHEMA.md" in text`
- `assert "falsif" in text.lower() or "null" in text.lower()`
