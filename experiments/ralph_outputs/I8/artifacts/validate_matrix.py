#!/usr/bin/env python3
"""Validate axes_matrix.json: shape, non-empty cells, resolvable repo citations.

Also runs NEGATIVE self-tests (a blanked cell and a bad path must be rejected) so a
green run proves the validator actually catches violations, not just that the file is well-formed.

Usage:  python3 validate_matrix.py   ->  exit 0 + "OK: ..."  |  exit 1 + first failure reason
"""
from __future__ import annotations

import copy
import json
import os
import sys

EXPECTED_PARADIGMS = {"code_as_policy", "rlhf", "constitutional_ai"}
EXPECTED_AXES = {
    "knowledge_location", "verifiability", "sample_efficiency",
    "safety_guarantees", "interpretability",
}
# At least these code-as-policy files must be cited (spec T5).
REQUIRED_CITATIONS = {"rex/scoring.py", "rex/tree.py", "agent/llm.py"}

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(HERE, "axes_matrix.json")


def find_repo_root(start: str) -> str:
    d = start
    while True:
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("repo root (.git) not found above " + start)
        d = parent


class ValidationError(Exception):
    pass


def validate(matrix: dict, repo_root: str) -> None:
    """Raise ValidationError on the first violation; return None if valid."""
    # T2: paradigms / axes sets
    if set(matrix.get("paradigms", [])) != EXPECTED_PARADIGMS:
        raise ValidationError(f"paradigms != {sorted(EXPECTED_PARADIGMS)}")
    if set(matrix.get("axes", [])) != EXPECTED_AXES:
        raise ValidationError(f"axes != {sorted(EXPECTED_AXES)}")

    cells = matrix.get("cells", {})
    if set(cells) != EXPECTED_PARADIGMS:
        raise ValidationError("cells keys must equal the paradigm set")

    # T3: every (paradigm, axis) present and non-empty
    for p in EXPECTED_PARADIGMS:
        row = cells.get(p, {})
        if set(row) != EXPECTED_AXES:
            raise ValidationError(f"cells[{p}] axes != expected axis set")
        for a in EXPECTED_AXES:
            v = row.get(a, "")
            if not isinstance(v, str) or len(v.strip()) == 0:
                raise ValidationError(f"empty cell: cells[{p}][{a}]")

    # T4: citations resolve
    cites = matrix.get("repo_citations", [])
    if not cites:
        raise ValidationError("repo_citations is empty")
    for rel in cites:
        if not os.path.exists(os.path.join(repo_root, rel)):
            raise ValidationError(f"citation does not resolve: {rel}")

    # T5: required core files cited
    missing = REQUIRED_CITATIONS - set(cites)
    if missing:
        raise ValidationError(f"missing required citations: {sorted(missing)}")


def _negative_self_tests(matrix: dict, repo_root: str) -> None:
    """The validator must REJECT a blanked cell and a bad citation path."""
    # blanked cell
    bad = copy.deepcopy(matrix)
    bad["cells"]["rlhf"]["verifiability"] = "   "
    try:
        validate(bad, repo_root)
    except ValidationError:
        pass
    else:
        raise AssertionError("negative self-test failed: blank cell was accepted")

    # bad citation path
    bad2 = copy.deepcopy(matrix)
    bad2["repo_citations"] = list(bad2["repo_citations"]) + ["does/not/exist_xyz.py"]
    try:
        validate(bad2, repo_root)
    except ValidationError:
        pass
    else:
        raise AssertionError("negative self-test failed: bad path was accepted")


def main() -> int:
    try:
        with open(MATRIX_PATH) as f:
            matrix = json.load(f)  # T1
    except (OSError, ValueError) as e:
        print(f"FAIL: cannot load JSON: {e}")
        return 1

    repo_root = find_repo_root(HERE)

    try:
        validate(matrix, repo_root)
        _negative_self_tests(matrix, repo_root)
    except (ValidationError, AssertionError) as e:
        print(f"FAIL: {e}")
        return 1

    n_cells = len(EXPECTED_PARADIGMS) * len(EXPECTED_AXES)
    print(f"OK: {len(EXPECTED_PARADIGMS)} paradigms x {len(EXPECTED_AXES)} axes "
          f"= {n_cells} non-empty cells; {len(matrix['repo_citations'])} citations resolve; "
          f"negative self-tests rejected as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
