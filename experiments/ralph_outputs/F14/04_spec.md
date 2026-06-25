# F14 — 04 Spec

## Deliverable 1: `talk_outline_15min.md`
A slide-by-slide outline. Each slide is a level-3 heading of the exact form:

```
### Slide <N> — <Title> (<M:SS>)
**Key point:** <1–3 sentences> [SOURCE]
> Note: <speaker note paragraph>
```

### Contract / invariants
- `N` is a contiguous integer 1..17.
- `<M:SS>` is the slide's spoken budget; valid range 0:00–9:59.
- Every quantitative claim carries a source tag `[ARCH]` or `[HEAD]`.
- Sum of all `(M:SS)` == target 15:00 (±0).
- No single slide > 75s (1:15).
- A "## Timing summary" line restates the arithmetic.
- A "## Backup slides" section lists Q&A-only material (B1..B5), excluded from the 15:00.

### Numbers that MUST appear and their source (ground truth):
| Claim | Value | Source |
|---|---|---|
| Reward function | 0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap | ARCH |
| "resolved" alone weight | 45% | ARCH |
| Env reward band (one-shot) | 20–50% with variance | HEAD |
| Weak vs strong separation | haiku 0.27 vs opus 0.50 | HEAD |
| Searched verifier held-out | 0.90 vs 0.95 hand-written | HEAD |
| Rule compression | 14 → 3 | HEAD |
| Verifier train/held-out split | 7 / 3 incidents | HEAD |
| Ablation (hint stripped) | REx 0.25 ≈ zero-shot 0.24 | HEAD |
| best-of-N / retry | 0.24 / 0.23 | HEAD |
| Curriculum hard-tier floor | ~0.19–0.42 zero-shot | ARCH |
| Open-model training | Qwen3-8B/30B, easy ~0.5, hard headroom ~0.35 | HEAD |

## Deliverable 2: `timing_check.py`
A stdlib-only (Python 3.13) validator.

### Function signatures
```python
def parse_slide_timings(markdown: str) -> list[tuple[int, str, int]]:
    """Return [(slide_number, title, seconds), ...] parsed from '### Slide N — T (M:SS)'.
       Only matches content slides (### Slide ...), not backup (### B...)."""

def validate(timings: list[tuple[int, str, int]],
             target_seconds: int = 900,
             max_slide_seconds: int = 75) -> dict:
    """Return {ok, total_seconds, target_seconds, n_slides, contiguous,
              over_long: [(n,title,sec)], total_matches_target: bool}."""

def main(path: str) -> int:
    """Parse the outline file, validate, print a report, return exit code 0/1."""
```

### Test cases (asserted inside the script's __main__ self-test before reading the file)
1. `parse_slide_timings("### Slide 1 — X (1:30)\n")` → `[(1, "X", 90)]`.
2. A 2-slide doc summing to 900s with target 900 → `ok True`.
3. A slide of 1:30 (90s) with max 75 → flagged in `over_long`, `ok False`.
4. Non-contiguous numbering (1,3) → `contiguous False`, `ok False`.
5. Backup `### B1 — ...` lines are ignored by the parser.

### Output format
Human-readable report: per-slide line `Slide N (M:SS) Title`, then totals, then PASS/FAIL.
Exit 0 on PASS, 1 on FAIL.

## File formats
- Both deliverables are UTF-8 text. The outline is GitHub-flavored markdown and must parse as
  such (headings, tables, blockquotes). The script is valid Python 3.13, runs with no args
  defaulting to the sibling outline file.
