#!/usr/bin/env python3
"""package_arxiv.py — bundle LaTeX source into an arXiv-ready tarball.

F15 deliverable. Stdlib-only (Python 3.13), deterministic, idempotent.

It does NOT submit. It packages the source (default: the F6 paper tree), runs
packaging-correctness + readiness checks, writes a reproducible gzip tarball and
a MANIFEST, and returns an exit code:

    0 = ready to submit
    1 = packaged but NOT ready (advisory; read MANIFEST READINESS block)
    2 = fatal (no main .tex with \\documentclass)  -> no tarball written

Design notes (from F15 grill + ouroboros):
  * Separation of concerns: we ALWAYS write the tar of whatever exists (unless
    fatal); completeness is REPORTED via the readiness verdict + advisory exit,
    not enforced by refusing to package.
  * Whitelist included extensions; exclude LaTeX aux junk.
  * arXiv runs AutoTeX (no BibTeX): if \\bibliography is present, a .bbl must exist.
  * Deterministic gzip: in-memory tar -> gzip with mtime=0; TarInfo mtime/uid/gid=0.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import re
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path

WHITELIST_EXT = {".tex", ".bbl", ".cls", ".sty", ".bib", ".bst",
                 ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps"}
JUNK_EXT = {".aux", ".log", ".out", ".toc", ".blg", ".fls",
            ".fdb_latexmk", ".synctex.gz", ".nav", ".snm", ".vrb"}

INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\{([^}]+)\}")


@dataclass
class Issue:
    level: str  # "fatal" | "block" | "warn"
    code: str
    msg: str


@dataclass
class Readiness:
    ready: bool
    issues: list[Issue] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    tar_sha256: str = ""


def _strip_comments(text: str) -> str:
    """Remove LaTeX %-comments (respecting escaped \\%)."""
    out = []
    for line in text.splitlines():
        res, i = [], 0
        while i < len(line):
            c = line[i]
            if c == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            res.append(c)
            i += 1
        out.append("".join(res))
    return "\n".join(out)


def find_main(src: Path, hint: str | None) -> Path | None:
    if hint:
        cand = src / hint
        if cand.is_file():
            return cand
    candidates = []
    for tex in sorted(src.rglob("*.tex")):
        try:
            txt = _strip_comments(tex.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if "\\documentclass" in txt:
            candidates.append(tex)
    if not candidates:
        return None
    # Prefer a top-level main.tex if present.
    for c in candidates:
        if c.name == "main.tex":
            return c
    return candidates[0]


def _resolve_input(target: str, src: Path) -> Path | None:
    p = src / target
    if p.is_file():
        return p
    pt = src / (target + ".tex")
    if pt.is_file():
        return pt
    return None


def collect_inputs(main: Path, src: Path) -> tuple[list[Path], list[Issue]]:
    """BFS over \\input/\\include starting at main."""
    issues: list[Issue] = []
    seen: set[Path] = set()
    order: list[Path] = []
    queue = [main]
    while queue:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        order.append(cur)
        try:
            txt = _strip_comments(cur.read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            issues.append(Issue("block", "READ_ERROR", f"cannot read {cur}: {e}"))
            continue
        for m in INPUT_RE.finditer(txt):
            target = m.group(1).strip()
            resolved = _resolve_input(target, src)
            if resolved is None:
                issues.append(Issue("block", "MISSING_INPUT",
                                    f"\\input/\\include target not found: {target}"))
            elif resolved.stat().st_size == 0:
                issues.append(Issue("block", "EMPTY_INPUT",
                                    f"referenced source is empty: "
                                    f"{resolved.relative_to(src)}"))
                if resolved not in seen:
                    seen.add(resolved)
                    order.append(resolved)
            else:
                queue.append(resolved)
    return order, issues


def collect_assets(src: Path) -> list[Path]:
    files: list[Path] = []
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        suf = "".join(p.suffixes[-1:]).lower()
        # handle multi-dot junk like .synctex.gz / .fdb_latexmk
        name_low = p.name.lower()
        if any(name_low.endswith(j) for j in JUNK_EXT):
            continue
        if p.suffix.lower() in WHITELIST_EXT:
            files.append(p)
    return files


def check_readiness(src: Path, main: Path, files: list[Path],
                    issues: list[Issue]) -> list[Issue]:
    out = list(issues)
    # arXiv runs AutoTeX, not BibTeX: \bibliography needs a sibling .bbl.
    has_bib_cmd = False
    for f in files:
        if f.suffix.lower() == ".tex":
            try:
                txt = _strip_comments(f.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if BIB_RE.search(txt):
                has_bib_cmd = True
                break
    has_bbl = any(f.suffix.lower() == ".bbl" for f in files)
    if has_bib_cmd and not has_bbl:
        out.append(Issue("block", "NO_BBL",
                         "\\bibliography{} present but no .bbl shipped "
                         "(arXiv will not run BibTeX)"))
    # Anonymity warning for the (non-anon) arXiv copy.
    try:
        mtxt = main.read_text(encoding="utf-8", errors="replace")
        if "Anonymous" in mtxt:
            out.append(Issue("warn", "ANON_AUTHOR",
                             "main still says 'Anonymous' — de-anonymize the arXiv copy"))
    except OSError:
        pass
    return out


def build_tarball(src: Path, files: list[Path], out_tar: Path) -> str:
    """Write a deterministic gzip tarball; return sha256 of the gz file."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:  # uncompressed into memory
        for f in sorted(files, key=lambda p: str(p.relative_to(src))):
            arcname = str(f.relative_to(src))
            ti = tf.gettarinfo(str(f), arcname=arcname)
            ti.mtime = 0
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            ti.mode = 0o644
            with open(f, "rb") as fh:
                tf.addfile(ti, fh)
    raw = buf.getvalue()
    out_tar.parent.mkdir(parents=True, exist_ok=True)
    with open(out_tar, "wb") as gz_out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=gz_out, mtime=0) as gz:
            gz.write(raw)
    return hashlib.sha256(out_tar.read_bytes()).hexdigest()


