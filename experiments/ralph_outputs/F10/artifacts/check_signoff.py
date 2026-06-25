#!/usr/bin/env python3
"""Validate and tally the co-author sign-off sheet.

Parses the markdown tables in signoff_sheet.md, finds the three author columns
(Ashish, Wenji, Sylvie), and reports per-claim status:
  - cleared  : all three authors APPROVED
  - partial  : some APPROVED, none REJECTED, some PENDING
  - rejected : at least one REJECTED
  - pending  : all three PENDING

Also verifies that every in-repo evidence pointer referenced in the sheet exists
on disk (external/unpushed evidence is reported as a known blocker, not an error).

Usage:  python3 check_signoff.py [path/to/signoff_sheet.md]
Exit 0 always (this is a status report, not a gate) unless the file is unparseable.
Stdlib only; Python 3.8+.
"""
import os
import re
import sys

AUTHORS = ("Ashish", "Wenji", "Sylvie")
VALID = ("PENDING", "APPROVED", "REJECTED")
# evidence files that are known to live outside the repo today (documented blocker)
EXTERNAL_EVIDENCE = ("GRPO run",)


def split_row(line):
    """Split a markdown table row into trimmed cells (drop outer empties)."""
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    return parts


def cell_status(cell):
    """Classify a sign-off cell into one of VALID (prefix match, case-insensitive)."""
    up = cell.upper()
    for v in VALID:
        if up.startswith(v):
            return v
    return None


def parse_tables(text):
    """Yield (header_cells, [data_rows]) for every pipe table that has author cols."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]
        ):
            header = split_row(line)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            if any(a in header for a in AUTHORS):
                yield header, rows
            i = j
        else:
            i += 1


def claim_id(cells):
    """Best-effort claim id = first cell (e.g. C1/S1/N1)."""
    return cells[0] if cells else "?"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "signoff_sheet.md"
    )
    if not os.path.exists(path):
        print(f"ERROR: sheet not found: {path}")
        return 2
    text = open(path, encoding="utf-8").read()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(path), "..", "..", "..", ".."))

    tally = {"cleared": [], "partial": [], "rejected": [], "pending": [], "malformed": []}
    evidence_refs = set()

    for header, rows in parse_tables(text):
        idx = {a: header.index(a) for a in AUTHORS if a in header}
        if len(idx) != 3:
            continue  # not a full sign-off table
        for cells in rows:
            cid = claim_id(cells)
            # collect repo-path evidence pointers (anything that looks like a/path/file.ext)
            for cell in cells:
                for m in re.findall(r"`([^`]+)`", cell):
                    if "/" in m and "." in m.split("/")[-1]:
                        evidence_refs.add(m)
            statuses = []
            ok = True
            for a in AUTHORS:
                if idx[a] >= len(cells):
                    ok = False
                    break
                s = cell_status(cells[idx[a]])
                if s is None:
                    ok = False
                    break
                statuses.append(s)
            if not ok:
                tally["malformed"].append(cid)
                continue
            if "REJECTED" in statuses:
                tally["rejected"].append(cid)
            elif all(s == "APPROVED" for s in statuses):
                tally["cleared"].append(cid)
            elif all(s == "PENDING" for s in statuses):
                tally["pending"].append(cid)
            else:
                tally["partial"].append(cid)

    # evidence existence check
    missing, external, present = [], [], []
    for ref in sorted(evidence_refs):
        if any(tok in ref for tok in EXTERNAL_EVIDENCE):
            external.append(ref)
            continue
        if os.path.exists(os.path.join(repo_root, ref)):
            present.append(ref)
        else:
            missing.append(ref)

    print("=== Sign-off tally ===")
    for k in ("cleared", "partial", "rejected", "pending", "malformed"):
        items = tally[k]
        print(f"  {k:9}: {len(items)}  {items}")
    total = sum(len(v) for v in tally.values())
    print(f"  TOTAL claims: {total}")

    print("\n=== Evidence pointers ===")
    print(f"  present in repo : {len(present)}")
    for r in present:
        print(f"    OK   {r}")
    if external:
        print(f"  external (known blocker): {len(external)}")
        for r in external:
            print(f"    EXT  {r}  (not in repo yet — see BLOCKER.md)")
    if missing:
        print(f"  MISSING in repo : {len(missing)}")
        for r in missing:
            print(f"    MISS {r}")

    blocked = len(tally["pending"]) + len(tally["partial"]) + len(tally["rejected"])
    print(f"\nSUMMARY: {len(tally['cleared'])} cleared, {blocked} not-yet-cleared, "
          f"{len(tally['malformed'])} malformed.")
    if tally["malformed"]:
        print("Sheet has malformed rows.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
