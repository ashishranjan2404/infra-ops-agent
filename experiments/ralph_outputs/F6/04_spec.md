# F6 — 04 Spec

## Package layout
```
artifacts/aaai-paper/
  main.tex                 # driver + AAAI preamble
  aaai2026-stub.sty        # guarded structural stand-in for aaai2026.sty
  references.bib           # 5 entries
  Makefile                 # make | make parse-check | make clean
  README.md                # build instructions + page-limit caveat + stub warning
  check_balance.py         # structural validator (exit 0/1)
  sections/
    00_abstract.tex        # <=250 words
    01_introduction.tex    # F1
    02_environment.tex     # F2
    03_reward_verifier.tex # F3
    04_experiments.tex     # F4  (Table tab:models, tab:verifier)
    05_ablation_limits.tex # F5  (Table tab:ablation)
    06_conclusion.tex
```

## main.tex preamble contract (AAAI 2026)
- `\documentclass[letterpaper]{article}` — exact, unchanged.
- Style selection: `\IfFileExists{aaai2026.sty}{\usepackage{aaai2026}}{\usepackage{aaai2026-stub}}`.
- `\usepackage{times,helvet,courier}` ; `\frenchspacing` ; pdf page size 8.5×11in.
- `\pdfinfo{ /Title (...) /Author (...) /TemplateVersion (2026.1) }`.
- `\setcounter{secnumdepth}{0}` (AAAI forbids section numbers).
- `\title{...}` ; `\author{}` (anonymous) ; `\affiliations{Anonymous Submission}`.
- Body: `\maketitle`, `\begin{abstract}\input{...}\end{abstract}`, six `\input`s,
  `\bibliographystyle{aaai2026}`, `\bibliography{references}`.
- Forbidden packages NOT used: geometry, fullpage, layout, enumerate.

## Reward equation contract (sec 03)
`r = 0.30 d + 0.25 f + 0.45 s - 0.60 t`, where d=diagnosis(mechanism judge),
f=correct-fix, s=resolved, t=trap indicator. Must match `rex/scoring.py`.

## Tables contract
- `tab:models`: Haiku 0.27 / Opus 0.50 (one-shot). Source comment present.
- `tab:verifier`: hand-written 0.95 acc / 14 rules ; searched 0.90 acc / 3 rules.
- `tab:ablation`: zero-shot 0.24, best-of-N 0.24, retry 0.23, REx-stripped 0.25.

## check_balance.py contract
Inputs: reads `main.tex` and every `\input`-ed `.tex`.
Checks & exit codes:
- Environment balance: each `\begin{e}` matched by `\end{e}`, correctly nested → else FAIL.
- Brace balance per file (escaped `\{ \}` and `%`-comments ignored) → else FAIL.
- `\input{...}` targets exist on disk → else FAIL.
- AAAI spine regexes present in main.tex: documentclass[letterpaper]{article},
  begin/end document, maketitle, abstract env, bibliography → else FAIL.
- Prints per-check PASS/FAIL; returns 0 iff all pass.

## Test cases for the validator
1. Happy path (the shipped package) → exit 0, "ALL CHECKS PASS".
2. Negative: a deliberately unbalanced `\begin{itemize}` (no `\end`) → exit 1, env FAIL.
3. Negative: a missing `\input` target → exit 1, input FAIL.
(2 and 3 are run as temp-copy smoke tests in 07, not shipped in the package.)
