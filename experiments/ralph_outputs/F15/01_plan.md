# F15 — 01 Plan: Submit to arXiv as preprint (submission-readiness package)

## Objective
Prepare a complete, audit-ready **arXiv submission package** for the SRE-Degrees paper
so a human can upload it in minutes and claim a preprint timestamp **before the AAAI
deadline** (priority/scoop protection). The task explicitly **does NOT submit** — actual
submission requires a compiled PDF and an authenticated arXiv account. That is the
documented blocker.

## Scope (what "done" means here)
Deliver the *readiness package*, not the act of submission:
1. **arXiv metadata** — title, author block, abstract (≤1920 char arXiv limit), primary +
   cross-list categories (`cs.SE` primary, `cs.AI`, `cs.LG` cross-list), MSC/ACM optional,
   comments line, license choice.
2. **Submission checklist** — ordered, human-runnable, covering compile, anonymity-removal,
   figure/bbl inclusion, category fit, license, endorsement, AAAI dual-submission policy check.
3. **Packaging script** — bundles the LaTeX source (from `F6/artifacts/aaai-paper` if present)
   into the exact tarball arXiv expects (flattened, `.bbl` included, no `.bib`-only, no aux junk),
   validates structure, and prints a manifest. Must run with no network and degrade gracefully
   when the source tree is incomplete.

## Files to create (all task-namespaced — no shared-core edits)
- `artifacts/arxiv_metadata.yaml` — machine-readable metadata (single source of truth).
- `artifacts/arxiv_metadata.md` — human-readable rendering of the same.
- `artifacts/SUBMISSION_CHECKLIST.md` — the checklist.
- `artifacts/package_arxiv.py` — packaging script (stdlib-only, Python 3.13).
- `artifacts/test_package_arxiv.py` — pytest for the script (synthetic source tree).
- (script output) `artifacts/dist/arxiv_submission.tar.gz` + `artifacts/dist/MANIFEST.txt`.

## Dependencies
- **Source of truth for the paper:** `experiments/ralph_outputs/F6/artifacts/aaai-paper/`
  (`main.tex` present; `sections/*.tex` currently EMPTY — a real blocker for a *compilable* PDF).
- Title + abstract text: extracted from `F6/.../main.tex` `\title{}` and the abstract `\input`.
- Python 3.13 stdlib (`tarfile`, `pathlib`, `argparse`, `re`). No third-party deps → reproducible.

## Risks
- **R1 (primary blocker):** F6 `sections/` are empty → no `.bbl`, paper does not yet compile to
  a real PDF. The package will be *structurally valid* but flagged INCOMPLETE until F6 fills in.
- **R2:** AAAI anonymity vs arXiv non-anonymity — must strip "Anonymous Submission" and add real
  authors before posting, AND confirm AAAI 2026 permits prior arXiv posting (most AAAI tracks do;
  some have anonymization windows). Checklist must call this out, not silently assume.
- **R3:** arXiv abstract char limit (~1920) and no-LaTeX-macros-in-metadata rule.
- **R4:** Packaging the wrong files (shipping `.aux`/`.log`/`.bib` instead of `.bbl`) → arXiv
  AutoTeX failure. Script must whitelist, not blacklist.

## Success criteria
- Metadata file parses (YAML) and has all required arXiv fields populated for *this* paper.
- Checklist is concrete and ordered, with the AAAI-dual-submission and de-anonymization gates.
- `package_arxiv.py` runs, builds a tarball from the F6 tree (or a synthetic tree), emits a
  manifest, and *correctly reports the incomplete-source blocker* with a non-zero advisory.
- `test_package_arxiv.py` passes under pytest.
- Blocker (no real PDF / no submit) documented honestly in 07 and 09.
- **No shared core file edited.**
