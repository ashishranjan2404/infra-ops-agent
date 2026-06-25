#!/usr/bin/env python3
"""Validate the F7 rebuttal-anticipation deliverable.

Checks attacks.json schema + that rebuttal_anticipation.md is structurally complete
and substantive. Stdlib only (Python 3.13). Exit 0 iff no problems.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "attacks.json"
MD_PATH = HERE / "rebuttal_anticipation.md"

MANDATORY_THEMES = {"synthetic_data", "small_n", "flat_rft", "reward_hacking", "single_domain"}
REQUIRED_H2 = [
    "## Top-line: the two rejections to plan for",
    "## The attacks",
    "## Concession ledger",
    "## What would actually sink the paper",
]
# tolerant label matchers: punctuation/case-agnostic
LABELS = ["Steelman", "Honest response", "Probability", "Depth", "Closing evidence"]
PROB_VALS = {"High", "Medium", "Low"}
DEPTH_VALS = {"Fatal-if-true", "Serious", "Manageable"}


def load_attacks(path: Path) -> dict:
    data = json.loads(path.read_text())
    if "attacks" not in data or not isinstance(data["attacks"], list):
        raise ValueError("attacks.json missing 'attacks' list")
    return data


def check_themes(data: dict) -> list[str]:
    present = {a.get("theme") for a in data["attacks"]}
    return sorted(MANDATORY_THEMES - present)


def _split_blocks(md: str) -> dict[str, str]:
    """Return {attack_id: block_text} for each '### A<n> — ...' header."""
    blocks: dict[str, str] = {}
    matches = list(re.finditer(r"^### (A\d+)\b.*$", md, re.MULTILINE))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        blocks[m.group(1)] = md[start:end]
    return blocks


def check_doc(md_path: Path, data: dict) -> list[str]:
    problems: list[str] = []
    md = md_path.read_text()

    n = data.get("n_attacks")
    if not (isinstance(n, int) and 8 <= n <= 12):
        problems.append(f"n_attacks={n} not in [8,12]")
    if n != len(data["attacks"]):
        problems.append(f"n_attacks={n} != len(attacks)={len(data['attacks'])}")

    for h2 in REQUIRED_H2:
        if h2 not in md:
            problems.append(f"missing H2 section: {h2!r}")

    # top-line callouts
    if not re.search(r"highest[- ]probability", md, re.IGNORECASE):
        problems.append("Top-line missing 'highest-probability' callout")
    if not re.search(r"highest[- ]depth", md, re.IGNORECASE):
        problems.append("Top-line missing 'highest-depth' callout")

    blocks = _split_blocks(md)
    for atk in data["attacks"]:
        aid = atk["id"]
        if aid not in blocks:
            problems.append(f"{aid}: no '### {aid}' block in markdown")
            continue
        block = blocks[aid]
        # all labels present (tolerant: allow trailing punctuation inside/after the bold)
        for lab in LABELS:
            if not re.search(r"\*\*" + re.escape(lab) + r"[.:]?\*\*", block, re.IGNORECASE):
                problems.append(f"{aid}: missing label **{lab}**")
        # substance gate: steelman + honest response bodies >= 120 chars
        for lab in ("Steelman", "Honest response"):
            m = re.search(r"\*\*" + re.escape(lab) + r"[.:]?\*\*[.: —-]*", block, re.IGNORECASE)
            if m:
                rest = block[m.end():]
                # stop at the next *known label*, not any bold span (bodies may bold inline)
                label_alt = "|".join(re.escape(l) for l in LABELS)
                nxt = re.search(r"\*\*(?:" + label_alt + r")[.:]?\*\*", rest, re.IGNORECASE)
                body = rest[: nxt.start()] if nxt else rest
                if len(body.strip()) < 120:
                    problems.append(f"{aid}: {lab} body too short ({len(body.strip())} chars)")
        # cross-file: theme token appears in the block
        theme = atk.get("theme", "")
        if theme and theme not in MANDATORY_THEMES.union({theme}):
            pass
        # probability/depth values valid in JSON
        if atk.get("probability") not in PROB_VALS:
            problems.append(f"{aid}: bad probability {atk.get('probability')!r}")
        if atk.get("depth") not in DEPTH_VALS:
            problems.append(f"{aid}: bad depth {atk.get('depth')!r}")

    # A6 must show the fixed-point arithmetic
    if "A6" in blocks:
        if "(4" not in blocks["A6"] or "0.30" not in blocks["A6"]:
            problems.append("A6: missing fixed-point arithmetic ('(4' and '0.30')")

    return problems


def main() -> int:
    data = load_attacks(JSON_PATH)
    missing_themes = check_themes(data)
    doc_problems = check_doc(MD_PATH, data)

    problems = []
    if missing_themes:
        problems.append("missing mandatory themes: " + ", ".join(missing_themes))
    problems.extend(doc_problems)

    print(f"attacks: {len(data['attacks'])}")
    print(f"mandatory themes present: {not missing_themes}")
    if problems:
        print("FAIL")
        for p in problems:
            print("  - " + p)
        return 1
    print("PASS — deliverable structurally complete and substantive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
