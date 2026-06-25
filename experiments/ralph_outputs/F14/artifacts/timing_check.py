#!/usr/bin/env python3
"""F14 timing validator for talk_outline_15min.md.

Parses '### Slide N — Title (M:SS)' content-slide headings and validates the talk's
timing budget: contiguous numbering, no over-long slide, and total == target.

Stdlib only (Python 3.13). Run with no args to validate the sibling outline file.
Exit 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import os
import re
import sys

# Title separator may be em-dash, en-dash, or hyphen (ouroboros Engineer A fix).
_SEP = r"[—–-]"
# Content slides only: '### Slide <int> <sep> <title> (M:SS)'. Backup '### B1 ...' ignored.
_SLIDE_RE = re.compile(
    rf"^###\s+Slide\s+(\d+)\s+{_SEP}\s+(.*?)\s+\((\d+):(\d{{2}})\)\s*$"
)


def parse_slide_timings(markdown: str) -> list[tuple[int, str, int]]:
    """Return [(slide_number, title, seconds), ...] for content slides.

    Raises ValueError on a malformed timestamp (SS >= 60)."""
    out: list[tuple[int, str, int]] = []
    for line in markdown.splitlines():
        m = _SLIDE_RE.match(line.strip())
        if not m:
            continue
        n = int(m.group(1))
        title = m.group(2).strip()
        minutes = int(m.group(3))
        seconds = int(m.group(4))
        if seconds >= 60:
            raise ValueError(f"Slide {n}: malformed timestamp {minutes}:{seconds:02d} (SS>=60)")
        out.append((n, title, minutes * 60 + seconds))
    return out


def validate(
    timings: list[tuple[int, str, int]],
    target_seconds: int = 900,
    max_slide_seconds: int = 75,
) -> dict:
    numbers = [n for n, _, _ in timings]
    total = sum(s for _, _, s in timings)
    contiguous = numbers == list(range(1, len(numbers) + 1))
    over_long = [(n, t, s) for n, t, s in timings if s > max_slide_seconds]
    total_matches = total == target_seconds
    ok = bool(timings) and contiguous and not over_long and total_matches
    return {
        "ok": ok,
        "total_seconds": total,
        "target_seconds": target_seconds,
        "n_slides": len(timings),
        "contiguous": contiguous,
        "over_long": over_long,
        "total_matches_target": total_matches,
        "no_slack_advisory": total == target_seconds,  # advisory only (Engineer C)
    }


def _fmt(sec: int) -> str:
    return f"{sec // 60}:{sec % 60:02d}"


def main(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    try:
        timings = parse_slide_timings(text)
    except ValueError as e:
        print(f"FAIL — {e}")
        return 1
    r = validate(timings)
    for n, title, sec in timings:
        print(f"  Slide {n:>2} ({_fmt(sec)})  {title}")
    print("-" * 60)
    print(f"  slides={r['n_slides']}  total={_fmt(r['total_seconds'])}  "
          f"target={_fmt(r['target_seconds'])}  contiguous={r['contiguous']}")
    if r["over_long"]:
        for n, t, s in r["over_long"]:
            print(f"  OVER-LONG: Slide {n} ({_fmt(s)}) {t}")
    if r["no_slack_advisory"] and r["ok"]:
        print("  ADVISORY: total exactly equals target — zero buffer (informational).")
    print("PASS" if r["ok"] else "FAIL")
    return 0 if r["ok"] else 1


def _selftest() -> None:
    assert parse_slide_timings("### Slide 1 — X (1:30)\n") == [(1, "X", 90)]
    assert validate([(1, "A", 60), (2, "B", 60)], target_seconds=120)["ok"] is True
    assert validate([(1, "A", 90)], max_slide_seconds=75)["ok"] is False  # over-long
    assert validate([(1, "A", 450), (3, "B", 450)])["contiguous"] is False
    # backup '### B1' lines ignored
    assert parse_slide_timings("### B1 — backup (2:00)\n") == []
    # empty doc
    e = validate(parse_slide_timings("no slides here"))
    assert e["n_slides"] == 0 and e["ok"] is False
    # en-dash and hyphen separators tolerated
    assert parse_slide_timings("### Slide 1 – Y (0:30)\n") == [(1, "Y", 30)]
    assert parse_slide_timings("### Slide 1 - Z (0:30)\n") == [(1, "Z", 30)]
    # malformed SS>=60 rejected
    try:
        parse_slide_timings("### Slide 1 — W (0:90)\n")
        raise AssertionError("expected ValueError on 0:90")
    except ValueError:
        pass
    print("[selftest] all assertions passed")


if __name__ == "__main__":
    _selftest()
    here = os.path.dirname(os.path.abspath(__file__))
    outline = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "talk_outline_15min.md")
    sys.exit(main(outline))
