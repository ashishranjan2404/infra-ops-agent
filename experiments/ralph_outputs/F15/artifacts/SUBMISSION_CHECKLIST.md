# arXiv Submission Checklist — SRE-Degrees (priority preprint before AAAI deadline)

Ordered, human-runnable. **Gates** (must pass) are marked 🚧. Do not click "submit" until every
gate is green. This task does NOT submit — it makes submitting a 10-minute, low-error operation.

## 0. Prerequisites (blockers)
- [ ] 🚧 **Paper body complete.** `F6/artifacts/aaai-paper/sections/*.tex` are NON-EMPTY.
      *Current status: EMPTY — this is the headline blocker. Cannot post until filled.*
- [ ] 🚧 **Compiles to PDF.** `pdflatex main && bibtex main && pdflatex main && pdflatex main`
      with the official `aaai2026.sty` produces `main.pdf` with no unresolved refs/citations.
- [ ] 🚧 **`main.bbl` exists** after BibTeX (arXiv runs AutoTeX and will NOT run BibTeX for you).

## 1. Two-artifact gate (anonymity) 🚧
- [ ] arXiv copy is **non-anonymous**: replace `\author{}` / "Anonymous Submission" with real authors
      + affiliations. (The packager warns `ANON_AUTHOR` if it still says "Anonymous".)
- [ ] AAAI review PDF stays **anonymous** — keep that build separate; do not upload the non-anon
      PDF to the AAAI system.
- [ ] Self-citations to this preprint are written in the **third person** (no "in our prior arXiv...").

## 2. AAAI dual-submission policy 🚧
- [ ] Confirm AAAI 2026 call-for-papers permits **prior/parallel arXiv posting** (it generally does;
      verify the exact track wording for any anonymization window).
- [ ] Posting timestamp is **before** the AAAI submission deadline (this is the priority point).

## 3. Package the source
- [ ] Run `python3 package_arxiv.py` (defaults to the F6 source tree).
- [ ] Exit code **0** = ready. Exit code **1** = packaged but NOT ready (read the READINESS block at
      the top of `dist/MANIFEST.txt` and fix). Exit code **2** = no main `.tex` (fatal).
- [ ] Inspect `dist/MANIFEST.txt`: confirm `main.tex`, all `sections/*.tex`, `*.bbl`, `*.sty`,
      figures are present; confirm NO `.aux/.log/.bib`-only artifacts.

## 4. arXiv form fields (paste from `arxiv_metadata.yaml`)
- [ ] Title (plain text, `\\` removed).
- [ ] Authors (one per line, real names).
- [ ] Abstract (≤1920 chars, **no LaTeX macros**, no `\cite`/`\ref`).
- [ ] Primary category `cs.SE`; cross-list `cs.AI`, `cs.LG`.
- [ ] ACM-class `I.2.6; D.2.5; D.4.5`.
- [ ] Comments line with **actual** page/figure counts + code URL.

## 5. Account / process
- [ ] 🚧 Authenticated arXiv account.
- [ ] 🚧 **Endorsement** for `cs.*` if first-time submitter (request early — it can take days).
- [ ] License: default **arXiv non-exclusive**. Only choose CC BY 4.0 if intended (irreversible).
- [ ] Upload `dist/arxiv_submission.tar.gz`; verify the arXiv AutoTeX preview PDF matches local PDF.
- [ ] Check the auto-generated PDF for missing figures / font / overfull boxes before finalizing.

## 6. Post-submit
- [ ] Record the arXiv ID + submission timestamp (priority evidence).
- [ ] Add the arXiv ID to the AAAI submission's "related preprint" field if/where required.
- [ ] Do NOT announce on social media during the AAAI review/anonymity window if the track restricts it.

---
**Current overall status:** READY-PENDING-PAPER-BODY. Blocked at gate 0 (empty `sections/*.tex`).
Everything downstream (metadata, packaging, checklist) is prepared and tested.
