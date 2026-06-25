# F15 — SUMMARY: arXiv preprint submission-readiness package

**Task:** Prepare to submit the SRE-Degrees paper to arXiv as a priority preprint before the AAAI
deadline. Do NOT actually submit (requires compiled PDF + arXiv account — documented blocker).

## Delivered (real, validated, task-namespaced under `F15/artifacts/`)
- **`arxiv_metadata.yaml`** + **`arxiv_metadata.md`** — title, authors (TBD, not fabricated),
  self-contained macro-free abstract (1215 chars < 1920 limit), categories **cs.SE** (primary) +
  **cs.AI, cs.LG** (cross-list) with justification, ACM class, comments, license.
- **`SUBMISSION_CHECKLIST.md`** — ordered gated checklist: paper-body gate, compile, `.bbl`,
  two-artifact anonymity gate, AAAI dual-submission policy, packaging, form fields, endorsement,
  license, post-submit.
- **`package_arxiv.py`** — stdlib-only, deterministic, idempotent packaging script that bundles the
  F6 LaTeX source into an arXiv AutoTeX-ready tarball, whitelists extensions, excludes aux junk,
  resolves the `\input` graph, checks `.bbl`/anonymity, and reports a readiness verdict with an
  advisory exit code (0 ready / 1 not-ready / 2 fatal).
- **`test_package_arxiv.py`** — 6 pytest cases, all passing.
- **`dist/arxiv_submission.tar.gz`** (6.9 KB, 10 real F6 files) + **`dist/MANIFEST.txt`**.

## Results
- pytest: 6 passed. YAML valid; abstract under limit, macro-free.
- Packager on the **real F6 tree**: packaged 10 files, deterministic (identical sha256 across runs),
  and correctly surfaced the live blockers `NO_BBL` (paper not yet compiled -> no bibliography) and
  `ANON_AUTHOR` (de-anonymize the arXiv copy) -> advisory exit 1.

## Blocker (honest)
Cannot actually submit: needs a compiled PDF + `main.bbl` (no LaTeX toolchain/official `aaai2026.sty`
here) and an authenticated arXiv account (+ possible endorsement). All are auto-detected by the
packager and enumerated in the checklist. No shared core files edited; F6 read-only.

**Status: completed** (readiness package real and tested; submission itself blocked as the task requires).
