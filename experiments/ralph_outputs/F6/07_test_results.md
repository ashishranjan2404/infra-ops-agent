# F6 — 07 Test Results

## Toolchain probe
```
$ which pdflatex xelatex latexmk tlmgr
pdflatex not found
xelatex not found
latexmk not found
tlmgr not found
```
**No LaTeX toolchain present.** Per the brief, validation is therefore **structural** (and a
real validator was written), not a `pdflatex` compile. The package is built to compile as-is
once a TeX distribution + `aaai2026.sty` (or the shipped stub) is available.

## Happy-path structural validation
```
$ python3 check_balance.py
== \input targets ==
  PASS: all 7 \input targets exist
== environment balance ==
  PASS: all \begin/\end environments balanced and nested
== brace balance (per file) ==
  PASS: main.tex
  PASS: sections/00_abstract.tex
  PASS: sections/01_introduction.tex
  PASS: sections/02_environment.tex
  PASS: sections/03_reward_verifier.tex
  PASS: sections/04_experiments.tex
  PASS: sections/05_ablation_limits.tex
  PASS: sections/06_conclusion.tex
== AAAI required spine ==
  PASS: \documentclass[letterpaper]{article}
  PASS: \begin{document}
  PASS: \end{document}
  PASS: \maketitle
  PASS: abstract env
  PASS: bibliography

RESULT: ALL CHECKS PASS    (exit 0)
```

## Negative smoke tests (prove the validator actually fails, not rubber-stamps)
Run on throwaway temp copies; the shipped package is untouched.
```
=== NEG TEST 1: unclosed environment (append dangling \begin{itemize}) ===
correctly FAILED (exit=1)
=== NEG TEST 2: missing \input target (repoint to does_not_exist) ===
correctly FAILED (exit=1)
```

## Other checks
- `make parse-check` → `RESULT: ALL CHECKS PASS`.
- Abstract length: `wc -w sections/00_abstract.tex` = 194 (≈180 words of prose excluding the
  `% comment`), under the AAAI 250-word cap.
- Scenario count claim: `ls scenarios/cidg/generated/*.yaml | wc -l` = **51** — matches the
  "51 generated scenarios" claim in the abstract and §2.

## Fixes applied during testing
None required — happy path passed first run; negative tests confirmed the validator's
discrimination, so no validator bug to fix.

## Blocker
`pdflatex` is unavailable in this environment, so an actual PDF compile and a true page-count
measurement could not be performed. The package is structurally validated and compile-ready.
