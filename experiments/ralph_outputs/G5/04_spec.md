# G5 — 04 Spec

## Deliverable artifacts
1. `artifacts/positioning_matrix.md` — the matrix document.
2. `artifacts/sources.json` — source registry.
3. `artifacts/validate_matrix.py` — structural validator.

## `sources.json` schema
```json
{
  "sources": {
    "S1": {
      "url": "https://...",
      "who": "us | SREGym | Komodor | Datadog | third-party",
      "claim": "<short claim the source backs>",
      "verification": "primary | vendor-stated | self-reported | third-party-review",
      "as_of": "YYYY-MM"
    }
  }
}
```
- `verification` values:
  - `primary` — peer-reviewed / arXiv / our own repo (ARCHITECTURE.md).
  - `vendor-stated` — vendor marketing/PR; NOT independently verified.
  - `self-reported` — our own internal numbers (small n).
  - `third-party-review` — independent comparison site.

## `positioning_matrix.md` structure
- H1 title + "As of" dates + category disclaimer paragraph.
- One markdown table: header row `| Dimension | SRE-Degrees (us) | SREGym | Komodor | Datadog Bits AI |`,
  then 5 dimension rows. **Every non-empty data cell must contain at least one `[Sn]` tag.**
- 5 prose subsections (one per dimension).
- "Where our position is honestly weaker" subsection.
- "Sources" list rendered from the same `[Sn]` ids.

## Dimensions (row keys, fixed)
1. `Open benchmark`
2. `Trap-action safety`
3. `Training method`
4. `Deployment posture`
5. `Evaluation rigor`

## `validate_matrix.py` contract
```
python3 validate_matrix.py            # validates files in same dir
exit 0  -> all checks pass, prints summary
exit 1  -> a check failed, prints the offending cell/tag
```
Checks:
- C1: the table parses to exactly 5 dimension rows × 4 competitor columns.
- C2: every competitor data cell contains ≥1 `[Sn]` tag (regex `\[S\d+\]`).
- C3: every `[Sn]` tag used anywhere in the matrix resolves to a key in `sources.json`.
- C4: every source in `sources.json` has all 5 required fields and a non-empty `url`.
- C5: at least one competitor cell per commercial vendor (Komodor, Datadog) is flagged
  `vendor-stated` in its backing source (honesty guard).

Functions:
```python
def load_sources(path: str) -> dict
def parse_matrix(md: str) -> list[dict]          # [{dimension, us, sregym, komodor, datadog}]
def extract_tags(text: str) -> set[str]          # {'S1','S4',...}
def validate(md_path: str, src_path: str) -> list[str]   # returns list of error strings ([] = pass)
```

## Test cases for the validator
- T1 (happy path): real files → `validate` returns `[]`, exit 0.
- T2: a cell missing a tag → error mentioning that dimension/column, exit 1.
- T3: a `[S99]` tag with no source → "unresolved tag S99", exit 1.
- T4: a source missing `url` → "source S? missing url", exit 1.
T2–T4 are exercised via inline temp strings in a `--selftest` mode so we don't mutate the real
deliverable.
