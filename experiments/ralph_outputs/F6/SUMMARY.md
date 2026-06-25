# F6 — Summary: Format paper for AAAI 2026 template

## Deliverable
A complete, structurally-validated **AAAI-2026 LaTeX paper package** at
`experiments/ralph_outputs/F6/artifacts/aaai-paper/`:
- `main.tex` — AAAI preamble (`\documentclass[letterpaper]{article}`, official style via
  `\IfFileExists{aaai2026.sty}` guard, Times/Helvetica/Courier, `\frenchspacing`, `\pdfinfo`,
  `secnumdepth=0`, anonymous author + `\affiliations`), `\input`s all sections + bibliography.
- `sections/00..06` — abstract + 6 sections mapping the **F1–F5 content structure**
  (Intro, Environment, Reward+Searched-Verifier, Experiments, Ablation+Limits, Conclusion),
  populated with real project content and three data tables.
- `aaai2026-stub.sty` — guarded structural stand-in (compiles without the licensed style;
  loudly marked non-compliant).
- `references.bib`, `Makefile`, `README.md`, `check_balance.py`.

## Validation
No LaTeX toolchain in this environment (`pdflatex` absent), so validation is **structural**
via a real validator: `check_balance.py` → **ALL CHECKS PASS** (balanced environments/braces,
all 7 `\input`s resolve, AAAI spine present). Negative smoke tests confirm the validator fails
on an unclosed environment and a missing `\input` (exit 1 each). Abstract is under the 250-word
cap; the "51 scenarios" claim is filesystem-verified.

## Content fidelity
All numbers trace to vetted sources (`docs/headline_insights.md`, `ARCHITECTURE.md`,
`rex/scoring.py`), cited in `.tex` comments: eval 0.27/0.50, verifier 0.90 vs 0.95 (14->3 rules),
ablation 0.24/0.25, reward `0.30d+0.25f+0.45s-0.60t`.

## Blocker (honest)
Actual PDF compile and page-count compliance are **blocked** (no TeX distribution). The package
is compile-ready; per the brief, a structurally-validated scaffold + documented blocker is the
deliverable.

## Shared-core safety
No shared core files edited; all artifacts are new and under the F6 task namespace.

**Status: completed.**
