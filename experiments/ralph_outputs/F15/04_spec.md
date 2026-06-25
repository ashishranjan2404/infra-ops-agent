# F15 — 04 Spec

## A. `arxiv_metadata.yaml` schema
```yaml
title: str                      # plain text, LaTeX line-break \\ removed
authors:                        # ordered
  - name: str
    affiliation: str
    email: str | null
abstract: str                   # <= 1920 chars, no LaTeX macros, no \cite/\ref
primary_category: "cs.SE"
cross_list: ["cs.AI", "cs.LG"]
acm_class: str | null           # e.g. "I.2.6; D.2.5"
msc_class: str | null
comments: str                   # pages/figures/code-url line shown on arXiv
license: "CC BY 4.0" | "arXiv non-exclusive" | ...
report_no: str | null
journal_ref: str | null         # null for preprint
doi: str | null
notes: str                      # internal: blockers / policy reminders
```
Required-non-null for a valid submission: title, authors[≥1].name, abstract,
primary_category, cross_list, license, comments.

## B. Category justification (must appear in metadata.md)
- **cs.SE (primary):** the contribution is a *verifiable environment + harness* for software/ops
  remediation — tooling, simulation, evaluation of an automated incident-fixing system.
- **cs.AI (cross):** searched verifier (REx / Thompson-sampling tree) is an AI search method.
- **cs.LG (cross):** pass@k evaluation, reward design, RL-adjacent agent framing.

## C. `package_arxiv.py` — contract
```
usage: package_arxiv.py [--src DIR] [--out DIR] [--main main.tex] [--name arxiv_submission]

Behavior:
  1. Resolve src (default: ../../F6/artifacts/aaai-paper relative to script).
  2. Discover main tex (has \documentclass). Error if none.
  3. Walk \input/\include graph from main; collect referenced .tex (resolve .tex ext).
  4. Collect whitelisted asset files in src tree (WHITELIST_EXT); skip JUNK_EXT.
  5. readiness checks -> list[Issue(level, code, msg)]:
       - EMPTY_INPUT: a referenced \input target is empty/0-byte  (level=block)
       - MISSING_INPUT: referenced target absent                  (level=block)
       - NO_BBL: \bibliography present but no .bbl                 (level=block)
       - NO_MAIN: no \documentclass file                          (level=fatal -> exit 2)
       - ANON_AUTHOR: main.tex still says "Anonymous"             (level=warn)
  6. Always (unless fatal) write {out}/{name}.tar.gz (flattened: arcname = path
     relative to src) deterministically (sorted, fixed mtime=0, uid/gid=0).
  7. Write {out}/MANIFEST.txt: file list + sizes + readiness verdict + sha256 of tar.
  8. Exit code: 0 = ready, 1 = packaged-but-not-ready (advisory), 2 = fatal (no main).

Determinism: tarfile entries sorted by arcname; TarInfo.mtime=0, uid=gid=0,
uname=gname="". Re-running yields byte-identical tar (same input).
Stdlib only: tarfile, hashlib, pathlib, argparse, re, sys, io.
```

### Data structures
```python
@dataclass
class Issue:   level: str   # "fatal" | "block" | "warn"
               code: str
               msg: str
@dataclass
class Readiness: ready: bool; issues: list[Issue]; files: list[str]; tar_sha256: str
```

### Key signatures
```python
def find_main(src: Path, hint: str | None) -> Path
def collect_inputs(main: Path, src: Path) -> tuple[list[Path], list[Issue]]
def collect_assets(src: Path) -> list[Path]
def check_readiness(src, main, files, issues) -> list[Issue]
def build_tarball(src, files, out_tar) -> str            # returns sha256
def write_manifest(out_manifest, files, readiness) -> None
def main(argv=None) -> int                               # exit code
```

## D. Test cases (`test_package_arxiv.py`, pytest)
1. `test_complete_tree_is_ready`: synthetic src with main.tex (non-anon author), one non-empty
   `sections/x.tex`, a `.bbl`, no `\bibliography` mismatch → exit 0, ready=True, tar exists.
2. `test_empty_input_blocks`: referenced `\input{sections/empty}` is 0-byte → exit 1,
   EMPTY_INPUT issue, tar STILL written.
3. `test_missing_bbl_blocks`: `\bibliography{refs}` present, no `.bbl` → exit 1, NO_BBL.
4. `test_no_main_is_fatal`: src has no `\documentclass` file → exit 2, no tar.
5. `test_tarball_deterministic`: build twice → identical sha256.
6. `test_junk_excluded`: a `.aux`/`.log` in src is NOT in the tar member list.

## E. File formats
- Tarball: gzip tar, flat-ish (arcnames relative to src, preserving `sections/`).
- MANIFEST.txt: plain text, one file per line `path<TAB>bytes`, then a `READINESS:` block.
