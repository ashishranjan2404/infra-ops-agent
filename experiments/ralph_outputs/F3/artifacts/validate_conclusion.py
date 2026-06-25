#!/usr/bin/env python3
"""Validate F3 CONCLUSION.md: structure, content contract, and provenance.

This is a DRIFT/CONSISTENCY checker, not a semantic linker: the provenance pass
confirms each cited value string still appears in its source file (so the Conclusion
cannot silently drift from the canonical docs). It does not prove the value sits on
the semantically-correct line. Stdlib only; Python 3.13.
"""
from __future__ import annotations
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent          # .../F3/artifacts
MD_PATH = HERE / "CONCLUSION.md"
TSV_PATH = HERE / "claims_provenance.tsv"


def repo_root() -> pathlib.Path:
    # .../experiments/ralph_outputs/F3/artifacts -> up 4 = repo root
    return HERE.parents[3]


# Disjoint, ordered structure regexes (see 05_ouroboros.md).
STRUCTURE = [
    (r"^#\s+Conclusion", "H1 'Conclusion'"),
    (r"^##\s+.*[Gg]raduation", "stance subsection naming graduation"),
    (r"^##\s+What .*graduation .*real", "mechanisms subsection ('What makes graduation real')"),
    (r"^##\s+.*[Ee]vidence", "evidence subsection"),
    (r"^##\s+What .*certif", "certifies subsection ('What this degree certifies')"),
    (r"^##\s+.*([Cc]ohort|[Ff]uture)", "future-cohorts subsection"),
]


def check_structure(md: str) -> list[str]:
    fails: list[str] = []
    pos = 0
    for pat, desc in STRUCTURE:
        m = re.compile(pat, re.MULTILINE).search(md, pos)
        if not m:
            fails.append(f"structure: missing/out-of-order heading: {desc}")
            # do not advance pos; keep scanning from same point
            continue
        pos = m.end()
    return fails


def check_content(md: str) -> list[str]:
    fails: list[str] = []
    words = len(md.split())
    if words < 700:
        fails.append(f"content: only {words} words (need >= 700)")

    if not re.search(r"graduation,?\s+not\s+deployment", md):
        fails.append("content: missing phrase 'graduation not deployment'")

    artifacts = ["tools_registry.json", "rex/scoring.py", "rex/curriculum.py",
                 "ARCHITECTURE.md", "autonomous", "approval", "blocked",
                 "safety gate", "singleton_node_notready"]
    named = sum(1 for a in artifacts if a in md)
    if named < 4:
        fails.append(f"content: only {named} concrete repo artifacts named (need >= 4)")

    for tok in ["0.30", "0.25", "0.45", "0.60"]:
        if tok not in md:
            fails.append(f"content: reward coefficient {tok} missing")

    for tok in ["0.86", "(4", "0.30)/5"]:
        if tok not in md:
            fails.append(f"content: ceiling-identity token {tok!r} missing")

    if "not automated" not in md and "not yet automated" not in md:
        fails.append("content: missing revocation-honesty clause ('not (yet) automated')")

    for ph in ["TODO", "TBD", "FIXME", "lorem", "<...>", "<TODO>"]:
        if ph in md:
            fails.append(f"content: placeholder token present: {ph}")
    return fails


def check_provenance(root: pathlib.Path, tsv: str) -> list[str]:
    fails: list[str] = []
    lines = [ln for ln in tsv.splitlines() if ln.strip()]
    if not lines:
        return ["provenance: empty tsv"]
    header = lines[0].split("\t")
    if header[:3] != ["claim", "value", "source"]:
        fails.append(f"provenance: bad header {header!r}")
    rows = lines[1:]
    if len(rows) < 5:
        fails.append(f"provenance: only {len(rows)} rows (need >= 5)")
    for i, row in enumerate(rows, start=2):
        parts = row.split("\t")
        if len(parts) != 3:
            fails.append(f"provenance row {i}: expected 3 cols, got {len(parts)}")
            continue
        _claim, value, source = parts
        fpath, _, line = source.partition(":")
        sp = root / fpath
        if not sp.exists():
            fails.append(f"provenance row {i}: source file missing: {fpath}")
            continue
        text = sp.read_text(encoding="utf-8", errors="replace")
        if line:
            src_lines = text.splitlines()
            ln = int(line)
            hay = src_lines[ln - 1] if 1 <= ln <= len(src_lines) else ""
            if value not in hay:
                # tolerate off-by-a-bit: fall back to whole-file presence
                if value in text:
                    fails.append(f"provenance row {i}: value not on line {ln} "
                                 f"but found elsewhere in {fpath} (drift?)")
                else:
                    fails.append(f"provenance row {i}: value {value!r} not in {fpath}")
        else:
            if value not in text:
                fails.append(f"provenance row {i}: value {value!r} not in {fpath}")
    return fails


def main() -> int:
    fails: list[str] = []
    if not MD_PATH.exists():
        print("FAIL: CONCLUSION.md missing")
        return 1
    md = MD_PATH.read_text(encoding="utf-8")
    fails += check_structure(md)
    fails += check_content(md)
    if not TSV_PATH.exists():
        fails.append("provenance: claims_provenance.tsv missing")
    else:
        fails += check_provenance(repo_root(), TSV_PATH.read_text(encoding="utf-8"))

    if fails:
        print(f"FAILED ({len(fails)} issue(s)):")
        for f in fails:
            print("  -", f)
        return 1
    n = len(STRUCTURE) + 1
    print(f"ALL CHECKS PASSED ({n} check groups; {len(md.split())} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
