# F6 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/F6/artifacts/aaai-paper/`)

A complete, validate-able AAAI-2026 LaTeX paper package:

| File | Purpose |
|---|---|
| `main.tex` | Driver. AAAI 2026 preamble: `\documentclass[letterpaper]{article}`, style via `\IfFileExists{aaai2026.sty}`, Times/Helvetica/Courier, `\frenchspacing`, `\pdfinfo` metadata, `secnumdepth=0`, anonymous `\author{}` + `\affiliations`. `\input`s all 6 sections + abstract; bibliography. |
| `aaai2026-stub.sty` | Guarded structural stand-in so the doc compiles without the licensed `aaai2026.sty`. Header + README warn in bold it is NOT submission-compliant. |
| `sections/00_abstract.tex` | Abstract (~180 words, < 250 cap). |
| `sections/01_introduction.tex` | **F1**: framing, one-line thesis, 4 contributions, code-as-policy position. |
| `sections/02_environment.tex` | **F2**: CIDG DSL, Tier-A `sim/engine.py` sim, Tier-B M-real GKE cluster, rollout harness. |
| `sections/03_reward_verifier.tex` | **F3**: graded reward Eq. (1) `0.30d+0.25f+0.45s-0.60t`, searched Thompson-tree verifier (rules-as-data, no LLM code exec). |
| `sections/04_experiments.tex` | **F4**: `tab:models` (Haiku 0.27 / Opus 0.50), `tab:verifier` (0.90 vs 0.95, 3 vs 14 rules), open-model RFT note. |
| `sections/05_ablation_limits.tex` | **F5**: `tab:ablation` (0.24/0.24/0.23/0.25), re-centering, 4 limitations. |
| `sections/06_conclusion.tex` | Conclusion + reproducibility. |
| `references.bib` | 5 entries (code-as-policies, GRPO/DeepSeekMath, Thompson 1933, FIREBALL, self). |
| `check_balance.py` | Structural validator: environment balance, brace balance, `\input` resolution, AAAI spine. Exit 0/1. |
| `Makefile` | `make` (pdflatex+bibtex+pdflatex×2), `make parse-check`, `make clean`. |
| `README.md` | Build instructions, page-limit caveat (draft-density only), stub warning. |

## Content grounding (no fabrication)
All numbers trace to vetted project sources, cited in `.tex` comments:
- `docs/headline_insights.md` — 0.27/0.50 eval, 0.90 vs 0.95 verifier, 14→3 rules, ablation.
- `ARCHITECTURE.md` — thesis line, reward weights, two-tier env, FIREBALL schema.
- `rex/scoring.py` — reward decomposition. `scenarios/cidg/generated/*.yaml` — 51 scenarios (verified by `ls | wc -l`).

## Mapping note on "F1–F5"
No `F1..F5` output directories exist in `experiments/ralph_outputs/`. In this task F1–F5 are
the **conceptual paper sections** of the project narrative; I mapped them onto AAAI sections
1–5 and populated each with real repo content rather than inventing F1–F5 artifacts.

## Shared-core safety
No shared core files (`rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, status/dashboard)
were edited. Everything is new, under the F6 task namespace.
