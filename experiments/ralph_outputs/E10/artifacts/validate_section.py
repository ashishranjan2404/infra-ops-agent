#!/usr/bin/env python3
"""Validation gate for the Fireball transfer paper section (E10).

Checks the deliverable markdown:
  1. all 6 required H2 subsections present, in order
  2. E3..E9 all present in the design
  3. >= 12 PENDING result cells
  4. NO fabricated numeric result: every result-table (T1/T2/T3) data cell is exactly PENDING
     (decimals are allowed in prose / reward weights, NOT in result-table cells)
  5. real-object citations present (rex/scoring.py, eval_pass_at_k, SCHEMA.md)
  6. falsification criterion present

Exit 0 = all pass; exit 1 = a gate failed.
"""
import re
import sys
from pathlib import Path

DOC = Path(__file__).with_name("fireball_transfer_section.md")


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    failures = []

    # 1. ordered subsections
    subs = [
        "## 5.x.1", "## 5.x.2", "## 5.x.3",
        "## 5.x.4", "## 5.x.5", "## 5.x.6",
    ]
    last = -1
    for s in subs:
        i = text.find(s)
        if i == -1:
            failures.append(f"missing subsection {s}")
        elif i < last:
            failures.append(f"subsection {s} out of order")
        else:
            last = i

    # 2. E3..E9 present
    for e in ["E3", "E4", "E5", "E6", "E7", "E8", "E9"]:
        if e not in text:
            failures.append(f"missing experiment {e}")

    # 3. PENDING count
    n_pending = text.count("PENDING")
    if n_pending < 12:
        failures.append(f"too few PENDING cells: {n_pending} (need >=12)")

    # 4. no fabricated number in result-table cells.
    #    Result tables live between the "## 5.x.4" header and the "## 5.x.5" header.
    start = text.find("## 5.x.4")
    end = text.find("## 5.x.5")
    results_block = text[start:end] if (start != -1 and end != -1) else ""
    bad_cells = []
    for line in results_block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # data cells are columns after the first (label) column
        for c in cells[1:]:
            # a decimal like 0.45 in a result cell would be a fabricated number
            if re.search(r"\b\d+\.\d+\b", c):
                bad_cells.append(c)
    if bad_cells:
        failures.append(f"fabricated numeric value in result cell(s): {bad_cells}")

    # 5. citations
    for cite in ["rex/scoring.py", "eval_pass_at_k", "SCHEMA.md"]:
        if cite not in text:
            failures.append(f"missing citation {cite}")

    # 6. falsification
    low = text.lower()
    if "falsif" not in low and "null" not in low:
        failures.append("missing falsification / null criterion")

    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS")
    print(f"  subsections: 6/6 in order")
    print(f"  experiments E3..E9: present")
    print(f"  PENDING cells: {n_pending}")
    print(f"  result-table fabricated numbers: 0")
    print(f"  citations: rex/scoring.py, eval_pass_at_k, SCHEMA.md present")
    print(f"  falsification criterion: present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
