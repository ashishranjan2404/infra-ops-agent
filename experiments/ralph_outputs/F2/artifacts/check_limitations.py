#!/usr/bin/env python3
"""Parse-check + citation-existence validator for F2 LIMITATIONS.md.

Stdlib only. Verifies (1) every repo file cited by LIMITATIONS.md exists,
(2) the generated-scenario glob has >= 30 specs, (3) LIMITATIONS.md contains the
expected section structure. Exit 0 on success, 1 listing failures otherwise.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Repo-relative paths cited by LIMITATIONS.md / evidence_index.md.
CITED_FILES = [
    "experiments/FINAL_SUMMARY.md",
    "experiments/CLAIMS_EVIDENCE.md",
    "experiments/build_incidents.py",
    "experiments/ralph_outputs/D13/SUMMARY.md",
    "experiments/tables/table3_harness_synthesis.md",
    "rex/scoring.py",
    "rex/runs/ablation.json",
]
GENERATED_GLOB = "scenarios/cidg/generated/*.yaml"
MIN_GENERATED = 30
REQUIRED_MARKERS = ["## Limitations", "### L1", "### L2", "### L3",
                    "### L4", "### L5", "### L6", "### Scope"]


def repo_root() -> Path:
    """Walk up from this script to the dir containing experiments/ and rex/."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "experiments").is_dir() and (parent / "rex").is_dir():
            return parent
    return Path("/Users/mei/rl")  # documented fallback


def check_cited_files(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in CITED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing cited file: {rel}")
    n = len(list(root.glob(GENERATED_GLOB)))
    if n < MIN_GENERATED:
        failures.append(f"generated scenarios = {n} (< {MIN_GENERATED})")
    else:
        print(f"  generated scenarios glob = {n} (>= {MIN_GENERATED}) OK")
    return failures


def check_section(limits_md: Path) -> list[str]:
    if not limits_md.exists():
        return [f"missing LIMITATIONS.md: {limits_md}"]
    text = limits_md.read_text(encoding="utf-8")
    return [f"LIMITATIONS.md missing marker: {m!r}"
            for m in REQUIRED_MARKERS if m not in text]


def main() -> int:
    root = repo_root()
    limits = Path(__file__).resolve().parent / "LIMITATIONS.md"
    print(f"repo_root = {root}")
    failures = check_cited_files(root) + check_section(limits)
    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nPASS: all cited files exist and LIMITATIONS.md is well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
