#!/usr/bin/env python3
"""Validator for the Related Work deliverable (Task F1).

Guarantees COVERAGE + STRUCTURE, not citation-metric correctness (a script cannot
verify a real DOI offline; accuracy is guaranteed by mechanism-based descriptions in
the prose — see 09_critique.md). stdlib only.

    python3 check_related_work.py [path/to/related_work.md]
"""
from __future__ import annotations

import os
import re
import sys

REQUIRED = [
    "SREGym", "AIOpsLab", "ITBench",
    "Code World Models", "CWM", "Code as Policies",
    "AutoHarness",
    "REx", "Thompson", "Reflexion", "Self-Refine",
    "FIREBALL",
    "GRPO", "RLVR", "Constitutional AI", "LLM-as-a-Judge",
    "pass@k", "Wilson", "McNemar",
]


def check(path: str) -> tuple[bool, dict]:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    low = text.lower()

    missing = [tok for tok in REQUIRED if tok.lower() not in low]

    has_heading = bool(re.search(r"^##\s*2\.?\s*Related Work", text, re.M | re.I))
    subsections = re.findall(r"^###\s*2\.\d", text, re.M)
    # a markdown table = a header row of pipes followed by a |---| separator row
    has_table = bool(re.search(r"^\|.*\|\s*\n\|[\s:|-]+\|\s*$", text, re.M))

    # soft check: bracket balance (warning only)
    bracket_balanced = text.count("[") == text.count("]")

    ok = (not missing) and has_heading and has_table and len(subsections) >= 6

    report = {
        "path": path,
        "ok": ok,
        "required_total": len(REQUIRED),
        "required_present": len(REQUIRED) - len(missing),
        "missing": missing,
        "has_heading_2_related_work": has_heading,
        "subsection_count": len(subsections),
        "has_markdown_table": has_table,
        "warn_bracket_balanced": bracket_balanced,
        "word_count": len(text.split()),
    }
    return ok, report


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "related_work.md")
    ok, report = check(path)
    for k, v in report.items():
        print(f"{k}: {v}")
    if not report["warn_bracket_balanced"]:
        print("WARN: unbalanced [ ] brackets (soft check, not a failure)")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
