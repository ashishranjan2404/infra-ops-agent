# F6 — 01 Plan

## Objective
Format the SRE-Degrees paper for the **AAAI 2026** LaTeX template: a real AAAI-style
LaTeX skeleton (`main.tex` with AAAI conference preamble), section stubs that pull in the
F1–F5 content structure, and a bibliography. Validate it compiles or, if no LaTeX
toolchain is present, validate structurally (balanced environments/braces, resolvable
`\input`s, required AAAI spine). Deliver the `.tex` package.

## Approach
1. Ground the paper content in real project material: `ARCHITECTURE.md`,
   `docs/headline_insights.md`, `rex/scoring.py` reward, `rex/harness_synth.py` verifier.
2. Map the F1–F5 structure onto AAAI sections:
   - F1 → Introduction (framing + thesis + contributions)
   - F2 → The CIDG Environment (DSL, Tier-A sim, Tier-B cluster)
   - F3 → Root-Cause Reward and Searched Verifier
   - F4 → Experiments (model eval + verifier generalization)
   - F5 → Honest Ablation and Limitations
   - + Conclusion
3. Write `main.tex` with the AAAI 2026 preamble (letterpaper article, `aaai2026` style,
   Times/Helvetica/Courier, `\frenchspacing`, `secnumdepth=0`, `pdfinfo` metadata,
   `\affiliations`).
4. Ship a structural stub style `aaai2026-stub.sty` guarded by `\IfFileExists` so the
   document is buildable without the licensed `aaai2026.sty`.
5. `references.bib`, `Makefile`, `README.md`.
6. Validate: try `pdflatex`; if absent, run a real structural validator
   (`check_balance.py`).

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/F6/artifacts/aaai-paper/main.tex`
- `.../sections/00_abstract.tex` … `06_conclusion.tex`
- `.../aaai2026-stub.sty`, `references.bib`, `Makefile`, `README.md`, `check_balance.py`

## Dependencies / risks
- **No TeX toolchain** in this environment (confirmed: no `pdflatex/xelatex/latexmk`).
  Mitigation: structural validator + a stub style; document the blocker honestly.
- The official `aaai2026.sty` is license-restricted and not redistributable. Mitigation:
  `\IfFileExists` guard + stub; README tells the author to drop the real style in.
- F1–F5 are conceptual paper sections here (no `F1..F5` output dirs exist); content is
  pulled from real repo docs, not invented.

## Success criteria
- A complete, self-consistent `.tex` package with AAAI preamble + 6 section files + bib.
- Structural validation passes (balanced envs/braces, all `\input`s resolve, AAAI spine).
- Content traces to real project numbers (0.27/0.50 eval; 0.90 vs 0.95 verifier; ablation).
- No shared core files edited.
