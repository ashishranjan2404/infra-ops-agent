# G6 — 04 Spec

## Artifacts & contracts

### A. `artifacts/sources.json`
Validated JSON. Schema:
```json
{
  "sources": [
    {"id": "S1", "kind": "primary|independent", "title": "...", "url": "https://...", "accessed": "2026-06-25"}
  ]
}
```
Invariant: every `url` starts with `https://`; every `id` is unique and matches `^S[0-9]+$`.

### B. `artifacts/claims_table.csv`
Header: `id,claim,type,source_id,our_position`
- `type` ∈ {`capability`, `quant`, `acknowledged_limit`, `not_disclosed`, `structural`}
- `source_id` references a `sources.json` id (must resolve).
- One row per discrete claim/gap.
Invariant: no empty `claim`, no empty `source_id`, every `source_id` exists in sources.json.

### C. `artifacts/bits_ai_sre_analysis.md`
The human-readable analysis. Sections per 03_improved_plan. Inline `[S#]` citations.

### D. `artifacts/validate.py`
```python
def load_sources(path) -> dict[str, dict]: ...   # id -> source; assert https + unique ids
def load_claims(path) -> list[dict]: ...          # csv.DictReader rows
def validate() -> int:
    # 1. every source url startswith https://
    # 2. every claim has non-empty claim + source_id
    # 3. every claim.source_id resolves in sources
    # 4. at least one row with type in {acknowledged_limit, not_disclosed, structural}
    # 5. at least one 'capability' and one 'quant'
    # returns 0 on success, prints PASS/FAIL counts; nonzero exit on failure
```
Run: `python3 artifacts/validate.py` from G6 dir → exit 0, prints `VALIDATE PASS`.

## Test cases
- T1: `sources.json` parses as JSON, all https. 
- T2: `claims_table.csv` parses, every `source_id` ∈ sources.
- T3: at least one of each required `type` present.
- T4: analysis.md references each source id at least once (`[S#]` substring present) — soft check, warn-only.
- T5: each differentiator file path in analysis.md exists on disk (`rex/scoring.py`, `rex/escalate.py`, `sim/engine.py`, `ARCHITECTURE.md`).
