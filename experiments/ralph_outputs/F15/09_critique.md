# F15 — 09 Critique (honest)

## What a reviewer would attack
1. **"You didn't actually submit, so the priority claim is unproven."** True and unavoidable: the
   task forbids submitting, and submission needs a compiled PDF + an authenticated arXiv account +
   (possibly) endorsement. The deliverable is *readiness*, not the timestamp. The package shrinks
   the human's remaining work to: fill authors, compile to get `.bbl`, upload. Honest, not magic.
2. **`NO_BBL` is the live blocker.** The paper is not yet compiled, so there is no `main.bbl`. arXiv
   runs AutoTeX (no BibTeX), so the current tarball would fail AutoTeX. The packager *detects* this
   (exit 1) rather than shipping a broken tar silently — but it cannot manufacture a `.bbl` without
   a working LaTeX toolchain + the official `aaai2026.sty`/`.bst`, which aren't in this environment.
3. **Abstract is authored here, not extracted from the compiled paper.** At plan time F6 sections
   were empty; the abstract in metadata is a faithful summary of the project scope but MUST be
   reconciled against `sections/00_abstract.tex` (now populated) before posting. The checklist flags
   this; I did not auto-sync it (that would risk silently diverging from the real abstract).
4. **Authors are `TBD`.** Some reviewers want a "finished" artifact. Fabricating author names would
   be worse. The non-anonymous arXiv requirement is a human decision, gated in the checklist.
5. **No LaTeX-macro linter on the abstract.** Macro-freeness is verified by grep (07), not enforced
   programmatically. Deliberately scoped out (ouroboros Eng2) to avoid over-engineering; a single
   grep is sufficient for a hand-authored field.

## What's genuinely weak
- The packager trusts that `references.bib` + a future `.bbl` are consistent; it can't verify
  citations actually resolve without compiling.
- No end-to-end "compile then package" path, because the LaTeX toolchain + official AAAI style are
  absent. A fuller version would shell out to `latexmk` when available and fail loudly otherwise.
- Page/figure counts in the `comments` line are placeholders (`NN`/`MM`) pending a real PDF.

## What's solid
- The packager's separation of concerns (always package, separately report readiness, advisory exit)
  is the right call and is proven on both synthetic and the real tree.
- Determinism is real and verified (byte-identical reruns), which matters for reproducible builds.
- The anonymity / AAAI-dual-submission reasoning is correct and turned into hard gates, not prose.

## Net
A real, tested, honest readiness package. The only thing standing between this and an actual arXiv
posting is a compiled PDF/.bbl and a human with an account — both explicitly out of scope, both
clearly documented and auto-detected.
