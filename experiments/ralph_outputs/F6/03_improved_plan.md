# F6 — 03 Improved Plan

## What changed after the grill

### Accepted critiques
1. **(SRE) Cite exact run files in `.tex` comments.** Every number now has a source comment:
   `hud_eval_showcase.log` (0.27/0.50), `harness_synth.json` HUD job abf124e2 (0.90 vs 0.95),
   `ablation.json` (0.24/0.25). Done in section files.
2. **(REV/DOL) Guard the stub + loud warning.** `main.tex` uses
   `\IfFileExists{aaai2026.sty}{official}{stub}`; the stub header and README both state in
   bold that the stub is NOT AAAI-compliant and must be replaced for submission.
3. **(REV) Full AAAI spine.** letterpaper `article`, Times/Helvetica/Courier,
   `\frenchspacing`, `\setcounter{secnumdepth}{0}`, `\pdfinfo{...}`, `\affiliations`,
   anonymous author, `\thispagestyle{empty}`.
4. **(RLE) No page-limit claim.** README says "fits at draft density, must be re-checked
   post-compile against the real style" — not "fits 7 pages."
5. **(SMR) Honest framing.** Ablation section + table are mandatory and present; the
   conclusion relocates the contribution to env+verifier, matching the headline doc.
6. **(RLE) Exact reward + verifier wording.** Eq. (1) uses 0.30/0.25/0.45/−0.60; verifier
   described as "Thompson-sampling tree over rules-as-data, no LLM code execution."

### Rejected critiques (with reasons)
- **(SMR) "Skeleton should carry full prose framing."** Partially rejected in favor of
  SRE's lean-stub view: stubs carry the *claims and tables* but stay short so F4/F5 owners
  fill detail without fighting prose. Compromise reached in R3.
- **(DOL implied) "Install a TeX toolchain / claim it compiles."** Rejected: no toolchain is
  present and installing MacTeX is out of scope and not parallel-safe. Instead deliver a
  real structural validator and document the blocker honestly per the brief.

## Final deliverable shape
`artifacts/aaai-paper/`: `main.tex`, `sections/00..06`, `aaai2026-stub.sty`,
`references.bib`, `Makefile`, `README.md`, `check_balance.py`.
Validation = `python3 check_balance.py` (envs, braces, `\input`s, AAAI spine) → must PASS.
