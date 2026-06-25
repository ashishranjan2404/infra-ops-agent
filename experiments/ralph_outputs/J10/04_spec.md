# J10 — Spec

## Deliverable 1: `artifacts/lessons_from_production.md`
Markdown section. Required structure (H2 headings, exact anchors used by the validator):

```
# Lessons from (Pre-)Production: A Deployment-Readiness Analysis
## 0. What "production" means here — and why this is honest
## 1. Lessons that transfer from simulation and eval
   ### L1 — The action layer is the binding safety constraint
   ### L2 — The reward is a gameable proxy, and that is an action-safety problem  [D13]
   ### L3 — Substrate fidelity bounds (and biases) everything we learned          [A16]
   ### L4 — We have no clean outcome ground truth                                  [A9]
## 2. Deployment-readiness gaps (what real prod must validate)
   ### G1 — Trap-action safety under distribution shift
   ### G2 — Shadow-mode results
   ### G3 — MTTR
## 3. Go / No-Go readiness checklist
## 4. Honest bottom line
```

Each gap (G1–G3) MUST contain, as labeled fields:
- **Why it's open** (1–3 sentences, grounded).
- **Validation protocol** (concrete, runnable-in-principle).
- **Acceptance gate** prefixed literally `TARGET — NOT YET MEASURED:` (so no number is ever
  mistaken for an observation).

## Deliverable 2: `artifacts/readiness_gaps.json`
Schema:
```json
{
  "task_id": "J10",
  "claim": "No production deployment has occurred; this is a readiness analysis.",
  "lessons": [
    {"id": "L1", "statement": str, "grounding": [<relpath>...]},
    ...
  ],
  "gaps": [
    {"id": "G1",
     "name": str,
     "why_open": str,
     "validation_protocol": str,
     "acceptance_gate": str,   // must start with "TARGET — NOT YET MEASURED:"
     "grounding": [<relpath>...]}   // each path must exist under repo root
  ],
  "readiness_checklist": [{"item": str, "status": "blocked|partial|done"}]
}
```
Invariants:
- `gaps` contains exactly the ids {G1,G2,G3} with names mentioning, respectively,
  "distribution shift", "shadow", "MTTR".
- Every `grounding` path resolves to a real file under `/Users/mei/rl`.
- Every `acceptance_gate` starts with the literal `TARGET — NOT YET MEASURED:`.

## Deliverable 3: `artifacts/check_readiness.py`
- `load(path) -> dict`
- `verify(data, repo_root) -> list[str]` returns a list of problems (empty == OK):
  checks the invariants above + bans fabricated-prod phrasing in the rendered statements.
- `BANNED_PHRASES = ["in production we", "we deployed to prod", "mttr reduction of",
   "reduced mttr by", "on-call for", "% mttr"]` (case-insensitive).
- `render(data) -> str` one-line-per-gap human summary.
- `main()`: `python3 check_readiness.py [gaps.json] [--md lessons.md]` → prints summary,
  exits 0 if no problems else 1. If `--md` given, also scans the markdown for banned phrases.

## Deliverable 4: `artifacts/test_readiness.py` (pytest, stdlib)
Test cases:
1. `test_json_parses_and_schema` — loads json, required top-level keys present.
2. `test_three_required_gaps` — ids == {G1,G2,G3}; names contain the three required tokens.
3. `test_grounding_paths_exist` — every grounding path under all lessons+gaps exists.
4. `test_acceptance_gates_labeled` — each gate starts with the TARGET prefix.
5. `test_no_fabricated_prod_phrasing_md` — the markdown contains none of BANNED_PHRASES.
6. `test_markdown_has_required_sections` — md contains the G1/G2/G3 + L1..L4 anchors.

## Out of scope (documented blockers, not faked)
Running an actual shadow-mode deployment, a real distribution-shift trap-recall measurement,
or computing a real MTTR delta — all require a live SRE integration we do not have.
