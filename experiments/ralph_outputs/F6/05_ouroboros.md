# F6 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the LaTeX pedant"
**Problems found:**
1. The stub redefines `\maketitle` with `\twocolumn[...]`; if a section accidentally also
   issues `\twocolumn` or `\onecolumn` the layout breaks. → Acceptable: sections never do;
   documented that stub is approximate only.
2. `\pdfinfo` is a pdfTeX primitive; under a non-pdfTeX engine (lualatex/xelatex) it errors.
   → AAAI mandates pdflatex, and `main.tex` build command is pdflatex; note it in README.
3. Validator ignores `%` comments but a stray `\%` (literal percent) inside text is handled
   by the `\`-escape rule — verified in `strip_comments`. OK.
**Verdict:** preamble is AAAI-faithful; stub caveats documented.

## Engineer B — "the content/reviewer skeptic"
**Problems found:**
1. Stubs assert numbers (0.50, 0.90) with source *comments* but the source files
   (`hud_eval_showcase.log`, `harness_synth.json`) are referenced, not embedded — a reviewer
   of THIS package can't see them. → Acceptable for a *formatting* deliverable; numbers trace
   to `docs/headline_insights.md` which is the project's vetted summary. Flagged in 09.
2. Abstract claims "51 generated scenarios" — must match reality. → Verified: 
   `ls scenarios/cidg/generated/*.yaml` = 51. Good.
3. Risk of over-claiming page-limit compliance. → Fixed: README states draft-density only.
**Verdict:** content is honest and grounded; one inherent limit (numbers not embedded).

## Engineer C — "the build/CI engineer"
**Problems found:**
1. `make parse-check` calls `python3 check_balance.py` but Makefile didn't `cd`; since the
   script resolves paths from its own `__file__`, it's location-independent. OK.
2. No negative test shipped, so a future regression in the validator goes unnoticed. → 
   Mitigation: 07 runs negative smoke tests on temp copies to prove the validator actually
   fails on bad input (not just rubber-stamps).
3. `bibtex` step in Makefile uses `-` prefix so a missing `.bst` (stub mode) won't abort the
   build. Intentional and documented.
**Verdict:** buildable with a toolchain; validated structurally without one.

## Final filtered spec
No change to file layout. Add to the plan: **07 must run negative smoke tests** proving the
validator fails on (a) an unclosed environment and (b) a missing `\input`, in addition to the
happy-path PASS. Keep numbers traceable via comments + `headline_insights.md`; accept that
embedding raw logs is out of scope for a template package (noted in 09).