def write_manifest(out_manifest: Path, src: Path, files: list[Path],
                   readiness: Readiness) -> None:
    lines = []
    lines.append("READINESS: " + ("READY" if readiness.ready else "NOT-READY"))
    if readiness.issues:
        for iss in readiness.issues:
            lines.append(f"  [{iss.level.upper():5}] {iss.code}: {iss.msg}")
    else:
        lines.append("  (no issues)")
    lines.append(f"TAR_SHA256: {readiness.tar_sha256}")
    lines.append("")
    lines.append("FILES:")
    for f in sorted(files, key=lambda p: str(p.relative_to(src))):
        rel = f.relative_to(src)
        lines.append(f"  {rel}\t{f.stat().st_size}")
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bundle LaTeX source into an arXiv-ready tarball.")
    here = Path(__file__).resolve().parent
    default_src = (here / ".." / ".." / "F6" / "artifacts" / "aaai-paper").resolve()
    ap.add_argument("--src", default=str(default_src),
                    help="LaTeX source dir (default: F6 paper tree)")
    ap.add_argument("--out", default=str(here / "dist"),
                    help="output dir for tarball + manifest")
    ap.add_argument("--main", default=None, help="main .tex filename hint")
    ap.add_argument("--name", default="arxiv_submission", help="tarball base name")
    args = ap.parse_args(argv)

    src = Path(args.src).resolve()
    out = Path(args.out).resolve()
    if not src.is_dir():
        print(f"FATAL: src not a directory: {src}", file=sys.stderr)
        return 2

    main_tex = find_main(src, args.main)
    if main_tex is None:
        print(f"FATAL: no .tex with \\documentclass under {src}", file=sys.stderr)
        return 2

    inputs, in_issues = collect_inputs(main_tex, src)
    assets = collect_assets(src)
    # union of referenced inputs + whitelisted assets (assets already include .tex)
    files = sorted(set(assets) | set(inputs), key=lambda p: str(p))

    issues = check_readiness(src, main_tex, files, in_issues)
    blocking = [i for i in issues if i.level in ("fatal", "block")]
    ready = len(blocking) == 0

    out_tar = out / f"{args.name}.tar.gz"
    sha = build_tarball(src, files, out_tar)

    readiness = Readiness(ready=ready, issues=issues,
                          files=[str(f.relative_to(src)) for f in files],
                          tar_sha256=sha)
    write_manifest(out / "MANIFEST.txt", src, files, readiness)

    print(f"main: {main_tex.relative_to(src)}")
    print(f"files packaged: {len(files)}")
    print(f"tarball: {out_tar}  sha256={sha[:16]}...")
    print("READINESS: " + ("READY" if ready else "NOT-READY"))
    for iss in issues:
        print(f"  [{iss.level.upper()}] {iss.code}: {iss.msg}")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
