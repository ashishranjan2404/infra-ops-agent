# F15 — 03 Improved Plan (post-grill)

## What changed vs 01_plan
1. **Readiness verdict separated from packaging (accepted PSRE↔RLE compromise).**
   The packager now *always* writes the tarball of whatever source exists, but additionally emits
   a `readiness` block (to stdout + MANIFEST) and returns a **non-zero advisory exit code (1)** when
   the source is not submission-ready. Packaging != quality-judging, but the human is warned loudly.

2. **Packaging-correctness checks added to the script (accepted DOL + RLE).**
   - Primary `.tex` must contain `\documentclass`.
   - Every `\input{}` / `\include{}` target must resolve to a non-empty file (empty = incompleteness flag).
   - If any `\bibliography{}` exists, a sibling `.bbl` must exist (arXiv runs AutoTeX, not BibTeX).
   - Whitelist included extensions (`.tex .bbl .cls .sty .bib .bst .pdf .png .jpg .jpeg .eps .ps`);
     explicitly **exclude** `.aux .log .out .toc .blg .fls .fdb_latexmk .synctex.gz`.

3. **Two-artifact gate made explicit in the checklist (accepted REV + SMR).**
   - Artifact A = **non-anonymous** arXiv tarball (real authors, real affiliations).
   - Artifact B = **anonymous** AAAI PDF (kept separate; "Anonymous Submission").
   - Checklist step: de-anonymize the arXiv copy, write self-citations in third person.

4. **AAAI dual-submission policy turned into a hard checklist gate (accepted REV).**
   Confirm AAAI 2026 permits parallel/prior arXiv posting before clicking submit.

## Critiques rejected (with reasons)
- **REV's "anonymity might mean don't post at all":** rejected. AAAI explicitly allows prior arXiv
  posting; the risk is self-citation phrasing, not the preprint's existence (SMR's correction).
  We mitigate with the third-person-self-cite checklist item, not by refusing to post.
- **PSRE's "packager must not check anything paper-shaped":** partially rejected. Pure
  packaging-*correctness* (bbl/aux/input-resolution) is in-scope for a packager and is the #1 cause
  of arXiv failures; we keep those. We *do* honor the boundary by not judging prose/novelty/length.

## Final deliverable shape
- `arxiv_metadata.yaml` + `.md` — single source of truth + human view.
- `SUBMISSION_CHECKLIST.md` — ordered, gated, AAAI-aware.
- `package_arxiv.py` — stdlib, deterministic, idempotent, whitelist, readiness verdict, advisory exit.
- `test_package_arxiv.py` — pytest over synthetic complete + incomplete trees.
- `dist/arxiv_submission.tar.gz` + `dist/MANIFEST.txt` — produced from the real F6 tree.

## Honest blocker carried forward
F6 `sections/*.tex` are empty ⇒ no `.bbl`, no compilable PDF ⇒ **cannot actually post**. The package
is "ready-pending-paper-body." This is documented in 07 and 09; status = completed (deliverable real)
with blocker noted.
