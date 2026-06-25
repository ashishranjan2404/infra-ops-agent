# SRE-Degrees --- AAAI-2026 paper package

LaTeX skeleton formatted for the AAAI 2026 author kit (letterpaper, two-column,
no section numbers, Times/Helvetica/Courier, `\frenchspacing`). Section stubs pull
in the F1--F5 content structure of the project.

## Files
- `main.tex` --- driver: AAAI preamble, metadata, `\input`s each section, bibliography.
- `aaai2026-stub.sty` --- structural stand-in for the licensed `aaai2026.sty` so the
  document parses/compiles without the official style. **Replace with the real
  `aaai2026.sty` for an actual submission** (the `\IfFileExists` guard auto-selects it).
- `sections/00_abstract.tex` --- abstract (<= 250 words).
- `sections/01_introduction.tex` --- F1: framing + thesis + contributions.
- `sections/02_environment.tex` --- F2: CIDG environment + Tier-A sim + Tier-B cluster.
- `sections/03_reward_verifier.tex` --- F3: root-cause reward + searched verifier.
- `sections/04_experiments.tex` --- F4: model eval + verifier generalization (2 tables).
- `sections/05_ablation_limits.tex` --- F5: honest ablation + limitations (1 table).
- `sections/06_conclusion.tex` --- conclusion + reproducibility.
- `references.bib` --- bibliography.
- `check_balance.py` --- structural validator (environments, braces, `\input` targets,
  AAAI spine) for environments with no TeX toolchain.
- `Makefile` --- `make` (pdflatex+bibtex) or `make parse-check`.

## Page limits (AAAI 2026)
Technical track: 7 pages of body + unlimited references; camera-ready adds 1 page.
This skeleton fits the budget at draft density; final length must be checked after
compilation with the real style.

## Building
With a TeX distribution:
```
make            # pdflatex -> bibtex -> pdflatex x2
```
Without one (this environment):
```
make parse-check    # python3 check_balance.py  --> ALL CHECKS PASS
```
