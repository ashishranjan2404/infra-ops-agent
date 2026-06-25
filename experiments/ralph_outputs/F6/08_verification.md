# F6 — 08 Verification

## Against success criteria (from 01_plan)

| Criterion | Status | Evidence |
|---|---|---|
| Complete `.tex` package: AAAI preamble + 6 sections + bib | **MET** | 13 files under `artifacts/aaai-paper/`; `find` listing in 06. |
| AAAI 2026 preamble correct | **MET** | `\documentclass[letterpaper]{article}`, official-style guard, Times/Helvetica/Courier, `\frenchspacing`, `\pdfinfo`, `secnumdepth=0`, anonymous author. Spine check PASS. |
| Section stubs pull in F1–F5 content structure | **MET** | §1=F1, §2=F2, §3=F3, §4=F4, §5=F5, each populated with real repo content (not empty). |
| Bibliography present | **MET** | `references.bib` (5 entries) + `\bibliography{references}` + `\bibliographystyle{aaai2026}`. |
| Validate compiles OR parses structurally | **MET (structural)** | No toolchain → `check_balance.py` ALL CHECKS PASS; negative tests confirm it discriminates. |
| Content traces to real numbers | **MET** | 0.27/0.50, 0.90 vs 0.95, 14→3, ablation 0.24/0.25 — all cited to `headline_insights.md`; 51 scenarios verified by `ls`. |
| No shared core files edited | **MET** | `git status` shows only new files under `experiments/ralph_outputs/F6/` (verified below). |

## Outputs are real, not placeholder
- The `.tex` files contain real prose, a real reward equation, and three real data tables —
  not `\section{TODO}` stubs.
- `check_balance.py` is a working program (passes happy path, fails injected bad input).
- The stub style is a real, functioning `.sty` (redefines `\maketitle`, `\affiliations`).

## Git cleanliness check
All F6 artifacts are net-new files under the task namespace; no tracked shared file is in the
working-set diff for this task.

## Honest caveats (carried to 09)
- "Compiles" is asserted structurally, not via `pdflatex`; page-count compliance is unproven.
- The stub is not AAAI-submission-compliant (guarded + warned).
- Numbers are referenced by source, not embedded as raw logs in the package.
