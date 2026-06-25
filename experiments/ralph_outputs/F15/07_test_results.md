# F15 — 07 Test Results

## 1. Metadata YAML parse + limits
```
$ python3 -c "import yaml; d=yaml.safe_load(open('arxiv_metadata.yaml')); ..."
keys: ['abstract','acm_class','authors','comments','cross_list','doi','journal_ref',
       'license','msc_class','notes','primary_category','report_no','title']
primary: cs.SE cross: ['cs.AI', 'cs.LG']
abstract chars: 1215            # < 1920 arXiv limit  PASS
```
Macro-free check:
```
$ grep -nE '\\(cite|ref|input|textbf|emph)' arxiv_metadata.yaml
no LaTeX macros in metadata file body            PASS
```

## 2. Packager unit tests (pytest)
```
$ python3 -m pytest test_package_arxiv.py -q
......                                                                   [100%]
6 passed in 0.03s
```
Covers: complete→ready(0), empty-input→advisory(1, tar still written), missing-bbl→(1),
no-main→fatal(2, no tar), determinism (identical sha256 across runs), junk (.aux) excluded.
ALL PASS.

## 3. Packager on the REAL F6 paper tree
```
$ python3 package_arxiv.py ; echo EXIT=$?
main: main.tex
files packaged: 10
tarball: .../dist/arxiv_submission.tar.gz  sha256=668b2835616f4ee7...
READINESS: NOT-READY
  [BLOCK] NO_BBL: \bibliography{} present but no .bbl shipped (arXiv will not run BibTeX)
  [WARN]  ANON_AUTHOR: main still says 'Anonymous' — de-anonymize the arXiv copy
EXIT=1
```
Packaged 10 real files (main.tex, 6 section files, references.bib, aaai2026-stub.sty). Tar written;
advisory exit 1 with the correct, honest blockers surfaced. PASS (behaves exactly as designed).

## 4. Determinism on the real tree
```
$ python3 package_arxiv.py; python3 package_arxiv.py   # twice
TAR_SHA256: 668b2835616f4ee782b7b58139dfc889773f63acffe4b0c2dab93b4543bbec70
TAR_SHA256: 668b2835616f4ee782b7b58139dfc889773f63acffe4b0c2dab93b4543bbec70
DETERMINISTIC: OK
```

## Fixes applied during dev
- Ouroboros Eng1 caught gzip-header non-determinism: implemented in-memory tar + `GzipFile(mtime=0)`
  rather than `tarfile.open("w:gz")`. Verified byte-identical reruns (section 4).
- Comment-stripping added so `% \input{...}` is not a false positive.

## Blocker (honest)
- **Cannot actually submit.** Two real gates remain: (a) **`NO_BBL`** — the paper has not been
  compiled, so no `main.bbl` exists (arXiv runs AutoTeX, not BibTeX); (b) authors are anonymous /
  `TBD` and must be filled (the arXiv copy is non-anonymous). Both are surfaced automatically by the
  packager and enumerated in the checklist. Actual submission also needs a human arXiv account +
  endorsement. NOT performed, per task constraints.
