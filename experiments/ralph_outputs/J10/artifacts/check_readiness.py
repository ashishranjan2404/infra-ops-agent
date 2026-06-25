#!/usr/bin/env python3
"""J10 — validator/renderer for the deployment-readiness gap registry.

Verifies the honesty invariants of readiness_gaps.json against the real repo:
  * exactly the three required gaps (distribution shift / shadow / MTTR),
  * every grounding path resolves to a real, NON-EMPTY file under the repo root,
  * every lesson and gap has >= 1 grounding path,
  * every acceptance gate is labeled "TARGET — NOT YET MEASURED:",
  * neither the JSON statements nor (optionally) the markdown contain fabricated
    production phrasing.

Usage:
    python3 check_readiness.py [readiness_gaps.json] [--md lessons_from_production.md]
Exit 0 if no problems, else 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/mei/rl")
GATE_PREFIX = "TARGET — NOT YET MEASURED:"
REQUIRED_GAPS = {
    "G1": "distribution shift",
    "G2": "shadow",
    "G3": "mttr",
}

# Literal banned substrings (case-insensitive) + regex patterns for sneaky MTTR claims.
BANNED_LITERAL = [
    "in production we",
    "we deployed to prod",
    "deployed to production",
    "mttr reduction of",
    "reduced mttr by",
    "on call for",
    "% mttr",
    "in prod we observed",
]
BANNED_REGEX = [
    re.compile(r"\bmttr\b[^.]{0,25}\b\d{1,3}\s*%", re.I),   # "MTTR ... 40%"
    re.compile(r"\b\d{1,3}\s*%[^.]{0,20}\bmttr\b", re.I),   # "40% ... MTTR"
    re.compile(r"\bmttr\b[^.]{0,20}\b(dropped|fell|cut)\b", re.I),
]


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def _scan_banned(text: str) -> list[str]:
    low = text.lower()
    hits = [p for p in BANNED_LITERAL if p in low]
    hits += [r.pattern for r in BANNED_REGEX if r.search(text)]
    return hits


def verify(data: dict, repo_root: Path = REPO_ROOT) -> list[str]:
    problems: list[str] = []

    for key in ("task_id", "claim", "lessons", "gaps", "readiness_checklist"):
        if key not in data:
            problems.append(f"missing top-level key: {key}")
    if problems:
        return problems

    # gaps: exactly the three required ids, names contain the required tokens.
    gap_ids = {g["id"] for g in data["gaps"]}
    if gap_ids != set(REQUIRED_GAPS):
        problems.append(f"gap ids {sorted(gap_ids)} != required {sorted(REQUIRED_GAPS)}")
    for g in data["gaps"]:
        token = REQUIRED_GAPS.get(g["id"])
        if token and token not in g.get("name", "").lower():
            problems.append(f"gap {g['id']} name lacks required token '{token}'")
        gate = g.get("acceptance_gate", "")
        if not gate.startswith(GATE_PREFIX):
            problems.append(f"gap {g['id']} acceptance_gate not labeled with '{GATE_PREFIX}'")

    # grounding: >=1 per lesson/gap, each path real and non-empty.
    for kind in ("lessons", "gaps"):
        for item in data[kind]:
            grounding = item.get("grounding", [])
            if not grounding:
                problems.append(f"{kind} {item['id']} has no grounding path")
            for rel in grounding:
                p = repo_root / rel
                if not p.exists():
                    problems.append(f"{kind} {item['id']} grounding missing: {rel}")
                elif p.is_file() and p.stat().st_size == 0:
                    problems.append(f"{kind} {item['id']} grounding is empty: {rel}")

    # fabricated-prod phrasing in JSON statements.
    blob = " ".join(
        [data["claim"]]
        + [l.get("statement", "") for l in data["lessons"]]
        + [g.get("why_open", "") + " " + g.get("validation_protocol", "") for g in data["gaps"]]
    )
    for hit in _scan_banned(blob):
        problems.append(f"fabricated-prod phrasing in JSON: '{hit}'")

    return problems


def verify_md(md_path: Path, gap_ids: set[str]) -> list[str]:
    text = Path(md_path).read_text()
    problems = [f"fabricated-prod phrasing in md: '{h}'" for h in _scan_banned(text)]
    # cross-check: each gap id appears as a heading anchor in the md.
    for gid in gap_ids:
        if not re.search(rf"###\s*{gid}\b", text):
            problems.append(f"md missing gap heading for {gid}")
    for lid in ("L1", "L2", "L3", "L4"):
        if not re.search(rf"###\s*{lid}\b", text):
            problems.append(f"md missing lesson heading for {lid}")
    return problems


def render(data: dict) -> str:
    lines = [f"J10 readiness — {data['claim']}", "", "Lessons:"]
    for l in data["lessons"]:
        lines.append(f"  [{l['id']}] {l['statement']}")
    lines.append("Gaps (all targets NOT YET MEASURED):")
    for g in data["gaps"]:
        lines.append(f"  [{g['id']}] {g['name']}")
    done = sum(1 for c in data["readiness_checklist"] if c["status"] == "done")
    lines.append(f"Checklist: {done}/{len(data['readiness_checklist'])} done")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    json_path = Path(args[0]) if args else Path(__file__).with_name("readiness_gaps.json")
    md_path = None
    if "--md" in argv:
        md_path = Path(argv[argv.index("--md") + 1])

    data = load(json_path)
    problems = verify(data)
    if md_path:
        problems += verify_md(md_path, {g["id"] for g in data["gaps"]})

    print(render(data))
    print()
    if problems:
        print(f"FAIL — {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK — all readiness invariants hold; no fabricated production claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
