# F15 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **REV** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes

**SMR:** arXiv before AAAI is the right move *only* if it doesn't violate the track's
anonymity policy. The real deliverable is a metadata block whose abstract is self-contained
and macro-free. Don't ship `\cite` or `\ref` in the arXiv abstract field.

**PSRE:** I care that the artifact is reproducible. A packaging script that depends on `latexmk`,
`tar` flags, or network is fragile. Make it stdlib Python, deterministic, and idempotent. Treat
it like a build step that runs in CI with no internet.

**REV:** As a reviewer I'll note: AAAI 2026 is double-blind during review. Posting a *non-anonymous*
preprint is allowed by AAAI's policy (it follows the "arXiv is fine, don't advertise" rule), but
the submission still must be anonymized in the AAAI system. The package must not conflate the two
artifacts: the arXiv tarball is *non-anonymous*, the AAAI PDF is *anonymous*.

**RLE:** The whole point of priority is the timestamp. If F6's sections are empty, you cannot
compile a real PDF, so you cannot actually post. The honest output is a *ready* package plus a
blocker. Don't pretend a PDF exists.

**DOL:** Packaging correctness is where arXiv submissions die. arXiv runs AutoTeX and wants the
`.bbl` shipped (it won't run BibTeX with your `.bib`). It wants a flat-ish tree, no `.aux/.log`,
and `\pdfoutput=1` if you use pdf-only graphics. The script should *whitelist* extensions.

## Round 2 — react to another persona by name (genuine disagreement)

**RLE → PSRE:** I disagree with "treat it like a CI build step" being enough. CI determinism is
necessary but not sufficient — the script must *fail loud* when the source is incomplete. A green
build over an empty `sections/` dir is worse than a red one, because it lulls a human into uploading
a broken paper. Determinism without a completeness gate is a footgun.

**PSRE → RLE:** Pushback. The script's job is to *package*, not to *judge paper quality*. If I bolt
"is the paper finished?" logic into a tarball builder I've coupled two concerns. Compromise: the
script packages whatever exists but emits a separate, machine-readable **readiness verdict**
(`status: incomplete`, with reasons) and a non-zero *advisory* exit code — packaging still succeeds,
completeness is reported, not enforced by refusing to write the tar.

**REV → SMR:** I disagree that anonymity is "only if." It is load-bearing, not conditional. If we
post a non-anonymous arXiv preprint and *also* submit to AAAI, the reviewer-facing PDF must remain
anonymous AND we must not cite the arXiv version in a way that de-anonymizes. The checklist must
make this a hard gate with two distinct artifacts, not a footnote.

**SMR → REV:** Partial agreement, but you're overstating risk. AAAI explicitly permits prior/parallel
arXiv posting; the de-anonymization risk is about *self-citation phrasing*, not the existence of the
preprint. So the gate isn't "don't post" — it's "post the non-anon version, keep the AAAI version
anon, and write self-cites in third person." I'll fold your two-artifact distinction in.

**DOL → PSRE:** I side with RLE over you on one point: the script *must* check that a `.bbl` exists
(or that there are no `\bibliography` calls). That's not "judging quality," that's packaging
correctness — shipping a `.bib` without `.bbl` is the single most common arXiv AutoTeX failure.
That check belongs in the packager.

## Round 3 — synthesis

Consensus reached:
1. **Two distinct artifacts, never conflated:** (a) non-anonymous arXiv tarball, (b) anonymous AAAI
   PDF. Checklist enforces this as a gate (REV + SMR).
2. **Packager = stdlib-only, deterministic, idempotent, whitelist-based** (PSRE + DOL).
3. **Separation of concerns w/ a readiness verdict:** the packager *always* builds the tar of what
   exists but emits a `readiness` block + advisory exit code (1 = not-ready) so a human is warned but
   not blocked (PSRE ↔ RLE compromise).
4. **Packaging-correctness checks live in the packager** specifically: `.bbl` present-or-no-bib,
   no aux junk, primary `.tex` with `\documentclass`, all `\input`/`\include` targets resolvable
   (DOL + RLE).
5. **AAAI dual-submission + de-anonymization** is a hard checklist gate; self-cites in third person
   (REV + SMR).
6. **Blocker is real and stated:** F6 `sections/*.tex` empty ⇒ no compilable PDF ⇒ cannot post yet.
   The package is "ready-pending-paper-body" (RLE).
